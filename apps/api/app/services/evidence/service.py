"""Evidence service -- Evidence CRUD, audit metadata (provenance), Neo4j sync.

verification_activity_id is nullable on the frozen safety.evidence schema --
create_evidence accepts None for standalone evidence (e.g. incident-linked,
via linked_entity_type/linked_entity_id). sync_evidence already handles the
None case (no PRODUCES edge attempted); no Neo4j change needed here.
"""

import uuid

from neo4j import Driver
from sqlalchemy.orm import Session

from app.graph import sync_service
from app.models.ontology import Concept
from app.models.provenance import ProvenanceRecord
from app.models.safety import Evidence, Person
from app.repositories import evidence_repository
from app.services.referential import require_exists


def list_evidence(db: Session, verification_activity_id: uuid.UUID) -> list[Evidence]:
    return evidence_repository.list_evidence(db, verification_activity_id)


def list_incident_evidence(db: Session, incident_id: uuid.UUID) -> list[Evidence]:
    return evidence_repository.list_incident_evidence(db, incident_id)


def create_evidence(
    db: Session,
    graph_driver: Driver,
    *,
    verification_activity_id: uuid.UUID | None,
    type_concept_id: uuid.UUID | None,
    source_document_id: uuid.UUID | None,
    uploaded_by_person_id: uuid.UUID | None,
    linked_entity_type: str | None,
    linked_entity_id: uuid.UUID | None,
) -> Evidence:
    require_exists(db, Concept, type_concept_id, field="type", entity="ontology concept")
    require_exists(
        db, "safety.documents", source_document_id, field="source_document_id", entity="document"
    )
    require_exists(
        db, Person, uploaded_by_person_id, field="uploaded_by_person_id", entity="person"
    )
    evidence = Evidence(
        verification_activity_id=verification_activity_id,
        type_concept_id=type_concept_id,
        source_document_id=source_document_id,
        uploaded_by_person_id=uploaded_by_person_id,
        linked_entity_type=linked_entity_type,
        linked_entity_id=linked_entity_id,
    )
    evidence_repository.create_evidence(db, evidence)

    db.add(
        ProvenanceRecord(
            entity_type="evidence",
            entity_id=evidence.id,
            source_type="human_entry",
            created_by_person_id=uploaded_by_person_id,
        )
    )
    db.commit()
    db.refresh(evidence)

    sync_service.sync_evidence(graph_driver, evidence)
    return evidence
