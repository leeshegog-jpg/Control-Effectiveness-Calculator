"""Ontology request/response DTOs. Companion to docs/knowledge-graph/10-openapi.yaml
`Ontology` tag -- field shapes match the `OntologyScheme` and `Concept` schemas
there exactly. R1 Milestone 0 implements the read-only GET paths only.
"""

import uuid
from datetime import date, datetime
from enum import StrEnum

from pydantic import BaseModel, ConfigDict


class ConceptStatus(StrEnum):
    """Query-param constraint for `GET /ontology/concepts?status=`. Mirrors
    `ontology.concept_status` (models/ontology.py `concept_status_enum`) --
    the Postgres ENUM type the column is actually declared with, so an
    out-of-range value fails FastAPI validation (422) instead of reaching
    the DB and raising `InvalidTextRepresentation` (500). ACR-C / P4.
    """

    DRAFT = "draft"
    REVIEWED = "reviewed"
    APPROVED = "approved"
    PUBLISHED = "published"
    DEPRECATED = "deprecated"


class OntologySchemeOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    description: str | None = None
    version: int


class ConceptOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    scheme_id: uuid.UUID
    parent_concept_id: uuid.UUID | None = None
    pref_label: str
    definition: str | None = None
    source_ref: str | None = None
    status: str
    effective_from: date
    effective_to: date | None = None
    created_at: datetime
    updated_at: datetime
