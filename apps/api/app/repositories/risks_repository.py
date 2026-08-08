"""Risks repository. Postgres/SQLAlchemy access only, no business logic."""

import uuid

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.safety import Risk


def list_risks(
    db: Session,
    hazard_id: uuid.UUID | None,
    current_rating: str | None,
    limit: int,
    offset: int,
) -> tuple[list[Risk], int]:
    stmt = select(Risk)
    count_stmt = select(func.count()).select_from(Risk)
    if hazard_id is not None:
        stmt = stmt.where(Risk.hazard_id == hazard_id)
        count_stmt = count_stmt.where(Risk.hazard_id == hazard_id)
    if current_rating is not None:
        stmt = stmt.where(Risk.current_rating == current_rating)
        count_stmt = count_stmt.where(Risk.current_rating == current_rating)

    total = db.execute(count_stmt).scalar_one()
    items = list(
        db.execute(stmt.order_by(Risk.created_at.desc()).limit(limit).offset(offset))
        .scalars()
        .all()
    )
    return items, total


def get_risk(db: Session, risk_id: uuid.UUID) -> Risk | None:
    return db.get(Risk, risk_id)


def create_risk(db: Session, risk: Risk) -> Risk:
    db.add(risk)
    db.flush()
    return risk


def update_risk(db: Session, risk: Risk) -> Risk:
    db.flush()
    return risk
