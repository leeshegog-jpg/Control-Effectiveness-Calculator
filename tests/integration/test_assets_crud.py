"""Assets CRUD against a real Postgres + Neo4j -- R1 Milestone 0 acceptance
criteria: create/read/update/retire, audit metadata, Postgres persistence,
Neo4j relationship creation. See docs/implementation-blueprint/16-r1-planning.md.
"""

import uuid


def test_create_read_update_retire_asset(client, db):
    create_resp = client.post("/assets", json={"name": f"Test Ride {uuid.uuid4()}"})
    assert create_resp.status_code == 201
    asset = create_resp.json()
    assert asset["status"] == "active"
    asset_id = asset["id"]

    get_resp = client.get(f"/assets/{asset_id}")
    assert get_resp.status_code == 200
    assert get_resp.json()["name"] == asset["name"]

    list_resp = client.get("/assets")
    assert list_resp.status_code == 200
    assert list_resp.json()["total"] >= 1
    assert any(item["id"] == asset_id for item in list_resp.json()["items"])

    # Retire (deactivate) -- no separate endpoint, PATCH status per the
    # approved OpenAPI contract (AssetInput.status).
    patch_resp = client.patch(
        f"/assets/{asset_id}", json={"name": asset["name"], "status": "retired"}
    )
    assert patch_resp.status_code == 200
    assert patch_resp.json()["status"] == "retired"

    # Audit metadata (provenance) captured on create.
    from app.models.provenance import ProvenanceRecord

    record = (
        db.query(ProvenanceRecord)
        .filter_by(entity_type="asset", entity_id=uuid.UUID(asset_id))
        .one_or_none()
    )
    assert record is not None
    assert record.source_type == "human_entry"


def test_asset_syncs_to_neo4j(client, graph_driver):
    from app.graph.sync_service import get_asset_node

    create_resp = client.post(
        "/assets", json={"name": f"Graph Sync Test {uuid.uuid4()}"}
    )
    asset_id = create_resp.json()["id"]

    node = get_asset_node(graph_driver, uuid.UUID(asset_id))
    assert node is not None
    assert node["name"] == create_resp.json()["name"]
    assert node["status"] == "active"


def test_asset_park_relationship_in_neo4j(client, db, graph_driver):
    from sqlalchemy import text

    park_id = db.execute(
        text("INSERT INTO safety.parks (name) VALUES (:name) RETURNING id"),
        {"name": f"Test Park {uuid.uuid4()}"},
    ).scalar_one()
    db.commit()

    create_resp = client.post(
        "/assets", json={"name": f"Park Asset {uuid.uuid4()}", "park_id": str(park_id)}
    )
    asset_id = create_resp.json()["id"]

    from app.graph.sync_service import get_asset_node

    node = get_asset_node(graph_driver, uuid.UUID(asset_id))
    assert node is not None
    assert node["park_pg_id"] == str(park_id)
