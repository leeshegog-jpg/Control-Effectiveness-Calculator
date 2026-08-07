"""Ontology Service -- R1 Milestone 0 scope: read-only lookup only
(schemes, concept search/list). Curator write workflow (propose/publish/
alias) is R1+ scope, not implemented here -- see
docs/knowledge-graph/01-enterprise-knowledge-graph-specification.md §6 for
the full governance workflow this will eventually implement.
"""

import uuid

from sqlalchemy.orm import Session

from app.models.ontology import Concept, Scheme
from app.repositories import ontology_repository


def list_schemes(db: Session) -> list[Scheme]:
    return ontology_repository.list_schemes(db)


def list_concepts(
    db: Session,
    scheme_id: uuid.UUID | None = None,
    query: str | None = None,
    status: str | None = None,
) -> list[Concept]:
    return ontology_repository.list_concepts(db, scheme_id=scheme_id, query=query, status=status)


def get_concept(db: Session, concept_id: uuid.UUID) -> Concept | None:
    return ontology_repository.get_concept(db, concept_id)
