"""Assets repository. Postgres/SQLAlchemy access only, no business logic."""

import uuid

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.safety import Asset


def list_assets(
    db: Session, park_id: uuid.UUID | None, limit: int, offset: int
) -> tuple[list[Asset], int]:
    stmt = select(Asset)
    count_stmt = select(func.count()).select_from(Asset)
    if park_id is not None:
        stmt = stmt.where(Asset.park_id == park_id)
        count_stmt = count_stmt.where(Asset.park_id == park_id)

    total = db.execute(count_stmt).scalar_one()
    items = list(db.execute(stmt.order_by(Asset.name).limit(limit).offset(offset)).scalars().all())
    return items, total


def get_asset(db: Session, asset_id: uuid.UUID) -> Asset | None:
    return db.get(Asset, asset_id)


def create_asset(db: Session, asset: Asset) -> Asset:
    db.add(asset)
    db.flush()
    return asset


def update_asset(db: Session, asset: Asset) -> Asset:
    db.flush()
    return asset
