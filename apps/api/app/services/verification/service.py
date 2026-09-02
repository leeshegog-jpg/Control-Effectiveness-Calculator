"""Verification service -- Verification Activity CRUD + R3 overdue
detection, audit metadata (provenance), Neo4j sync.
"""

import uuid
from datetime import date

from neo4j import Driver
from sqlalchemy.orm import Session

from app.graph import sync_service
from app.models.ontology import Concept
from app.models.provenance import ProvenanceRecord
from app.models.safety import Person, VerificationActivity
from app.repositories import verification_repository
from app.services.critical_controls.rules import is_overdue
from app.services.referential import require_exists


def is_activity_overdue(activity: VerificationActivity) -> bool:
    return is_overdue(activity.due_date, activity.last_completed, date.today())


def list_verification_activities(
    db: Session, performance_standard_id: uuid.UUID
) -> list[VerificationActivity]:
    return verification_repository.list_verification_activities(db, performance_standard_id)


def get_verification_activity(
    db: Session, verification_activity_id: uuid.UUID
) -> VerificationActivity | None:
    return verification_repository.get_verification_activity(db, verification_activity_id)


def create_verification_activity(
    db: Session,
    graph_driver: Driver,
    *,
    performance_standard_id: uuid.UUID,
    method_concept_id: uuid.UUID | None,
    frequency: str | None,
    due_date: date | None,
    last_completed: date | None,
    performed_by_person_id: uuid.UUID | None,
    result: str | None,
    created_by_person_id: uuid.UUID | None = None,
) -> VerificationActivity:
    require_exists(db, Concept, method_concept_id, field="method", entity="ontology concept")
    require_exists(
        db, Person, performed_by_person_id, field="performed_by_person_id", entity="person"
    )
    activity = VerificationActivity(
        performance_standard_id=performance_standard_id,
        method_concept_id=method_concept_id,
        frequency=frequency,
        due_date=due_date,
        last_completed=last_completed,
        performed_by_person_id=performed_by_person_id,
        result=result,
    )
    verification_repository.create_verification_activity(db, activity)

    db.add(
        ProvenanceRecord(
            entity_type="verification_activity",
            entity_id=activity.id,
            source_type="human_entry",
            created_by_person_id=created_by_person_id,
        )
    )
    db.commit()
    db.refresh(activity)

    sync_service.sync_verification_activity(graph_driver, activity)
    return activity
