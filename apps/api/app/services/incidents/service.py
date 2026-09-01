"""Incidents service -- CRUD + Neo4j sync (bare Incident node only) +
relational hazard-link (safety.incident_hazards, ACR-004 Option A) and
Action-link (safety.incident_actions, ACR-006 Option A), both with graph
sync driven off the relational rows.

Investigation lives in services/investigations (ADR-003 sibling structure,
not nested here) -- Action is likewise a shared entity (services/actions
owns Action CRUD), only its Incident link lives here. Evidence wiring,
completion_date/notes, action_controls/REMEDIATES, and osr_notified logic
remain out of scope -- see
docs/implementation-blueprint/22-r1-incident-reconciliation-decision-review.md.
"""

import uuid
from datetime import datetime

from neo4j import Driver
from sqlalchemy.orm import Session

from app.graph import sync_service
from app.models.ontology import Concept
from app.models.safety import Action, Asset, Hazard, Incident, Person
from app.repositories import incidents_repository
from app.services.referential import require_exists


def list_incidents(db: Session, limit: int, offset: int) -> tuple[list[Incident], int]:
    return incidents_repository.list_incidents(db, limit=limit, offset=offset)


def get_incident(db: Session, incident_id: uuid.UUID) -> Incident | None:
    return incidents_repository.get_incident(db, incident_id)


def create_incident(
    db: Session,
    graph_driver: Driver,
    *,
    incident_datetime: datetime,
    incident_type_concept_id: uuid.UUID | None,
    severity: int | None,
    vrtp_severity: str | None,
    location: str | None,
    asset_id: uuid.UUID | None,
    reporter_person_id: uuid.UUID | None,
    description: str,
    injuries: str | None,
    witnesses: str | None,
    immediate_actions: str | None,
    immediate_cause: str | None,
    root_cause: str | None,
    whsq_notified: str | None,
    osr_notified: str | None,
    investigation_status: str | None,
    status: str | None,
    is_notifiable_incident: bool,
) -> Incident:
    require_exists(
        db, Concept, incident_type_concept_id, field="incident_type", entity="ontology concept"
    )
    require_exists(db, Asset, asset_id, field="asset_id", entity="asset")
    require_exists(db, Person, reporter_person_id, field="reporter_person_id", entity="person")
    incident = Incident(
        datetime=incident_datetime,
        incident_type_concept_id=incident_type_concept_id,
        severity=severity,
        vrtp_severity=vrtp_severity,
        location=location,
        asset_id=asset_id,
        reporter_person_id=reporter_person_id,
        description=description,
        injuries=injuries,
        witnesses=witnesses,
        immediate_actions=immediate_actions,
        immediate_cause=immediate_cause,
        root_cause=root_cause,
        is_notifiable_incident=is_notifiable_incident,
    )
    if whsq_notified is not None:
        incident.whsq_notified = whsq_notified
    if osr_notified is not None:
        incident.osr_notified = osr_notified
    if investigation_status is not None:
        incident.investigation_status = investigation_status
    if status is not None:
        incident.status = status

    incidents_repository.create_incident(db, incident)
    db.commit()
    db.refresh(incident)

    sync_service.sync_incident(graph_driver, incident)
    return incident


def update_incident(
    db: Session,
    graph_driver: Driver,
    incident: Incident,
    *,
    incident_datetime: datetime | None = None,
    incident_type_concept_id: uuid.UUID | None = None,
    severity: int | None = None,
    vrtp_severity: str | None = None,
    location: str | None = None,
    asset_id: uuid.UUID | None = None,
    reporter_person_id: uuid.UUID | None = None,
    description: str | None = None,
    injuries: str | None = None,
    witnesses: str | None = None,
    immediate_actions: str | None = None,
    immediate_cause: str | None = None,
    root_cause: str | None = None,
    whsq_notified: str | None = None,
    osr_notified: str | None = None,
    investigation_status: str | None = None,
    status: str | None = None,
    is_notifiable_incident: bool | None = None,
) -> Incident:
    if incident_datetime is not None:
        incident.datetime = incident_datetime
    if incident_type_concept_id is not None:
        incident.incident_type_concept_id = incident_type_concept_id
    if severity is not None:
        incident.severity = severity
    if vrtp_severity is not None:
        incident.vrtp_severity = vrtp_severity
    if location is not None:
        incident.location = location
    if asset_id is not None:
        incident.asset_id = asset_id
    if reporter_person_id is not None:
        incident.reporter_person_id = reporter_person_id
    if description is not None:
        incident.description = description
    if injuries is not None:
        incident.injuries = injuries
    if witnesses is not None:
        incident.witnesses = witnesses
    if immediate_actions is not None:
        incident.immediate_actions = immediate_actions
    if immediate_cause is not None:
        incident.immediate_cause = immediate_cause
    if root_cause is not None:
        incident.root_cause = root_cause
    if whsq_notified is not None:
        incident.whsq_notified = whsq_notified
    if osr_notified is not None:
        incident.osr_notified = osr_notified
    if investigation_status is not None:
        incident.investigation_status = investigation_status
    if status is not None:
        incident.status = status
    if is_notifiable_incident is not None:
        incident.is_notifiable_incident = is_notifiable_incident

    incidents_repository.update_incident(db, incident)
    db.commit()
    db.refresh(incident)

    sync_service.sync_incident(graph_driver, incident)
    return incident


def list_incident_hazards(db: Session, incident_id: uuid.UUID) -> list[Hazard]:
    return incidents_repository.list_incident_hazards(db, incident_id)


def link_incident_hazard(
    db: Session, graph_driver: Driver, incident_id: uuid.UUID, hazard_id: uuid.UUID
) -> None:
    """Relational link (source of truth) + REVEALS sync -- incident_hazards
    rows drive the graph edge, not the other way around.
    """
    incidents_repository.link_incident_hazard(db, incident_id, hazard_id)
    db.commit()
    sync_service.sync_incident_hazard_link(graph_driver, incident_id, hazard_id)


def unlink_incident_hazard(
    db: Session, graph_driver: Driver, incident_id: uuid.UUID, hazard_id: uuid.UUID
) -> bool:
    existed = incidents_repository.unlink_incident_hazard(db, incident_id, hazard_id)
    db.commit()
    if existed:
        sync_service.unsync_incident_hazard_link(graph_driver, incident_id, hazard_id)
    return existed


def list_incident_actions(db: Session, incident_id: uuid.UUID) -> list[Action]:
    return incidents_repository.list_incident_actions(db, incident_id)


def link_incident_action(
    db: Session, graph_driver: Driver, incident_id: uuid.UUID, action_id: uuid.UUID
) -> None:
    """Relational link (source of truth) + TRIGGERS sync -- incident_actions
    rows drive the graph edge, not the other way around. ACR-006 Option A:
    links an existing Action only, does not create one.
    """
    incidents_repository.link_incident_action(db, incident_id, action_id)
    db.commit()
    sync_service.sync_incident_action_link(graph_driver, incident_id, action_id)


def unlink_incident_action(
    db: Session, graph_driver: Driver, incident_id: uuid.UUID, action_id: uuid.UUID
) -> bool:
    existed = incidents_repository.unlink_incident_action(db, incident_id, action_id)
    db.commit()
    if existed:
        sync_service.unsync_incident_action_link(graph_driver, incident_id, action_id)
    return existed
