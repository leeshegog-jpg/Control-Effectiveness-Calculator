"""Unit coverage for the Action and IncidentAction ORM mappings.

Action is a shared, polymorphic entity (ADR-003) -- reachable from Incident
or AuditFinding via source_type_concept_id/source_id. IncidentAction backs
safety.incident_actions (ACR-006 Option A -- bare composite key, no columns
beyond incident_id/action_id).
"""

from app.models.safety import Action, IncidentAction
from sqlalchemy import inspect


def test_action_maps_to_frozen_table_and_columns():
    mapper = inspect(Action)
    assert mapper.local_table.schema == "safety"
    assert mapper.local_table.name == "actions"

    expected = {
        "id",
        "source_type_concept_id",
        "source_id",
        "description",
        "root_cause_category_concept_id",
        "priority",
        "assigned_to_person_id",
        "due_date",
        "status",
        "completion_date",
        "effectiveness_review",
        "notes",
        "created_at",
        "updated_at",
    }
    assert set(mapper.columns.keys()) == expected


def test_incident_action_maps_to_frozen_table_and_columns():
    mapper = inspect(IncidentAction)
    assert mapper.local_table.schema == "safety"
    assert mapper.local_table.name == "incident_actions"
    assert set(mapper.columns.keys()) == {"incident_id", "action_id"}


def test_incident_action_composite_primary_key():
    pk_columns = {col.name for col in inspect(IncidentAction).primary_key}
    assert pk_columns == {"incident_id", "action_id"}
