"""Investigation CRUD against a real Postgres + Neo4j -- "R1 Incident
Management -- Investigation API & Hazard-Link Graph Sync" slice.
Action/Evidence wiring remain out of scope.
"""

import uuid


def _create_incident(client) -> str:
    resp = client.post(
        "/incidents",
        json={
            "datetime": "2026-08-20T09:00:00Z",
            "description": f"Investigation test incident {uuid.uuid4()}",
        },
    )
    return resp.json()["id"]


def test_investigation_not_found_before_creation(client):
    incident_id = _create_incident(client)
    resp = client.get(f"/incidents/{incident_id}/investigation")
    assert resp.status_code == 404


def test_create_read_update_investigation(client):
    incident_id = _create_incident(client)

    create_resp = client.post(
        f"/incidents/{incident_id}/investigation",
        json={"method": "ICAM", "findings": "Initial findings"},
    )
    assert create_resp.status_code == 201
    investigation = create_resp.json()
    assert investigation["incident_id"] == incident_id
    assert investigation["method"] == "ICAM"

    get_resp = client.get(f"/incidents/{incident_id}/investigation")
    assert get_resp.status_code == 200
    assert get_resp.json()["findings"] == "Initial findings"

    patch_resp = client.patch(
        f"/incidents/{incident_id}/investigation",
        json={"findings": "Updated findings", "contributing_factors": "Fatigue"},
    )
    assert patch_resp.status_code == 200
    assert patch_resp.json()["findings"] == "Updated findings"
    assert patch_resp.json()["contributing_factors"] == "Fatigue"
    assert patch_resp.json()["method"] == "ICAM"  # unspecified fields left unchanged


def test_investigation_create_conflicts_on_second_call(client):
    incident_id = _create_incident(client)
    client.post(f"/incidents/{incident_id}/investigation", json={"method": "ICAM"})

    second_resp = client.post(
        f"/incidents/{incident_id}/investigation", json={"method": "5-Why"}
    )
    assert second_resp.status_code == 409


def test_investigation_for_missing_incident_returns_404(client):
    resp = client.get(f"/incidents/{uuid.uuid4()}/investigation")
    assert resp.status_code == 404


def test_investigation_syncs_to_neo4j_with_investigated_as(client, graph_driver):
    incident_id = _create_incident(client)
    client.post(
        f"/incidents/{incident_id}/investigation",
        json={"method": "ICAM", "findings": "Neo4j sync test"},
    )

    from app.graph.sync_service import get_investigation_node

    node = get_investigation_node(graph_driver, uuid.UUID(incident_id))
    assert node is not None
    assert node["method"] == "ICAM"
