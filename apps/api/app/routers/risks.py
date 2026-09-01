"""Risks router (OpenAPI tag). R1 Milestone 1 Phase 2 -- Risk Register
migration. Contract: docs/knowledge-graph/10-openapi.yaml.

/risks/{riskId}/controls and /controls/{id} are deliberately not
implemented here -- V1 only ever captured "Existing Controls" as free text
(see app/models/safety.py module docstring); structured Control records
belong to the dedicated Critical Controls milestone.
"""

import uuid

from fastapi import APIRouter, Depends, HTTPException, Query
from neo4j import Driver
from sqlalchemy.orm import Session

from app.dependencies.db import get_db
from app.dependencies.graph import get_graph_driver
from app.dto.risks import RiskInput, RiskListOut, RiskOut
from app.services.referential import ReferentialIntegrityError
from app.services.risks import service
from app.services.risks.service import SfarpJustificationError

router = APIRouter(prefix="/risks", tags=["risks"])


@router.get("", response_model=RiskListOut)
def list_risks(
    hazard_id: uuid.UUID | None = Query(default=None),
    current_rating: str | None = Query(default=None),
    limit: int = Query(default=50, le=200),
    offset: int = Query(default=0),
    db: Session = Depends(get_db),
) -> RiskListOut:
    items, total = service.list_risks(
        db, hazard_id=hazard_id, current_rating=current_rating, limit=limit, offset=offset
    )
    return RiskListOut(items=[RiskOut.model_validate(r) for r in items], total=total)


@router.post("", response_model=RiskOut, status_code=201)
def create_risk(
    body: RiskInput,
    db: Session = Depends(get_db),
    graph_driver: Driver = Depends(get_graph_driver),
) -> RiskOut:
    try:
        risk = service.create_risk(
            db,
            graph_driver,
            hazard_id=body.hazard_id,
            description=body.description,
            cause=body.cause,
            inherent_likelihood=body.inherent_likelihood,
            inherent_consequence=body.inherent_consequence,
            current_likelihood=body.current_likelihood,
            current_consequence=body.current_consequence,
            target_likelihood=body.target_likelihood,
            target_consequence=body.target_consequence,
            sfarp_justification=body.sfarp_justification,
            status=body.status,
            review_date=body.review_date,
            is_serious_risk=body.is_serious_risk,
            serious_risk_justification=body.serious_risk_justification,
        )
    except ReferentialIntegrityError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except SfarpJustificationError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    return RiskOut.model_validate(risk)


@router.get("/{risk_id}", response_model=RiskOut)
def get_risk(risk_id: uuid.UUID, db: Session = Depends(get_db)) -> RiskOut:
    risk = service.get_risk(db, risk_id)
    if risk is None:
        raise HTTPException(status_code=404, detail="Risk not found")
    return RiskOut.model_validate(risk)


@router.patch("/{risk_id}", response_model=RiskOut)
def update_risk(
    risk_id: uuid.UUID,
    body: RiskInput,
    db: Session = Depends(get_db),
    graph_driver: Driver = Depends(get_graph_driver),
) -> RiskOut:
    risk = service.get_risk(db, risk_id)
    if risk is None:
        raise HTTPException(status_code=404, detail="Risk not found")
    try:
        updated = service.update_risk(
            db,
            graph_driver,
            risk,
            description=body.description,
            cause=body.cause,
            inherent_likelihood=body.inherent_likelihood,
            inherent_consequence=body.inherent_consequence,
            current_likelihood=body.current_likelihood,
            current_consequence=body.current_consequence,
            target_likelihood=body.target_likelihood,
            target_consequence=body.target_consequence,
            sfarp_justification=body.sfarp_justification,
            status=body.status,
            review_date=body.review_date,
            is_serious_risk=body.is_serious_risk,
            serious_risk_justification=body.serious_risk_justification,
        )
    except SfarpJustificationError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    return RiskOut.model_validate(updated)
