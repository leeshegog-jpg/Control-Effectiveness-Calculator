"""Investigation request/response DTOs. Companion to
docs/knowledge-graph/10-openapi.yaml `Incidents` tag -- field shapes match
`Investigation`/`InvestigationInput` exactly.

method is carried as free text -- TO BE CONFIRMED (no V1 grounding, no
methodology mandate identified; see app/models/safety.py Investigation
docstring). Not resolved by this DTO.
"""

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class InvestigationInput(BaseModel):
    method: str | None = None
    findings: str | None = None
    contributing_factors: str | None = None


class InvestigationOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    incident_id: uuid.UUID
    method: str | None = None
    findings: str | None = None
    contributing_factors: str | None = None
    created_at: datetime
    updated_at: datetime
