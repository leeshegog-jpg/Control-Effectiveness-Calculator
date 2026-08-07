"""ORM models for the `ontology` schema.
Source of truth: docs/knowledge-graph/03-postgresql-schema.sql. Column shapes
mirror that file exactly -- do not add/remove columns here without an ACR
against the frozen schema first.
"""

import uuid
from datetime import date, datetime

from sqlalchemy import (
    CheckConstraint,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    func,
    text,
)
from sqlalchemy.dialects.postgresql import ENUM, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models import Base

concept_status_enum = ENUM(
    "draft",
    "reviewed",
    "approved",
    "published",
    "deprecated",
    name="concept_status",
    schema="ontology",
    create_type=False,
)
alias_type_enum = ENUM(
    "synonym",
    "abbreviation",
    "deprecated_term",
    name="alias_type",
    schema="ontology",
    create_type=False,
)
relation_type_enum = ENUM(
    "broader",
    "narrower",
    "related",
    "equivalent",
    name="relation_type",
    schema="ontology",
    create_type=False,
)


class Scheme(Base):
    __tablename__ = "schemes"
    __table_args__ = {"schema": "ontology"}

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()")
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    description: Mapped[str | None] = mapped_column(Text)
    version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    concepts: Mapped[list["Concept"]] = relationship(back_populates="scheme")


class Concept(Base):
    __tablename__ = "concepts"
    __table_args__ = (
        CheckConstraint(
            "effective_to IS NULL OR effective_to > effective_from",
            name="concepts_effective_range",
        ),
        {"schema": "ontology"},
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()")
    )
    scheme_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("ontology.schemes.id"), nullable=False)
    parent_concept_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("ontology.concepts.id"))
    pref_label: Mapped[str] = mapped_column(String(200), nullable=False)
    definition: Mapped[str | None] = mapped_column(Text)
    status: Mapped[str] = mapped_column(concept_status_enum, nullable=False, default="draft")
    source_ref: Mapped[str | None] = mapped_column(String(200))
    effective_from: Mapped[date] = mapped_column(Date, server_default=func.current_date())
    effective_to: Mapped[date | None] = mapped_column(Date)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    scheme: Mapped["Scheme"] = relationship(back_populates="concepts")
    aliases: Mapped[list["ConceptAlias"]] = relationship(back_populates="concept")


class ConceptAlias(Base):
    __tablename__ = "concept_aliases"
    __table_args__ = {"schema": "ontology"}

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()")
    )
    concept_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("ontology.concepts.id", ondelete="CASCADE"), nullable=False
    )
    alias_text: Mapped[str] = mapped_column(String(200), nullable=False)
    alias_type: Mapped[str] = mapped_column(alias_type_enum, nullable=False, default="synonym")

    concept: Mapped["Concept"] = relationship(back_populates="aliases")


class ConceptRelation(Base):
    __tablename__ = "concept_relations"
    __table_args__ = (
        CheckConstraint("subject_concept_id <> object_concept_id"),
        {"schema": "ontology"},
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()")
    )
    subject_concept_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("ontology.concepts.id"), nullable=False
    )
    relation_type: Mapped[str] = mapped_column(relation_type_enum, nullable=False)
    object_concept_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("ontology.concepts.id"), nullable=False
    )


class RelationshipType(Base):
    __tablename__ = "relationship_types"
    __table_args__ = {"schema": "ontology"}

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()")
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    domain_scheme_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("ontology.schemes.id"))
    range_scheme_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("ontology.schemes.id"))
    description: Mapped[str | None] = mapped_column(Text)
    cardinality: Mapped[str] = mapped_column(String(10), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
