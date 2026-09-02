"""Incidents router (OpenAPI tag). Contract: docs/knowledge-graph/10-openapi.yaml.

/incidents/{id}/evidence and /incidents/{id}/run-investigation-pipeline are
deliberately not implemented here -- Evidence wiring and the AI-layer
pipeline are separate, not-yet-authorized slices. See
docs/implementation-blueprint/22-r1-incident-reconciliation-decision-review.md.
"""

import uuid

from fastapi import APIRouter, Depends, HTTPException, Query
from neo4j import Driver
from sqlalchemy.orm import Session

from app.dependencies.db import get_db
from app.dependencies.graph import get_graph_driver
from app.dto.actions import ActionOut, IncidentActionLinkInput
from app.dto.assets import ConceptRef
from app.dto.hazards import HazardOut
from app.dto.incidents import IncidentHazardLinkInput, IncidentInput, IncidentListOut, IncidentOut
from app.dto.investigations import InvestigationInput, InvestigationOut
from app.models.ontology import Concept
from app.services.incidents import service
from app.services.investigations import service as investigations_service
from app.services.referential import ReferentialIntegrityError

router = APIRouter(prefix="/incidents", tags=["incidents"])


def _concept_ref(db: Session, concept_id: uuid.UUID | None) -> ConceptRef | None:
    if concept_id is None:
        return None
    concept = db.get(Concept, concept_id)
    return ConceptRef(concept_id=concept_id, pref_label=concept.pref_label if concept else None)


def _to_out(db: Session, incident) -> IncidentOut:
    return IncidentOut(
        id=incident.id,
        datetime=incident.datetime,
        incident_type=_concept_ref(db, incident.incident_type_concept_id),
        severity=incident.severity,
        vrtp_severity=incident.vrtp_severity,
        location=incident.location,
        asset_id=incident.asset_id,
        reporter_person_id=incident.reporter_person_id,
        description=incident.description,
        injuries=incident.injuries,
        witnesses=incident.witnesses,
        immediate_actions=incident.immediate_actions,
        immediate_cause=incident.immediate_cause,
        root_cause=incident.root_cause,
        whsq_notified=incident.whsq_notified,
        osr_notified=incident.osr_notified,
        investigation_status=incident.investigation_status,
        status=incident.status,
        is_notifiable_incident=incident.is_notifiable_incident,
        created_at=incident.created_at,
    )


def _action_to_out(db: Session, action) -> ActionOut:
    return ActionOut(
        id=action.id,
        source_type=_concept_ref(db, action.source_type_concept_id),
        source_id=action.source_id,
        description=action.description,
        root_cause_category=_concept_ref(db, action.root_cause_category_concept_id),
        priority=action.priority,
        assigned_to_person_id=action.assigned_to_person_id,
        due_date=action.due_date,
        status=action.status,
        effectiveness_review=action.effectiveness_review,
        completion_date=action.completion_date,
        notes=action.notes,
    )


def _hazard_to_out(db: Session, hazard) -> HazardOut:
    return HazardOut(
        id=hazard.id,
        asset_id=hazard.asset_id,
        name=hazard.name,
        description=hazard.description,
        exposure_pathway=hazard.exposure_pathway,
        possible_consequence=hazard.possible_consequence,
        category=_concept_ref(db, hazard.category_concept_id),
        energy_source=_concept_ref(db, hazard.energy_source_concept_id),
        date_identified=hazard.date_identified,
        owner_person_id=hazard.owner_person_id,
        is_adh=hazard.is_adh,
        device_boundary_id=hazard.device_boundary_id,
        created_at=hazard.created_at,
        updated_at=hazard.updated_at,
    )


@router.get("", response_model=IncidentListOut)
def list_incidents(
    limit: int = Query(default=50, le=200),
    offset: int = Query(default=0),
    db: Session = Depends(get_db),
) -> IncidentListOut:
    items, total = service.list_incidents(db, limit=limit, offset=offset)
    return IncidentListOut(items=[_to_out(db, i) for i in items], total=total)


