"""Evidence repository. Postgres/SQLAlchemy access only, no business logic."""

import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.safety import Evidence


def list_evidence(db: Session, verification_activity_id: uuid.UUID) -> list[Evidence]:
    stmt = (
        select(Evidence)
        .where(Evidence.verification_activity_id == verification_activity_id)
        .order_by(Evidence.uploaded_at)
    )
    return list(db.execute(stmt).scalars().all())


def list_incident_evidence(db: Session, incident_id: uuid.UUID) -> list[Evidence]:
    stmt = (
        select(Evidence)
        .where(Evidence.linked_entity_type == "incident", Evidence.linked_entity_id == incident_id)
        .order_by(Evidence.uploaded_at)
    )
    return list(db.execute(stmt).scalars().all())


def create_evidence(db: Session, evidence: Evidence) -> Evidence:
    db.add(evidence)
    db.flush()
    return evidence
