"""Unit coverage for the R1 Milestone 3D-1 Incident ORM mapping."""

from sqlalchemy import inspect

from app.models.safety import Incident


def test_incident_maps_to_frozen_table_and_columns():
    mapper = inspect(Incident)
    assert mapper.local_table.schema == "safety"
    assert mapper.local_table.name == "incidents"

    expected = {
        "id",
        "datetime",
        "report_date",
        "incident_type_concept_id",
        "severity",
        "vrtp_severity",
        "location",
        "asset_id",
        "reporter_person_id",
        "description",
        "injuries",
        "witnesses",
        "immediate_actions",
        "immediate_cause",
        "root_cause",
        "whsq_notified",
        "osr_notified",
        "investigation_status",
        "status",
        "created_at",
        "updated_at",
        "is_notifiable_incident",
    }
    assert set(mapper.columns.keys()) == expected


def test_incident_persistence_defaults_match_schema():
    columns = inspect(Incident).columns
    assert columns.report_date.server_default is not None
    assert columns.whsq_notified.server_default is not None
    assert columns.osr_notified.server_default is not None
    assert columns.investigation_status.server_default is not None
    assert columns.status.server_default is not None
    assert columns.is_notifiable_incident.server_default is not None
