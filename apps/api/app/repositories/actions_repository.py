"""Actions repository. Postgres/SQLAlchemy access only, no business logic.

Relational incident_actions (ACR-006 Option A) persistence lives in
incidents_repository.py, mirroring incident_hazards -- Action itself is a
shared, polymorphic entity (ADR-003), not owned by the Incident domain.
"""

import uuid

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.safety import Action


def list_actions(
    db: Session,
    status: str | None,
    limit: int,
    offset: int,
) -> tuple[list[Action], int]:
    stmt = select(Action)
    count_stmt = select(func.count()).select_from(Action)
    if status is not None:
        stmt = stmt.where(Action.status == status)
        count_stmt = count_stmt.where(Action.status == status)

    total = db.execute(count_stmt).scalar_one()
    items = list(
        db.execute(stmt.order_by(Action.created_at.desc()).limit(limit).offset(offset))
        .scalars()
        .all()
    )
    return items, total


def get_action(db: Session, action_id: uuid.UUID) -> Action | None:
    return db.get(Action, action_id)


def create_action(db: Session, action: Action) -> Action:
    db.add(action)
    db.flush()
    return action


def update_action(db: Session, action: Action) -> Action:
    db.flush()
    return action
