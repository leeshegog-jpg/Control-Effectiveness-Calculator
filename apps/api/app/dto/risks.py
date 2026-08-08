"""Risks request/response DTOs. Companion to docs/knowledge-graph/10-openapi.yaml
`Risks` tag -- field shapes match `Risk`/`RiskInput` exactly.

inherent_rating/current_rating are readOnly per the contract -- derived
server-side by app/services/risks/rules.py (R1), never client-writable.
"""

import uuid
from datetime import date, datetime

from pydantic import BaseModel, ConfigDict


class RiskInput(BaseModel):
    hazard_id: uuid.UUID
    description: str
    cause: str | None = None
    inherent_likelihood: int | None = None
    inherent_consequence: int | None = None
    current_likelihood: int | None = None
    current_consequence: int | None = None
    target_likelihood: int | None = None
    target_consequence: int | None = None
    sfarp_justification: str | None = None
    status: str = "Open"
    review_date: date | None = None
    is_serious_risk: bool = False
    serious_risk_justification: str | None = None


class RiskOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    hazard_id: uuid.UUID
    description: str
    cause: str | None = None
    inherent_likelihood: int | None = None
    inherent_consequence: int | None = None
    inherent_rating: str | None = None
    current_likelihood: int | None = None
    current_consequence: int | None = None
    current_rating: str | None = None
    target_likelihood: int | None = None
    target_consequence: int | None = None
    sfarp_justification: str | None = None
    status: str
    review_date: date | None = None
    is_serious_risk: bool
    serious_risk_justification: str | None = None
    created_at: datetime
    updated_at: datetime


class RiskListOut(BaseModel):
    items: list[RiskOut]
    total: int
