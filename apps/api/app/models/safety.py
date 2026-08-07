"""ORM models for the `safety` schema.
Source of truth: docs/knowledge-graph/03-postgresql-schema.sql. Only the
tables R1 Milestone 0/1 actually touch (persons, parks, assets) are modeled
here -- the remaining ~30 safety.* tables (hazards, risks, incidents,
critical_controls, emergency_plans, competencies, ...) are deferred to the
milestones that use them (R1 Milestone 1 onward), not forgotten. Do not add
a table here ahead of the milestone that needs it -- YAGNI, and every extra
unused mapping is one more thing that can silently drift from the frozen
schema before it's ever tested against real code.
"""

import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import ARRAY, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models import Base


class Person(Base):
    __tablename__ = "persons"
    __table_args__ = {"schema": "safety"}

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    role_title: Mapped[str | None] = mapped_column(String(200))
    email: Mapped[str | None] = mapped_column(String(320), unique=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class Park(Base):
    __tablename__ = "parks"
    __table_args__ = {"schema": "safety"}

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)

    assets: Mapped[list["Asset"]] = relationship(back_populates="park")


class Asset(Base):
    __tablename__ = "assets"
    __table_args__ = {"schema": "safety"}

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True)
    name: Mapped[str] = mapped_column(String(300), nullable=False)
    park_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("safety.parks.id"))
    asset_type_concept_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("ontology.concepts.id")
    )
    iso55000_class: Mapped[str | None] = mapped_column(String(100))  # TO_BE_CONFIRMED, per schema
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="active")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))

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
