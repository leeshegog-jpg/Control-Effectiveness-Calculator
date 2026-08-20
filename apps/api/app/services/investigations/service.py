"""Investigation service -- CRUD + Neo4j sync.

Sibling of Incident (ADR-003), not a stage under services/incidents --
kept as its own service module deliberately, matching the frozen graph
model's INVESTIGATED_AS shape (Incident->Investigation, not a nested
sub-resource of the Incident aggregate).
"""

import uuid

from neo4j import Driver
from sqlalchemy.orm import Session

from app.graph import sync_service
from app.models.safety import Investigation
from app.repositories import investigations_repository


def get_investigation(db: Session, incident_id: uuid.UUID) -> Investigation | None:
    return investigations_repository.get_investigation_by_incident(db, incident_id)


def create_investigation(
    db: Session,
    graph_driver: Driver,
    *,
    incident_id: uuid.UUID,
    method: str | None,
    findings: str | None,
    contributing_factors: str | None,
) -> Investigation:
    investigation = Investigation(
        incident_id=incident_id,
        method=method,
        findings=findings,
        contributing_factors=contributing_factors,
    )
    investigations_repository.create_investigation(db, investigation)
    db.commit()
    db.refresh(investigation)

    sync_service.sync_investigation(graph_driver, investigation)
    return investigation


def update_investigation(
    db: Session,
    graph_driver: Driver,
    investigation: Investigation,
    *,
    method: str | None = None,
    findings: str | None = None,
    contributing_factors: str | None = None,
) -> Investigation:
    if method is not None:
        investigation.method = method
    if findings is not None:
        investigation.findings = findings
    if contributing_factors is not None:
        investigation.contributing_factors = contributing_factors

    investigations_repository.update_investigation(db, investigation)
    db.commit()
    db.refresh(investigation)

    sync_service.sync_investigation(graph_driver, investigation)
    return investigation
