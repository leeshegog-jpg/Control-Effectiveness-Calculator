"""Critical Controls router (OpenAPI tag). R1 Milestone 2 -- FARSI scoring,
computed Control Health state, Performance Standard CRUD.
Contract: docs/knowledge-graph/10-openapi.yaml. No fixed prefix -- matches
the frozen contract's `/critical-controls/...` paths exactly.
"""

import uuid

from fastapi import APIRouter, Depends, HTTPException
from neo4j import Driver
from sqlalchemy.orm import Session

from app.dependencies.db import get_db
from app.dependencies.graph import get_graph_driver
from app.dto.critical_controls import (
    CriticalControlFarsiInput,
    CriticalControlOut,
    PerformanceStandardInput,
    PerformanceStandardOut,
)
from app.services.critical_controls import service

router = APIRouter(tags=["critical-controls"])


def _to_out(db: Session, control_id: uuid.UUID, critical_control) -> CriticalControlOut:
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
        eia_effective=critical_control.control.eia_effective,
        eia_independent=critical_control.control.eia_independent,
        eia_auditable=critical_control.control.eia_auditable,
        health_state=service.compute_health_state(db, control_id),
    )


@router.get("/critical-controls/{control_id}", response_model=CriticalControlOut)
def get_critical_control(
    control_id: uuid.UUID, db: Session = Depends(get_db)
) -> CriticalControlOut:
    critical_control = service.get_critical_control(db, control_id)
    if critical_control is None:
        raise HTTPException(status_code=404, detail="Critical control not found")
    return _to_out(db, control_id, critical_control)


@router.patch("/critical-controls/{control_id}", response_model=CriticalControlOut)
def update_farsi(
    control_id: uuid.UUID,
    body: CriticalControlFarsiInput,
    db: Session = Depends(get_db),
    graph_driver: Driver = Depends(get_graph_driver),
) -> CriticalControlOut:
    critical_control = service.get_critical_control(db, control_id)
    if critical_control is None:
        raise HTTPException(status_code=404, detail="Critical control not found")
    updated = service.update_farsi(
        db,
        graph_driver,
        critical_control,
        farsi_functionality=body.farsi_functionality,
        farsi_availability=body.farsi_availability,
        farsi_reliability=body.farsi_reliability,
        farsi_survivability=body.farsi_survivability,
        farsi_interdependency=body.farsi_interdependency,
    )
    return _to_out(db, control_id, updated)


@router.get(
    "/critical-controls/{control_id}/performance-standards",
    response_model=list[PerformanceStandardOut],
)
def list_performance_standards(
    control_id: uuid.UUID, db: Session = Depends(get_db)
) -> list[PerformanceStandardOut]:
    critical_control = service.get_critical_control(db, control_id)
    if critical_control is None:
        raise HTTPException(status_code=404, detail="Critical control not found")
    standards = service.list_performance_standards(db, control_id)
    return [PerformanceStandardOut.model_validate(s) for s in standards]


@router.post(
    "/critical-controls/{control_id}/performance-standards",
    response_model=PerformanceStandardOut,
    status_code=201,
)
def create_performance_standard(
    control_id: uuid.UUID,
    body: PerformanceStandardInput,
    db: Session = Depends(get_db),
    graph_driver: Driver = Depends(get_graph_driver),
) -> PerformanceStandardOut:
    critical_control = service.get_critical_control(db, control_id)
    if critical_control is None:
        raise HTTPException(status_code=404, detail="Critical control not found")
    standard = service.create_performance_standard(
        db,
        graph_driver,
        critical_control_id=control_id,
        requirement_text=body.requirement_text,
        measurable_criteria=body.measurable_criteria,
    )
    return PerformanceStandardOut.model_validate(standard)
