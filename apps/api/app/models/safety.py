"""ORM models for the `safety` schema.
Source of truth: docs/knowledge-graph/03-postgresql-schema.sql. Tables are
added per-milestone -- the remaining safety.* tables (consequences,
incidents, emergency_plans, competencies, device_boundaries, ...) are
deferred to the milestones that use them, not forgotten. Do not add a
table here ahead of the milestone that needs it -- YAGNI, and every extra
unused mapping is one more thing that can silently drift from the frozen
schema before it's ever tested against real code.

Consequence is deliberately unmapped: the frozen OpenAPI contract exposes
no endpoint for it at all.

R1 Milestone 2 (Critical Control Management) adds Control/CriticalControl/
PerformanceStandard/VerificationActivity/Evidence, per
docs/implementation-blueprint/17-r1-milestone-2-ccm-discovery-reconciliation.md.
Control/Support/Verification are the SAME table (`controls`), distinguished
by the `classification` column -- not three separate tables, and not
subordinate objects under a "Critical Control" parent (that reconciliation
confirmed this exactly, converging V1/schema/OpenAPI/06-relationship-rules
on "Option A"). FailureMode/TriggerActionResponsePlan/MonitoringSummary
remain unmapped -- out of this milestone's authorized scope.
"""

import uuid
from datetime import date, datetime
from datetime import datetime as PyDT  # avoids Incident.datetime column shadowing this type

from sqlalchemy import (
    Date,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    SmallInteger,
    String,
    Text,
    func,
    text,
)
from sqlalchemy.dialects.postgresql import ARRAY, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.schema import FetchedValue

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


class Control(Base):
    """Control, Support, and Verification are all this same table --
    `classification` distinguishes the role, set by the gate-test workflow
    (app/services/controls/rules.py), never client-writable directly. See
    the module docstring and 17-r1-milestone-2-ccm-discovery-reconciliation.md.
    """

    __tablename__ = "controls"
    __table_args__ = {"schema": "safety"}

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()")
    )
    risk_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("safety.risks.id"), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    control_type: Mapped[str] = mapped_column(String(20), nullable=False)
    hierarchy_concept_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("ontology.concepts.id")
    )
    # Workflow-set only -- app/services/controls/rules.py:classify_from_gates.
    classification: Mapped[str | None] = mapped_column(String(20))
    gate_1: Mapped[bool | None] = mapped_column()
    gate_2: Mapped[bool | None] = mapped_column()
    gate_3: Mapped[bool | None] = mapped_column()
    eia_effective: Mapped[bool | None] = mapped_column()
    eia_independent: Mapped[bool | None] = mapped_column()
    eia_auditable: Mapped[bool | None] = mapped_column()
    effectiveness_rating: Mapped[str | None] = mapped_column(String(30))
    owner_person_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("safety.persons.id"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    critical_control: Mapped["CriticalControl | None"] = relationship(back_populates="control")


class CriticalControl(Base):
    """1:1 extension of a Control row where classification='Control' and the
    Stage 2 critical-control test passed. control_id has no server-side
    default -- it is always the parent Control's id, supplied explicitly,
    never independently generated.
    """

    __tablename__ = "critical_controls"
    __table_args__ = {"schema": "safety"}

    control_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("safety.controls.id"), primary_key=True
    )
    farsi_functionality: Mapped[int | None] = mapped_column(SmallInteger)
    farsi_availability: Mapped[int | None] = mapped_column(SmallInteger)
    farsi_reliability: Mapped[int | None] = mapped_column(SmallInteger)
    farsi_survivability: Mapped[int | None] = mapped_column(SmallInteger)
    farsi_interdependency: Mapped[int | None] = mapped_column(SmallInteger)
    # GENERATED ALWAYS ... STORED in the DB -- never written by the ORM;
    # FetchedValue tells SQLAlchemy to omit it from INSERT/UPDATE and read
    # the DB-computed value back on refresh.
    farsi_score: Mapped[float | None] = mapped_column(Numeric(3, 2), server_default=FetchedValue())
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    control: Mapped["Control"] = relationship(back_populates="critical_control")
    performance_standards: Mapped[list["PerformanceStandard"]] = relationship(
        back_populates="critical_control"
    )


