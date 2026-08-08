"""Hazards repository. Postgres/SQLAlchemy access only, no business logic."""

import uuid

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.safety import Hazard


def list_hazards(
    db: Session,
    asset_id: uuid.UUID | None,
    category_concept_id: uuid.UUID | None,
    limit: int,
    offset: int,
) -> tuple[list[Hazard], int]:
    stmt = select(Hazard)
    count_stmt = select(func.count()).select_from(Hazard)
    if asset_id is not None:
        stmt = stmt.where(Hazard.asset_id == asset_id)
        count_stmt = count_stmt.where(Hazard.asset_id == asset_id)
    if category_concept_id is not None:
        stmt = stmt.where(Hazard.category_concept_id == category_concept_id)
        count_stmt = count_stmt.where(Hazard.category_concept_id == category_concept_id)

    total = db.execute(count_stmt).scalar_one()
    items = list(db.execute(stmt.order_by(Hazard.name).limit(limit).offset(offset)).scalars().all())
    return items, total


def get_hazard(db: Session, hazard_id: uuid.UUID) -> Hazard | None:
    return db.get(Hazard, hazard_id)


def create_hazard(db: Session, hazard: Hazard) -> Hazard:
    db.add(hazard)
    db.flush()
    return hazard


def update_hazard(db: Session, hazard: Hazard) -> Hazard:
    db.flush()
    return hazard
