"""Incident-Action linking against a real Postgres + Neo4j -- ACR-006
Option A (link existing Action, no create-and-link) + TRIGGERS sync.
"""

import uuid


def _create_incident(client) -> str:
    resp = client.post(
        "/incidents",
        json={
            "datetime": "2026-08-22T09:00:00Z",
            "description": f"Action link test incident {uuid.uuid4()}",
        },
    )
    return resp.json()["id"]


def test_incident_action_link_and_unlink(client):
    incident_id = _create_incident(client)
    action_resp = client.post(
        "/actions", json={"description": f"Linked Action {uuid.uuid4()}"}
    )
    action_id = action_resp.json()["id"]

    link_resp = client.post(
        f"/incidents/{incident_id}/actions", json={"action_id": action_id}
    )
    assert link_resp.status_code == 201

    list_resp = client.get(f"/incidents/{incident_id}/actions")
    assert list_resp.status_code == 200
    assert any(a["id"] == action_id for a in list_resp.json())

    unlink_resp = client.delete(f"/incidents/{incident_id}/actions/{action_id}")
    assert unlink_resp.status_code == 204

    list_resp_after = client.get(f"/incidents/{incident_id}/actions")
    assert not any(a["id"] == action_id for a in list_resp_after.json())


def test_incident_action_unlink_missing_link_returns_404(client):
    incident_id = _create_incident(client)
    action_resp = client.post(
        "/actions", json={"description": f"Unlinked Action {uuid.uuid4()}"}
    )
    action_id = action_resp.json()["id"]

    resp = client.delete(f"/incidents/{incident_id}/actions/{action_id}")
    assert resp.status_code == 404


def test_incident_action_link_for_missing_incident_returns_404(client):
    action_resp = client.post(
        "/actions", json={"description": f"Orphan test {uuid.uuid4()}"}
    )
    action_id = action_resp.json()["id"]

    resp = client.post(
        f"/incidents/{uuid.uuid4()}/actions", json={"action_id": action_id}
    )
    assert resp.status_code == 404


def test_incident_action_link_syncs_triggers_to_neo4j(client, graph_driver):
    incident_id = _create_incident(client)
    action_resp = client.post(
        "/actions", json={"description": f"TRIGGERS sync test {uuid.uuid4()}"}
    )
    action_id = action_resp.json()["id"]

    client.post(f"/incidents/{incident_id}/actions", json={"action_id": action_id})

    with graph_driver.session() as session:
        result = session.run(
            "MATCH (:Incident {pg_id: $incident_pg_id})-[:TRIGGERS]->(:Action {pg_id: $action_pg_id}) "
            "RETURN count(*) AS c",
            incident_pg_id=incident_id,
            action_pg_id=action_id,
        )
        assert result.single()["c"] == 1

    client.delete(f"/incidents/{incident_id}/actions/{action_id}")

    with graph_driver.session() as session:
        result = session.run(
            "MATCH (:Incident {pg_id: $incident_pg_id})-[:TRIGGERS]->(:Action {pg_id: $action_pg_id}) "
            "RETURN count(*) AS c",
            incident_pg_id=incident_id,
            action_pg_id=action_id,
        )
        assert result.single()["c"] == 0
