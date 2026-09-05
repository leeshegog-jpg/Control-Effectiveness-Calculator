"""Action request/response DTOs. Companion to docs/knowledge-graph/10-openapi.yaml
`Actions` tag -- field shapes match `Action`/`ActionInput` exactly.
"""

import uuid
from datetime import date
from enum import StrEnum

from pydantic import BaseModel, ConfigDict

from app.dto.assets import ConceptRef


class ActionStatus(StrEnum):
    """Query-param constraint for `GET /actions?status=`. Mirrors the
    `safety.actions.status` CHECK constraint (03-postgresql-schema.sql
    line 569) -- a plain `varchar` column, not a Postgres ENUM type, so an
    out-of-range value previously matched zero rows and returned 200
    silent-accept instead of 422. ACR-C / P4.
    """

    OPEN = "Open"
    IN_PROGRESS = "In Progress"
    CLOSED = "Closed"


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
    completion_date: date | None = None
    notes: str | None = None


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
    completion_date: date | None = None
    notes: str | None = None


class IncidentActionLinkInput(BaseModel):
    action_id: uuid.UUID
