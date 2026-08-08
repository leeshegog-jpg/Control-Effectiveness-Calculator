"""Critical Controls business rules -- Control Health State Machine.
See docs/knowledge-graph/08-critical-control-assurance-model.md §6 and
docs/knowledge-graph/07-inference-rules-catalogue.md R3/R6.

Scoped to what this milestone can compute: R5 (drift detection) needs
MonitoringSummary trend history, which is Safety Case Demonstration domain
and explicitly out of R1 Milestone 2's authorized scope -- so `Degraded`
is never returned here. `Verified` is a transient pass-through state per
the state diagram's own text ("Verified --> Healthy: R3/R5/R6 all clear"),
not a distinct queryable outcome, so it is also never returned by this
function -- "cleared, no issues" resolves directly to `Healthy`.
"""

from datetime import date
from typing import NamedTuple


class VerificationSnapshot(NamedTuple):
    due_date: date | None
    last_completed: date | None
    has_evidence: bool


def is_overdue(due_date: date | None, last_completed: date | None, today: date) -> bool:
    """R3 -- verification_activities.due_date < current_date AND
    (last_completed IS NULL OR last_completed < due_date).
    """
    if due_date is None:
        return False
    return due_date < today and (last_completed is None or last_completed < due_date)


def compute_health_state(activities: list[VerificationSnapshot], today: date) -> str:
    """Returns one of: Unverified, Overdue, Healthy."""
    completed = [a for a in activities if a.last_completed is not None]
    if not completed:
        return "Unverified"  # never verified -- no confidence evidence exists
    if any(not a.has_evidence for a in completed):
        return "Unverified"  # R6 -- superficial verification (completed, no evidence)
    if any(is_overdue(a.due_date, a.last_completed, today) for a in activities):
        return "Overdue"  # R3
    return "Healthy"
