"""Hazards request/response DTOs. Companion to docs/knowledge-graph/10-openapi.yaml
`Hazards` tag -- field shapes match `Hazard`/`HazardInput`/`ConceptRef` exactly.

category/energy_source are accepted but category resolution always comes
back null in Milestone 1 -- see app/models/safety.py Hazard.category_concept_id
docstring (ontology expansion deferred pending ADR).
"""

import uuid
from datetime import date, datetime

from pydantic import BaseModel, ConfigDict

from app.dto.assets import ConceptRef


class HazardInput(BaseModel):
    asset_id: uuid.UUID | None = None
    name: str
    description: str
    exposure_pathway: str | None = None
    possible_consequence: str | None = None
    category: ConceptRef | None = None
    energy_source: ConceptRef | None = None
    date_identified: date | None = None
    owner_person_id: uuid.UUID | None = None
    is_adh: bool = False
    device_boundary_id: uuid.UUID | None = None


class HazardOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    asset_id: uuid.UUID | None = None
    name: str
    description: str
    exposure_pathway: str | None = None
    possible_consequence: str | None = None
    category: ConceptRef | None = None
    energy_source: ConceptRef | None = None
    date_identified: date
    owner_person_id: uuid.UUID | None = None
    is_adh: bool
    device_boundary_id: uuid.UUID | None = None
    created_at: datetime
    updated_at: datetime


class HazardListOut(BaseModel):
    items: list[HazardOut]
    total: int
