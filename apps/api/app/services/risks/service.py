"""Risks service -- CRUD + R1 rating derivation + R4 SFARP gate + audit
metadata (provenance) + Neo4j sync.
See docs/knowledge-graph/07-inference-rules-catalogue.md R1/R4.
"""

import uuid
from datetime import date

from neo4j import Driver
from sqlalchemy.orm import Session

from app.graph import sync_service
from app.models.provenance import ProvenanceRecord
from app.models.safety import Hazard, Risk
from app.repositories import risks_repository
from app.services.referential import require_exists
from app.services.risks import rules


class SfarpJustificationError(Exception):
    """Raised when R4's SFARP gate rejects a justification -- 422, not 500."""


def _apply_ratings(risk: Risk) -> None:
    risk.inherent_rating = rules.risk_band(
        rules.risk_score(risk.inherent_likelihood, risk.inherent_consequence)
    )
    risk.current_rating = rules.risk_band(
        rules.risk_score(risk.current_likelihood, risk.current_consequence)
    )


def _enforce_sfarp_gate(risk: Risk) -> None:
    if rules.sfarp_justification_insufficient(risk.current_rating, risk.sfarp_justification):
        raise SfarpJustificationError(
            "SFARP justification is required for Extreme/High current risk and must not "
            "simply say the risk is acceptable."
        )


def list_risks(
    db: Session,
    hazard_id: uuid.UUID | None,
    current_rating: str | None,
    limit: int,
    offset: int,
) -> tuple[list[Risk], int]:
    return risks_repository.list_risks(
        db, hazard_id=hazard_id, current_rating=current_rating, limit=limit, offset=offset
    )


def get_risk(db: Session, risk_id: uuid.UUID) -> Risk | None:
    return risks_repository.get_risk(db, risk_id)


def create_risk(
    db: Session,
    graph_driver: Driver,
    *,
    hazard_id: uuid.UUID,
    description: str,
    cause: str | None,
    inherent_likelihood: int | None,
    inherent_consequence: int | None,
    current_likelihood: int | None,
    current_consequence: int | None,
    target_likelihood: int | None,
    target_consequence: int | None,
    sfarp_justification: str | None,
    status: str,
    review_date: date | None,
    is_serious_risk: bool,
    serious_risk_justification: str | None,
    created_by_person_id: uuid.UUID | None = None,
) -> Risk:
    require_exists(db, Hazard, hazard_id, field="hazard_id", entity="hazard")
    risk = Risk(
        hazard_id=hazard_id,
        description=description,
        cause=cause,
        inherent_likelihood=inherent_likelihood,
        inherent_consequence=inherent_consequence,
        current_likelihood=current_likelihood,
        current_consequence=current_consequence,
        target_likelihood=target_likelihood,
        target_consequence=target_consequence,
        sfarp_justification=sfarp_justification,
        status=status,
        review_date=review_date,
        is_serious_risk=is_serious_risk,
        serious_risk_justification=serious_risk_justification,
    )
    _apply_ratings(risk)
    _enforce_sfarp_gate(risk)

    risks_repository.create_risk(db, risk)

    db.add(
        ProvenanceRecord(
            entity_type="risk",
            entity_id=risk.id,
            source_type="human_entry",
            created_by_person_id=created_by_person_id,
        )
    )
    db.commit()
    db.refresh(risk)

    sync_service.sync_risk(graph_driver, risk)
    return risk


def update_risk(
    db: Session,
    graph_driver: Driver,
    risk: Risk,
    *,
    description: str | None = None,
    cause: str | None = None,
    inherent_likelihood: int | None = None,
    inherent_consequence: int | None = None,
    current_likelihood: int | None = None,
    current_consequence: int | None = None,
    target_likelihood: int | None = None,
    target_consequence: int | None = None,
    sfarp_justification: str | None = None,
    status: str | None = None,
    review_date: date | None = None,
    is_serious_risk: bool | None = None,
    serious_risk_justification: str | None = None,
) -> Risk:
    if description is not None:
        risk.description = description
    if cause is not None:
        risk.cause = cause
    if inherent_likelihood is not None:
        risk.inherent_likelihood = inherent_likelihood
    if inherent_consequence is not None:
        risk.inherent_consequence = inherent_consequence
    if current_likelihood is not None:
        risk.current_likelihood = current_likelihood
    if current_consequence is not None:
        risk.current_consequence = current_consequence
    if target_likelihood is not None:
        risk.target_likelihood = target_likelihood
    if target_consequence is not None:
        risk.target_consequence = target_consequence
    if sfarp_justification is not None:
        risk.sfarp_justification = sfarp_justification
    if status is not None:
        risk.status = status
    if review_date is not None:
        risk.review_date = review_date
    if is_serious_risk is not None:
        risk.is_serious_risk = is_serious_risk
    if serious_risk_justification is not None:
        risk.serious_risk_justification = serious_risk_justification

    _apply_ratings(risk)
    _enforce_sfarp_gate(risk)

    risks_repository.update_risk(db, risk)
    db.commit()
    db.refresh(risk)

    sync_service.sync_risk(graph_driver, risk)
    return risk
