"""R1 Milestone 3D-1 persistence integration coverage against Postgres."""

from datetime import datetime, timezone
import uuid

from app.models.safety import Incident
from app.repositories.incidents_repository import (
    create_incident,
    get_incident,
    list_incidents,
    update_incident,
)


def test_incident_repository_create_read_update_list(db):
    incident = Incident(
        datetime=datetime.now(timezone.utc),
        description=f"3D-1 persistence test {uuid.uuid4()}",
    )

    created = create_incident(db, incident)
    db.commit()
    db.refresh(created)

    assert created.id is not None
    assert created.report_date is not None
    assert created.whsq_notified == "Not yet assessed"
    assert created.osr_notified == "Not applicable / under assessment"
    assert created.investigation_status == "Not Started"
    assert created.status == "Open"
    assert created.is_notifiable_incident is False

    loaded = get_incident(db, created.id)
    assert loaded is not None
    assert loaded.id == created.id
    assert loaded.description == incident.description

    loaded.description = "Updated persistence description"
    update_incident(db, loaded)
    db.commit()
    db.refresh(loaded)
    assert loaded.description == "Updated persistence description"

    items, total = list_incidents(db, limit=100, offset=0)
    assert total >= 1
    assert any(item.id == created.id for item in items)
