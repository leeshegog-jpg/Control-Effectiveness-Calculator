"""Hazards router (OpenAPI tag). R1 Milestone 1 Phase 1 -- the reusable
enterprise hazard object. Contract: docs/knowledge-graph/10-openapi.yaml.

/hazards/{id}/duplicate-candidates (R9 duplicate detection, AI-driven) and
/hazards/{id}/credible-events (ADI/ADH pathway, Safety Case Demonstration
domain) are deliberately not implemented here -- separate feature domains,
not part of the Hazard Library CRUD baseline this milestone builds.
"""

import uuid

from fastapi import APIRouter, Depends, HTTPException, Query
from neo4j import Driver
from sqlalchemy.orm import Session

from app.dependencies.db import get_db
from app.dependencies.graph import get_graph_driver
from app.dto.assets import ConceptRef
from app.dto.hazards import HazardInput, HazardListOut, HazardOut
from app.models.ontology import Concept
from app.services.hazards import service
from app.services.referential import ReferentialIntegrityError

router = APIRouter(prefix="/hazards", tags=["hazards"])


def _concept_ref(db: Session, concept_id: uuid.UUID | None) -> ConceptRef | None:
    if concept_id is None:
        return None
    concept = db.get(Concept, concept_id)
    return ConceptRef(concept_id=concept_id, pref_label=concept.pref_label if concept else None)


def _to_out(db: Session, hazard) -> HazardOut:
    return HazardOut(
        id=hazard.id,
        asset_id=hazard.asset_id,
        name=hazard.name,
        description=hazard.description,
        exposure_pathway=hazard.exposure_pathway,
        possible_consequence=hazard.possible_consequence,
        category=_concept_ref(db, hazard.category_concept_id),
        energy_source=_concept_ref(db, hazard.energy_source_concept_id),
        date_identified=hazard.date_identified,
        owner_person_id=hazard.owner_person_id,
        is_adh=hazard.is_adh,
        device_boundary_id=hazard.device_boundary_id,
        created_at=hazard.created_at,
        updated_at=hazard.updated_at,
    )


@router.get("", response_model=HazardListOut)
def list_hazards(
    asset_id: uuid.UUID | None = Query(default=None),
    category_concept_id: uuid.UUID | None = Query(default=None),
    limit: int = Query(default=50, le=200),
    offset: int = Query(default=0),
    db: Session = Depends(get_db),
) -> HazardListOut:
    items, total = service.list_hazards(
        db, asset_id=asset_id, category_concept_id=category_concept_id, limit=limit, offset=offset
    )
    return HazardListOut(items=[_to_out(db, h) for h in items], total=total)


@router.post("", response_model=HazardOut, status_code=201)
def create_hazard(
    body: HazardInput,
    db: Session = Depends(get_db),
    graph_driver: Driver = Depends(get_graph_driver),
) -> HazardOut:
    try:
        hazard = service.create_hazard(
            db,
            graph_driver,
            asset_id=body.asset_id,
            name=body.name,
            description=body.description,
            exposure_pathway=body.exposure_pathway,
            possible_consequence=body.possible_consequence,
            category_concept_id=body.category.concept_id if body.category else None,
            energy_source_concept_id=body.energy_source.concept_id if body.energy_source else None,
            date_identified=body.date_identified,
            owner_person_id=body.owner_person_id,
            is_adh=body.is_adh,
            device_boundary_id=body.device_boundary_id,
        )
    except ReferentialIntegrityError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    return _to_out(db, hazard)


@router.get("/{hazard_id}", response_model=HazardOut)
def get_hazard(hazard_id: uuid.UUID, db: Session = Depends(get_db)) -> HazardOut:
    hazard = service.get_hazard(db, hazard_id)
    if hazard is None:
        raise HTTPException(status_code=404, detail="Hazard not found")
    return _to_out(db, hazard)


@router.patch("/{hazard_id}", response_model=HazardOut)
def update_hazard(
    hazard_id: uuid.UUID,
    body: HazardInput,
    db: Session = Depends(get_db),
    graph_driver: Driver = Depends(get_graph_driver),
) -> HazardOut:
    hazard = service.get_hazard(db, hazard_id)
    if hazard is None:
        raise HTTPException(status_code=404, detail="Hazard not found")
    updated = service.update_hazard(
        db,
        graph_driver,
        hazard,
        asset_id=body.asset_id,
        name=body.name,
        description=body.description,
        exposure_pathway=body.exposure_pathway,
        possible_consequence=body.possible_consequence,
        category_concept_id=body.category.concept_id if body.category else None,
        energy_source_concept_id=body.energy_source.concept_id if body.energy_source else None,
        date_identified=body.date_identified,
        owner_person_id=body.owner_person_id,
        is_adh=body.is_adh,
        device_boundary_id=body.device_boundary_id,
    )
    return _to_out(db, updated)
