"""Controls repository. Postgres/SQLAlchemy access only, no business logic."""

import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.safety import Control


def list_controls_for_risk(db: Session, risk_id: uuid.UUID) -> list[Control]:
    stmt = select(Control).where(Control.risk_id == risk_id).order_by(Control.created_at)
    return list(db.execute(stmt).scalars().all())


def get_control(db: Session, control_id: uuid.UUID) -> Control | None:
    return db.get(Control, control_id)


def create_control(db: Session, control: Control) -> Control:
    db.add(control)
    db.flush()
    return control


def update_control(db: Session, control: Control) -> Control:
    db.flush()
    return control
