"""ORM models for the `safety` schema.
Source of truth: docs/knowledge-graph/03-postgresql-schema.sql. Only the
tables R1 Milestone 0/1 actually touch (persons, parks, assets, hazards,
risks) are modeled here -- the remaining safety.* tables (consequences,
controls, critical_controls, incidents, emergency_plans, competencies, ...)
are deferred to the milestones that use them, not forgotten. Do not add
a table here ahead of the milestone that needs it -- YAGNI, and every extra
unused mapping is one more thing that can silently drift from the frozen
schema before it's ever tested against real code.

Consequence/Control are deliberately unmapped in Milestone 1: the frozen
OpenAPI contract exposes no endpoint for Consequence at all, and V1's Risk
Register only ever captured "Existing Controls" as free text -- modeling
structured safety.controls rows now would mean inventing per-control data
V1 never recorded. Structured Controls belong to the dedicated Critical
Controls milestone.
"""

import uuid
from datetime import date, datetime

from sqlalchemy import Date, DateTime, ForeignKey, Integer, SmallInteger, String, Text, func, text
from sqlalchemy.dialects.postgresql import ARRAY, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models import Base


class Person(Base):
    __tablename__ = "persons"
    __table_args__ = {"schema": "safety"}

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()")
    )
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    role_title: Mapped[str | None] = mapped_column(String(200))
    email: Mapped[str | None] = mapped_column(String(320), unique=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class Park(Base):
    __tablename__ = "parks"
    __table_args__ = {"schema": "safety"}

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()")
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)

    assets: Mapped[list["Asset"]] = relationship(back_populates="park")


class Asset(Base):
    __tablename__ = "assets"
    __table_args__ = {"schema": "safety"}

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()")
    )
    name: Mapped[str] = mapped_column(String(300), nullable=False)
    park_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("safety.parks.id"))
    asset_type_concept_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("ontology.concepts.id")
    )
    iso55000_class: Mapped[str | None] = mapped_column(String(100))  # TO_BE_CONFIRMED, per schema
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="active")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    # Device description fields -- added by ALTER TABLE in the Safety Case
    # Demonstration Model section of the frozen schema, confirmed required
    # by Guide §8.3. Not populated by Milestone 0 UI, but real columns on
    # the real table -- the ORM model must reflect them.
    is_amusement_device: Mapped[bool] = mapped_column(default=False)
    manufacturer: Mapped[str | None] = mapped_column(String(200))
    as3533_device_class: Mapped[str | None] = mapped_column(String(50))
    plant_design_registration_number: Mapped[str | None] = mapped_column(String(100))
    year_manufactured_or_commissioned: Mapped[int | None] = mapped_column(Integer)
    previous_names: Mapped[list[str] | None] = mapped_column(ARRAY(String))
    modification_history: Mapped[str | None] = mapped_column(String)

    park: Mapped["Park"] = relationship(back_populates="assets")


class Hazard(Base):
    __tablename__ = "hazards"
    __table_args__ = {"schema": "safety"}

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()")
    )
    asset_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("safety.assets.id"))
    name: Mapped[str] = mapped_column(String(300), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    exposure_pathway: Mapped[str | None] = mapped_column(Text)
    possible_consequence: Mapped[str | None] = mapped_column(Text)
    # Hazard taxonomy -- deliberately left unpopulated in Milestone 1. V1 has
    # a real fixed-option category dropdown, but adding a new OntologyScheme
    # for it is an ontology expansion this milestone's authorization requires
    # an ADR for. Flagged as a known gap, not silently ported or discarded.
    category_concept_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("ontology.concepts.id")
    )
    energy_source_concept_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("ontology.concepts.id")
    )
    date_identified: Mapped[date] = mapped_column(Date, server_default=func.current_date())
    owner_person_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("safety.persons.id"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    # ADI/ADH pathway columns -- added by ALTER TABLE in the Safety Case
    # Demonstration Model section of the frozen schema. device_boundary_id
    # is a plain column, not ForeignKey-wrapped: safety.device_boundaries
    # isn't ORM-mapped yet (out of Milestone 1 scope), and SQLAlchemy can't
    # resolve a FK target that isn't registered on Base.metadata.
    is_adh: Mapped[bool] = mapped_column(default=False)
    device_boundary_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True))

    risks: Mapped[list["Risk"]] = relationship(back_populates="hazard")


class Risk(Base):
    __tablename__ = "risks"
    __table_args__ = {"schema": "safety"}

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()")
    )
    hazard_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("safety.hazards.id"), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    cause: Mapped[str | None] = mapped_column(Text)
    inherent_likelihood: Mapped[int | None] = mapped_column(SmallInteger)
    inherent_consequence: Mapped[int | None] = mapped_column(SmallInteger)
    inherent_rating: Mapped[str | None] = mapped_column(
        String(10)
    )  # derived -- R1, service-set only
    current_likelihood: Mapped[int | None] = mapped_column(SmallInteger)
    current_consequence: Mapped[int | None] = mapped_column(SmallInteger)
    current_rating: Mapped[str | None] = mapped_column(
        String(10)
    )  # derived -- R1, service-set only
    target_likelihood: Mapped[int | None] = mapped_column(SmallInteger)
    target_consequence: Mapped[int | None] = mapped_column(SmallInteger)
    sfarp_justification: Mapped[str | None] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="Open")
    review_date: Mapped[date | None] = mapped_column(Date)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    # Chapter 9A serious-risk columns -- added by ALTER TABLE in the Safety
    # Case Demonstration Model section of the frozen schema.
    is_serious_risk: Mapped[bool] = mapped_column(default=False)
    serious_risk_justification: Mapped[str | None] = mapped_column()

    hazard: Mapped["Hazard"] = relationship(back_populates="risks")
