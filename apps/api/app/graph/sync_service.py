"""Graph Sync Service -- Postgres -> Neo4j propagation.
See docs/knowledge-graph/01-enterprise-knowledge-graph-specification.md §4.

R1 Milestone 0 scope: Asset node + LOCATED_AT edge only, matching
docs/knowledge-graph/02-neo4j-node-relationship-model.md §3.1/§4. Postgres
remains the system of record -- if this write fails, the Postgres row still
exists and the graph is simply stale until the next sync, never the other
way around.
"""

import uuid

from neo4j import Driver

from app.models.safety import Asset


def sync_asset(driver: Driver, asset: Asset) -> None:
    with driver.session() as session:
        session.run(
            """
            MERGE (a:Asset {pg_id: $pg_id})
            SET a.name = $name, a.status = $status
            WITH a
            OPTIONAL MATCH (a)-[old:LOCATED_AT]->(:Park)
            DELETE old
            WITH a
            FOREACH (_ IN CASE WHEN $park_pg_id IS NOT NULL THEN [1] ELSE [] END |
                MERGE (p:Park {pg_id: $park_pg_id})
                MERGE (a)-[:LOCATED_AT]->(p)
            )
            """,
            pg_id=str(asset.id),
            name=asset.name,
            status=asset.status,
            park_pg_id=str(asset.park_id) if asset.park_id else None,
        )


def get_asset_node(driver: Driver, asset_id: uuid.UUID) -> dict | None:
    with driver.session() as session:
        result = session.run(
            "MATCH (a:Asset {pg_id: $pg_id}) OPTIONAL MATCH (a)-[:LOCATED_AT]->(p:Park) "
            "RETURN a.pg_id AS pg_id, a.name AS name, a.status AS status, p.pg_id AS park_pg_id",
            pg_id=str(asset_id),
        )
        record = result.single()
        return dict(record) if record else None
