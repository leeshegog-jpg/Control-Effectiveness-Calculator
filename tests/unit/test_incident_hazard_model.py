"""Unit coverage for the IncidentHazard ORM mapping (ACR-004 Option A --
bare composite key, no columns beyond incident_id/hazard_id).
"""

from app.models.safety import IncidentHazard
from sqlalchemy import inspect


def test_incident_hazard_maps_to_frozen_table_and_columns():
    mapper = inspect(IncidentHazard)
    assert mapper.local_table.schema == "safety"
    assert mapper.local_table.name == "incident_hazards"
    assert set(mapper.columns.keys()) == {"incident_id", "hazard_id"}


def test_incident_hazard_composite_primary_key():
    mapper = inspect(IncidentHazard)
    pk_columns = {col.name for col in mapper.primary_key}
    assert pk_columns == {"incident_id", "hazard_id"}
