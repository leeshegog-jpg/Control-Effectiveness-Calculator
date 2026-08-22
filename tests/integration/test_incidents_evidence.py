"""Incident-scoped Evidence against a real Postgres + Neo4j -- "R1 Incident
Management -- Evidence API Wiring & Incident-Scoped Evidence" slice.
Reuses the existing Milestone-2 Evidence service/repository; no schema,
OpenAPI, or Neo4j model change. No Incident->Evidence graph edge -- Evidence
stays a bare synced node, verification_activity_id absent (None) for
incident-linked evidence.
"""

import uuid


def _create_incident(client) -> str:
    resp = client.post(
        "/incidents",
        json={
            "datetime": "2026-08-22T09:00:00Z",
            "description": f"Evidence test incident {uuid.uuid4()}",
        },
    )
    return resp.json()["id"]


def test_incident_evidence_empty_before_creation(client):
    incident_id = _create_incident(client)
    resp = client.get(f"/incidents/{incident_id}/evidence")
    assert resp.status_code == 200
    assert resp.json() == []


def test_create_and_list_incident_evidence(client):
    incident_id = _create_incident(client)

    create_resp = client.post(f"/incidents/{incident_id}/evidence", json={})
    assert create_resp.status_code == 201
    evidence = create_resp.json()
    assert evidence["linked_entity_type"] == "incident"
    assert evidence["linked_entity_id"] == incident_id
    assert evidence["verification_activity_id"] is None

    list_resp = client.get(f"/incidents/{incident_id}/evidence")
    assert list_resp.status_code == 200
    assert any(e["id"] == evidence["id"] for e in list_resp.json())


def test_incident_evidence_for_missing_incident_returns_404(client):
    resp = client.get(f"/incidents/{uuid.uuid4()}/evidence")
    assert resp.status_code == 404

    resp = client.post(f"/incidents/{uuid.uuid4()}/evidence", json={})
    assert resp.status_code == 404


def test_incident_evidence_syncs_as_bare_node_no_incident_edge(client, graph_driver):
    incident_id = _create_incident(client)
    create_resp = client.post(f"/incidents/{incident_id}/evidence", json={})
    evidence_id = create_resp.json()["id"]

    with graph_driver.session() as session:
        node_result = session.run(
            "MATCH (e:Evidence {pg_id: $evidence_pg_id}) RETURN count(*) AS c",
            evidence_pg_id=evidence_id,
        )
        assert node_result.single()["c"] == 1

        edge_result = session.run(
            "MATCH (:Incident {pg_id: $incident_pg_id})-[r]->(:Evidence {pg_id: $evidence_pg_id}) "
            "RETURN count(r) AS c",
            incident_pg_id=incident_id,
            evidence_pg_id=evidence_id,
        )
        assert edge_result.single()["c"] == 0
