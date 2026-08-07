"""ORM model for the `provenance` schema.
Source of truth: docs/knowledge-graph/03-postgresql-schema.sql (provenance.records).
See docs/knowledge-graph/05-knowledge-provenance-model.md.
"""

import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Numeric, String, func, text
from sqlalchemy.dialects.postgresql import ENUM, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models import Base

source_type_enum = ENUM(
    "document_extraction",
    "human_entry",
    "v1_migration",
    "system_derived",
    name="source_type",
    schema="provenance",
    create_type=False,
)


class ProvenanceRecord(Base):
    __tablename__ = "records"
    __table_args__ = {"schema": "provenance"}

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()")
    )
    entity_type: Mapped[str] = mapped_column(String(50), nullable=False)
    entity_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    source_type: Mapped[str] = mapped_column(source_type_enum, nullable=False)
    document_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("safety.documents.id"))
    extraction_run_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True))
    created_by_person_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("safety.persons.id"))
    confidence: Mapped[float | None] = mapped_column(Numeric(4, 3))
    previous_version_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("provenance.records.id")
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
