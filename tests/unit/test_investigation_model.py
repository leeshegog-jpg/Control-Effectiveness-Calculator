"""Unit coverage for the Investigation ORM mapping (ADR-003 sibling
structure -- 1:1 via incident_id UNIQUE, not a chain).
"""

from app.models.safety import Investigation
from sqlalchemy import inspect


def test_investigation_maps_to_frozen_table_and_columns():
    mapper = inspect(Investigation)
    assert mapper.local_table.schema == "safety"
    assert mapper.local_table.name == "investigations"

    expected = {
        "id",
        "incident_id",
        "method",
        "findings",
        "contributing_factors",
        "created_at",
        "updated_at",
    }
    assert set(mapper.columns.keys()) == expected


def test_investigation_incident_id_is_unique():
    columns = inspect(Investigation).columns
    assert columns.incident_id.unique is True
    assert columns.incident_id.nullable is False
