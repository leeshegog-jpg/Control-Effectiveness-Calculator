"""Critical Controls repository (includes Performance Standards -- nested
1:N under CriticalControl per the frozen OpenAPI contract, no separate
router/module). Postgres/SQLAlchemy access only, no business logic.
"""

import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.safety import CriticalControl, Evidence, PerformanceStandard, VerificationActivity
from app.services.critical_controls.rules import VerificationSnapshot


def get_critical_control(db: Session, control_id: uuid.UUID) -> CriticalControl | None:
    return db.get(CriticalControl, control_id)


def create_critical_control(db: Session, critical_control: CriticalControl) -> CriticalControl:
    db.add(critical_control)
    db.flush()
    return critical_control


def update_critical_control(db: Session, critical_control: CriticalControl) -> CriticalControl:
    db.flush()
    return critical_control


def list_performance_standards(
    db: Session, critical_control_id: uuid.UUID
) -> list[PerformanceStandard]:
    stmt = (
        select(PerformanceStandard)
        .where(PerformanceStandard.critical_control_id == critical_control_id)
        .order_by(PerformanceStandard.created_at)
    )
    return list(db.execute(stmt).scalars().all())


def get_performance_standard(
    db: Session, performance_standard_id: uuid.UUID
) -> PerformanceStandard | None:
    return db.get(PerformanceStandard, performance_standard_id)


def create_performance_standard(
    db: Session, performance_standard: PerformanceStandard
) -> PerformanceStandard:
    db.add(performance_standard)
    db.flush()
    return performance_standard


def list_verification_snapshots(
    db: Session, critical_control_id: uuid.UUID
) -> list[VerificationSnapshot]:
    """Assembles the (due_date, last_completed, has_evidence) data
    app/services/critical_controls/rules.py:compute_health_state needs,
    across every VerificationActivity under every PerformanceStandard this
    CriticalControl governs.
    """
    activities = list(
        db.execute(
            select(VerificationActivity)
            .join(
                PerformanceStandard,
                VerificationActivity.performance_standard_id == PerformanceStandard.id,
            )
            .where(PerformanceStandard.critical_control_id == critical_control_id)
        )
        .scalars()
        .all()
    )
    if not activities:
        return []

    activity_ids = [a.id for a in activities]
    evidenced_ids = set(
        db.execute(
            select(Evidence.verification_activity_id).where(
                Evidence.verification_activity_id.in_(activity_ids)
            )
        )
        .scalars()
        .all()
    )
    return [
        VerificationSnapshot(
            due_date=a.due_date,
            last_completed=a.last_completed,
            has_evidence=a.id in evidenced_ids,
        )
        for a in activities
    ]
