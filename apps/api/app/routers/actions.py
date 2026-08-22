"""Actions router (OpenAPI tag). Contract: docs/knowledge-graph/10-openapi.yaml.

Incident-scoped linking (/incidents/{id}/actions*) lives in
routers/incidents.py -- Action itself is a shared, polymorphic entity
(ADR-003), not owned by the Incident domain.
"""

import uuid

from fastapi import APIRouter, Depends, HTTPException, Query
from neo4j import Driver
from sqlalchemy.orm import Session

from app.dependencies.db import get_db
from app.dependencies.graph import get_graph_driver
from app.dto.actions import ActionInput, ActionOut
from app.dto.assets import ConceptRef
from app.models.ontology import Concept
from app.services.actions import service

router = APIRouter(prefix="/actions", tags=["actions"])


def _concept_ref(db: Session, concept_id: uuid.UUID | None) -> ConceptRef | None:
    if concept_id is None:
        return None
    concept = db.get(Concept, concept_id)
    return ConceptRef(concept_id=concept_id, pref_label=concept.pref_label if concept else None)


def _to_out(db: Session, action) -> ActionOut:
    return ActionOut(
        id=action.id,
        source_type=_concept_ref(db, action.source_type_concept_id),
        source_id=action.source_id,
        description=action.description,
        root_cause_category=_concept_ref(db, action.root_cause_category_concept_id),
        priority=action.priority,
        assigned_to_person_id=action.assigned_to_person_id,
        due_date=action.due_date,
        status=action.status,
        effectiveness_review=action.effectiveness_review,
    )


@router.get("", response_model=list[ActionOut])
def list_actions(
    status: str | None = Query(default=None),
    limit: int = Query(default=50, le=200),
    offset: int = Query(default=0),
    db: Session = Depends(get_db),
) -> list[ActionOut]:
    items, _ = service.list_actions(db, status=status, limit=limit, offset=offset)
    return [_to_out(db, a) for a in items]


@router.post("", response_model=ActionOut, status_code=201)
def create_action(
    body: ActionInput,
    db: Session = Depends(get_db),
    graph_driver: Driver = Depends(get_graph_driver),
) -> ActionOut:
    action = service.create_action(
        db,
        graph_driver,
        source_type_concept_id=body.source_type.concept_id if body.source_type else None,
        source_id=body.source_id,
        description=body.description,
        root_cause_category_concept_id=(
            body.root_cause_category.concept_id if body.root_cause_category else None
        ),
        priority=body.priority,
        assigned_to_person_id=body.assigned_to_person_id,
        due_date=body.due_date,
        status=body.status,
        effectiveness_review=body.effectiveness_review,
    )
    return _to_out(db, action)


@router.patch("/{action_id}", response_model=ActionOut)
def update_action(
    action_id: uuid.UUID,
    body: ActionInput,
    db: Session = Depends(get_db),
    graph_driver: Driver = Depends(get_graph_driver),
) -> ActionOut:
    action = service.get_action(db, action_id)
    if action is None:
        raise HTTPException(status_code=404, detail="Action not found")
    updated = service.update_action(
        db,
        graph_driver,
        action,
        source_type_concept_id=body.source_type.concept_id if body.source_type else None,
        source_id=body.source_id,
        description=body.description,
        root_cause_category_concept_id=(
            body.root_cause_category.concept_id if body.root_cause_category else None
        ),
        priority=body.priority,
        assigned_to_person_id=body.assigned_to_person_id,
        due_date=body.due_date,
        status=body.status,
        effectiveness_review=body.effectiveness_review,
    )
    return _to_out(db, updated)
