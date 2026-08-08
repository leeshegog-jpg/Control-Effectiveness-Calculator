"""Evidence request/response DTOs. Companion to docs/knowledge-graph/10-openapi.yaml
`Evidence` tag -- field shapes match `Evidence`/`EvidenceInput` exactly.
"""

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.dto.assets import ConceptRef


class EvidenceInput(BaseModel):
    type: ConceptRef | None = None
    source_document_id: uuid.UUID | None = None
    uploaded_by_person_id: uuid.UUID | None = None
    linked_entity_type: str | None = None
    linked_entity_id: uuid.UUID | None = None


class EvidenceOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    verification_activity_id: uuid.UUID | None = None
    type: ConceptRef | None = None
    source_document_id: uuid.UUID | None = None
    uploaded_by_person_id: uuid.UUID | None = None
    uploaded_at: datetime
    linked_entity_type: str | None = None
    linked_entity_id: uuid.UUID | None = None
