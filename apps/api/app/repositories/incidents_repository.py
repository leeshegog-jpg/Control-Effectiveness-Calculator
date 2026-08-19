"""Incident persistence repository. Postgres/SQLAlchemy access only.

Includes relational incident_hazards (ACR-004 Option A) persistence --
bare link/unlink, no Neo4j REVEALS sync (out of this slice's scope).
"""

import uuid

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.safety import Hazard, Incident, IncidentHazard


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


def list_incident_hazards(db: Session, incident_id: uuid.UUID) -> list[Hazard]:
    """Return the hazards linked to this incident via safety.incident_hazards."""
    stmt = (
        select(Hazard)
        .join(IncidentHazard, IncidentHazard.hazard_id == Hazard.id)
        .where(IncidentHazard.incident_id == incident_id)
        .order_by(Hazard.name)
    )
    return list(db.execute(stmt).scalars().all())


def link_incident_hazard(
    db: Session, incident_id: uuid.UUID, hazard_id: uuid.UUID
) -> IncidentHazard:
    """Create the incident_hazards row; transaction ownership remains with caller."""
    link = IncidentHazard(incident_id=incident_id, hazard_id=hazard_id)
    db.add(link)
    db.flush()
    return link


def unlink_incident_hazard(db: Session, incident_id: uuid.UUID, hazard_id: uuid.UUID) -> bool:
    """Delete the incident_hazards row if present. Returns whether it existed."""
    link = db.get(IncidentHazard, {"incident_id": incident_id, "hazard_id": hazard_id})
    if link is None:
        return False
    db.delete(link)
    db.flush()
    return True