@router.post("", response_model=IncidentOut, status_code=201)
def create_incident(
    body: IncidentInput,
    db: Session = Depends(get_db),
    graph_driver: Driver = Depends(get_graph_driver),
) -> IncidentOut:
    try:
        incident = service.create_incident(
            db,
            graph_driver,
            incident_datetime=body.datetime,
            incident_type_concept_id=body.incident_type.concept_id if body.incident_type else None,
            severity=body.severity,
            vrtp_severity=body.vrtp_severity,
            location=body.location,
            asset_id=body.asset_id,
            reporter_person_id=body.reporter_person_id,
            description=body.description,
            injuries=body.injuries,
            witnesses=body.witnesses,
            immediate_actions=body.immediate_actions,
            immediate_cause=body.immediate_cause,
            root_cause=body.root_cause,
            whsq_notified=body.whsq_notified,
            osr_notified=body.osr_notified,
            investigation_status=body.investigation_status,
            status=body.status,
            is_notifiable_incident=body.is_notifiable_incident,
        )
    except ReferentialIntegrityError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    return _to_out(db, incident)


@router.get("/{incident_id}", response_model=IncidentOut)
def get_incident(incident_id: uuid.UUID, db: Session = Depends(get_db)) -> IncidentOut:
    incident = service.get_incident(db, incident_id)
    if incident is None:
        raise HTTPException(status_code=404, detail="Incident not found")
    return _to_out(db, incident)


@router.patch("/{incident_id}", response_model=IncidentOut)
def update_incident(
    incident_id: uuid.UUID,
    body: IncidentInput,
    db: Session = Depends(get_db),
    graph_driver: Driver = Depends(get_graph_driver),
) -> IncidentOut:
    incident = service.get_incident(db, incident_id)
    if incident is None:
        raise HTTPException(status_code=404, detail="Incident not found")
    updated = service.update_incident(
        db,
        graph_driver,
        incident,
        incident_datetime=body.datetime,
        incident_type_concept_id=body.incident_type.concept_id if body.incident_type else None,
        severity=body.severity,
        vrtp_severity=body.vrtp_severity,
        location=body.location,
        asset_id=body.asset_id,
        reporter_person_id=body.reporter_person_id,
        description=body.description,
        injuries=body.injuries,
        witnesses=body.witnesses,
        immediate_actions=body.immediate_actions,
        immediate_cause=body.immediate_cause,
        root_cause=body.root_cause,
        whsq_notified=body.whsq_notified,
        osr_notified=body.osr_notified,
        investigation_status=body.investigation_status,
        status=body.status,
        is_notifiable_incident=body.is_notifiable_incident,
    )
    return _to_out(db, updated)


@router.get("/{incident_id}/hazards", response_model=list[HazardOut])
def list_incident_hazards(incident_id: uuid.UUID, db: Session = Depends(get_db)) -> list[HazardOut]:
    if service.get_incident(db, incident_id) is None:
        raise HTTPException(status_code=404, detail="Incident not found")
    hazards = service.list_incident_hazards(db, incident_id)
    return [_hazard_to_out(db, h) for h in hazards]


@router.post("/{incident_id}/hazards", status_code=201)
def link_incident_hazard(
    incident_id: uuid.UUID,
    body: IncidentHazardLinkInput,
    db: Session = Depends(get_db),
    graph_driver: Driver = Depends(get_graph_driver),
) -> dict:
    if service.get_incident(db, incident_id) is None:
        raise HTTPException(status_code=404, detail="Incident not found")
    service.link_incident_hazard(db, graph_driver, incident_id, body.hazard_id)
    return {}


@router.delete("/{incident_id}/hazards/{hazard_id}", status_code=204)
def unlink_incident_hazard(
    incident_id: uuid.UUID,
    hazard_id: uuid.UUID,
    db: Session = Depends(get_db),
    graph_driver: Driver = Depends(get_graph_driver),
) -> None:
    if service.get_incident(db, incident_id) is None:
        raise HTTPException(status_code=404, detail="Incident not found")
    existed = service.unlink_incident_hazard(db, graph_driver, incident_id, hazard_id)
    if not existed:
        raise HTTPException(status_code=404, detail="Hazard not linked to this incident")


