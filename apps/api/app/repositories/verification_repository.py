"""Verification repository. Postgres/SQLAlchemy access only, no business logic."""

import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.safety import VerificationActivity


def list_verification_activities(
    db: Session, performance_standard_id: uuid.UUID
) -> list[VerificationActivity]:
    stmt = (
        select(VerificationActivity)
        .where(VerificationActivity.performance_standard_id == performance_standard_id)
        .order_by(VerificationActivity.created_at)
    )
    return list(db.execute(stmt).scalars().all())


def get_verification_activity(
    db: Session, verification_activity_id: uuid.UUID
) -> VerificationActivity | None:
    return db.get(VerificationActivity, verification_activity_id)


def create_verification_activity(
    db: Session, activity: VerificationActivity
) -> VerificationActivity:
    db.add(activity)
    db.flush()
    return activity
