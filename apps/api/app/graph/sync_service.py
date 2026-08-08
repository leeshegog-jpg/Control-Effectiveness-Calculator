"""Graph Sync Service -- Postgres -> Neo4j propagation.
See docs/knowledge-graph/01-enterprise-knowledge-graph-specification.md §4.

R1 Milestone 0 added Asset + LOCATED_AT. R1 Milestone 1 added Hazard/Risk +
HAS_HAZARD/GIVES_RISE_TO/CLASSIFIED_AS. R1 Milestone 2 adds the Critical
Control Management chain (Control/CriticalControl/PerformanceStandard/
VerificationActivity/Evidence) + MITIGATED_BY/CLASSIFIED_AS_CRITICAL/
GOVERNED_BY/VERIFIED_BY/PRODUCES, matching
docs/knowledge-graph/02-neo4j-node-relationship-model.md §3.1/§3.2/§4.
Postgres remains the system of record -- if this write fails, the Postgres
row still exists and the graph is simply stale until the next sync, never
the other way around.
"""

import uuid

from neo4j import Driver

from app.models.safety import (
    Asset,
    Control,
    CriticalControl,
    Evidence,
    Hazard,
    PerformanceStandard,
    Risk,
    VerificationActivity,
)


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


def sync_control(driver: Driver, control: Control) -> None:
    with driver.session() as session:
        session.run(
            """
            MATCH (r:Risk {pg_id: $risk_pg_id})
            MERGE (c:Control {pg_id: $pg_id})
            SET c.description = $description, c.type = $control_type,
                c.classification = $classification
            MERGE (r)-[:MITIGATED_BY]->(c)
            """,
            pg_id=str(control.id),
            risk_pg_id=str(control.risk_id),
            description=control.description,
            control_type=control.control_type,
            classification=control.classification,
        )


def get_control_node(driver: Driver, control_id: uuid.UUID) -> dict | None:
    with driver.session() as session:
        result = session.run(
            "MATCH (r:Risk)-[:MITIGATED_BY]->(c:Control {pg_id: $pg_id}) "
            "RETURN c.pg_id AS pg_id, c.classification AS classification, r.pg_id AS risk_pg_id",
            pg_id=str(control_id),
        )
        record = result.single()
        return dict(record) if record else None


def sync_critical_control(driver: Driver, critical_control: CriticalControl) -> None:
    with driver.session() as session:
        session.run(
            """
            MATCH (c:Control {pg_id: $control_pg_id})
            MERGE (cc:CriticalControl {pg_id: $pg_id})
            SET cc.farsi_functionality = $farsi_functionality,
                cc.farsi_availability = $farsi_availability,
                cc.farsi_reliability = $farsi_reliability,
                cc.farsi_survivability = $farsi_survivability,
                cc.farsi_interdependency = $farsi_interdependency,
                cc.farsi_score = $farsi_score,
                cc.eia_effective = $eia_effective,
                cc.eia_independent = $eia_independent,
                cc.eia_auditable = $eia_auditable
            MERGE (c)-[:CLASSIFIED_AS_CRITICAL]->(cc)
            """,
            pg_id=str(critical_control.control_id),
            control_pg_id=str(critical_control.control_id),
            farsi_functionality=critical_control.farsi_functionality,
            farsi_availability=critical_control.farsi_availability,
            farsi_reliability=critical_control.farsi_reliability,
            farsi_survivability=critical_control.farsi_survivability,
            farsi_interdependency=critical_control.farsi_interdependency,
            farsi_score=float(critical_control.farsi_score)
            if critical_control.farsi_score is not None
            else None,
            # eia_* live on the parent Control row in Postgres (08 §4a: EIA
            # applies to any candidate control, not just critical ones) --
            # denormalized onto the :CriticalControl node here because that's
            # where 02-neo4j-node-relationship-model.md §3.2 specifies them.
            eia_effective=critical_control.control.eia_effective,
            eia_independent=critical_control.control.eia_independent,
            eia_auditable=critical_control.control.eia_auditable,
        )


def get_critical_control_node(driver: Driver, control_id: uuid.UUID) -> dict | None:
    with driver.session() as session:
        result = session.run(
            "MATCH (c:Control)-[:CLASSIFIED_AS_CRITICAL]->(cc:CriticalControl {pg_id: $pg_id}) "
            "RETURN cc.pg_id AS pg_id, cc.farsi_score AS farsi_score, c.pg_id AS control_pg_id",
            pg_id=str(control_id),
        )
        record = result.single()
        return dict(record) if record else None


def sync_performance_standard(driver: Driver, standard: PerformanceStandard) -> None:
    with driver.session() as session:
        session.run(
            """
            MATCH (cc:CriticalControl {pg_id: $critical_control_pg_id})
            MERGE (ps:PerformanceStandard {pg_id: $pg_id})
            SET ps.requirement_text = $requirement_text,
                ps.measurable_criteria = $measurable_criteria
            MERGE (cc)-[:GOVERNED_BY]->(ps)
            """,
            pg_id=str(standard.id),
            critical_control_pg_id=str(standard.critical_control_id),
            requirement_text=standard.requirement_text,
            measurable_criteria=standard.measurable_criteria,
        )


def sync_verification_activity(driver: Driver, activity: VerificationActivity) -> None:
    with driver.session() as session:
        session.run(
            """
            MATCH (ps:PerformanceStandard {pg_id: $performance_standard_pg_id})
            MERGE (v:VerificationActivity {pg_id: $pg_id})
            SET v.frequency = $frequency, v.due_date = $due_date,
                v.last_completed = $last_completed, v.result = $result
            MERGE (ps)-[:VERIFIED_BY]->(v)
            """,
            pg_id=str(activity.id),
            performance_standard_pg_id=str(activity.performance_standard_id),
            frequency=activity.frequency,
            due_date=activity.due_date.isoformat() if activity.due_date else None,
            last_completed=activity.last_completed.isoformat() if activity.last_completed else None,
            result=activity.result,
        )


def sync_evidence(driver: Driver, evidence: Evidence) -> None:
    if evidence.verification_activity_id is None:
        return  # standalone evidence -- no VerificationActivity to attach PRODUCES to
    with driver.session() as session:
        session.run(
            """
            MATCH (v:VerificationActivity {pg_id: $verification_activity_pg_id})
            MERGE (e:Evidence {pg_id: $pg_id})
            SET e.linked_entity_type = $linked_entity_type
            MERGE (v)-[:PRODUCES]->(e)
            """,
            pg_id=str(evidence.id),
            verification_activity_pg_id=str(evidence.verification_activity_id),
            linked_entity_type=evidence.linked_entity_type,
        )
