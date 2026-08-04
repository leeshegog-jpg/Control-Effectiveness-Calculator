# ACR-001: Training Domain

**Raised by:** Project sponsor (leeshegog@icloud.com), 2026-08-04
**Affected document(s):** [03-postgresql-schema.sql](../docs/knowledge-graph/03-postgresql-schema.sql), [02-neo4j-node-relationship-model.md](../docs/knowledge-graph/02-neo4j-node-relationship-model.md), [10-openapi.yaml](../docs/knowledge-graph/10-openapi.yaml), [01-enterprise-knowledge-graph-specification.md](../docs/knowledge-graph/01-enterprise-knowledge-graph-specification.md) §6 (ontology governance), [13-application-foundation-scaffold.md](../docs/implementation-blueprint/13-application-foundation-scaffold.md) §12 (Training module — flagged, unimplemented)

## Current state

Design Baseline v1.0 has **no Training entity**. No table in `03-postgresql-schema.sql`, no node label in the Neo4j model, no `Training` tag in `10-openapi.yaml`, no ontology scheme. `safety.persons` records people but carries no competency/training fields. No V1 tool in the platform architecture inventory ([PLATFORM_ARCHITECTURE_V2.md](../docs/PLATFORM_ARCHITECTURE_V2.md)) covered training records. The Phase 2.2 scaffold ([13-application-foundation-scaffold.md](../docs/implementation-blueprint/13-application-foundation-scaffold.md) §12) created an empty `apps/web/src/modules/training/` placeholder and explicitly refused to attach any schema, endpoint, or ontology work to it pending this ACR.

## Proposed change

Assess whether Training becomes a first-class domain entity in Design Baseline v1.1. Assessment must resolve:

1. Whether `Training` is modelled as its own entity, or subsumed under a broader Competency entity (see ACR-003 — the two should be resolved together, not independently, since a standalone Training entity decided here could be immediately superseded).
2. Required PostgreSQL table(s) — fields, ownership schema (`safety.*` vs. a new namespace).
3. Required Neo4j node label(s) and relationship types (e.g. `PERSON -[COMPLETED]-> TRAINING_RECORD`, `TRAINING_RECORD -[QUALIFIES_FOR]-> ROLE`).
4. Ontology concepts — training category taxonomy, course/qualification classification scheme.
5. OpenAPI changes — new tag, paths, schemas in `10-openapi.yaml`.
6. AI extraction implications — is training completion/certificate content in scope for [04-ai-extraction-specification.md](../docs/knowledge-graph/04-ai-extraction-specification.md), and does it need its own `ExtractionRule`s.
7. Safety Case traceability — can a `SafetyArgument` cite a training record as `Evidence` (`safety.safety_argument_evidence`), and if so what evidence-quality bar applies.
8. Relationship links to: Competency (ACR-003), Verification (is a training record a form of `safety.verification_activities`?), Roles (not currently modelled anywhere in the baseline — a second gap this ACR may surface), Critical Controls (does control-operator competency gate a control's assurance status?), Regulatory Requirements (`regulatory.requirements`).

## Impact

Touches the PostgreSQL schema, Neo4j model, OpenAPI contract, ontology scheme set, AI extraction specification, and relationship/inference rule catalogues if approved — a Design Baseline v1.0 → v1.1 change, not a Phase 2.2 scaffolding change. No implementation work (schema, endpoint, ontology, or UI beyond the existing empty placeholder folder) proceeds against Training until this ACR is resolved, per [02-development-standards.md](../docs/implementation-blueprint/02-development-standards.md) §7.

## Outcome paths

- **Approve** → Design Baseline updated to v1.1 (controlled change): schema, Neo4j model, OpenAPI, relationship/inference catalogues, and documentation index regenerated in a single controlled pass, not piecemeal.
- **Reject** → Training remains an external integration or reporting view only; the placeholder module folder is either removed from the module list or repurposed as a read-only external-system link.

## Approval

**Rejected** — Architecture Review Board (project sponsor), 2026-08-04. Superseded by [ACR-003](ACR-003-competency-management-domain.md). Rationale and full review: [implementation-blueprint/14-architecture-change-requests.md](../docs/implementation-blueprint/14-architecture-change-requests.md) §2, §6.
