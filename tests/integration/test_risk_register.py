"""Risk Register CRUD against a real Postgres + Neo4j -- R1 Milestone 1
Phase 2 acceptance criteria: create/read/update, hazard linkage, R1 rating
derivation, R4 SFARP gate, PostgreSQL persistence, Neo4j GIVES_RISE_TO
relationship. See docs/implementation-blueprint/16-r1-planning.md.
"""

import uuid


def _create_hazard(client, name: str) -> str:
    resp = client.post("/hazards", json={"name": name, "description": "d"})
    return resp.json()["id"]


def test_create_read_update_risk_with_rating_derivation(client, db):
    hazard_id = _create_hazard(client, f"Rating Hazard {uuid.uuid4()}")

    create_resp = client.post(
        "/risks",
        json={
            "hazard_id": hazard_id,
            "description": "Fall from height during maintenance",
            "inherent_likelihood": 4,
            "inherent_consequence": 4,
            "current_likelihood": 2,
            "current_consequence": 3,
        },
    )
    assert create_resp.status_code == 201
    risk = create_resp.json()
    assert risk["inherent_rating"] == "Extreme"  # 4*4=16
    risk_id = risk["id"]

    get_resp = client.get(f"/risks/{risk_id}")
    assert get_resp.status_code == 200
    assert get_resp.json()["current_rating"] == "Medium"  # 2*3=6

    list_resp = client.get("/risks", params={"hazard_id": hazard_id})
    assert list_resp.status_code == 200
    assert any(item["id"] == risk_id for item in list_resp.json()["items"])

    # Re-rate current risk down to Low and confirm derivation updates.
    patch_resp = client.patch(
        f"/risks/{risk_id}",
        json={
            "hazard_id": hazard_id,
            "description": risk["description"],
            "current_likelihood": 1,
            "current_consequence": 2,
        },
    )
    assert patch_resp.status_code == 200
    assert patch_resp.json()["current_rating"] == "Low"  # 1*2=2

    from app.models.provenance import ProvenanceRecord

    record = (
        db.query(ProvenanceRecord)
        .filter_by(entity_type="risk", entity_id=uuid.UUID(risk_id))
        .one_or_none()
    )
    assert record is not None


def test_sfarp_gate_rejects_weak_justification_on_high_current_risk(client):
    hazard_id = _create_hazard(client, f"SFARP Hazard {uuid.uuid4()}")

    resp = client.post(
        "/risks",
        json={
            "hazard_id": hazard_id,
            "description": "Uncontrolled energy release",
            "current_likelihood": 4,
            "current_consequence": 4,  # score 16 -> Extreme
            "sfarp_justification": "The risk is acceptable.",
        },
    )
    assert resp.status_code == 422


def test_sfarp_gate_accepts_substantiated_justification(client):
    hazard_id = _create_hazard(client, f"SFARP Pass Hazard {uuid.uuid4()}")

    resp = client.post(
        "/risks",
        json={
            "hazard_id": hazard_id,
            "description": "Uncontrolled energy release",
            "current_likelihood": 4,
            "current_consequence": 4,
            "sfarp_justification": (
                "Independently verified critical controls reduce residual likelihood; "
                "quarterly verification evidence attached per performance standard."
            ),
        },
    )
    assert resp.status_code == 201
    assert resp.json()["current_rating"] == "Extreme"


def test_risk_syncs_to_neo4j_with_hazard_relationship(client, graph_driver):
    hazard_id = _create_hazard(client, f"Graph Sync Hazard {uuid.uuid4()}")

    create_resp = client.post(
        "/risks", json={"hazard_id": hazard_id, "description": "Graph sync test risk"}
    )
    risk_id = create_resp.json()["id"]

    from app.graph.sync_service import get_risk_node

    node = get_risk_node(graph_driver, uuid.UUID(risk_id))
    assert node is not None
    assert node["hazard_pg_id"] == hazard_id
