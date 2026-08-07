"""Ontology router (OpenAPI tag). R1 Milestone 0: read-only endpoints only
(GET /ontology/schemes, GET /ontology/concepts, GET /ontology/concepts/{id}).
Write paths (POST concepts/publish/aliases, extraction-rules) are R1+ scope
per docs/knowledge-graph/10-openapi.yaml -- not implemented yet.
"""

import uuid

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.dependencies.db import get_db
from app.dto.ontology import ConceptOut, OntologySchemeOut
from app.services.ontology import service

router = APIRouter(prefix="/ontology", tags=["ontology"])


@router.get("/schemes", response_model=list[OntologySchemeOut])
def get_schemes(db: Session = Depends(get_db)) -> list[OntologySchemeOut]:
    return [OntologySchemeOut.model_validate(s) for s in service.list_schemes(db)]


@router.get("/concepts", response_model=list[ConceptOut])
def get_concepts(
    scheme_id: uuid.UUID | None = Query(default=None),
    q: str | None = Query(default=None, description="Search pref_label + aliases"),
    status: str | None = Query(default=None),
    db: Session = Depends(get_db),
) -> list[ConceptOut]:
    concepts = service.list_concepts(db, scheme_id=scheme_id, query=q, status=status)
    return [ConceptOut.model_validate(c) for c in concepts]


@router.get("/concepts/{concept_id}", response_model=ConceptOut)
def get_concept(concept_id: uuid.UUID, db: Session = Depends(get_db)) -> ConceptOut:
    concept = service.get_concept(db, concept_id)
    if concept is None:
        raise HTTPException(status_code=404, detail="Concept not found")
    return ConceptOut.model_validate(concept)
