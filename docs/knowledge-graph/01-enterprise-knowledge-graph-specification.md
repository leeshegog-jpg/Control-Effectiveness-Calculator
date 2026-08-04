# Enterprise Knowledge Graph Specification
**Status: DRAFT — controlled design document. Requires approval before implementation.**
**Parent document:** [`PLATFORM_ARCHITECTURE_V2.md`](../PLATFORM_ARCHITECTURE_V2.md)
**Depends on / is depended on by:** [02-neo4j-node-relationship-model.md](02-neo4j-node-relationship-model.md), [06-relationship-rules-catalogue.md](06-relationship-rules-catalogue.md), [07-inference-rules-catalogue.md](07-inference-rules-catalogue.md)

---

## 1. Purpose

The Enterprise Knowledge Graph (EKG) is the platform's authoritative representation of **how VRTP's safety knowledge connects** — which assets have which hazards, which risks those hazards give rise to, which controls mitigate those risks, which of those controls are critical, how each is verified, what evidence exists, and how all of that traces to a regulatory or standards obligation. It exists to answer the question stated as the platform's core objective:

> "Show me every critical risk, the controls preventing the risk from occurring, how those controls are verified, what evidence exists, and where gaps remain."

This question is not answerable on V1's data (flat rows, free-text cross-references, four incompatible schemas — see `PLATFORM_ARCHITECTURE_V2.md` §1.4). It is a graph-traversal query by nature, not a join query bounded to two or three tables, and it gets harder, not easier, as the register grows. The EKG is the component that makes it answerable, and answerable *with provenance* (§5, and see [05-knowledge-provenance-model.md](05-knowledge-provenance-model.md)).

## 2. Scope

In scope: the safety domain model (assets → hazards → risks → controls → critical controls → performance standards → verification → evidence → safety case claims → regulatory requirements), the ontology that constrains it (§3), incident/investigation/corrective-action/audit data as it relates to that model, and the query/inference layer over all of it.

Out of scope: general business data (rostering, ticketing, finance) — the EKG is a safety knowledge graph, not an enterprise data warehouse. Document *storage* is out of scope (Blob Storage, per architecture §2/§8) — the EKG stores facts extracted from documents and a provenance link back to them, not the documents themselves.

## 3. Two-Layer Model

The EKG is explicitly two layers, both living in Neo4j, both explorable through the same Cytoscape.js viewer (architecture §2), and this separation is a design decision, not an implementation detail — it is what stops the graph from re-accumulating the vocabulary fragmentation that broke V1.

| Layer | Contents | Changes how often | Owner |
|---|---|---|---|
| **Ontology graph** | `Concept`, `ConceptAlias`, `ConceptRelation`, `OntologyScheme`, `RelationshipTypeRegistry`, `ExtractionRule` (full detail: `PLATFORM_ARCHITECTURE_V2.md` §3) | Slow — governed, versioned, curator-approved | VRTP HSE ontology curator |
| **Instance graph** | Real records: `Asset`, `Hazard`, `Risk`, `Control`, `CriticalControl`, `Incident`, `Evidence`, `SafetyCaseClaim`, etc. (full detail: [02-neo4j-node-relationship-model.md](02-neo4j-node-relationship-model.md)) | Fast — created/updated continuously by users and the AI extraction pipeline | System users, AI Extraction Service |

Every instance-graph node's classification property (`Hazard.category`, `Control.hierarchy`, etc.) is a reference to an ontology-graph `Concept`, not a free string. This is enforced at the Postgres level (foreign key — [03-postgresql-schema.sql](03-postgresql-schema.sql)) and mirrored into Neo4j as a `CLASSIFIED_AS` edge from the instance node to the ontology `Concept` node. A query can therefore traverse from an instance straight into its taxonomy position (e.g. "this hazard is a *Crushing* hazard, which is a *Moving Machinery* hazard, which is a *Mechanical Energy* hazard") without any string matching.

## 4. System of Record vs. Graph — Sync Model

**Postgres is the system of record for structured entity data.** Neo4j is a synchronized traversal-optimized projection of that same data, not a second independent source of truth (architecture §2). Practically:

- Writes go to Postgres first (via the FastAPI REST layer — [10-openapi.yaml](10-openapi.yaml)), inside a transaction.
- The **Graph Sync Service** (architecture §2 `GraphSvc`) propagates the change to Neo4j as an idempotent upsert, keyed by the Postgres primary key (stored on the Neo4j node as `pg_id`).
- Sync is near-real-time (event-driven off the Postgres write, target < 5s lag), not batch/nightly — the whole point of the graph is that it reflects current state for gap analysis and dashboards.
- Neo4j is the **only** place hierarchical/relationship queries run (e.g. "all controls, transitively, protecting Asset X"). Postgres is never asked to do recursive CTEs for this — that duplication of query logic across two engines is an anti-pattern this spec explicitly avoids.
- If Neo4j is unavailable, writes to Postgres still succeed (the system of record stays authoritative); graph-dependent views degrade to "graph temporarily unavailable," not data loss.

## 5. Query Pattern Catalogue (representative, not exhaustive)

