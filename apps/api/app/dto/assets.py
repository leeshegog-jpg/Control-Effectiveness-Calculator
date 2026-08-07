"""Assets request/response DTOs. Companion to docs/knowledge-graph/10-openapi.yaml
`Assets` tag -- field shapes match `Asset`/`AssetInput`/`ConceptRef` exactly.
"""

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ConceptRef(BaseModel):
    concept_id: uuid.UUID | None = None
    pref_label: str | None = None  # read-only, resolved server-side


class AssetInput(BaseModel):
    name: str
    park_id: uuid.UUID | None = None
    asset_type: ConceptRef | None = None
    # TO_BE_CONFIRMED, per docs/knowledge-graph/03-postgresql-schema.sql
    iso55000_class: str | None = None
    status: str = "active"


class AssetOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    park_id: uuid.UUID | None = None
    asset_type: ConceptRef | None = None
    iso55000_class: str | None = None
    status: str
    created_at: datetime
    updated_at: datetime


class AssetListOut(BaseModel):
    items: list[AssetOut]
    total: int
