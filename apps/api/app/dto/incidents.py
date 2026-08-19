"""Incident request/response DTOs. Companion to docs/knowledge-graph/10-openapi.yaml
`Incidents` tag -- field shapes match `Incident`/`IncidentInput` exactly.

incident_type is accepted but always resolves null -- ontology expansion
deferred, see app/models/safety.py Incident.incident_type_concept_id and
ADR-004 (D3, mirrors the Hazard Taxonomy deferral precedent).
"""

import uuid
from datetime import datetime
from datetime import datetime as PyDT  # avoids IncidentOut.datetime field shadowing this type

from pydantic import BaseModel, ConfigDict

from app.dto.assets import ConceptRef


class IncidentInput(BaseModel):
    datetime: datetime
    incident_type: ConceptRef | None = None
    severity: int | None = None
    vrtp_severity: str | None = None
    location: str | None = None
    asset_id: uuid.UUID | None = None
    reporter_person_id: uuid.UUID | None = None
    description: str
    injuries: str | None = None
    witnesses: str | None = None
    immediate_actions: str | None = None
    immediate_cause: str | None = None
    root_cause: str | None = None
    whsq_notified: str | None = None
    osr_notified: str | None = None
    investigation_status: str | None = None
    status: str | None = None
    is_notifiable_incident: bool = False


class IncidentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    datetime: datetime
    incident_type: ConceptRef | None = None
    severity: int | None = None
    vrtp_severity: str | None = None
    location: str | None = None
    asset_id: uuid.UUID | None = None
    reporter_person_id: uuid.UUID | None = None
    description: str
    injuries: str | None = None
    witnesses: str | None = None
    immediate_actions: str | None = None
    immediate_cause: str | None = None
    root_cause: str | None = None
    whsq_notified: str
    osr_notified: str
    investigation_status: str
    status: str
    is_notifiable_incident: bool
    created_at: PyDT


class IncidentListOut(BaseModel):
    items: list[IncidentOut]
    total: int


class IncidentHazardLinkInput(BaseModel):
    hazard_id: uuid.UUID
