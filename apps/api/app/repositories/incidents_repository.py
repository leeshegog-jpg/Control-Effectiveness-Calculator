"""Incident persistence repository. Postgres/SQLAlchemy access only.

R1 Milestone 3D-1 scope: persistence only. Business rules, DTOs, routers,
Neo4j synchronisation, and notification propagation remain outside this slice.
"""

import uuid

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.safety import Incident


def list_incidents(
    db: Session,
    limit: int,
    offset: int,
) -> tuple[list[Incident], int]:
    """Return incidents ordered newest-first with total count."""
    stmt = select(Incident).order_by(Incident.datetime.desc()).limit(limit).offset(offset)
    count_stmt = select(func.count()).select_from(Incident)
    total = db.execute(count_stmt).scalar_one()
    items = list(db.execute(stmt).scalars().all())
    return items, total


def get_incident(db: Session, incident_id: uuid.UUID) -> Incident | None:
    """Return one Incident by primary key."""
    return db.get(Incident, incident_id)


def create_incident(db: Session, incident: Incident) -> Incident:
    """Add and flush an Incident; transaction ownership remains with caller."""
    db.add(incident)
    db.flush()
    return incident


def update_incident(db: Session, incident: Incident) -> Incident:
    """Flush changes to an existing Incident; transaction ownership remains with caller."""
    db.flush()
    return incident
