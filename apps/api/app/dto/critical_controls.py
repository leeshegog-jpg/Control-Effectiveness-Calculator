"""CriticalControls request/response DTOs. Companion to
docs/knowledge-graph/10-openapi.yaml `CriticalControls` tag -- field shapes
match `CriticalControl`/`CriticalControlFarsiInput`/`PerformanceStandard`/
`PerformanceStandardInput` exactly.

farsi_score and health_state are readOnly -- farsi_score is DB-generated
(safety.critical_controls.farsi_score, GENERATED ALWAYS), health_state is
computed at read time (08-critical-control-assurance-model.md §6).
"""

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class CriticalControlFarsiInput(BaseModel):
    farsi_functionality: int | None = None
    farsi_availability: int | None = None
    farsi_reliability: int | None = None
    farsi_survivability: int | None = None
    farsi_interdependency: int | None = None


class CriticalControlOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    control_id: uuid.UUID
    farsi_functionality: int | None = None
    farsi_availability: int | None = None
    farsi_reliability: int | None = None
    farsi_survivability: int | None = None
    farsi_interdependency: int | None = None
    farsi_score: float | None = None
    eia_effective: bool | None = None
    eia_independent: bool | None = None
    eia_auditable: bool | None = None
    health_state: str


class PerformanceStandardInput(BaseModel):
    requirement_text: str
    measurable_criteria: str | None = None


class PerformanceStandardOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    critical_control_id: uuid.UUID
    requirement_text: str
    measurable_criteria: str | None = None
    created_at: datetime
    updated_at: datetime
