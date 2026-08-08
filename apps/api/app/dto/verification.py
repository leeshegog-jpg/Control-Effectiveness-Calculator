"""Verification request/response DTOs. Companion to
docs/knowledge-graph/10-openapi.yaml `Verification` tag -- field shapes
match `VerificationActivity`/`VerificationActivityInput` exactly.

`overdue` is readOnly -- computed at read time (07-inference-rules-catalogue.md R3).
"""

import uuid
from datetime import date, datetime

from pydantic import BaseModel, ConfigDict

from app.dto.assets import ConceptRef


class VerificationActivityInput(BaseModel):
    method: ConceptRef | None = None
    frequency: str | None = None
    due_date: date | None = None
    last_completed: date | None = None
    performed_by_person_id: uuid.UUID | None = None
    result: str | None = None


class VerificationActivityOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    performance_standard_id: uuid.UUID
    method: ConceptRef | None = None
    frequency: str | None = None
    due_date: date | None = None
    last_completed: date | None = None
    performed_by_person_id: uuid.UUID | None = None
    result: str | None = None
    overdue: bool
    created_at: datetime
    updated_at: datetime
