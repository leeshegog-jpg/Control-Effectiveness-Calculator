"""Evidence router (OpenAPI tag). R1 Milestone 2 -- Evidence CRUD nested
under Verification Activity. Contract: docs/knowledge-graph/10-openapi.yaml.
No fixed prefix -- matches the frozen contract's
`/verification-activities/{id}/evidence` path.
"""

import uuid

from fastapi import APIRouter, Depends
from neo4j import Driver
from sqlalchemy.orm import Session

from app.dependencies.db import get_db
from app.dependencies.graph import get_graph_driver
from app.dto.assets import ConceptRef
from app.dto.evidence import EvidenceInput, EvidenceOut
from app.models.ontology import Concept
from app.services.evidence import service

router = APIRouter(tags=["evidence"])


def _to_out(db: Session, evidence) -> EvidenceOut:
    evidence_type = None
    if evidence.type_concept_id is not None:
        concept = db.get(Concept, evidence.type_concept_id)
        evidence_type = ConceptRef(
            concept_id=evidence.type_concept_id,
            pref_label=concept.pref_label if concept else None,
        )
    return EvidenceOut(
        id=evidence.id,
        verification_activity_id=evidence.verification_activity_id,
        type=evidence_type,
        source_document_id=evidence.source_document_id,
        uploaded_by_person_id=evidence.uploaded_by_person_id,
        uploaded_at=evidence.uploaded_at,
        linked_entity_type=evidence.linked_entity_type,
        linked_entity_id=evidence.linked_entity_id,
    )


@router.get("/verification-activities/{activity_id}/evidence", response_model=list[EvidenceOut])
def list_evidence(activity_id: uuid.UUID, db: Session = Depends(get_db)) -> list[EvidenceOut]:
    evidence_items = service.list_evidence(db, activity_id)
    return [_to_out(db, e) for e in evidence_items]


@router.post(
    "/verification-activities/{activity_id}/evidence", response_model=EvidenceOut, status_code=201
)
def create_evidence(
    activity_id: uuid.UUID,
    body: EvidenceInput,
    db: Session = Depends(get_db),
    graph_driver: Driver = Depends(get_graph_driver),
) -> EvidenceOut:
    evidence = service.create_evidence(
        db,
        graph_driver,
        verification_activity_id=activity_id,
        type_concept_id=body.type.concept_id if body.type else None,
        source_document_id=body.source_document_id,
        uploaded_by_person_id=body.uploaded_by_person_id,
        linked_entity_type=body.linked_entity_type,
        linked_entity_id=body.linked_entity_id,
    )
    return _to_out(db, evidence)
