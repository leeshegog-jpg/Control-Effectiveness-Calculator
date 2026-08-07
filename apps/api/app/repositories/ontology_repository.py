"""Ontology repository. Postgres/SQLAlchemy access only, no business logic --
see app/services/ontology/service.py for classification/lookup rules.
"""

import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.ontology import Concept, ConceptAlias, Scheme


def list_schemes(db: Session) -> list[Scheme]:
    return list(db.execute(select(Scheme).order_by(Scheme.name)).scalars().all())


def list_concepts(
    db: Session,
    scheme_id: uuid.UUID | None = None,
    query: str | None = None,
    status: str | None = None,
) -> list[Concept]:
    stmt = select(Concept)
    if scheme_id is not None:
        stmt = stmt.where(Concept.scheme_id == scheme_id)
    if status is not None:
        stmt = stmt.where(Concept.status == status)
    if query:
        # pref_label match; alias match via EXISTS against concept_aliases
        alias_match = select(ConceptAlias.concept_id).where(
            ConceptAlias.alias_text.ilike(f"%{query}%")
        )
        stmt = stmt.where(Concept.pref_label.ilike(f"%{query}%") | Concept.id.in_(alias_match))
    return list(db.execute(stmt.order_by(Concept.pref_label)).scalars().all())


def get_concept(db: Session, concept_id: uuid.UUID) -> Concept | None:
    return db.get(Concept, concept_id)
