"""Assets service -- R1 Milestone 0: CRUD + audit metadata (provenance) +
Neo4j sync. Validates the graph-first architecture end to end before
Hazard/Risk (higher-risk business domains, R1 Milestone 1) build on it.
"""

import uuid

from neo4j import Driver
from sqlalchemy.orm import Session

from app.graph import sync_service
from app.models.provenance import ProvenanceRecord
from app.models.safety import Asset
from app.repositories import assets_repository


def list_assets(
    db: Session, park_id: uuid.UUID | None, limit: int, offset: int
) -> tuple[list[Asset], int]:
    return assets_repository.list_assets(db, park_id=park_id, limit=limit, offset=offset)


def get_asset(db: Session, asset_id: uuid.UUID) -> Asset | None:
    return assets_repository.get_asset(db, asset_id)


def create_asset(
    db: Session,
    graph_driver: Driver,
    *,
    name: str,
    park_id: uuid.UUID | None,
    asset_type_concept_id: uuid.UUID | None,
    iso55000_class: str | None,
    status: str,
    created_by_person_id: uuid.UUID | None = None,
) -> Asset:
    asset = Asset(
        name=name,
        park_id=park_id,
        asset_type_concept_id=asset_type_concept_id,
        iso55000_class=iso55000_class,
        status=status,
    )
    assets_repository.create_asset(db, asset)

    # Audit metadata -- who/what/when created this row, per
    # docs/knowledge-graph/05-knowledge-provenance-model.md.
    db.add(
        ProvenanceRecord(
            entity_type="asset",
            entity_id=asset.id,
            source_type="human_entry",
            created_by_person_id=created_by_person_id,
        )
    )
    db.commit()
    db.refresh(asset)

    sync_service.sync_asset(graph_driver, asset)
    return asset


def update_asset(
    db: Session,
    graph_driver: Driver,
    asset: Asset,
    *,
    name: str | None = None,
    park_id: uuid.UUID | None = None,
    asset_type_concept_id: uuid.UUID | None = None,
    iso55000_class: str | None = None,
    status: str | None = None,
) -> Asset:
    if name is not None:
        asset.name = name
    if park_id is not None:
        asset.park_id = park_id
    if asset_type_concept_id is not None:
        asset.asset_type_concept_id = asset_type_concept_id
    if iso55000_class is not None:
        asset.iso55000_class = iso55000_class
    if status is not None:
        # includes retire/deactivate -- status='retired', no separate endpoint
        asset.status = status

    assets_repository.update_asset(db, asset)
    db.commit()
    db.refresh(asset)

    sync_service.sync_asset(graph_driver, asset)
    return asset
