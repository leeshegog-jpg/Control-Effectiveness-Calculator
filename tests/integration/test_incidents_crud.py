"""Incidents CRUD against a real Postgres + Neo4j -- API/service/graph-sync
acceptance criteria for the "R1 Incident Management -- API, Service & Graph
Synchronisation" slice. Neo4j hazard-link (REVEALS) sync and
Investigation/Action wiring are deliberately not covered here -- out of
this slice's scope. See
docs/implementation-blueprint/22-r1-incident-reconciliation-decision-review.md.
"""

import uuid


def test_create_read_update_incident(client, db):
    create_resp = client.post(
        "/incidents",
        json={
            "datetime": "2026-08-20T09:00:00Z",
            "description": f"Test incident {uuid.uuid4()}",
        },
    )
    assert create_resp.status_code == 201
    incident = create_resp.json()
    assert incident["whsq_notified"] == "Not yet assessed"
    assert incident["osr_notified"] == "Not applicable / under assessment"
    assert incident["is_notifiable_incident"] is False
    incident_id = incident["id"]

    get_resp = client.get(f"/incidents/{incident_id}")
    assert get_resp.status_code == 200
    assert get_resp.json()["description"] == incident["description"]

    list_resp = client.get("/incidents")
    assert list_resp.status_code == 200
    assert any(item["id"] == incident_id for item in list_resp.json()["items"])

    patch_resp = client.patch(
        f"/incidents/{incident_id}",
        json={
            "datetime": incident["datetime"],
            "description": "Updated description",
            "is_notifiable_incident": True,
        },
    )
    assert patch_resp.status_code == 200
    assert patch_resp.json()["description"] == "Updated description"
    assert patch_resp.json()["is_notifiable_incident"] is True


def test_incident_type_stays_unpopulated(client):
    """Ontology deferral, ADR-004 -- mirrors the Hazard Taxonomy precedent."""
    create_resp = client.post(
        "/incidents",
        json={"datetime": "2026-08-20T09:00:00Z", "description": "d"},
    )
    assert create_resp.json()["incident_type"] is None


def test_incident_not_found(client):
    assert client.get(f"/incidents/{uuid.uuid4()}").status_code == 404


def test_incident_syncs_to_neo4j_as_bare_node(client, graph_driver):
    create_resp = client.post(
        "/incidents",
        json={
            "datetime": "2026-08-20T09:00:00Z",
            "description": f"Neo4j sync test {uuid.uuid4()}",
            "is_notifiable_incident": True,
        },
    )
    incident_id = create_resp.json()["id"]

    from app.graph.sync_service import get_incident_node

    node = get_incident_node(graph_driver, uuid.UUID(incident_id))
    assert node is not None
    assert node["is_notifiable_incident"] is True


def test_incident_hazard_link_and_unlink(client, db):
    incident_resp = client.post(
        "/incidents",
        json={
            "datetime": "2026-08-20T09:00:00Z",
            "description": f"Hazard link test {uuid.uuid4()}",
        },
    )
    incident_id = incident_resp.json()["id"]

    hazard_resp = client.post(
        "/hazards",
        json={"name": f"Linked Hazard {uuid.uuid4()}", "description": "d"},
    )
    hazard_id = hazard_resp.json()["id"]

    link_resp = client.post(
        f"/incidents/{incident_id}/hazards", json={"hazard_id": hazard_id}
    )
    assert link_resp.status_code == 201

    list_resp = client.get(f"/incidents/{incident_id}/hazards")
    assert list_resp.status_code == 200
    assert any(h["id"] == hazard_id for h in list_resp.json())

    unlink_resp = client.delete(f"/incidents/{incident_id}/hazards/{hazard_id}")
    assert unlink_resp.status_code == 204

    list_resp_after = client.get(f"/incidents/{incident_id}/hazards")
    assert not any(h["id"] == hazard_id for h in list_resp_after.json())


def test_incident_hazard_unlink_missing_link_returns_404(client):
    incident_resp = client.post(
        "/incidents",
        json={
            "datetime": "2026-08-20T09:00:00Z",
            "description": f"No link {uuid.uuid4()}",
        },
    )
    incident_id = incident_resp.json()["id"]
    hazard_resp = client.post(
        "/hazards", json={"name": f"Unlinked Hazard {uuid.uuid4()}", "description": "d"}
    )
    hazard_id = hazard_resp.json()["id"]

    resp = client.delete(f"/incidents/{incident_id}/hazards/{hazard_id}")
    assert resp.status_code == 404


def test_incident_hazard_link_does_not_sync_reveals_to_neo4j(client, graph_driver):
    """Explicit boundary check: hazard-link is relational-only in this slice."""
    incident_resp = client.post(
        "/incidents",
        json={
            "datetime": "2026-08-20T09:00:00Z",
            "description": f"No REVEALS {uuid.uuid4()}",
        },
    )
    incident_id = incident_resp.json()["id"]
    hazard_resp = client.post(
        "/hazards", json={"name": f"No-Sync Hazard {uuid.uuid4()}", "description": "d"}
    )
    hazard_id = hazard_resp.json()["id"]

    client.post(f"/incidents/{incident_id}/hazards", json={"hazard_id": hazard_id})

    with graph_driver.session() as session:
        result = session.run(
            "MATCH (:Incident {pg_id: $incident_pg_id})-[:REVEALS]->(:Hazard {pg_id: $hazard_pg_id}) "
            "RETURN count(*) AS c",
            incident_pg_id=incident_id,
            hazard_pg_id=hazard_id,
        )
        assert result.single()["c"] == 0