class PerformanceStandard(Base):
    __tablename__ = "performance_standards"
    __table_args__ = {"schema": "safety"}

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()")
    )
    critical_control_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("safety.critical_controls.control_id"), nullable=False
    )
    requirement_text: Mapped[str] = mapped_column(Text, nullable=False)
    measurable_criteria: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    critical_control: Mapped["CriticalControl"] = relationship(
        back_populates="performance_standards"
    )
    verification_activities: Mapped[list["VerificationActivity"]] = relationship(
        back_populates="performance_standard"
    )


class VerificationActivity(Base):
    __tablename__ = "verification_activities"
    __table_args__ = {"schema": "safety"}

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()")
    )
    performance_standard_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("safety.performance_standards.id"), nullable=False
    )
    method_concept_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("ontology.concepts.id"))
    frequency: Mapped[str | None] = mapped_column(String(30))
    due_date: Mapped[date | None] = mapped_column(Date)
    last_completed: Mapped[date | None] = mapped_column(Date)
    performed_by_person_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("safety.persons.id")
    )
    result: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    performance_standard: Mapped["PerformanceStandard"] = relationship(
        back_populates="verification_activities"
    )
    evidence: Mapped[list["Evidence"]] = relationship(back_populates="verification_activity")


class Evidence(Base):
    __tablename__ = "evidence"
    __table_args__ = {"schema": "safety"}

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()")
    )
    type_concept_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("ontology.concepts.id"))
    verification_activity_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("safety.verification_activities.id")
    )
    # Not ForeignKey-wrapped -- safety.documents isn't ORM-mapped yet, same
    # reasoning as ProvenanceRecord.document_id (Milestone 0).
    source_document_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True))
    uploaded_by_person_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("safety.persons.id"))
    uploaded_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    # Polymorphic pointer -- plain columns, not a FK to any single table.
    linked_entity_type: Mapped[str | None] = mapped_column(String(50))
    linked_entity_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True))

    verification_activity: Mapped["VerificationActivity | None"] = relationship(
        back_populates="evidence"
    )


class Incident(Base):
    """R1 Milestone 3D-1 persistence mapping for the frozen safety.incidents table.

    Persistence only. Incident business rules, DTOs, routers, Neo4j sync, and
    notification propagation are deliberately outside 3D-1.
    """

    __tablename__ = "incidents"
    __table_args__ = {"schema": "safety"}

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()")
    )
    datetime: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    report_date: Mapped[date] = mapped_column(
        Date, nullable=False, server_default=func.current_date()
    )
    incident_type_concept_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("ontology.concepts.id")
    )
    severity: Mapped[int | None] = mapped_column(SmallInteger)
    vrtp_severity: Mapped[str | None] = mapped_column(String(30))
    location: Mapped[str | None] = mapped_column(String(300))
    asset_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("safety.assets.id"))
    reporter_person_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("safety.persons.id"))
    description: Mapped[str] = mapped_column(Text, nullable=False)
    injuries: Mapped[str | None] = mapped_column(Text)
    witnesses: Mapped[str | None] = mapped_column(Text)
    immediate_actions: Mapped[str | None] = mapped_column(Text)
    immediate_cause: Mapped[str | None] = mapped_column(Text)
    root_cause: Mapped[str | None] = mapped_column(Text)
    whsq_notified: Mapped[str] = mapped_column(
        String(40), nullable=False, server_default=text("'Not yet assessed'")
    )
    osr_notified: Mapped[str] = mapped_column(
        String(40), nullable=False, server_default=text("'Not applicable / under assessment'")
    )
    investigation_status: Mapped[str] = mapped_column(
        String(20), nullable=False, server_default=text("'Not Started'")
    )
    status: Mapped[str] = mapped_column(String(20), nullable=False, server_default=text("'Open'"))
    created_at: Mapped[PyDT] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[PyDT] = mapped_column(DateTime(timezone=True), server_default=func.now())
    is_notifiable_incident: Mapped[bool] = mapped_column(
        nullable=False, server_default=text("false")
    )
