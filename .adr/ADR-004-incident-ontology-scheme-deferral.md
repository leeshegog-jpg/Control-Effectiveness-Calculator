# ADR-004: Incident Domain — Defer Ontology Scheme for Incident Type / Root Cause Category

**Status:** Accepted (2026-08-12)

## 1. Decision Statement

`incidents.incident_type_concept_id` and `actions.root_cause_category_concept_id` are left unseeded — no new ontology scheme is created for either. Both fields remain nullable/optional exactly as the frozen schema and OpenAPI contract already specify. This decision resolves [19-r1-milestone-3b-incident-decision-register.md](../docs/implementation-blueprint/19-r1-milestone-3b-incident-decision-register.md) **D3**.

## 2. Context

`safety.incidents.incident_type_concept_id` and `safety.actions.root_cause_category_concept_id` are both foreign keys to `ontology.concepts`, per [03-postgresql-schema.sql](../docs/knowledge-graph/03-postgresql-schema.sql):519, :565. V1's `incident-report.html` (`fType`, line 81) carries a flat, hardcoded 6-value enum — Injury, Near Miss, Property Damage, Environmental, Security, Other — with no ontology backing anywhere in the V1 source. No root-cause-category concept exists in V1 at all; V1 only has free-text Immediate Cause/Root Cause fields ([18-r1-milestone-3a-incident-discovery-reconciliation.md](../docs/implementation-blueprint/18-r1-milestone-3a-incident-discovery-reconciliation.md) §2.1, §6). This is the same category of gap already standing for `Hazard.category_concept_id` — deferred, undecided, tracked as an open item since before this milestone.

## 3. Evidence Reviewed

- `ontology/schemes/` — empty directory, no scheme files.
- `ontology/seed-concepts/` — three files only: `consequence-domains.yaml`, `control-hierarchy.yaml`, `energy-sources.yaml`. No incident-type or root-cause-category scheme among them.
- `03-postgresql-schema.sql:519` — `incident_type_concept_id uuid REFERENCES ontology.concepts(id)`, no `NOT NULL`.
- `03-postgresql-schema.sql:565` — `root_cause_category_concept_id uuid REFERENCES ontology.concepts(id)`, no `NOT NULL`.
- `10-openapi.yaml:1089` (`IncidentInput.required: [datetime, description]`) and `:1116` (`ActionInput.required: [description]`) — neither `incident_type` nor `root_cause_category` is required.
- `03-postgresql-schema.sql:155` — `hazards.category_concept_id`, comment `-- Hazard taxonomy`, the standing precedent left `NULL`, cited in the handoff record as needing an ADR before any ontology expansion.
- [18-r1-milestone-3a-incident-discovery-reconciliation.md](../docs/implementation-blueprint/18-r1-milestone-3a-incident-discovery-reconciliation.md) §6 — original finding; [19](../docs/implementation-blueprint/19-r1-milestone-3b-incident-decision-register.md) D3 — governance routing (ADR, no baseline change under the deferral option).

## 4. Options Considered

- **(a) Defer** — leave both concept FKs `NULL`-capable, exactly as the frozen schema and OpenAPI already allow. No new `ontology.schemes`/`ontology.concepts` rows.
- **(b) Seed a scheme now**, mapped from V1's flat 6-value `incidentType` enum and inventing a root-cause-category taxonomy V1 never had. Would mean creating ontology data ahead of any milestone that requires it, and — for root-cause-category — inventing a classification scheme with no V1 precedent at all, not merely porting one.

## 5. Decision and Rationale

**(a) is adopted.** Both fields are already nullable at the schema level and optional in the OpenAPI contract — the deferral requires no change to either. Inventing a scheme now would violate the project's standing discipline against fabricating ontology structure ahead of an explicit, evidence-grounded mapping decision — the same discipline already applied to `Hazard.category_concept_id`. Treating this as a second, independent open question rather than folding it into the existing Hazard Taxonomy deferral would fragment governance over what is functionally the same unresolved design question (how — and whether — V1's flat category enums become controlled ontology schemes) applied to a different entity.

## 6. Consequences

- `Incident.incident_type` and `Action.root_cause_category` remain unset (`NULL`) for any record created without ontology input — implementation must not silently default them to a fabricated value or to V1's raw string labels stored where a `ConceptRef` is expected.
- Any future Incident implementation may still capture V1's raw category strings as free text elsewhere (e.g. in `description` or a dedicated field) if needed for V1 data parity — that is a separate, not-yet-raised question, not resolved by this ADR.
- If a scheme is later proposed for either field, that proposal is evaluated on its own evidence at that time — this ADR does not pre-approve or foreclose it, and does not bundle it with the Hazard Taxonomy question's eventual resolution merely because both are now tracked together.
- No CI/validation impact — `scripts/validate_openapi.py` and `ontology-validation` are unaffected; nothing in the OpenAPI contract or ontology directories changes.

## 7. Relationship to Other Decisions

This ADR is independent of D2/ADR-003 and D4/ACR-004 — it touches neither the Incident/Investigation/Action relationship structure nor the OpenAPI contract. It does not block, and is not blocked by, D5 or D6. It is explicitly linked to the standing **Hazard Taxonomy ontology scheme** deferred item (handoff record item 1) — both are the same open question (V1 flat-enum → ontology-scheme mapping), applied to different entities, and should be revisited together if either is ever taken up.

## 8. Explicit Scope Boundary

This ADR resolves **D3 only**. It does not resolve, and takes no position on:
- **D5** (five V1 fields with no schema home) — remains PENDING.
- **D6** (R10 notification-rule scope) — remains PENDING, awaiting Compliance/Legal input.
- The standing Hazard Taxonomy deferral itself — unchanged, still open, merely cross-referenced.
- No schema, OpenAPI, Neo4j, or application-code change is made or authorized by this ADR. No ontology scheme or concept row is created.
- No implementation of the Incident domain is authorized by this ADR.

## 9. Status

**Accepted (2026-08-12).** D3 closed. D5, D6 remain open per [19-r1-milestone-3b-incident-decision-register.md](../docs/implementation-blueprint/19-r1-milestone-3b-incident-decision-register.md).
