"""Controls request/response DTOs. Companion to docs/knowledge-graph/10-openapi.yaml
`Controls` tag -- field shapes match `Control`/`ControlInput` exactly.

classification/is_critical are readOnly -- set only by the gate-test and
critical-control-test workflow endpoints, never client-writable via
create/update.
"""

import uuid

from pydantic import BaseModel, ConfigDict

from app.dto.assets import ConceptRef


class ControlInput(BaseModel):
    risk_id: uuid.UUID
    description: str
    control_type: str
    hierarchy: ConceptRef | None = None
    owner_person_id: uuid.UUID | None = None
    effectiveness_rating: str | None = None


class ControlOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    risk_id: uuid.UUID
    description: str
    control_type: str
    hierarchy: ConceptRef | None = None
    owner_person_id: uuid.UUID | None = None
    effectiveness_rating: str | None = None
    classification: str | None = None
    is_critical: bool


class GateTestInput(BaseModel):
    gate_1: bool
    gate_2: bool
    gate_3: bool
    is_verification_check: bool = False


class GateTestResult(BaseModel):
    classification: str


class EiaTestInput(BaseModel):
    eia_effective: bool | None = None
    eia_independent: bool | None = None
    eia_auditable: bool | None = None


class CriticalControlTestInput(BaseModel):
    is_critical: bool
