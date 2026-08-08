"""Control Health State Machine -- 08-critical-control-assurance-model.md §6,
scoped to R3 (overdue) and R6 (superficial verification); R5 (drift) is out
of this milestone's scope (needs MonitoringSummary trend history, Safety
Case Demonstration domain).
"""

from datetime import date

import pytest
from app.services.critical_controls.rules import (
    VerificationSnapshot,
    compute_health_state,
    is_overdue,
)

TODAY = date(2026, 8, 8)


def snap(due_date=None, last_completed=None, has_evidence=True):
    return VerificationSnapshot(
        due_date=due_date, last_completed=last_completed, has_evidence=has_evidence
    )


@pytest.mark.parametrize(
    ("due_date", "last_completed", "expected"),
    [
        (None, None, False),
        (date(2026, 9, 1), None, False),  # due in the future
        (date(2026, 7, 1), None, True),  # overdue, never completed
        (date(2026, 7, 1), date(2026, 6, 1), True),  # last completion predates due date
        (
            date(2026, 7, 1),
            date(2026, 7, 15),
            False,
        ),  # completed after due date -- current
        (date(2026, 9, 1), date(2026, 6, 1), False),  # not yet due again
    ],
)
def test_is_overdue_matches_r3(due_date, last_completed, expected):
    assert is_overdue(due_date, last_completed, TODAY) is expected


def test_health_state_unverified_when_never_completed():
    assert (
        compute_health_state([snap(due_date=date(2026, 9, 1))], TODAY) == "Unverified"
    )


def test_health_state_unverified_when_no_activities_at_all():
    assert compute_health_state([], TODAY) == "Unverified"


def test_health_state_unverified_when_completed_without_evidence():
    activities = [snap(last_completed=date(2026, 8, 1), has_evidence=False)]
    assert compute_health_state(activities, TODAY) == "Unverified"


def test_health_state_overdue_when_a_scheduled_check_is_late():
    activities = [
        snap(
            due_date=date(2026, 7, 1),
            last_completed=date(2026, 8, 1),
            has_evidence=True,
        ),
        snap(due_date=date(2026, 7, 1), last_completed=None, has_evidence=True),
    ]
    assert compute_health_state(activities, TODAY) == "Overdue"


def test_health_state_healthy_when_all_clear():
    activities = [
        snap(
            due_date=date(2026, 9, 1),
            last_completed=date(2026, 8, 1),
            has_evidence=True,
        ),
    ]
    assert compute_health_state(activities, TODAY) == "Healthy"
