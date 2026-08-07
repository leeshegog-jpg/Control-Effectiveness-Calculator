"""Assets router (OpenAPI tag). R1 Milestone 0: first domain implementation --
validates the end-to-end architecture (Postgres + Neo4j + provenance) before
Hazard/Risk Register (R1 Milestone 1) build on it.
"""

import uuid

from fastapi import APIRouter, Depends, HTTPException, Query
from neo4j import Driver
from sqlalchemy.orm import Session

from app.dependencies.db import get_db
from app.dependencies.graph import get_graph_driver
from app.dto.assets import AssetInput, AssetListOut, AssetOut, ConceptRef
from app.models.ontology import Concept
from app.services.assets import service

router = APIRouter(prefix="/assets", tags=["assets"])


def _to_out(db: Session, asset) -> AssetOut:
    asset_type = None
    if asset.asset_type_concept_id is not None:
        concept = db.get(Concept, asset.asset_type_concept_id)
        asset_type = ConceptRef(
            concept_id=asset.asset_type_concept_id,
            pref_label=concept.pref_label if concept else None,
        )
    return AssetOut(
        id=asset.id,
        name=asset.name,
        park_id=asset.park_id,
        asset_type=asset_type,
        iso55000_class=asset.iso55000_class,
        status=asset.status,
        created_at=asset.created_at,
        updated_at=asset.updated_at,
    )


@router.get("", response_model=AssetListOut)
def list_assets(
    park_id: uuid.UUID | None = Query(default=None),
    limit: int = Query(default=50, le=200),
    offset: int = Query(default=0),
    db: Session = Depends(get_db),
) -> AssetListOut:
    items, total = service.list_assets(db, park_id=park_id, limit=limit, offset=offset)
    return AssetListOut(items=[_to_out(db, a) for a in items], total=total)


@router.post("", response_model=AssetOut, status_code=201)
def create_asset(
    body: AssetInput,
    db: Session = Depends(get_db),
    graph_driver: Driver = Depends(get_graph_driver),
) -> AssetOut:
    asset = service.create_asset(
        db,
        graph_driver,
        name=body.name,
        park_id=body.park_id,
        asset_type_concept_id=body.asset_type.concept_id if body.asset_type else None,
        iso55000_class=body.iso55000_class,
        status=body.status,
    )
    return _to_out(db, asset)


@router.get("/{asset_id}", response_model=AssetOut)
def get_asset(asset_id: uuid.UUID, db: Session = Depends(get_db)) -> AssetOut:
    asset = service.get_asset(db, asset_id)
    if asset is None:
        raise HTTPException(status_code=404, detail="Asset not found")
    return _to_out(db, asset)


@router.patch("/{asset_id}", response_model=AssetOut)
def update_asset(
    asset_id: uuid.UUID,
    body: AssetInput,
    db: Session = Depends(get_db),
    graph_driver: Driver = Depends(get_graph_driver),
) -> AssetOut:
    asset = service.get_asset(db, asset_id)
    if asset is None:
        raise HTTPException(status_code=404, detail="Asset not found")
    updated = service.update_asset(
        db,
        graph_driver,
        asset,
        name=body.name,
        park_id=body.park_id,
        asset_type_concept_id=body.asset_type.concept_id if body.asset_type else None,
        iso55000_class=body.iso55000_class,
        status=body.status,
    )
    return _to_out(db, updated)
