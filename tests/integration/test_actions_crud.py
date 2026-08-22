"""Actions CRUD against a real Postgres + Neo4j -- "R1 Incident Management --
Action API, Incident Linking & TRIGGERS Sync" slice. completion_date/notes
are deliberately not exercised here -- excluded from this slice's OpenAPI
surface (ACR-006).
"""

import uuid


def test_create_read_update_action(client):
    create_resp = client.post(
        "/actions",
        json={"description": f"Test action {uuid.uuid4()}"},
    )
    assert create_resp.status_code == 201
    action = create_resp.json()
    assert action["status"] == "Open"
    assert action["effectiveness_review"] == "Not Reviewed"
    action_id = action["id"]

    list_resp = client.get("/actions")
    assert list_resp.status_code == 200
    assert any(item["id"] == action_id for item in list_resp.json())

    patch_resp = client.patch(
        f"/actions/{action_id}",
        json={"description": "Updated description", "status": "In Progress"},
    )
    assert patch_resp.status_code == 200
    assert patch_resp.json()["description"] == "Updated description"
    assert patch_resp.json()["status"] == "In Progress"


def test_action_list_filters_by_status(client):
    client.post(
        "/actions",
        json={"description": f"Closed action {uuid.uuid4()}", "status": "Closed"},
    )
    open_resp = client.post(
        "/actions", json={"description": f"Open action {uuid.uuid4()}"}
    )
    open_id = open_resp.json()["id"]

    list_resp = client.get("/actions", params={"status": "Open"})
    assert list_resp.status_code == 200
    assert any(a["id"] == open_id for a in list_resp.json())
    assert all(a["status"] == "Open" for a in list_resp.json())


def test_action_update_not_found(client):
    resp = client.patch(f"/actions/{uuid.uuid4()}", json={"description": "d"})
    assert resp.status_code == 404


def test_action_syncs_to_neo4j_as_bare_node(client, graph_driver):
    create_resp = client.post(
        "/actions", json={"description": f"Neo4j sync test {uuid.uuid4()}"}
    )
    action_id = create_resp.json()["id"]

    from app.graph.sync_service import get_action_node

    node = get_action_node(graph_driver, uuid.UUID(action_id))
    assert node is not None
    assert node["status"] == "Open"