def _investigation_to_out(investigation) -> InvestigationOut:
    return InvestigationOut(
        id=investigation.id,
        incident_id=investigation.incident_id,
        method=investigation.method,
        findings=investigation.findings,
        contributing_factors=investigation.contributing_factors,
        created_at=investigation.created_at,
        updated_at=investigation.updated_at,
    )


@router.get("/{incident_id}/investigation", response_model=InvestigationOut)
def get_investigation(incident_id: uuid.UUID, db: Session = Depends(get_db)) -> InvestigationOut:
    if service.get_incident(db, incident_id) is None:
        raise HTTPException(status_code=404, detail="Incident not found")
    investigation = investigations_service.get_investigation(db, incident_id)
    if investigation is None:
        raise HTTPException(status_code=404, detail="Investigation not found")
    return _investigation_to_out(investigation)


@router.post("/{incident_id}/investigation", response_model=InvestigationOut, status_code=201)
def create_investigation(
    incident_id: uuid.UUID,
    body: InvestigationInput,
    db: Session = Depends(get_db),
    graph_driver: Driver = Depends(get_graph_driver),
) -> InvestigationOut:
    if service.get_incident(db, incident_id) is None:
        raise HTTPException(status_code=404, detail="Incident not found")
    if investigations_service.get_investigation(db, incident_id) is not None:
        raise HTTPException(
            status_code=409, detail="Investigation already exists for this incident"
        )
    investigation = investigations_service.create_investigation(
        db,
        graph_driver,
        incident_id=incident_id,
        method=body.method,
        findings=body.findings,
        contributing_factors=body.contributing_factors,
    )
    return _investigation_to_out(investigation)


@router.patch("/{incident_id}/investigation", response_model=InvestigationOut)
def update_investigation(
    incident_id: uuid.UUID,
    body: InvestigationInput,
    db: Session = Depends(get_db),
    graph_driver: Driver = Depends(get_graph_driver),
) -> InvestigationOut:
    if service.get_incident(db, incident_id) is None:
        raise HTTPException(status_code=404, detail="Incident not found")
    investigation = investigations_service.get_investigation(db, incident_id)
    if investigation is None:
        raise HTTPException(status_code=404, detail="Investigation not found")
    updated = investigations_service.update_investigation(
        db,
        graph_driver,
        investigation,
        method=body.method,
        findings=body.findings,
        contributing_factors=body.contributing_factors,
    )
    return _investigation_to_out(updated)


@router.get("/{incident_id}/actions", response_model=list[ActionOut])
def list_incident_actions(incident_id: uuid.UUID, db: Session = Depends(get_db)) -> list[ActionOut]:
    if service.get_incident(db, incident_id) is None:
        raise HTTPException(status_code=404, detail="Incident not found")
    actions = service.list_incident_actions(db, incident_id)
    return [_action_to_out(db, a) for a in actions]


@router.post("/{incident_id}/actions", status_code=201)
def link_incident_action(
    incident_id: uuid.UUID,
    body: IncidentActionLinkInput,
    db: Session = Depends(get_db),
    graph_driver: Driver = Depends(get_graph_driver),
) -> dict:
    if service.get_incident(db, incident_id) is None:
        raise HTTPException(status_code=404, detail="Incident not found")
    service.link_incident_action(db, graph_driver, incident_id, body.action_id)
    return {}


@router.delete("/{incident_id}/actions/{action_id}", status_code=204)
def unlink_incident_action(
    incident_id: uuid.UUID,
    action_id: uuid.UUID,
    db: Session = Depends(get_db),
    graph_driver: Driver = Depends(get_graph_driver),
) -> None:
    if service.get_incident(db, incident_id) is None:
        raise HTTPException(status_code=404, detail="Incident not found")
    existed = service.unlink_incident_action(db, graph_driver, incident_id, action_id)
    if not existed:
        raise HTTPException(status_code=404, detail="Action not linked to this incident")
