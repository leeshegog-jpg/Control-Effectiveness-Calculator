# ACR-003: Competency Management Domain

**Raised by:** Project sponsor (leeshegog@icloud.com), 2026-08-04
**Affected document(s):** [03-postgresql-schema.sql](../docs/knowledge-graph/03-postgresql-schema.sql) (`safety.persons`), [01-enterprise-knowledge-graph-specification.md](../docs/knowledge-graph/01-enterprise-knowledge-graph-specification.md) §6, [13-application-foundation-scaffold.md](../docs/implementation-blueprint/13-application-foundation-scaffold.md) §12, ACR-001 (Training Domain — resolve together, not independently)

## Current state

Design Baseline v1.0 has no Competency entity, and (per ACR-001) no Training entity either. `safety.persons` records identity only, no competency/qualification/authorisation fields. From a Safety Case perspective, the claim a demonstration needs to support is normally "workers are competent," not "workers attended training" — training is one evidence source for competence, not the claim itself. Raising this as a separate ACR from ACR-001 rather than folding it in, because approving Training in isolation risks modelling the wrong canonical entity (Training) and needing to retrofit Competency around it later — the two proposed changes are coupled and should be assessed together before either is implemented.

## Proposed change

Assess whether **Competency** (not Training) is the canonical domain entity, with Training as one evidence type feeding it alongside:

1. **Qualifications** — formal, time-bound or permanent.
2. **Licences** — regulator-issued, may have expiry/renewal.
3. **OEM certifications** — manufacturer-specific, relevant given Assets/Device Boundary already models ride-specific equipment.
4. **Currency / refresher requirements** — a competency can lapse; this is a state, not a one-time fact, and needs a review-trigger mechanism (compare `safety.review_triggers`, already used for MOC).
5. **Competency assessments** — the actual determination event, distinct from any single evidence item feeding it.
6. **Authorisations** — role-specific sign-off to operate a specific asset or perform a specific control-critical task.
7. **Experience** — cumulative, harder to model as a discrete record; assessment must determine whether this is in scope for v1.1 or deferred.

Resolve jointly with ACR-001:
- Does `Training` become a subtype/evidence-source under `Competency`, or a peer entity?
- Required PostgreSQL tables, Neo4j nodes/relationships, ontology concepts, OpenAPI changes — same categories as ACR-001 §2–5, assessed for Competency as the parent concept.
- Links to Critical Controls (operator competency as a control-assurance input — does a critical control's assurance status depend on a linked `Competency` record's currency?), Regulatory Requirements, Safety Case (competency claims as `SafetyArgument`s grounded in `Evidence`).

## Impact

If approved, likely supersedes or substantially reframes ACR-001's scope rather than adding alongside it — both ACRs should be decided in the same review session, not sequentially, to avoid resolving ACR-001 first and then reopening it. Touches the same document set as ACR-001 if approved: schema, Neo4j model, OpenAPI, ontology, relationship/inference catalogues.

## Outcome paths

- **Approve** → Competency becomes the canonical entity in Design Baseline v1.1; Training is modelled as one evidence type within it. ACR-001 is resolved as superseded-by-ACR-003 rather than implemented independently.
- **Reject** → Fall back to ACR-001's Training-only scope (if ACR-001 is separately approved) or no competency/training domain at all (if both rejected) — either way, an explicit decision recorded here, not a default.

## Approval

**Approved** — Architecture Review Board (project sponsor), 2026-08-04, as canonical entity superseding [ACR-001](ACR-001-training-domain.md); Training is a `competency_type` evidence value, not its own table; `roles` + `role_competency_requirements` added per Guide §10.8 verification. Experience deferred to a future baseline version. Design Baseline updated to **v1.1**. Full review and regeneration record: [implementation-blueprint/14-architecture-change-requests.md](../docs/implementation-blueprint/14-architecture-change-requests.md) §4, §4a, §6, §8.
