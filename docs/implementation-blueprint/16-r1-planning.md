# 16 — R1 Planning Artefact

**Status: APPROVED (2026-08-07).** Baseline: Design Baseline v1.1 (frozen), tag `v1.1.0-R0`. R1 formally commences.

**Scope discipline:** this document does not re-decide R1's scope. [04-implementation-roadmap.md](04-implementation-roadmap.md) (IB4, already approved) already defines R1 as the Risk Register cutover. This artefact operationalizes that row into a contract, and records how the one real gap it surfaced (§Gap) was resolved.

| Field | Value |
|---|---|
| Baseline tag | `v1.1.0-R0` (commit `e63b315`) |
| Release | R1 — Risk Register cutover ([04-implementation-roadmap.md](04-implementation-roadmap.md) row R1) |
| Objective | Deliver a production-ready Risk Register module by migrating V1 functionality into the new platform without regression, while establishing the foundational backend services (PostgreSQL, Neo4j, ontology service, authentication, API layer) required for subsequent module migrations. |
| Dependency | R0 — gap resolved, see §Gap |

## In scope

Per IB4 R1 + [03-module-dependency-map.md](03-module-dependency-map.md):

- **Hazard Library** — `safety.hazards`, Hazard taxonomy classification (ontology FK, not free text)
- **Risk Register** — `safety.risks`, `safety.consequences`; R1 rating derivation ([07-inference-rules-catalogue.md](../knowledge-graph/07-inference-rules-catalogue.md) R1: `score = likelihood × consequence`, banded per VRTP Risk Matrix GOHS2.1.2)
- API endpoints per [10-openapi.yaml](../knowledge-graph/10-openapi.yaml) `Hazards` and `Risks` tags (currently empty routers in `apps/api/app/routers/hazards.py` / `risks.py` — implement against the existing contract, do not redesign it)
- React module screens for `apps/web/src/modules/hazards/` and `risk-register/` (currently placeholder-only)
- V1 `risk-register.html` data export + migration into the new schema (architecture §8 decision 4) — reconciling V1's 4 divergent hazard/risk schemas into 1 canonical model (architecture §1.4 finding 1)
- Nav repointing `risk-register.html` → the new module, **only once parity is confirmed**, not before

## Out of scope (explicitly deferred, not silently assumed)

- Incidents, Investigations (R2)
- Critical Controls, Performance Standards, Verification, TARPs, MOC (R3)
- Actions, Audits (R4)
- Dashboard (R5)
- AI Extraction, Knowledge Graph Sync (R6)
- Safety Assessment, Demonstration Engine, Safety Case (R7)
- Any UI beyond feature parity with V1 `risk-register.html` — no new functionality not already in the Design Baseline
- Any change to ontology, schema, Neo4j model, or OpenAPI contract — if R1 implementation surfaces a genuine gap, that's an ACR, not a direct edit (per [ACR-002](../../.acr/ACR-002-emergency-planning-domain.md)/[ACR-003](../../.acr/ACR-003-competency-management-domain.md) precedent)

## Gap: R0 as executed is narrower than R0 as originally scoped — RESOLVED

**Decision (2026-08-07): Option 2.** Foundational backend services are R1's own first milestone, sequenced explicitly before Hazard Library/Risk Register business logic — not a separate R0.1 pass. This is now stated directly in R1's Objective above, not left implicit.

IB4's own R0 row specified deliverables that the R0 actually executed ([15-r0-exit-review.md](15-r0-exit-review.md)) did **not** include, because this session's R0 work order explicitly narrowed scope to "engineering foundation only" (no endpoints, no database population, no infrastructure provisioning):

| IB4's original R0 deliverable | Delivered by executed R0? |
|---|---|
| Repo scaffold, CI/CD | ✅ Yes |
| Azure resources (Container Apps, Postgres Flexible Server, Blob Storage, Key Vault) | ❌ No — `infrastructure/bicep` wires only the Key Vault module shape; nothing is provisioned |
| Entra ID app registrations | ❌ No |
| **Ontology Service + seed concepts** (control hierarchy, consequence domains, energy sources) | ❌ No — `ontology/seed-concepts/` is empty |
| **Assets module (CRUD functional in Dev)** | ❌ No — `assets.py` router is empty, no ORM model populated |

IB4 §Sequencing Notes is explicit: *"R0 is not optional scaffolding — Ontology must exist and be seeded before R1, because every classification field in Risk Register is an ontology FK. Attempting R1 without R0 complete reproduces V1's original defect inside the new platform."*

Risk Register's `hazards.category_concept_id` and `risks`' classification fields are ontology FKs per [03-postgresql-schema.sql](../knowledge-graph/03-postgresql-schema.sql). **R1 cannot implement Hazard Library/Risk Register against a real database until the Ontology Service is seeded and Postgres is actually provisioned and reachable.** This is not new scope creep into R1 — it's R0 work IB4 already called for for that was deferred out of the executed R0.

**R1 Milestone 0 (before Hazard Library/Risk Register work begins):**
1. Ontology Service reachable, seed concepts loaded (control hierarchy, consequence domains, energy sources — ported from V1 per architecture §6)
2. Postgres provisioned and reachable (Dev environment minimum)
3. Assets module CRUD functional (device boundary schema, unpopulated) — Hazard Library FKs to it
4. Entra ID Dev app registration — `apps/api/app/dependencies/auth.py` currently unimplemented

Only once these are in place does Milestone 1 (Hazard Library + Risk Register) start.

## Acceptance criteria (per IB4 R1 exit criteria)

- Feature parity with V1 `risk-register.html` confirmed by VRTP HSE
- Live `localStorage` data exported and migrated (architecture §8 decision 4) — verified row-count/spot-check reconciliation, not just "it ran"
- `hazards`/`risks` API endpoints pass contract tests against [10-openapi.yaml](../knowledge-graph/10-openapi.yaml) (schemathesis or equivalent, per [08-testing-strategy.md](08-testing-strategy.md) §3)
- R1 rating derivation ([07-inference-rules-catalogue.md](../knowledge-graph/07-inference-rules-catalogue.md)) matches VRTP Risk Matrix GOHS2.1.2 exactly — verified against `sms-shared.js`'s current `SMS.riskScore`/`riskBand` implementation (Extreme/High/Medium/Low banding), not reinvented
- CI green: build, lint, typecheck, unit + contract tests

## Risks

- **Largest data-migration risk in the roadmap** (IB4's own framing): V1's 4 divergent hazard/risk schemas (`sms-shared.js`'s Risk entity, `bowtie-ccm-generator.html`'s 55-column CSV schema, `OHS_Command_Centre`'s register, the FARSI calculator's fields) must reconcile into 1 canonical model without silent data loss.
- Ontology seeding stalls waiting for a "complete" taxonomy — mitigated by the existing governance model (publish v1, version, iterate — [EKG spec](../knowledge-graph/01-enterprise-knowledge-graph-specification.md) §6), not by blocking R1 on taxonomy completeness.
- The Gap above, if not resolved deliberately, risks R1 work starting against a database that doesn't exist yet.

## Dependencies

- Milestone 0 deliverables above (now in-scope for R1 itself, not an external blocker)
- Five open frontend ADRs ([.adr/README.md](../../.adr/README.md)) — routing/server-state/client-state/forms should be settled before module screens are built, not decided ad hoc per module

## Baseline immutability

`v1.1.0-R0` is immutable. Any defect discovered in it is fixed on a branch and merged through the normal PR process, not by moving or re-pointing the tag. See [.adr/README.md](../../.adr/README.md) for this recorded as a standing convention.
