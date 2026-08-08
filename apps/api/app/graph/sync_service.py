"""Graph Sync Service -- Postgres -> Neo4j propagation.
See docs/knowledge-graph/01-enterprise-knowledge-graph-specification.md §4.

R1 Milestone 0 added Asset + LOCATED_AT. R1 Milestone 1 adds Hazard/Risk +
HAS_HAZARD/GIVES_RISE_TO/CLASSIFIED_AS, matching
docs/knowledge-graph/02-neo4j-node-relationship-model.md §3.1/§4. Postgres
remains the system of record -- if this write fails, the Postgres row still
exists and the graph is simply stale until the next sync, never the other
way around.
"""

import uuid

from neo4j import Driver

from app.models.safety import Asset, Hazard, Risk


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


def sync_hazard(driver: Driver, hazard: Hazard) -> None:
    with driver.session() as session:
        session.run(
            """
            MERGE (h:Hazard {pg_id: $pg_id})
            SET h.name = $name, h.description = $description,
                h.exposure_pathway = $exposure_pathway,
                h.possible_consequence = $possible_consequence,
                h.date_identified = $date_identified
            WITH h
            OPTIONAL MATCH (:Asset)-[old_hh:HAS_HAZARD]->(h)
            DELETE old_hh
            WITH h
            OPTIONAL MATCH (h)-[old_es:CLASSIFIED_AS]->(:Concept)
            DELETE old_es
            WITH h
            FOREACH (_ IN CASE WHEN $asset_pg_id IS NOT NULL THEN [1] ELSE [] END |
                MERGE (a:Asset {pg_id: $asset_pg_id})
                MERGE (a)-[:HAS_HAZARD]->(h)
            )
            FOREACH (_ IN CASE WHEN $energy_source_concept_id IS NOT NULL THEN [1] ELSE [] END |
                MERGE (c:Concept {id: $energy_source_concept_id})
                MERGE (h)-[:CLASSIFIED_AS]->(c)
            )
            """,
            pg_id=str(hazard.id),
            name=hazard.name,
            description=hazard.description,
            exposure_pathway=hazard.exposure_pathway,
            possible_consequence=hazard.possible_consequence,
            date_identified=hazard.date_identified.isoformat(),
            asset_pg_id=str(hazard.asset_id) if hazard.asset_id else None,
            energy_source_concept_id=(
                str(hazard.energy_source_concept_id) if hazard.energy_source_concept_id else None
            ),
        )


def get_hazard_node(driver: Driver, hazard_id: uuid.UUID) -> dict | None:
    with driver.session() as session:
        result = session.run(
            "MATCH (h:Hazard {pg_id: $pg_id}) "
            "OPTIONAL MATCH (a:Asset)-[:HAS_HAZARD]->(h) "
            "RETURN h.pg_id AS pg_id, h.name AS name, a.pg_id AS asset_pg_id",
            pg_id=str(hazard_id),
        )
        record = result.single()
        return dict(record) if record else None


def sync_risk(driver: Driver, risk: Risk) -> None:
    with driver.session() as session:
        session.run(
            """
            MATCH (h:Hazard {pg_id: $hazard_pg_id})
            MERGE (r:Risk {pg_id: $pg_id})
            SET r.description = $description, r.cause = $cause,
                r.inherent_rating = $inherent_rating, r.current_rating = $current_rating,
                r.status = $status
            MERGE (h)-[:GIVES_RISE_TO]->(r)
            """,
            pg_id=str(risk.id),
            hazard_pg_id=str(risk.hazard_id),
            description=risk.description,
            cause=risk.cause,
            inherent_rating=risk.inherent_rating,
            current_rating=risk.current_rating,
            status=risk.status,
        )


def get_risk_node(driver: Driver, risk_id: uuid.UUID) -> dict | None:
    with driver.session() as session:
        result = session.run(
            "MATCH (h:Hazard)-[:GIVES_RISE_TO]->(r:Risk {pg_id: $pg_id}) "
            "RETURN r.pg_id AS pg_id, r.current_rating AS current_rating, h.pg_id AS hazard_pg_id",
            pg_id=str(risk_id),
        )
        record = result.single()
        return dict(record) if record else None
