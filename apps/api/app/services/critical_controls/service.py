"""Critical Controls service -- FARSI scoring, computed Control Health
state, Performance Standard CRUD, audit metadata (provenance), Neo4j sync.
See docs/knowledge-graph/08-critical-control-assurance-model.md §4b, §6.
"""

import uuid
from datetime import date

from neo4j import Driver
from sqlalchemy.orm import Session

from app.graph import sync_service
from app.models.provenance import ProvenanceRecord
from app.models.safety import CriticalControl, PerformanceStandard
from app.repositories import critical_controls_repository
from app.services.critical_controls import rules


def get_critical_control(db: Session, control_id: uuid.UUID) -> CriticalControl | None:
    return critical_controls_repository.get_critical_control(db, control_id)


def compute_health_state(db: Session, control_id: uuid.UUID) -> str:
    snapshots = critical_controls_repository.list_verification_snapshots(db, control_id)
    return rules.compute_health_state(snapshots, date.today())


def update_farsi(
    db: Session,
    graph_driver: Driver,
    critical_control: CriticalControl,
    *,
    farsi_functionality: int | None = None,
    farsi_availability: int | None = None,
    farsi_reliability: int | None = None,
    farsi_survivability: int | None = None,
    farsi_interdependency: int | None = None,
) -> CriticalControl:
    if farsi_functionality is not None:
        critical_control.farsi_functionality = farsi_functionality
    if farsi_availability is not None:
        critical_control.farsi_availability = farsi_availability
    if farsi_reliability is not None:
        critical_control.farsi_reliability = farsi_reliability
    if farsi_survivability is not None:
        critical_control.farsi_survivability = farsi_survivability
    if farsi_interdependency is not None:
        critical_control.farsi_interdependency = farsi_interdependency

    critical_controls_repository.update_critical_control(db, critical_control)
    db.commit()
    db.refresh(critical_control)  # picks up the DB-generated farsi_score

    sync_service.sync_critical_control(graph_driver, critical_control)
    return critical_control


def list_performance_standards(
    db: Session, critical_control_id: uuid.UUID
) -> list[PerformanceStandard]:
    return critical_controls_repository.list_performance_standards(db, critical_control_id)


def create_performance_standard(
    db: Session,
    graph_driver: Driver,
    *,
    critical_control_id: uuid.UUID,
    requirement_text: str,
    measurable_criteria: str | None,
    created_by_person_id: uuid.UUID | None = None,
) -> PerformanceStandard:
    standard = PerformanceStandard(
        critical_control_id=critical_control_id,
        requirement_text=requirement_text,
        measurable_criteria=measurable_criteria,
    )
    critical_controls_repository.create_performance_standard(db, standard)

    db.add(
        ProvenanceRecord(
            entity_type="performance_standard",
            entity_id=standard.id,
            source_type="human_entry",
            created_by_person_id=created_by_person_id,
        )
    )
    db.commit()
    db.refresh(standard)

    sync_service.sync_performance_standard(graph_driver, standard)
    return standard
