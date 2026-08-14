# 12 — Deliverables Index
**Status: Design Baseline v1.1 (Approved 2026-08-04) — Phase 1, Phase 2.1, and Phase 2.2 all Approved. R0 — Repository Initialisation COMPLETE (merged 2026-08-05, PR #11, tag `v1.1.0-R0`) — see [15-r0-exit-review.md](15-r0-exit-review.md). See §ACR table below and [14-architecture-change-requests.md](14-architecture-change-requests.md) §6–§10.**
**Scope:** every document produced across all phases to date — architecture, Design Baseline v1.1, and this Implementation Blueprint.

---

## Phase 1 — Architecture

| Doc # | Title | Purpose | Status | Dependencies |
|---|---|---|---|---|
| A0 | [PLATFORM_ARCHITECTURE_V2.md](../PLATFORM_ARCHITECTURE_V2.md) | V1 inventory, proposed architecture, entity model, migration plan, reuse map, gaps, decisions | Approved — Design Baseline v1.0 | — |

## Design Baseline v1.1 — Knowledge Graph Foundation Artefacts

| Doc # | Title | Purpose | Status | Dependencies |
|---|---|---|---|---|
| 1 | [Enterprise Knowledge Graph Specification](../knowledge-graph/01-enterprise-knowledge-graph-specification.md) | Two-layer graph model, sync model, query patterns, governance, ontology scheme catalogue (§6a: v1.1 additions) | Approved — Design Baseline v1.1 | A0 |
| 2 | [Neo4j Node and Relationship Model](../knowledge-graph/02-neo4j-node-relationship-model.md) | Node labels, relationship types, constraints, worked example, §3.6 v1.1 amendment (Emergency Planning + Competency) | Approved — Design Baseline v1.1 | 1 |
| 3 | [PostgreSQL Schema](../knowledge-graph/03-postgresql-schema.sql) | Full DDL — system of record, incl. v1.1 amendment section (emergency planning + competency tables) | Approved — Design Baseline v1.1 | 1 |
| 4 | [AI Extraction Specification](../knowledge-graph/04-ai-extraction-specification.md) | Extraction pipeline, schema, confidence routing, security | Approved — Design Baseline v1.0 (unamended) | 1, 3 |
| 5 | [Knowledge Provenance Model](../knowledge-graph/05-knowledge-provenance-model.md) | Source tracing, confidence propagation, immutable history | Approved — Design Baseline v1.0 (unamended) | 3 |
| 6 | [Relationship Rules Catalogue](../knowledge-graph/06-relationship-rules-catalogue.md) | Business rules per edge type, cross-chain integrity, §5b v1.1 amendment | Approved — Design Baseline v1.1 | 2 |
| 7 | [Inference Rules Catalogue](../knowledge-graph/07-inference-rules-catalogue.md) | R1–R18 derived-fact and gap-detection rules, R19–R22 v1.1 amendment | Approved — Design Baseline v1.1 | 3, 6 |
| 8 | [Critical Control Assurance Model](../knowledge-graph/08-critical-control-assurance-model.md) | 3-gate test, EIA test, FARSI scoring, assurance lines, TARPs | Approved — Design Baseline v1.0 (unamended) | 3, 7 |
| 9 | [Regulatory Knowledge Model](../knowledge-graph/09-regulatory-knowledge-model.md) | Regulatory ontology, confirmed WHS Reg/Schedule 18C citations, §5a Schedule 18B → EmergencyPlan resolution | Approved — Design Baseline v1.1 (2 of original 3 `TO_BE_CONFIRMED` Schedule 18C sub-items remain open) | 3 |
| 10 | [OpenAPI 3.1 Specification](../knowledge-graph/10-openapi.yaml) | REST contract — v0.2.0-draft, `Competency` tag + emergency-plan paths added | Approved — Design Baseline v1.1 | 2, 3 |
| 11 | [Safety Case Demonstration Model](../knowledge-graph/11-safety-case-demonstration-model.md) | SMS≠Safety Case layering, ADH→ADI pathway, Demonstration Engine, MOC | Approved — Design Baseline v1.0 (unamended; §0 cross-referenced to v1.1) | 1–3, 8, 9 |

## Phase 2.1 — Implementation Blueprint (this set)

| Doc # | Title | Purpose | Status | Dependencies |
|---|---|---|---|---|
| IB1 | [Repository Structure](01-repository-structure.md) | Monorepo layout, folder purposes | Draft | A0, 1–11 |
| IB2 | [Development Standards](02-development-standards.md) | Branching, semver, commits, PR/review, ADR, ACR, DoR/DoD | Draft | IB1 |
| IB3 | [Module Dependency Map](03-module-dependency-map.md) | Prerequisite/dependent modules, interfaces, API boundaries | Draft | 2, 6, 1–11 |
| IB4 | [Implementation Roadmap](04-implementation-roadmap.md) | Releases R0–R7, aligned to the decided strangler-fig order | Draft | IB3, A0 §8 |
| IB5 | [Database Migration Strategy](05-database-migration-strategy.md) | Postgres/Neo4j migrations, ontology versioning, seed data, rollback | Draft | 3, 2 |
| IB6 | [Environment Strategy](06-environment-strategy.md) | Dev/Test/UAT/Prod infra, auth, DB, AI, storage, monitoring | Draft | A0 §8 |
| IB7 | [CI/CD Architecture](07-cicd-architecture.md) | GitHub Actions pipelines, validation gates | Draft | IB1, IB5 |
| IB8 | [Testing Strategy](08-testing-strategy.md) | Unit/integration/API/graph/ontology/AI/perf/security/UAT | Draft | 6, 7, 4 |
| IB9 | [Configuration Management](09-configuration-management.md) | Env vars, Key Vault, config hierarchy, feature flags, licensing | Draft | IB6 |
| IB10 | [Operational Readiness Checklist](10-operational-readiness-checklist.md) | Deployment/backup/restore/monitoring/audit/security/DR/BC | Draft | IB5, IB6, 5, 8 |
| IB11 | [Implementation Risk Register](11-implementation-risk-register.md) | Technical/project/security/data/AI/regulatory risks | Draft | All of the above |
| IB12 | [Deliverables Index](12-deliverables-index.md) | This document | Draft | All of the above |

## Phase 2.2 — Application Foundation

| Doc # | Title | Purpose | Status | Dependencies |
|---|---|---|---|---|
| IB13 | [Application Foundation Scaffold](13-application-foundation-scaffold.md) | React/FastAPI internal scaffold, package ownership, GitHub templates, 18 module skeletons (Training→Competency renamed), config strategy detail | **Approved (2026-08-04)** | IB1–IB12, A0, 1–11 |
| IB14 | [Architecture Change Request Review Pack](14-architecture-change-requests.md) | Consolidates ACR-001/002/003 — impact assessment, verification findings, Board decision, regeneration record, freeze, release gate | **Closed (2026-08-04)** — Board decision recorded | ACR-001, ACR-002, ACR-003, IB13 |
| IB15 | [R0 Exit Review](15-r0-exit-review.md) | Checklist verification + full release record — build/lint/typecheck/test/validation results, no-implementation checks, PR #11 merge/tag details, CI incident resolution | **Complete (2026-08-05)** — merged as `e63b315`, tagged `v1.1.0-R0` | IB13, IB14 |
| IB16 | [R1 Planning Artefact](16-r1-planning.md) | R1 contract per IB4's already-approved Risk Register cutover scope — in/out of scope, acceptance criteria, risks, dependencies. Surfaces a real gap: IB4's original R0 (Ontology Service seeded, Assets CRUD, Azure provisioning) was not delivered by the narrower R0 actually executed | Approved — R1 Milestone 0 and Milestone 1 both complete and merged | IB4, IB15 |
| IB17 | [R1 Milestone 2A — CCM Discovery & Reconciliation](17-r1-milestone-2-ccm-discovery-reconciliation.md) | Research-only pass reconciling V1 (`bowtie-ccm-generator.html`, FARSI calculator), the frozen schema/OpenAPI, and `06`/`07`/`08` against a proposed Critical Control = Control+Support+Verification model. Confirms Option A (classification on sibling rows) over Option B (parent/child); surfaces 6 decision points, none requiring an ACR as recommended | **Complete** — no code changed; 5 decision points (D2–D6) await ADR before CCM implementation begins | IB16, 03/06/07/08/10 (knowledge-graph) |
| IB18 | [R1 Milestone 3A — Incident Discovery & Reconciliation](18-r1-milestone-3a-incident-discovery-reconciliation.md) | Research-only pass reconciling V1 (`incident-report.html`, `corrective-actions.html`), the frozen schema/OpenAPI/Neo4j model, and `06`/`07`/`09` against the Incident Management domain. Confirms Incident/Investigation/Action is a sibling structure (`REVEALS`/`INVESTIGATED_AS`/`TRIGGERS`), not a linear chain. Surfaces 7 decision points; D4 (`safety.investigations`, `incident_hazards`, incident-scoped `Evidence` have zero OpenAPI surface) corrected at 3A Review to route via **ACR**, not ADR — additive/low-risk is not a carve-out from Design Baseline artefact control | **Complete, unmerged** (PR #18) — findings accepted at 3A Review 2026-08-08; no implementation authorised; merge ≠ approval of D1–D7 | IB17, 02/03/06/07/09/10 (knowledge-graph) |
| IB19 | [R1 Milestone 3B — Incident Decision Register (D1–D7)](19-r1-milestone-3b-incident-decision-register.md) | Governance-methodology pass resolving the ACR/ADR/No-Change/Defer routing for each of IB18's 7 decision points, with evidence, options, impact, and a clearly-marked recommendation per decision (none converted to a decision). Confirms D4 requires an ACR; identifies cross-decision dependencies (D7→D6, D2→D4) and a resolution order | **Complete** — all 7 decisions have a recorded disposition: D1 (evidence-resolved), D2 ([ADR-003](../../.adr/ADR-003-incident-investigation-action-sibling-structure.md)), D3 ([ADR-004](../../.adr/ADR-004-incident-ontology-scheme-deferral.md)), D4 ([ACR-004](../../.acr/ACR-004-incident-openapi-extension.md), Approved + contract-implemented), D5 ([ADR-005](../../.adr/ADR-005-incident-orphan-v1-fields-disposition.md)), D6 ([ADR-006](../../.adr/ADR-006-incident-notification-rule-formal-defer.md), resolved — scope decided, ACR required, not yet raised; "OSR"/`osr_notified` residual open), D7 (accepted) | IB18, 02/03/06/07/09/10 (knowledge-graph), 14 (ACR precedent) |
| IB20 | [R1 Milestone 3C — D6 Notification-Rule Scope: Discovery & Evidence Matrix](20-r1-milestone-3c-d6-notification-evidence-matrix.md) | Discovery-only pass building a cited evidence matrix (Source/Requirement/Authority/Mandatory-Discretionary/Trigger/Recipient/Timeframe/V1 impl/Platform representation/Gap) for D6, reading WHS Act 2011 Part 3 (ss.35-39) and WHS Regulation 2011 Chapter 9A (§§608B/608J/608K/608L) in full. Finds R10 currently touches only `osr_notified`, never `whsq_notified` — the general, penalty-backed WHS Act s.38 duty has zero rule representation anywhere. Surfaces that "OSR" is never defined in the WHS Act, WHS Regulation, or any controlled doc — flagged as the material open question for Compliance/Legal, not resolved | **Complete** — no ADR/ACR raised at the time, no recommendation offered, no code/schema/API/ontology/Neo4j change; superseded procedurally by [ADR-006](../../.adr/ADR-006-incident-notification-rule-formal-defer.md)'s formal defer | IB19, WHS Act 2011.md, WHS Reg 2011.md, 04/07/09 (knowledge-graph) |

## Architecture Change Requests — Closed

| ACR # | Title | Raised | Decision | Confidence | Outcome |
|---|---|---|---|---|---|
| [ACR-001](../../.acr/ACR-001-training-domain.md) | Training Domain | 2026-08-04 | **Rejected** (2026-08-04) | Very High | Superseded by ACR-003 — no standalone Training entity |
| [ACR-002](../../.acr/ACR-002-emergency-planning-domain.md) | Emergency Planning Domain | 2026-08-04 | **Approved** (2026-08-04) | Very High | `emergency_plans` + `emergency_exercises` + `emergency_plan_credible_events` + `emergency_service_consultations` added to Design Baseline v1.1; risk D4 closed |
| [ACR-003](../../.acr/ACR-003-competency-management-domain.md) | Competency Management Domain | 2026-08-04 | **Approved** (2026-08-04) | Very High | `competencies` + `roles` + `role_competency_requirements` + `competency_evidence` added to Design Baseline v1.1; Training folded in as an evidence type |

Board decision, rationale, and the completed artefact-regeneration record are in [IB14](14-architecture-change-requests.md) §6–§8. Design Baseline is now **v1.1**, re-frozen 2026-08-04 ([IB14](14-architecture-change-requests.md) §9). **R0 — Repository Initialisation is AUTHORISED** ([IB14](14-architecture-change-requests.md) §10).

## Architecture Change Requests — Approved and Contract-Implemented

| ACR # | Title | Raised | Approved | Implemented | Basis | Touched |
|---|---|---|---|---|---|---|
| [ACR-004](../../.acr/ACR-004-incident-openapi-extension.md) | Incident Domain — OpenAPI Extension (Investigation, `incident_hazards`/`REVEALS`, incident-scoped Evidence) | 2026-08-09 | 2026-08-11 | **2026-08-11** | [IB19](19-r1-milestone-3b-incident-decision-register.md) D4; [ADR-003](../../.adr/ADR-003-incident-investigation-action-sibling-structure.md) | `10-openapi.yaml` only (now v0.3.0-draft) — additive, validated 0 dangling `$ref`s. Contract-only; no application code |

Distinct from the Closed table above: ACR-002/003 were approved **and** their artefact regeneration was completed in the same governance pass (IB14 §6–§8) — same treatment ACR-004 has now received for its own scope. Design Baseline itself stays **v1.1** — ACR-004 extended the OpenAPI contract additively under that baseline, it did not re-freeze it.

## Architecture Change Requests — Required, Not Yet Raised

| Origin | Reason ACR is required | Status |
|---|---|---|
| D6 ([IB19](19-r1-milestone-3b-incident-decision-register.md), [ADR-006](../../.adr/ADR-006-incident-notification-rule-formal-defer.md) §10) | Extending R10's definition in `07-inference-rules-catalogue.md` (a Design Baseline v1.1 artefact) to cover general WHS Act incident categories, and likely adding a new trigger-flag column mirroring `is_serious_risk`/`flag_608b` for the general notifiable-incident test | **Not raised.** Scope decided (ADR-006 §9); ACR drafting requires a separate, explicit GO. |

## Open Items Requiring Resolution Before Full Sign-Off

Carried forward, not duplicated — see the authoritative source for each. These do not block R0 (none are prerequisites for repository scaffolding) but remain open for R1–R7:

- **Two unconfirmed Schedule 18C sub-item numbers** (contractor management §10.6, incident management §10.7 — narrowed from three: training/asset integrity, §10.8–10.9, are now confirmed as of 2026-08-04), plus ISO 45001/AS 3533/AS 4024/ISO 17842 and Schedule 19's verbatim device-definition text — [knowledge-graph/09 §2, §5](../knowledge-graph/09-regulatory-knowledge-model.md); tracked as risk REG3 in [IB11](11-implementation-risk-register.md). **Schedule 18B is confirmed and now structurally modelled** (`safety.emergency_plans` et al., [knowledge-graph/09 §5a](../knowledge-graph/09-regulatory-knowledge-model.md)) — risk D4 **closed**. **There is no Schedule 19C** — Schedule 19 is the Dictionary schedule, not a device-specific one; corrected throughout.
- Companion *Guide for Developing Major Amusement Parks Safety Case Outline* and the *ICMM Critical Control Management Practical Guide* — provided, not yet read; tracked as risk REG4 in [IB11](11-implementation-risk-register.md).
- Investigation methodology, VRTP audit cycle frequency — see [knowledge-graph/README.md](../knowledge-graph/README.md) open items. AuthN/AuthZ provider is confirmed (Microsoft Entra ID).
- Neo4j/Qdrant managed-vs-self-hosted decision — deferred to R0 per [A0 §8](../PLATFORM_ARCHITECTURE_V2.md), tracked in [06-environment-strategy.md](06-environment-strategy.md).
- Frontend routing/state/form/build-tool choices are working assumptions pending five ADRs at R0 start ([IB13](13-application-foundation-scaffold.md) §2).
- Dashboard aggregation endpoints, feature-flag storage mechanism, stored procedure policy, Administration/Competency `roles` naming collision — all tracked in [IB13 §13](13-application-foundation-scaffold.md).

**Design Baseline v1.1 is Approved and frozen (2026-08-04). Phase 2.1, Phase 2.2, and the ACR Review Pack are all Approved/Closed. R0 — Repository Initialisation is authorised.**
