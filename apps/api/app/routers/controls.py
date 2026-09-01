"""Controls router (OpenAPI tag). R1 Milestone 2 -- Critical Control
Management, Control/Support/Verification classification workflow.
Contract: docs/knowledge-graph/10-openapi.yaml.

No fixed prefix -- paths cross resource boundaries (nested under /risks,
and under /controls itself for the workflow sub-endpoints), matching the
frozen contract exactly rather than forcing a single router prefix.
"""

import uuid

from fastapi import APIRouter, Depends, HTTPException, Response
from neo4j import Driver
from sqlalchemy.orm import Session

from app.dependencies.db import get_db
from app.dependencies.graph import get_graph_driver
from app.dto.assets import ConceptRef
from app.dto.controls import (
    ControlInput,
    ControlOut,
    CriticalControlTestInput,
    EiaTestInput,
    GateTestInput,
    GateTestResult,
)
from app.dto.critical_controls import CriticalControlOut
from app.models.ontology import Concept
from app.services.controls import service
from app.services.controls.service import ControlNotClassifiedError
from app.services.critical_controls import service as critical_controls_service
from app.services.referential import ReferentialIntegrityError
from app.services.risks import service as risks_service

router = APIRouter(tags=["controls"])


def _concept_ref(db: Session, concept_id: uuid.UUID | None) -> ConceptRef | None:
    if concept_id is None:
        return None
    concept = db.get(Concept, concept_id)
    return ConceptRef(concept_id=concept_id, pref_label=concept.pref_label if concept else None)


def _to_out(db: Session, control) -> ControlOut:
    return ControlOut(
        id=control.id,
        risk_id=control.risk_id,
        description=control.description,
        control_type=control.control_type,
        hierarchy=_concept_ref(db, control.hierarchy_concept_id),
        owner_person_id=control.owner_person_id,
        effectiveness_rating=control.effectiveness_rating,
        classification=control.classification,
        is_critical=control.critical_control is not None,
    )


@router.get("/risks/{risk_id}/controls", response_model=list[ControlOut])
def list_controls_for_risk(risk_id: uuid.UUID, db: Session = Depends(get_db)) -> list[ControlOut]:
    controls = service.list_controls_for_risk(db, risk_id)
    return [_to_out(db, c) for c in controls]


@router.post("/risks/{risk_id}/controls", response_model=ControlOut, status_code=201)
def create_control_for_risk(
    risk_id: uuid.UUID,
    body: ControlInput,
    db: Session = Depends(get_db),
    graph_driver: Driver = Depends(get_graph_driver),
) -> ControlOut:
    if risks_service.get_risk(db, risk_id) is None:
        raise HTTPException(status_code=404, detail="Risk not found")
    try:
        control = service.create_control(
            db,
            graph_driver,
            risk_id=risk_id,
            description=body.description,
            control_type=body.control_type,
            hierarchy_concept_id=body.hierarchy.concept_id if body.hierarchy else None,
            owner_person_id=body.owner_person_id,
            effectiveness_rating=body.effectiveness_rating,
        )
    except ReferentialIntegrityError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    return _to_out(db, control)


@router.get("/controls/{control_id}", response_model=ControlOut)
def get_control(control_id: uuid.UUID, db: Session = Depends(get_db)) -> ControlOut:
    control = service.get_control(db, control_id)
    if control is None:
        raise HTTPException(status_code=404, detail="Control not found")
    return _to_out(db, control)


@router.post("/controls/{control_id}/gate-test", response_model=GateTestResult)
def submit_gate_test(
    control_id: uuid.UUID,
    body: GateTestInput,
    db: Session = Depends(get_db),
    graph_driver: Driver = Depends(get_graph_driver),
) -> GateTestResult:
    control = service.get_control(db, control_id)
    if control is None:
        raise HTTPException(status_code=404, detail="Control not found")
    updated = service.run_gate_test(
        db,
        graph_driver,
        control,
        gate_1=body.gate_1,
        gate_2=body.gate_2,
        gate_3=body.gate_3,
        is_verification_check=body.is_verification_check,
    )
    # classify_from_gates always returns a str -- classification is only
    # nullable in the schema before the gate test has ever run.
    assert updated.classification is not None
    return GateTestResult(classification=updated.classification)


@router.post("/controls/{control_id}/eia-test", response_model=ControlOut)
def submit_eia_test(
    control_id: uuid.UUID,
    body: EiaTestInput,
    db: Session = Depends(get_db),
    graph_driver: Driver = Depends(get_graph_driver),
) -> ControlOut:
    control = service.get_control(db, control_id)
    if control is None:
        raise HTTPException(status_code=404, detail="Control not found")
    updated = service.run_eia_test(
        db,
        graph_driver,
        control,
        eia_effective=body.eia_effective,
        eia_independent=body.eia_independent,
        eia_auditable=body.eia_auditable,
    )
    return _to_out(db, updated)


@router.post("/controls/{control_id}/critical-control-test")
def submit_critical_control_test(
    control_id: uuid.UUID,
    body: CriticalControlTestInput,
    response: Response,
    db: Session = Depends(get_db),
    graph_driver: Driver = Depends(get_graph_driver),
):
    control = service.get_control(db, control_id)
    if control is None:
        raise HTTPException(status_code=404, detail="Control not found")
    try:
        critical_control = service.run_critical_control_test(
            db, graph_driver, control, is_critical=body.is_critical
        )
    except ControlNotClassifiedError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc

    if critical_control is None:
        # Contract only documents 201/409 for this endpoint -- is_critical=False
        # isn't a defined case. Minimal, schema-neutral 200 rather than
        # inventing a new component schema for an unspecified branch.
        return {"is_critical": False}

    response.status_code = 201
    return CriticalControlOut(
        control_id=critical_control.control_id,
        farsi_functionality=critical_control.farsi_functionality,
        farsi_availability=critical_control.farsi_availability,
        farsi_reliability=critical_control.farsi_reliability,
        farsi_survivability=critical_control.farsi_survivability,
        farsi_interdependency=critical_control.farsi_interdependency,
        farsi_score=float(critical_control.farsi_score)
        if critical_control.farsi_score is not None
        else None,
        eia_effective=control.eia_effective,
        eia_independent=control.eia_independent,
        eia_auditable=control.eia_auditable,
        health_state=critical_controls_service.compute_health_state(
            db, critical_control.control_id
        ),
    )
