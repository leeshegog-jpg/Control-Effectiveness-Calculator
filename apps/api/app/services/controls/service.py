"""Controls service -- CRUD + 3-gate classification workflow + EIA test +
critical-control test + audit metadata (provenance) + Neo4j sync.
See docs/knowledge-graph/08-critical-control-assurance-model.md §2-3.
"""

import uuid

from neo4j import Driver
from sqlalchemy.orm import Session

from app.graph import sync_service
from app.models.provenance import ProvenanceRecord
from app.models.safety import Control, CriticalControl
from app.repositories import controls_repository, critical_controls_repository
from app.services.controls import rules


class ControlNotClassifiedError(Exception):
    """Raised when the critical-control test is attempted on a control that
    hasn't passed the 3-gate test as classification='Control' -- 409, not 500.
    """


def list_controls_for_risk(db: Session, risk_id: uuid.UUID) -> list[Control]:
    return controls_repository.list_controls_for_risk(db, risk_id)


def get_control(db: Session, control_id: uuid.UUID) -> Control | None:
    return controls_repository.get_control(db, control_id)


def create_control(
    db: Session,
    graph_driver: Driver,
    *,
    risk_id: uuid.UUID,
    description: str,
    control_type: str,
    hierarchy_concept_id: uuid.UUID | None,
    owner_person_id: uuid.UUID | None,
    effectiveness_rating: str | None,
    created_by_person_id: uuid.UUID | None = None,
) -> Control:
    control = Control(
        risk_id=risk_id,
        description=description,
        control_type=control_type,
        hierarchy_concept_id=hierarchy_concept_id,
        owner_person_id=owner_person_id,
        effectiveness_rating=effectiveness_rating,
    )
    controls_repository.create_control(db, control)

    db.add(
        ProvenanceRecord(
            entity_type="control",
            entity_id=control.id,
            source_type="human_entry",
            created_by_person_id=created_by_person_id,
        )
    )
    db.commit()
    db.refresh(control)

    sync_service.sync_control(graph_driver, control)
    return control


def run_gate_test(
    db: Session,
    graph_driver: Driver,
    control: Control,
    *,
    gate_1: bool,
    gate_2: bool,
    gate_3: bool,
    is_verification_check: bool,
) -> Control:
    control.gate_1 = gate_1
    control.gate_2 = gate_2
    control.gate_3 = gate_3
    control.classification = rules.classify_from_gates(
        gate_1, gate_2, gate_3, is_verification_check
    )

    controls_repository.update_control(db, control)
    db.commit()
    db.refresh(control)

    sync_service.sync_control(graph_driver, control)
    return control


def run_eia_test(
    db: Session,
    graph_driver: Driver,
    control: Control,
    *,
    eia_effective: bool | None,
    eia_independent: bool | None,
    eia_auditable: bool | None,
) -> Control:
    if eia_effective is not None:
        control.eia_effective = eia_effective
    if eia_independent is not None:
        control.eia_independent = eia_independent
    if eia_auditable is not None:
        control.eia_auditable = eia_auditable

    controls_repository.update_control(db, control)
    db.commit()
    db.refresh(control)

    sync_service.sync_control(graph_driver, control)
    return control


def run_critical_control_test(
    db: Session,
    graph_driver: Driver,
    control: Control,
    *,
    is_critical: bool,
    created_by_person_id: uuid.UUID | None = None,
) -> CriticalControl | None:
    if control.classification != "Control":
        raise ControlNotClassifiedError(
            "Control is not classified 'Control' -- cannot be tested for criticality."
        )
    if not is_critical:
        return None

    critical_control = CriticalControl(control_id=control.id)
    critical_controls_repository.create_critical_control(db, critical_control)

    db.add(
        ProvenanceRecord(
            entity_type="critical_control",
            entity_id=critical_control.control_id,
            source_type="human_entry",
            created_by_person_id=created_by_person_id,
        )
    )
    db.commit()
    db.refresh(critical_control)

    sync_service.sync_critical_control(graph_driver, critical_control)
    return critical_control
