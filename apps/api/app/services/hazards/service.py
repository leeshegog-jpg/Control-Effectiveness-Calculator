"""Hazards service -- CRUD + audit metadata (provenance) + Neo4j sync.
R1 Milestone 1 Phase 1: the reusable enterprise hazard object that Risk
Register (Phase 2) links against, instead of every risk inventing its own
hazard terminology.
"""

import uuid
from datetime import date

from neo4j import Driver
from sqlalchemy.orm import Session

from app.graph import sync_service
from app.models.provenance import ProvenanceRecord
from app.models.safety import Hazard
from app.repositories import hazards_repository


def list_hazards(
    db: Session,
    asset_id: uuid.UUID | None,
    category_concept_id: uuid.UUID | None,
    limit: int,
    offset: int,
) -> tuple[list[Hazard], int]:
    return hazards_repository.list_hazards(
        db, asset_id=asset_id, category_concept_id=category_concept_id, limit=limit, offset=offset
    )


def get_hazard(db: Session, hazard_id: uuid.UUID) -> Hazard | None:
    return hazards_repository.get_hazard(db, hazard_id)


def create_hazard(
    db: Session,
    graph_driver: Driver,
    *,
    asset_id: uuid.UUID | None,
    name: str,
    description: str,
    exposure_pathway: str | None,
    possible_consequence: str | None,
    category_concept_id: uuid.UUID | None,
    energy_source_concept_id: uuid.UUID | None,
    date_identified: date | None,
    owner_person_id: uuid.UUID | None,
    is_adh: bool,
    device_boundary_id: uuid.UUID | None,
    created_by_person_id: uuid.UUID | None = None,
) -> Hazard:
    hazard = Hazard(
        asset_id=asset_id,
        name=name,
        description=description,
        exposure_pathway=exposure_pathway,
        possible_consequence=possible_consequence,
        category_concept_id=category_concept_id,
        energy_source_concept_id=energy_source_concept_id,
        owner_person_id=owner_person_id,
        is_adh=is_adh,
        device_boundary_id=device_boundary_id,
    )
    if date_identified is not None:
        hazard.date_identified = date_identified
    hazards_repository.create_hazard(db, hazard)

    db.add(
        ProvenanceRecord(
            entity_type="hazard",
            entity_id=hazard.id,
            source_type="human_entry",
            created_by_person_id=created_by_person_id,
        )
    )
    db.commit()
    db.refresh(hazard)

    sync_service.sync_hazard(graph_driver, hazard)
    return hazard


def update_hazard(
    db: Session,
    graph_driver: Driver,
    hazard: Hazard,
    *,
    asset_id: uuid.UUID | None = None,
    name: str | None = None,
    description: str | None = None,
    exposure_pathway: str | None = None,
    possible_consequence: str | None = None,
    category_concept_id: uuid.UUID | None = None,
    energy_source_concept_id: uuid.UUID | None = None,
    date_identified: date | None = None,
    owner_person_id: uuid.UUID | None = None,
    is_adh: bool | None = None,
    device_boundary_id: uuid.UUID | None = None,
) -> Hazard:
    if asset_id is not None:
        hazard.asset_id = asset_id
    if name is not None:
        hazard.name = name
    if description is not None:
        hazard.description = description
    if exposure_pathway is not None:
        hazard.exposure_pathway = exposure_pathway
    if possible_consequence is not None:
        hazard.possible_consequence = possible_consequence
    if category_concept_id is not None:
        hazard.category_concept_id = category_concept_id
    if energy_source_concept_id is not None:
        hazard.energy_source_concept_id = energy_source_concept_id
    if date_identified is not None:
        hazard.date_identified = date_identified
    if owner_person_id is not None:
        hazard.owner_person_id = owner_person_id
    if is_adh is not None:
        hazard.is_adh = is_adh
    if device_boundary_id is not None:
        hazard.device_boundary_id = device_boundary_id

    hazards_repository.update_hazard(db, hazard)
    db.commit()
    db.refresh(hazard)

    sync_service.sync_hazard(graph_driver, hazard)
    return hazard
