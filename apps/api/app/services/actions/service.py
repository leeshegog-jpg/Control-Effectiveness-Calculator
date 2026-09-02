"""Actions service -- CRUD + Neo4j sync (bare Action node only).

Incident-linking lives in services/incidents (mirrors link_incident_hazard)
-- Action is a shared, polymorphic entity per ADR-003, not owned by the
Incident domain.
"""

import uuid
from datetime import date

from neo4j import Driver
from sqlalchemy.orm import Session

from app.graph import sync_service
from app.models.ontology import Concept
from app.models.safety import Action, Person
from app.repositories import actions_repository
from app.services.referential import require_exists


def list_actions(
    db: Session, status: str | None, limit: int, offset: int
) -> tuple[list[Action], int]:
    return actions_repository.list_actions(db, status=status, limit=limit, offset=offset)


def get_action(db: Session, action_id: uuid.UUID) -> Action | None:
    return actions_repository.get_action(db, action_id)


def create_action(
    db: Session,
    graph_driver: Driver,
    *,
    source_type_concept_id: uuid.UUID | None,
    source_id: uuid.UUID | None,
    description: str,
    root_cause_category_concept_id: uuid.UUID | None,
    priority: str | None,
    assigned_to_person_id: uuid.UUID | None,
    due_date: date | None,
    status: str | None,
    effectiveness_review: str | None,
    completion_date: date | None = None,
    notes: str | None = None,
) -> Action:
    require_exists(
        db, Concept, source_type_concept_id, field="source_type", entity="ontology concept"
    )
    require_exists(
        db,
        Concept,
        root_cause_category_concept_id,
        field="root_cause_category",
        entity="ontology concept",
    )
    require_exists(
        db, Person, assigned_to_person_id, field="assigned_to_person_id", entity="person"
    )
    action = Action(
        source_type_concept_id=source_type_concept_id,
        source_id=source_id,
        description=description,
        root_cause_category_concept_id=root_cause_category_concept_id,
        priority=priority,
        assigned_to_person_id=assigned_to_person_id,
        due_date=due_date,
        completion_date=completion_date,
        notes=notes,
    )
    if status is not None:
        action.status = status
    if effectiveness_review is not None:
        action.effectiveness_review = effectiveness_review

    actions_repository.create_action(db, action)
    db.commit()
    db.refresh(action)

    sync_service.sync_action(graph_driver, action)
    return action


def update_action(
    db: Session,
    graph_driver: Driver,
    action: Action,
    *,
    source_type_concept_id: uuid.UUID | None = None,
    source_id: uuid.UUID | None = None,
    description: str | None = None,
    root_cause_category_concept_id: uuid.UUID | None = None,
    priority: str | None = None,
    assigned_to_person_id: uuid.UUID | None = None,
    due_date: date | None = None,
    status: str | None = None,
    effectiveness_review: str | None = None,
    completion_date: date | None = None,
    notes: str | None = None,
) -> Action:
    if source_type_concept_id is not None:
        action.source_type_concept_id = source_type_concept_id
    if source_id is not None:
        action.source_id = source_id
    if description is not None:
        action.description = description
    if root_cause_category_concept_id is not None:
        action.root_cause_category_concept_id = root_cause_category_concept_id
    if priority is not None:
        action.priority = priority
    if assigned_to_person_id is not None:
        action.assigned_to_person_id = assigned_to_person_id
    if due_date is not None:
        action.due_date = due_date
    if status is not None:
        action.status = status
    if effectiveness_review is not None:
        action.effectiveness_review = effectiveness_review
    if completion_date is not None:
        action.completion_date = completion_date
    if notes is not None:
        action.notes = notes

    actions_repository.update_action(db, action)
    db.commit()
    db.refresh(action)

    sync_service.sync_action(graph_driver, action)
    return action
