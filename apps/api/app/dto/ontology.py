"""Ontology request/response DTOs. Companion to docs/knowledge-graph/10-openapi.yaml
`Ontology` tag -- field shapes match the `OntologyScheme` and `Concept` schemas
there exactly. R1 Milestone 0 implements the read-only GET paths only.
"""

import uuid
from datetime import date, datetime

from pydantic import BaseModel, ConfigDict


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
