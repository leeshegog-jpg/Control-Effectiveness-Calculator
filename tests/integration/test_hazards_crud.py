"""Hazards CRUD against a real Postgres + Neo4j -- R1 Milestone 1 Phase 1
acceptance criteria: create/read/update, audit metadata, PostgreSQL
persistence, Neo4j relationship creation. See
docs/implementation-blueprint/16-r1-planning.md.
"""

import uuid


def test_create_read_update_hazard(client, db):
    create_resp = client.post(
        "/hazards",
        json={
            "name": f"Test Hazard {uuid.uuid4()}",
            "description": "Working at heights",
        },
    )
    assert create_resp.status_code == 201
    hazard = create_resp.json()
    assert hazard["is_adh"] is False
    hazard_id = hazard["id"]

    get_resp = client.get(f"/hazards/{hazard_id}")
    assert get_resp.status_code == 200
    assert get_resp.json()["description"] == "Working at heights"

    list_resp = client.get("/hazards")
    assert list_resp.status_code == 200
    assert any(item["id"] == hazard_id for item in list_resp.json()["items"])

    patch_resp = client.patch(
        f"/hazards/{hazard_id}",
        json={
            "name": hazard["name"],
            "description": "Working at heights -- updated exposure",
        },
    )
    assert patch_resp.status_code == 200
    assert patch_resp.json()["description"] == "Working at heights -- updated exposure"

    # Audit metadata (provenance) captured on create.
    from app.models.provenance import ProvenanceRecord

    record = (
        db.query(ProvenanceRecord)
        .filter_by(entity_type="hazard", entity_id=uuid.UUID(hazard_id))
        .one_or_none()
    )
    assert record is not None
    assert record.source_type == "human_entry"


def test_hazard_category_stays_unpopulated(client):
    """Deliberate Milestone 1 scope decision -- see app/models/safety.py
    Hazard.category_concept_id docstring. Not a bug: ontology expansion for
    Hazard Taxonomy requires a future ADR.
    """
    create_resp = client.post(
        "/hazards", json={"name": f"Category Test {uuid.uuid4()}", "description": "d"}
    )
    assert create_resp.json()["category"] is None


def test_hazard_syncs_to_neo4j_with_asset_relationship(client, db, graph_driver):
    from sqlalchemy import text

    park_id = db.execute(
        text("INSERT INTO safety.parks (name) VALUES (:name) RETURNING id"),
        {"name": f"Hazard Test Park {uuid.uuid4()}"},
    ).scalar_one()
    db.commit()

    asset_resp = client.post(
        "/assets",
        json={"name": f"Hazard Test Asset {uuid.uuid4()}", "park_id": str(park_id)},
    )
    asset_id = asset_resp.json()["id"]

    create_resp = client.post(
        "/hazards",
        json={
            "asset_id": asset_id,
            "name": f"Asset-Linked Hazard {uuid.uuid4()}",
            "description": "Crush point on ride mechanism",
        },
    )
    hazard_id = create_resp.json()["id"]

    from app.graph.sync_service import get_hazard_node

    node = get_hazard_node(graph_driver, uuid.UUID(hazard_id))
    assert node is not None
    assert node["asset_pg_id"] == asset_id
