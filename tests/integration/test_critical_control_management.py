"""Critical Control Management CRUD against a real Postgres + Neo4j -- R1
Milestone 2 acceptance criteria: Control/Support/Verification
classification (3-gate workflow), EIA test, critical-control test, FARSI
scoring, Performance Standard + Verification Activity + Evidence CRUD,
computed Control Health state, PostgreSQL persistence, Neo4j relationship
creation across the full chain. See
docs/implementation-blueprint/16-r1-planning.md and
docs/implementation-blueprint/17-r1-milestone-2-ccm-discovery-reconciliation.md.
"""

import uuid


def _create_hazard_risk(client) -> str:
    hazard_id = client.post(
        "/hazards", json={"name": f"CCM Hazard {uuid.uuid4()}", "description": "d"}
    ).json()["id"]
    risk_id = client.post(
        "/risks", json={"hazard_id": hazard_id, "description": "CCM test risk"}
    ).json()["id"]
    return risk_id


def test_control_passes_all_gates_becomes_critical_with_full_chain(
    client, db, graph_driver
):
    risk_id = _create_hazard_risk(client)

    create_resp = client.post(
        f"/risks/{risk_id}/controls",
        json={
            "risk_id": risk_id,
            "description": "Lap bar restraint",
            "control_type": "Prevention",
        },
    )
    assert create_resp.status_code == 201
    control = create_resp.json()
    assert control["classification"] is None
    control_id = control["id"]

    gate_resp = client.post(
        f"/controls/{control_id}/gate-test",
        json={"gate_1": True, "gate_2": True, "gate_3": True},
    )
    assert gate_resp.status_code == 200
    assert gate_resp.json()["classification"] == "Control"

    eia_resp = client.post(
        f"/controls/{control_id}/eia-test",
        json={"eia_effective": True, "eia_independent": True, "eia_auditable": True},
    )
    assert eia_resp.status_code == 200
    assert eia_resp.json()["eia_effective"] is True

    cct_resp = client.post(
        f"/controls/{control_id}/critical-control-test", json={"is_critical": True}
    )
    assert cct_resp.status_code == 201
    critical_control = cct_resp.json()
    assert critical_control["control_id"] == control_id
    assert critical_control["health_state"] == "Unverified"

    farsi_resp = client.patch(
        f"/critical-controls/{control_id}",
        json={
            "farsi_functionality": 5,
            "farsi_availability": 5,
            "farsi_reliability": 1,
            "farsi_survivability": 5,
            "farsi_interdependency": 5,
        },
    )
    assert farsi_resp.status_code == 200
    assert farsi_resp.json()["farsi_score"] == 4.2  # (5+5+1+5+5)/5

    ps_resp = client.post(
        f"/critical-controls/{control_id}/performance-standards",
        json={
            "requirement_text": "Lap bar must lock within 0.5s of activation",
            "measurable_criteria": "100% lock engagement on functional test",
        },
    )
    assert ps_resp.status_code == 201
    standard_id = ps_resp.json()["id"]

    va_resp = client.post(
        f"/performance-standards/{standard_id}/verification-activities",
        json={"frequency": "Daily", "due_date": "2020-01-01"},
    )
    assert va_resp.status_code == 201
    activity = va_resp.json()
    activity_id = activity["id"]
    assert activity["overdue"] is True  # due_date in the past, never completed

    evidence_resp = client.post(
        f"/verification-activities/{activity_id}/evidence",
        json={"linked_entity_type": "verification_activity"},
    )
    assert evidence_resp.status_code == 201

    health_resp = client.get(f"/critical-controls/{control_id}")
    assert health_resp.status_code == 200
    # Never completed -> Unverified, regardless of evidence or overdue status.
    assert health_resp.json()["health_state"] == "Unverified"

    from app.models.provenance import ProvenanceRecord

    for entity_type, entity_id in [
        ("control", uuid.UUID(control_id)),
        ("critical_control", uuid.UUID(control_id)),
        ("performance_standard", uuid.UUID(standard_id)),
        ("verification_activity", uuid.UUID(activity_id)),
    ]:
        record = (
            db.query(ProvenanceRecord)
            .filter_by(entity_type=entity_type, entity_id=entity_id)
            .one_or_none()
        )
        assert record is not None, f"missing provenance for {entity_type}"

    from app.graph.sync_service import get_control_node, get_critical_control_node

    control_node = get_control_node(graph_driver, uuid.UUID(control_id))
    assert control_node is not None
    assert control_node["classification"] == "Control"
    assert control_node["risk_pg_id"] == risk_id

    critical_node = get_critical_control_node(graph_driver, uuid.UUID(control_id))
    assert critical_node is not None
    assert critical_node["control_pg_id"] == control_id


def test_control_failing_gates_classifies_as_support(client):
    risk_id = _create_hazard_risk(client)
    control_id = client.post(
        f"/risks/{risk_id}/controls",
        json={
            "risk_id": risk_id,
            "description": "Toolbox talk",
            "control_type": "Prevention",
        },
    ).json()["id"]

    gate_resp = client.post(
        f"/controls/{control_id}/gate-test",
        json={
            "gate_1": False,
            "gate_2": True,
            "gate_3": True,
            "is_verification_check": False,
        },
    )
    assert gate_resp.json()["classification"] == "Support"

    # Support-classified controls cannot pass the critical-control test.
    cct_resp = client.post(
        f"/controls/{control_id}/critical-control-test", json={"is_critical": True}
    )
    assert cct_resp.status_code == 409


def test_control_verification_check_classifies_as_verification(client):
    risk_id = _create_hazard_risk(client)
    control_id = client.post(
        f"/risks/{risk_id}/controls",
        json={
            "risk_id": risk_id,
            "description": "Daily brake inspection",
            "control_type": "Prevention",
        },
    ).json()["id"]

    gate_resp = client.post(
        f"/controls/{control_id}/gate-test",
        json={
            "gate_1": False,
            "gate_2": True,
            "gate_3": True,
            "is_verification_check": True,
        },
    )
    assert gate_resp.json()["classification"] == "Verification"


def test_health_state_healthy_when_verification_current_and_evidenced(client):
    risk_id = _create_hazard_risk(client)
    control_id = client.post(
        f"/risks/{risk_id}/controls",
        json={
            "risk_id": risk_id,
            "description": "Zone detection interlock",
            "control_type": "Prevention",
        },
    ).json()["id"]
    client.post(
        f"/controls/{control_id}/gate-test",
        json={"gate_1": True, "gate_2": True, "gate_3": True},
    )
    client.post(
        f"/controls/{control_id}/critical-control-test", json={"is_critical": True}
    )
    standard_id = client.post(
        f"/critical-controls/{control_id}/performance-standards",
        json={"requirement_text": "Interlock must trip within 200ms"},
    ).json()["id"]
    activity_id = client.post(
        f"/performance-standards/{standard_id}/verification-activities",
        json={
            "frequency": "Monthly",
            "due_date": "2099-01-01",
            "last_completed": "2026-08-01",
        },
    ).json()["id"]
    client.post(
        f"/verification-activities/{activity_id}/evidence",
        json={"linked_entity_type": "verification_activity"},
    )

    resp = client.get(f"/critical-controls/{control_id}")
    assert resp.json()["health_state"] == "Healthy"
