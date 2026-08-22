"""Action request/response DTOs. Companion to docs/knowledge-graph/10-openapi.yaml
`Actions` tag -- field shapes match `Action`/`ActionInput` exactly.

completion_date and notes exist as columns on the ORM model but are
deliberately not exposed here -- ACR-006 excludes them from this slice's
OpenAPI surface; each needs its own ACR to expose.
"""

import uuid
from datetime import date

from pydantic import BaseModel, ConfigDict

from app.dto.assets import ConceptRef


class ActionInput(BaseModel):
    source_type: ConceptRef | None = None
    source_id: uuid.UUID | None = None
    description: str
    root_cause_category: ConceptRef | None = None
    priority: str | None = None
    assigned_to_person_id: uuid.UUID | None = None
    due_date: date | None = None
    status: str | None = None
    effectiveness_review: str | None = None


class ActionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    source_type: ConceptRef | None = None
    source_id: uuid.UUID | None = None
    description: str
    root_cause_category: ConceptRef | None = None
    priority: str | None = None
    assigned_to_person_id: uuid.UUID | None = None
    due_date: date | None = None
    status: str
    effectiveness_review: str


class IncidentActionLinkInput(BaseModel):
    action_id: uuid.UUID
