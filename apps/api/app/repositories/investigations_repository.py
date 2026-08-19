"""Investigation persistence repository. Postgres/SQLAlchemy access only."""

import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.safety import Investigation


def get_investigation_by_incident(db: Session, incident_id: uuid.UUID) -> Investigation | None:
    stmt = select(Investigation).where(Investigation.incident_id == incident_id)
    return db.execute(stmt).scalar_one_or_none()


def create_investigation(db: Session, investigation: Investigation) -> Investigation:
    db.add(investigation)
    db.flush()
    return investigation


def update_investigation(db: Session, investigation: Investigation) -> Investigation:
    db.flush()
    return investigation