These are the traversal shapes the graph must support well — they drive the relationship model in §2 of the Neo4j document and the indexing strategy there.

| # | Pattern (natural language) | Graph shape |
|---|---|---|
| Q1 | Every critical risk, its controls, verification status, evidence, and gaps (the platform's core objective query) | `Risk{critical}` → `Control` → `CriticalControl` → `VerificationActivity` → `Evidence`, with `OPTIONAL MATCH` surfacing missing links as gaps |
| Q2 | What controls protect against [hazard type] across all assets? | `Concept{name:'Uncontrolled movement'}` ← `CLASSIFIED_AS` ← `Hazard` (any asset) → `GIVES_RISE_TO` → `Risk` → `MITIGATED_BY` → `Control` |
| Q3 | Which critical controls have no verification activity logged in the last N days? | `CriticalControl` where no `VerificationActivity` with `performed_at > now() - N days` |
| Q4 | Which hazards map to the same ontology concept but were recorded with different free text (duplicate candidates)? | `Hazard` nodes sharing a `CLASSIFIED_AS → Concept` edge, grouped, text-similarity below equivalence threshold |
| Q5 | Full traceability for a Safety Case claim | `SafetyCaseClaim` → back through `SUPPORTS`⁻¹ → `Evidence` → `VerificationActivity` → `PerformanceStandard` → `CriticalControl` → `Control` → `Risk` → `Hazard` → `Asset`, plus → `TRACES_TO` → `Requirement` |
| Q6 | Everything an Incident revealed, and what actions resulted | `Incident` → `REVEALS` → `Hazard`; `Incident` → `TRIGGERS` → `Action` → `REMEDIATES` → `Control` |
| Q7 | Regulatory coverage: which requirements have no linked control/evidence anywhere | `Requirement` with no inbound `TRACES_TO` |

## 6. Governance & Versioning

- **Ontology layer:** draft → reviewed → approved → published workflow, `effective_from`/`effective_to` on every `Concept` (`PLATFORM_ARCHITECTURE_V2.md` §3.3). A published concept is never hard-deleted; it is deprecated and superseded, so historical instance nodes referencing it remain valid and queryable.
- **Instance layer:** every write carries a provenance record (who/what/when/source — [05-knowledge-provenance-model.md](05-knowledge-provenance-model.md)). No instance node is ever silently overwritten; corrections are new versions with the prior version retained for audit (this is a regulatory requirement in a Safety Case context, not a nicety).
- **Schema evolution:** changes to node labels/relationship types go through the same approval gate as this document set — a `RelationshipTypeRegistry` entry must exist and be approved *before* a new edge type is used anywhere in code ([06-relationship-rules-catalogue.md](06-relationship-rules-catalogue.md)).

### 6a. Ontology Schemes Added — Design Baseline v1.1 (approved 2026-08-04)

Three new `OntologyScheme`s registered per [implementation-blueprint/14-architecture-change-requests.md](../implementation-blueprint/14-architecture-change-requests.md) (ACR-002, ACR-003), following the same governance workflow as §6 above — seeded as `draft`, to be reviewed/approved/published by the ontology curator before use, not pre-populated as fact:

| Scheme | Populates | Seed source |
|---|---|---|
| Emergency Service Organisation | `safety.emergency_service_consultations.organisation_concept_id` | QFES, QPS, QAS, other — Guide §12.2, §12.3 |
| Competency Category | `safety.competencies.competency_type_concept_id`, `safety.role_competency_requirements.competency_type_concept_id` | training, qualification, licence, oem_certification, authorisation, information_briefing — Guide §10.8 |
| Emergency Exercise Classification | Reference only — `emergency_exercises.exercise_type` is a Postgres CHECK enum, not ontology-governed (fixed, small, regulator-shaped set, same treatment as `management_of_change.change_type`) | drill, scenario_test, desktop_exercise, evacuation_exercise, corporate_response_exercise — Guide §12.1, §12.3 |

`safety.roles.role_category` is likewise a Postgres CHECK enum, not an ontology scheme — role categories are a small, stable, Guide-named set (§10.8), the same treatment already given to `management_of_change.change_category` and `demonstrations.demonstration_type` elsewhere in this schema.

## 7. Consumers

| Consumer | Uses |
|---|---|
| Executive Dashboard | Aggregated counts/status via Q1, Q3 shapes |
| Hazard Knowledge Library / Major Hazard Register UI | Direct entity CRUD (Postgres) + taxonomy browse (ontology graph) |
| Knowledge Graph Explorer (Cytoscape) | Both layers, ad-hoc traversal |
| AI Gap Analysis Service | Q3, Q4, Q7 shapes, scheduled + on-demand |
| Safety Case Workspace | Q5 |
| AI Extraction Service | Reads ontology layer (concept/alias list) to constrain extraction; writes instance layer via Postgres |

## 8. Non-Goals

This is not a general-purpose triple store or a public ontology (no OWL reasoner, no external ontology import like SNOMED/ISO 15926 at this stage — evaluate only if a real need surfaces). It is not a replacement for Postgres transactional integrity — Neo4j never receives a write the system of record hasn't already accepted.
