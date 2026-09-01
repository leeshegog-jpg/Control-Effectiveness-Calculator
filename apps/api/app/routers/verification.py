"""Verification router (OpenAPI tag). R1 Milestone 2 -- Verification
Activity CRUD nested under Performance Standard. Contract:
docs/knowledge-graph/10-openapi.yaml. No fixed prefix -- matches the
frozen contract's `/performance-standards/{id}/verification-activities` path.
"""

import uuid

from fastapi import APIRouter, Depends, HTTPException
from neo4j import Driver
from sqlalchemy.orm import Session

from app.dependencies.db import get_db
from app.dependencies.graph import get_graph_driver
from app.dto.assets import ConceptRef
from app.dto.verification import VerificationActivityInput, VerificationActivityOut
from app.models.ontology import Concept
from app.repositories import critical_controls_repository
from app.services.referential import ReferentialIntegrityError
from app.services.verification import service

router = APIRouter(tags=["verification"])


def _to_out(db: Session, activity) -> VerificationActivityOut:
    method = None
    if activity.method_concept_id is not None:
        concept = db.get(Concept, activity.method_concept_id)
        method = ConceptRef(
            concept_id=activity.method_concept_id,
            pref_label=concept.pref_label if concept else None,
        )
    return VerificationActivityOut(
        id=activity.id,
        performance_standard_id=activity.performance_standard_id,
        method=method,
        frequency=activity.frequency,
        due_date=activity.due_date,
        last_completed=activity.last_completed,
        performed_by_person_id=activity.performed_by_person_id,
        result=activity.result,
        overdue=service.is_activity_overdue(activity),
        created_at=activity.created_at,
        updated_at=activity.updated_at,
    )


@router.get(
    "/performance-standards/{standard_id}/verification-activities",
    response_model=list[VerificationActivityOut],
)
def list_verification_activities(
    standard_id: uuid.UUID, db: Session = Depends(get_db)
) -> list[VerificationActivityOut]:
    activities = service.list_verification_activities(db, standard_id)
    return [_to_out(db, a) for a in activities]


@router.post(
    "/performance-standards/{standard_id}/verification-activities",
    response_model=VerificationActivityOut,
    status_code=201,
)
def create_verification_activity(
    standard_id: uuid.UUID,
    body: VerificationActivityInput,
    db: Session = Depends(get_db),
    graph_driver: Driver = Depends(get_graph_driver),
) -> VerificationActivityOut:
    if critical_controls_repository.get_performance_standard(db, standard_id) is None:
        raise HTTPException(status_code=404, detail="Performance standard not found")
    try:
        activity = service.create_verification_activity(
            db,
            graph_driver,
            performance_standard_id=standard_id,
            method_concept_id=body.method.concept_id if body.method else None,
            frequency=body.frequency,
            due_date=body.due_date,
            last_completed=body.last_completed,
            performed_by_person_id=body.performed_by_person_id,
            result=body.result,
        )
    except ReferentialIntegrityError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    return _to_out(db, activity)
