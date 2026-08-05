# 13 — Application Foundation Scaffold (Phase 2.2)
**Status: APPROVED — Application Foundation baseline for repository structure and application architecture, approved 2026-08-04. Baseline: Design Baseline v1.0 (Approved) + Phase 2.1 Implementation Blueprint (IB1–IB12, Approved).**

**Gate before R0 — CLOSED, 2026-08-04:** three ACRs were raised against gaps this scaffold surfaced. Architecture Review Board decision ([implementation-blueprint/14-architecture-change-requests.md](14-architecture-change-requests.md) §6): **ACR-001 rejected** (superseded by ACR-003), **ACR-002 approved** (Emergency Planning), **ACR-003 approved** (Competency Management). Design Baseline is now **v1.1**. Affected artefacts (ontology, PostgreSQL schema, Neo4j model, relationship/inference catalogues, OpenAPI) have been regenerated in a controlled pass — see [knowledge-graph/03-postgresql-schema.sql](../knowledge-graph/03-postgresql-schema.sql), [02-neo4j-node-relationship-model.md §3.6](../knowledge-graph/02-neo4j-node-relationship-model.md), [06 §5b](../knowledge-graph/06-relationship-rules-catalogue.md), [07 R19–R22](../knowledge-graph/07-inference-rules-catalogue.md), [10-openapi.yaml v0.2.0-draft](../knowledge-graph/10-openapi.yaml). This scaffold document's module skeleton (§12) is updated below accordingly; the `training/` folder named in §2's tree is superseded by `competency/` (see §12).

**Traceability:** this document elaborates [01-repository-structure.md](01-repository-structure.md) (IB1) into an implementable scaffold. It adds detail — internal folder layout of `apps/web` and `apps/api`, package ownership rules, GitHub templates, module skeletons — **it does not change any decision already made in IB1–IB12 or the 11 knowledge-graph documents**. Where this document's detail level exceeds what IB1–IB12 specified, that is additive elaboration, not a new decision; where a genuine gap exists against the frozen baseline, it is marked `TO_BE_CONFIRMED` or flagged as an ACR candidate rather than resolved by invention.

**Scope boundary:** this is repository scaffolding only — directory structure, empty module definitions, configuration strategy, and process templates. **No business logic, no endpoint implementation, no component implementation, no AI implementation, no Safety Case implementation, no database population.** Section 4 (What Does Not Exist Yet) in [01-repository-structure.md](01-repository-structure.md) still applies: nothing in this document instructs anyone to write `apps/web/src` or `apps/api/app` source files. This is R0 preparatory documentation ([04-implementation-roadmap.md](04-implementation-roadmap.md) — "Repo scaffold" is R0's first deliverable).

---

## 1. Repository Structure

The complete tree below is [01-repository-structure.md](01-repository-structure.md) §2 reproduced in full, since every subsequent section of this document depends on it and it must not be re-derived or drift from the original.

```
/
├── apps/
│   ├── web/                        # React + TypeScript frontend — detailed in §2
│   └── api/                        # FastAPI backend — detailed in §3
├── packages/                       # Shared code — detailed in §4
│   ├── shared-types/
│   ├── api-client/
│   ├── ontology-client/
│   └── ui-components/
├── ontology/                       # Ontology content (data, not code)
│   ├── schemes/
│   ├── seed-concepts/
│   └── validation/
├── database/                       # Detailed in §5
│   ├── postgres/
│   │   ├── migrations/
│   │   └── seeds/
│   └── neo4j/
│       ├── constraints/
│       └── migrations/
├── infrastructure/                 # Detailed in §6
│   ├── bicep/
│   └── environments/
├── docs/                           # Detailed in §7
│   ├── PLATFORM_ARCHITECTURE_V2.md
│   ├── knowledge-graph/
│   └── implementation-blueprint/
├── tests/                          # Detailed in §10
│   ├── unit/
│   ├── integration/
│   ├── contract/
│   ├── e2e/
│   ├── graph/
│   ├── ontology/
│   ├── ai-extraction/
│   ├── performance/
│   ├── security/
│   ├── uat/
│   └── fixtures/
├── scripts/
├── .adr/
├── .acr/
├── .github/
│   ├── workflows/                  # Detailed in §11
│   └── ISSUE_TEMPLATE/             # Detailed in §9
├── docker-compose.yml
├── .env.example
└── README.md
```

**Delta from IB1 §2, and why:** `tests/` gains four folders — `contract/`, `performance/`, `security/`, `uat/` — that IB1's tree did not enumerate but [08-testing-strategy.md](08-testing-strategy.md) already specifies as distinct testing dimensions (§3 API contract, §7 performance, §8 security, §9 UAT). IB1 predates this level of test-folder granularity; giving each IB8 dimension its own folder is elaboration consistent with IB8, not a change to it. Everything else in the tree is unchanged from IB1 §2.

| Folder | Purpose | Detail |
|---|---|---|
| `apps/`, `packages/`, `ontology/`, `database/`, `infrastructure/`, `docs/`, `tests/`, `scripts/`, `.adr/`, `.acr/`, `.github/` | As defined in [01-repository-structure.md](01-repository-structure.md) §3 | See linked doc for the authoritative per-folder purpose/owner table |

---

## 2. React Application Scaffold (`apps/web`)

**Confirmed stack** (architecture §2, §8; not decided here): React + TypeScript + Tailwind CSS + shadcn/ui component primitives; React Flow for bow-tie/MoC diagrams; Cytoscape for the Knowledge Graph Explorer (instance graph and ontology graph, one viewer for both per architecture line 144).

**Not yet decided in any frozen document — `TO_BE_CONFIRMED` at R0, structure below assumes the stated default and must not be treated as locked:**
- Routing library (assumed: React Router — standard pairing, not yet an ADR)
- Server-state library (assumed: TanStack Query, paired with `packages/api-client`)
- Client-state library (assumed: Zustand for UI-local state only — server state is not duplicated into client stores per [03-patterns.md](../../rules/ecc/web/patterns.md) style guidance already followed elsewhere in this codebase's tooling conventions)
- Form library (assumed: React Hook Form + Zod, since Zod schemas can be generated alongside `packages/shared-types`)
- Build tool (assumed: Vite)

These five items should become ADRs in `.adr/` at R0 start, not silently hardened into architecture by virtue of appearing in this scaffold.

```
apps/web/
├── src/
│   ├── app/                        # App shell: router config, providers, layout composition
│   │   ├── routes.tsx              # Route tree — TO_BE_CONFIRMED: React Router
│   │   ├── providers.tsx           # Query client, auth context, theme provider composition root
│   │   └── App.tsx
│   ├── layouts/                    # Shared page chrome
│   │   ├── AppShellLayout.tsx      # Authenticated shell: nav, header, module switcher
│   │   ├── AuthLayout.tsx          # Pre-auth (Entra ID redirect) layout
│   │   └── PrintableLayout.tsx     # Layout for exportable views (Safety Case, Demonstration documents)
│   ├── modules/                    # One folder per module — see §12 for the full module list
│   │   ├── dashboard/
│   │   ├── assets/
│   │   ├── hazards/
│   │   ├── risk-register/
│   │   ├── critical-controls/
│   │   ├── performance-standards/
│   │   ├── verification/
│   │   ├── incidents/
│   │   ├── investigations/
│   │   ├── audits/
│   │   ├── actions/
│   │   ├── competency/               # Renamed from training/ — Design Baseline v1.1, ACR-003, see §12
│   │   ├── management-of-change/
│   │   ├── safety-assessment/
│   │   ├── safety-demonstration/
│   │   ├── knowledge-graph/
│   │   ├── ai-review-queue/
│   │   └── administration/
│   │       └── <module>/
│   │           ├── routes.tsx      # Module's own route sub-tree, mounted into app/routes.tsx
│   │           ├── pages/          # Route-level components (no implementation yet)
│   │           ├── components/     # Module-local components not shared elsewhere
│   │           ├── hooks/          # Module-local hooks (e.g. useCriticalControlGates)
│   │           ├── api.ts          # Module's typed calls into packages/api-client
│   │           └── types.ts        # Module-local types not in packages/shared-types
│   ├── components/                 # Cross-module, app-specific components (not generic enough for packages/ui-components)
│   ├── hooks/                      # Cross-module hooks (useAuth, usePermissions, useOntologyConcept)
│   ├── lib/
│   │   ├── api-client.ts           # Thin wrapper instantiating packages/api-client with auth token injection
│   │   ├── auth.ts                 # Entra ID MSAL integration — token acquisition, silent refresh
│   │   └── query-client.ts         # TanStack Query client config — TO_BE_CONFIRMED pending ADR
│   ├── state/                      # Client-only state stores (UI state, not server state — see stack note above)
│   ├── config/
│   │   ├── env.ts                  # Typed wrapper over Vite env vars — validates presence at boot, never holds secrets (§8)
│   │   └── feature-flags.ts        # Reads flags per 09-configuration-management.md §4
│   ├── utils/                      # Pure functions — formatting, date handling, no side effects
│   └── main.tsx                    # Entry point
├── public/
├── index.html
├── vite.config.ts                  # TO_BE_CONFIRMED: build tool
├── tailwind.config.ts
├── tsconfig.json
└── package.json
```

**Authentication note:** Authentication (Entra ID) has no dedicated module folder under `modules/` — per [03-module-dependency-map.md](03-module-dependency-map.md) it is a prerequisite of all others, enforced via `lib/auth.ts`, route guards in `app/routes.tsx`, and `AuthLayout.tsx`, not a nav-visible screen beyond the sign-in redirect.

**State management boundary rule:** server data (anything returned by `apps/api`) lives in TanStack Query's cache via `packages/api-client`, never duplicated into a Zustand store — this is the same "one place per value" principle [09-configuration-management.md](09-configuration-management.md) §3 already applies to configuration, applied here to application state.

---

## 3. FastAPI Application Scaffold (`apps/api`)

Layering follows the Repository Pattern already named in this codebase's own pattern conventions (business logic depends on an abstract data-access interface, not the storage mechanism directly) applied per-module, consistent with [03-module-dependency-map.md](03-module-dependency-map.md)'s module boundaries and the OpenAPI tags in [10-openapi.yaml](../knowledge-graph/10-openapi.yaml).

```
apps/api/
├── app/
│   ├── main.py                     # FastAPI app factory, middleware registration, router mounting
│   ├── routers/                    # One file per OpenAPI tag — thin, delegates to services
│   │   ├── assets.py               # tag: Assets
│   │   ├── hazards.py              # tag: Hazards
│   │   ├── risks.py                # tag: Risks
│   │   ├── controls.py             # tag: Controls
│   │   ├── critical_controls.py    # tag: CriticalControls
│   │   ├── verification.py         # tag: Verification
│   │   ├── evidence.py             # tag: Evidence
│   │   ├── tarps.py                # tag: TARPs
│   │   ├── incidents.py            # tag: Incidents (incl. Investigations, per IB3)
│   │   ├── actions.py              # tag: Actions
│   │   ├── audits.py               # tag: Audits
│   │   ├── safety_case.py          # tag: SafetyCase (incl. MOC, Safety Assessment, Demonstration Engine, per IB3)
│   │   ├── requirements.py         # tag: Requirements
│   │   ├── documents.py            # tag: Documents
│   │   ├── extraction.py           # tag: Extraction
│   │   ├── ontology.py             # tag: Ontology
│   │   ├── knowledge_graph.py      # tag: KnowledgeGraph
│   │   ├── gap_analysis.py         # tag: GapAnalysis — read-only, no independent module per IB3 §3
│   │   └── people.py               # tag: People
│   ├── services/                   # One folder per module — business logic, orchestration, rule evaluation
│   │   └── <module>/
│   │       ├── service.py          # Orchestrates repositories + domain rules for one module
│   │       └── rules.py            # Module-specific rule implementations (e.g. 3-gate test, R1–R18 inference rules)
│   ├── repositories/                # One file per aggregate root — Postgres/SQLAlchemy access only, no business logic
│   │   └── <entity>_repository.py  # e.g. hazard_repository.py, critical_control_repository.py
│   ├── graph/                       # Neo4j-facing code — isolated from repositories/ since it's a projection, not the system of record (EKG spec §4)
│   │   ├── sync_service.py         # Graph Sync Service — Postgres → Neo4j propagation
│   │   └── queries/                # Cypher query modules, one per query-pattern (EKG spec §5, Q1–Q7)
│   ├── domain/                      # Domain models — framework-independent representations of entities, distinct from DTOs and ORM models
│   │   └── <module>/
│   ├── dto/                         # Request/response schemas — generated companions to 10-openapi.yaml, hand-written Pydantic models only where generation doesn't cover a case
│   ├── models/                      # SQLAlchemy ORM models — one module per schema (ontology, safety, regulatory, provenance — matching 03-postgresql-schema.sql's schema namespaces)
│   │   ├── ontology.py
│   │   ├── safety.py
│   │   ├── regulatory.py
│   │   └── provenance.py
│   ├── dependencies/                 # FastAPI dependency-injection providers
│   │   ├── auth.py                  # Entra ID token validation → current-user dependency
│   │   ├── db.py                    # Postgres session provider
│   │   ├── graph.py                 # Neo4j driver provider
│   │   └── permissions.py           # AuthZ dependency — role/scope checks per endpoint
│   ├── middleware/
│   │   ├── logging.py                # Structured request logging
│   │   ├── error_handling.py         # Maps domain/validation exceptions → OpenAPI-conformant error responses
│   │   └── correlation.py            # Request correlation ID propagation (ties to provenance model, KG spec 05)
│   ├── exceptions/
│   │   ├── domain_exceptions.py      # e.g. GateTestFailedError, OntologyConceptNotFoundError
│   │   └── handlers.py               # Registered exception → HTTP response mapping
│   ├── core/
│   │   ├── config.py                 # Settings object (pydantic-settings) — reads env vars per 09-configuration-management.md §1
│   │   ├── logging_config.py
│   │   └── security.py               # Token/secret handling helpers — never logs secret values
│   └── ai/                           # AI Extraction + Demonstration Engine LLM-calling code — isolated so the Anthropic key never leaves this layer (architecture §1.4 finding 3)
│       ├── extraction/
│       └── demonstration/
├── alembic/
│   ├── versions/                     # Mirrors database/postgres/migrations — see §5 for the canonical location question
│   └── env.py
├── tests/                            # Co-located fast unit tests may exist here per team convention; canonical suite is /tests at repo root (§10)
├── pyproject.toml
└── Dockerfile
```

**Layer dependency rule:** `routers → services → repositories/graph → models`. A router must never import a repository directly, and a repository must never contain a business rule (a rule belongs in `services/<module>/rules.py`) — this is the enforcement mechanism for [02-development-standards.md](02-development-standards.md) §5's review checklist item about not bypassing business rules like the 3-gate test.

**Exception handling boundary:** domain exceptions are raised in `services/`, never in `routers/`; `middleware/error_handling.py` is the single place that translates them to HTTP responses, so no router hand-rolls its own error shape — keeping every error response conformant with [10-openapi.yaml](../knowledge-graph/10-openapi.yaml)'s error schemas.

---

## 4. Shared Packages

| Package | Owns | Consumed by | Dependency rule |
|---|---|---|---|
| `packages/shared-types` | TypeScript types generated from [10-openapi.yaml](../knowledge-graph/10-openapi.yaml) | `apps/web`, `packages/api-client`, `packages/ui-components` (prop types only) | **Generated, never hand-edited** (IB1 §3). Regenerated by CI whenever the OpenAPI spec changes; a PR touching the spec must include the regenerated output in the same PR ([02-development-standards.md](02-development-standards.md) §4). Depends on nothing else in the monorepo. |
| `packages/api-client` | Typed fetch wrappers over `shared-types`, one function per OpenAPI operation | `apps/web` only | Depends on `shared-types`. Never imported by `apps/api` (the client is a consumer of the contract, not a definer of it) or by `packages/ui-components` (keeps UI primitives network-agnostic). |
| `packages/ontology-client` | Concept lookup/validation logic — Python and TypeScript builds from one conceptual spec, so both `apps/web` and `apps/api` resolve a concept string against the ontology the same way | `apps/web` (TS build), `apps/api` (Python build) | Depends on `shared-types` (TS side) for concept/scheme shape. This package exists specifically to prevent the V1 failure mode of four independently-invented category lists (architecture §1.4 finding 1) — no module may re-implement concept resolution locally. |
| `packages/ui-components` | Shared shadcn/ui-based design-system components — one visual language across every module | `apps/web` modules | Depends on `shared-types` for prop typing only. Must not depend on `api-client` or any module — a UI component that needs data receives it via props, it does not fetch. |

**Ownership:** Platform/DevOps owns `shared-types` and its generation tooling; Backend owns `ontology-client`'s Python build and the ontology concept model it wraps; Frontend owns `api-client`, `ui-components`, and `ontology-client`'s TS build. This mirrors [01-repository-structure.md](01-repository-structure.md) §3's owner-discipline table.

**Acyclic rule:** dependency direction is strictly `apps/* → packages/*`; no package depends on an app, and among packages the only permitted edges are `api-client → shared-types`, `ontology-client → shared-types` (TS side), `ui-components → shared-types`. `ontology-client`'s Python build and `ui-components` never depend on each other.

---

## 5. Database Project Structure

### PostgreSQL

```
database/postgres/
├── migrations/                     # Alembic-generated, hand-reviewed (05-database-migration-strategy.md §1)
│   └── <revision>_<slug>.py
├── seeds/
│   ├── ontology/                   # Ported V1 taxonomies — see ontology/seed-concepts/ (this folder loads them, doesn't duplicate content)
│   ├── dev-fixtures/               # Synthetic — Dev/Test only (05 §4)
│   ├── pilot-register/             # V1 108-row / 14-hazard pilot register migration script (05 §4) — real reference data, not disposable
│   └── views/                      # Read-optimized SQL views — e.g. control-health rollups feeding the Dashboard module (§12)
└── procedures/                     # Stored procedures — TO_BE_CONFIRMED: none approved in Design Baseline v1.0; folder exists as a placeholder only. Any stored procedure requires an ACR before use, since business logic in the database layer bypasses the services/ layer's rule-enforcement point (§3) — this is a deliberate high bar, not an oversight.
```

Note on Alembic's canonical location: [01-repository-structure.md](01-repository-structure.md) places migrations at `database/postgres/migrations/`, while §3 of this document shows an `apps/api/alembic/versions/` folder as a possible Alembic default layout. **These must not both hold real migration files.** `alembic.ini`'s `script_location` should point at `database/postgres/migrations/` so there is one migration history, not two — `apps/api/alembic/env.py` is configuration pointing outward, not a second content folder. This is flagged here specifically so R0 setup doesn't accidentally create two migration histories.

### Neo4j

```
database/neo4j/
├── schema/
│   └── node-labels.md              # Reference copy of 02-neo4j-node-relationship-model.md §2–§3 labels, for scripting convenience — the .md doc remains authoritative
├── constraints/                    # Cypher DDL, versioned (02-neo4j-node-relationship-model.md §5)
│   └── <version>_constraints.cypher
├── indexes/
│   └── <version>_indexes.cypher
├── ontology-import/                # Scripts loading ontology/schemes + ontology/seed-concepts into the ontology graph
├── inference-rules/                # Cypher implementations of 07-inference-rules-catalogue.md R1–R18, run as scheduled/on-demand queries (not stored procedures — Neo4j has no equivalent restriction concern since this is query logic, not write-path business logic)
└── migrations/                     # Versioned, idempotent — re-run-safe per 05-database-migration-strategy.md §2; "migration" here means constraint/index change, not instance-data migration
```

Consistent with [05-database-migration-strategy.md](05-database-migration-strategy.md) §2: this folder stays small by design because instance data is a rebuildable projection from Postgres via the Graph Sync Service, not migrated here.

---

## 6. Infrastructure Layout

```
infrastructure/
├── bicep/                          # Bicep chosen per IB1 §2 folder naming; final IaC tool confirmation is an R0 exit item (04-implementation-roadmap.md), not re-litigated here — TO_BE_CONFIRMED if R0 selects otherwise
│   ├── modules/
│   │   ├── container-apps.bicep    # apps/web, apps/api, extraction/gap-analysis workers (architecture §8 compute decision)
│   │   ├── postgres.bicep          # Azure Database for PostgreSQL Flexible Server
│   │   ├── neo4j.bicep             # TO_BE_CONFIRMED: AuraDB vs. self-hosted container (06-environment-strategy.md, architecture §8) — module structured to support either, decision deferred to R0
│   │   ├── qdrant.bicep            # Same hosting-decision caveat as neo4j.bicep
│   │   ├── storage.bicep           # Azure Blob Storage — document/evidence storage
│   │   ├── key-vault.bicep         # Per-environment secret store (09-configuration-management.md §2)
│   │   ├── networking.bicep        # VNet, private endpoints for Postgres/Storage/Key Vault
│   │   ├── identity.bicep          # Managed identities for Container Apps → Key Vault/Storage access
│   │   └── monitoring.bicep        # Application Insights, alerting (06-environment-strategy.md monitoring row)
│   └── main.bicep                  # Composition root, parameterized per environment
└── environments/
    ├── dev.bicepparam
    ├── test.bicepparam
    ├── uat.bicepparam
    └── prod.bicepparam
```

Each `.bicepparam` file supplies the environment-specific values in [06-environment-strategy.md](06-environment-strategy.md)'s comparison table (sizing tier, HA config, retention policy) — non-secret only, per the configuration hierarchy in §8 below.

---

## 7. Documentation Structure

```
docs/
├── PLATFORM_ARCHITECTURE_V2.md          # Phase 1 — frozen
├── knowledge-graph/                     # Design Baseline v1.0 — frozen, 11 docs
├── implementation-blueprint/            # Phase 2.1 + 2.2 (this document) — IB1–IB13
├── api/                                  # Rendered/browsable form of 10-openapi.yaml (e.g. Redoc/Swagger static export) — generated, not hand-authored
├── ontology/                             # Curator-facing documentation on scheme governance, distinct from the ontology/ data folder at repo root
├── operations/                           # Runbooks — deployment, backup/restore, incident response, tied to 10-operational-readiness-checklist.md
├── deployment/                           # Environment setup guides per 06-environment-strategy.md, one per environment
├── user-guides/                          # Per-module end-user guides — populated as each module ships (roadmap R1–R7), not written speculatively ahead of the module existing
├── developer-guides/                     # Onboarding, local dev setup (docker-compose.yml), contribution workflow (02-development-standards.md)
├── adr/                                   # Rendered index of .adr/ at repo root — the .adr/ folder is the source of truth, this is a browsable index
└── acr/                                   # Rendered index of .acr/ at repo root, same relationship as adr/ above
```

**Rule:** `docs/adr/` and `docs/acr/` never hold content that isn't also in `.adr/`/`.acr/` at repo root — they are generated indexes (e.g. a simple script listing files with title/status), preventing the two-homes-for-one-fact problem this entire document set has been correcting for at the data layer, now applied to process documentation.

---

## 8. Configuration Strategy

This section presents [09-configuration-management.md](09-configuration-management.md) (IB9) in the structure requested for this deliverable; it does not add new configuration decisions.

**Hierarchy** (IB9 §3):
```
Base config (repo, non-secret defaults)
  → Environment overrides (infrastructure/environments/*.bicepparam, non-secret)
    → Key Vault secrets (runtime-injected, secret values only)
```

| Concern | Where it lives | Reference |
|---|---|---|
| Environment variables | `.env.example` (names only) at repo root; `apps/web/src/config/env.ts` and `apps/api/app/core/config.py` as typed readers | IB9 §1 |
| Feature flags | `apps/web/src/config/feature-flags.ts` (read path), flag definitions owned centrally — not yet assigned a storage mechanism beyond IB9 §4's table; **TO_BE_CONFIRMED**: flag storage (env var vs. a dedicated flags table vs. a third-party service) is not decided in IB9 and should not be assumed here | IB9 §4 |
| Key Vault references | `infrastructure/bicep/modules/key-vault.bicep` provisions; `apps/api/app/core/security.py` and Container Apps' managed-identity binding consume — never a raw secret value checked into any file in this repo | IB9 §2 |
| Logging configuration | `apps/api/app/core/logging_config.py`; frontend logging (if any beyond browser console) — not specified in IB9, **TO_BE_CONFIRMED** | — |
| AI configuration | `ANTHROPIC_API_KEY` — Key Vault only, `apps/api/app/ai/` is the sole consumer; `EXTRACTION_CONFIDENCE_OVERRIDE_*` — Dev/Test only | IB9 §1 |
| Database connections | `DATABASE_URL`, `NEO4J_URI`/`NEO4J_USER`/`NEO4J_PASSWORD`, `QDRANT_URL` — Key Vault-injected, consumed via `apps/api/app/dependencies/db.py` and `graph.py` | IB9 §1 |
| Security settings | `ENTRA_TENANT_ID`/`ENTRA_CLIENT_ID`/`ENTRA_CLIENT_SECRET` per-environment app registrations | IB9 §1, [06-environment-strategy.md](06-environment-strategy.md) |

---

## 9. GitHub Standards

Templates live in `.github/ISSUE_TEMPLATE/` and `.github/PULL_REQUEST_TEMPLATE.md`. Content is structural only — fields to fill, not implementation.

**Issue — general bug report** (`.github/ISSUE_TEMPLATE/bug_report.yml`): affected module (dropdown from [03-module-dependency-map.md](03-module-dependency-map.md)'s module list), environment, steps to reproduce, expected vs. actual, whether it touches a critical control/regulatory citation ([02-development-standards.md](02-development-standards.md) §5 review flag), severity.

**Feature request** (`feature_request.yml`): module, referenced Design Baseline entity/relationship/rule ID (per [02](02-development-standards.md) §8 Definition of Ready — "implement R14," not "build the boundary feature"), acceptance criteria.

**Architecture Change Request** (`acr_request.yml`): mirrors the `.acr/` template body exactly — Raised by, Affected document(s), Current state, Proposed change, Impact, Approval — so an ACR can be opened as a GitHub Issue and then formalized into `.acr/` once approved, per [02-development-standards.md](02-development-standards.md) §7.

**Pull request** (`.github/PULL_REQUEST_TEMPLATE.md`): linked work item, module(s) touched, checklist mirroring [02-development-standards.md](02-development-standards.md) §4–§5 (shared-types regenerated if OpenAPI changed; migration included if schema changed; relationship-rules/critical-item-override/ontology/`TO_BE_CONFIRMED` review checklist items), test evidence.

**Release** (`.github/ISSUE_TEMPLATE/release.yml` or a release-drafter config): release identifier matching [04-implementation-roadmap.md](04-implementation-roadmap.md)'s R0–R7 labels, exit-criteria checklist copied from that release's row, UAT sign-off reference ([08-testing-strategy.md](08-testing-strategy.md) §9).

---

## 10. Testing Structure

```
tests/
├── unit/                # Mirrors apps/api and apps/web module structure (08-testing-strategy.md §1) — R1–R18, 3-gate/EIA/FARSI
├── integration/         # API + ephemeral DB containers (§2) — cross-entity writes, Graph Sync propagation
├── contract/            # Schemathesis-generated, all 56 OpenAPI paths (§3)
├── e2e/                 # Full-stack Playwright scenarios (per IB1 §2 — full-stack acceptance flows)
├── graph/               # Cypher-backed relationship-rule tests (§4) — 06-relationship-rules-catalogue.md §3–§5a
├── ontology/             # Acyclic/orphan/alias/ExtractionRule-resolution checks (§5)
├── ai-extraction/        # Golden-set accuracy tests (§6) — includes the hydraulic-isolation worked example as a permanent regression case
├── performance/          # Load tests against query-pattern catalogue Q1–Q7 (§7), UAT-scale data
├── security/             # SAST/DAST harness config, pre-Prod pentest checklist artefacts (§8)
├── uat/                  # Sign-off checklists per release, not automated tests — parity checklists (R1–R5), extraction/KG Explorer review (R6), Demonstration narrative review (R7) (§9)
└── fixtures/             # Shared test data — synthetic only, never production data (06-environment-strategy.md cross-environment rule)
```

Every subfolder's content is scoped by rule/section ID from [08-testing-strategy.md](08-testing-strategy.md), not a generic "write tests" instruction — per that document's own Coverage Principle.

---

## 11. Build Pipeline Structure

Reproduces [07-cicd-architecture.md](07-cicd-architecture.md) (IB7) organized as requested; no new pipeline behavior introduced.

```
.github/workflows/
├── pr-validation.yml         # Lint → typecheck → unit tests → OpenAPI validation → ontology validation (if changed) → migration validation (if changed) → contract tests (if apps/api changed)
├── merge-main-build.yml      # Container build (apps/web, apps/api) → integration tests → Knowledge Graph validation → auto-deploy Dev
├── deploy-environment.yml    # Triggered by release/x.y tag → migration gate → Neo4j constraint apply → deploy → smoke tests → auto-rollback on failure → manual approval gate before Prod
├── scheduled-security-scan.yml      # Nightly SAST/dependency/container scan
├── scheduled-kg-drift-check.yml     # Daily Neo4j↔Postgres structural check
├── scheduled-extraction-regression.yml  # Weekly golden-set re-run
└── scheduled-ontology-integrity.yml     # Weekly full-scope ontology scan
```

| Stage | Maps to |
|---|---|
| Validation (lint/typecheck) | IB7 §2.1–2.2 |
| Testing (unit/contract) | IB7 §2.3, §2.7 |
| OpenAPI validation | IB7 §2.4 |
| Ontology validation | IB7 §2.5 |
| Graph validation | IB7 §3.3 |
| Security scan | IB7 §6 |
| Container build | IB7 §3.1 |
| Deployment | IB7 §4 |

---

## 12. Initial Module Skeleton

Eighteen modules, structure only — each entry below states purpose, dependencies, interfaces, and Design Baseline references. **No component, endpoint, or entity is implemented by this document.** Where a requested module has no corresponding entity in Design Baseline v1.0, that gap is stated explicitly rather than filled by invention (constraint: "do not invent additional entities").

Cross-reference for all "prerequisite/dependent" columns: [03-module-dependency-map.md](03-module-dependency-map.md) (IB3). Cross-reference for all entity names: [03-postgresql-schema.sql](../knowledge-graph/03-postgresql-schema.sql), [02-neo4j-node-relationship-model.md](../knowledge-graph/02-neo4j-node-relationship-model.md), [10-openapi.yaml](../knowledge-graph/10-openapi.yaml) tags.

### Dashboard
- **Purpose:** read-only cross-module aggregation (control health state, TARP status, open actions) — replaces V1 `safety-dashboard.html` (roadmap R5).
- **Dependencies:** Risk Register, Critical Controls, Incidents, Actions (all as read sources; no write path).
- **Public interfaces:** none of its own — consumes existing endpoints from `Risks`, `CriticalControls`, `Incidents`, `Actions`, `TARPs` tags.
- **Planned APIs:** none net-new; possible aggregation endpoints are **TO_BE_CONFIRMED** — not specified in [10-openapi.yaml](../knowledge-graph/10-openapi.yaml) as of Design Baseline v1.0. If dashboard-specific aggregation endpoints prove necessary, that is an ACR against the OpenAPI spec, not an assumed addition here.
- **Planned database entities:** none — reads `database/postgres/seeds/views/` rollup views (§5) or existing tables directly.
- **Related ontology concepts:** none directly; surfaces classifications already assigned elsewhere.

### Assets
- **Purpose:** ride/device register including Device Boundary — foundational module, R0.
- **Dependencies:** Authentication, Ontology.
- **Public interfaces:** `Assets` tag.
- **Planned APIs:** `safety.assets`, `safety.device_boundaries`, `safety.interfaces` ([10-openapi.yaml](../knowledge-graph/10-openapi.yaml)).
- **Planned database entities:** `safety.assets`, `safety.device_boundaries`, `safety.interfaces`, `safety.parks`.
- **Related ontology concepts:** Asset taxonomy; ISO 55000 class field — **TO_BE_CONFIRMED** ([PLATFORM_ARCHITECTURE_V2.md](../PLATFORM_ARCHITECTURE_V2.md) §6 entity table).

### Hazards
- **Purpose:** Hazard Library — single canonical hazard model replacing V1's four incompatible schemas.
- **Dependencies:** Ontology, Assets.
- **Public interfaces:** `Hazards` tag.
- **Planned APIs:** `safety.hazards`.
- **Planned database entities:** `safety.hazards`.
- **Related ontology concepts:** hazard classification schemes ([01-enterprise-knowledge-graph-specification.md](../knowledge-graph/01-enterprise-knowledge-graph-specification.md)).

### Risk Register
- **Purpose:** risk rating and consequence modelling — first strangler-fig cutover (R1).
- **Dependencies:** Hazard Library.
- **Public interfaces:** `Risks` tag.
- **Planned APIs:** `safety.risks`, `safety.consequences`.
- **Planned database entities:** `safety.risks`, `safety.consequences`.
- **Related ontology concepts:** consequence domains (ported from V1 `REF.consequenceDomains`).

### Critical Controls
- **Purpose:** unified control/critical-control model — 3-gate test, EIA test, FARSI (Interdependency) banding — replacing V1's separate bow-tie generator and FARSI calculator (R3, highest-complexity release).
- **Dependencies:** Risk Register, Ontology.
- **Public interfaces:** `Controls`, `CriticalControls` tags.
- **Planned APIs:** `safety.controls`, `safety.critical_controls`, `safety.failure_modes`.
- **Planned database entities:** `safety.controls`, `safety.critical_controls`, `safety.failure_modes`.
- **Related ontology concepts:** control hierarchy (ported from V1 `REF.controlHierarchy`); energy-source list.

### Performance Standards
- **Purpose:** performance standards attached to critical controls ([08-critical-control-assurance-model.md](../knowledge-graph/08-critical-control-assurance-model.md)).
- **Dependencies:** Critical Controls.
- **Public interfaces:** under `CriticalControls` tag (no dedicated tag per IB3 §2).
- **Planned APIs:** `safety.performance_standards`.
- **Planned database entities:** `safety.performance_standards`.
- **Related ontology concepts:** none additional beyond Critical Controls' own.

### Verification
- **Purpose:** verification activities and evidence against performance standards.
- **Dependencies:** Performance Standards.
- **Public interfaces:** `Verification`, `Evidence` tags.
- **Planned APIs:** `safety.verification_activities`, `safety.evidence`, `safety.monitoring_summaries`.
- **Planned database entities:** `safety.verification_activities`, `safety.evidence`, `safety.monitoring_summaries`.
- **Related ontology concepts:** none additional.

### Incidents
- **Purpose:** incident recording and hazard linkage — second strangler-fig cutover (R2).
- **Dependencies:** Assets, Hazard Library.
- **Public interfaces:** `Incidents` tag.
- **Planned APIs:** `safety.incidents`, `safety.incident_hazards`.
- **Planned database entities:** `safety.incidents`, `safety.incident_hazards`.
- **Related ontology concepts:** notifiable-incident classification — determination remains human-gated per roadmap R2 note, never automated.

### Investigations
- **Purpose:** incident investigation records.
- **Dependencies:** Incidents.
- **Public interfaces:** under `Incidents` tag (no dedicated tag per IB3 §2).
- **Planned APIs:** `safety.investigations`.
- **Planned database entities:** `safety.investigations`.
- **Related ontology concepts:** none additional. Investigation methodology itself is **TO_BE_CONFIRMED** ([knowledge-graph/README.md](../knowledge-graph/README.md) open items).

### Audits
- **Purpose:** audit and audit finding records, three-lines-of-assurance model.
- **Dependencies:** Authentication.
- **Public interfaces:** `Audits` tag.
- **Planned APIs:** `safety.audits`, `safety.audit_findings`.
- **Planned database entities:** `safety.audits`, `safety.audit_findings`, `safety.audit_finding_actions`.
- **Related ontology concepts:** `Audit.audit_type` (three-lines-of-assurance, [08-critical-control-assurance-model.md](../knowledge-graph/08-critical-control-assurance-model.md) §5). Audit cycle frequency is **TO_BE_CONFIRMED**.

### Actions
- **Purpose:** corrective/preventive actions arising from incidents, audits, or risk treatment.
- **Dependencies:** Incidents, Audits, Risk Register.
- **Public interfaces:** `Actions` tag.
- **Planned APIs:** `safety.actions`, `safety.action_controls`.
- **Planned database entities:** `safety.actions`, `safety.action_controls`, `safety.incident_actions`.
- **Related ontology concepts:** none additional.

### Training — superseded by Competency (Design Baseline v1.1, approved 2026-08-04)
- **Purpose:** originally requested with no corresponding entity in Design Baseline v1.0 ([ACR-001](../../.acr/ACR-001-training-domain.md)). The Architecture Review Board rejected ACR-001 as an independent entity and approved [ACR-003](../../.acr/ACR-003-competency-management-domain.md) instead — training is now a `competency_type` classification value on `safety.competencies`, not its own module. **Rename `apps/web/src/modules/training/` to `apps/web/src/modules/competency/` at R0** — the new `Competency` OpenAPI tag warrants its own module (sibling to `administration/`, not folded into it) rather than a rename-in-place of the stale placeholder.
- **Dependencies:** Administration (Ontology — Competency Category scheme), People.
- **Public interfaces:** `Competency` tag.
- **Planned APIs:** `/roles`, `/competencies`, `/competencies/{id}`, `/competencies/{id}/evidence` ([10-openapi.yaml](../knowledge-graph/10-openapi.yaml)).
- **Planned database entities:** `safety.roles`, `safety.role_competency_requirements`, `safety.competencies`, `safety.competency_evidence`.
- **Related ontology concepts:** Competency Category scheme ([knowledge-graph/01](../knowledge-graph/01-enterprise-knowledge-graph-specification.md) §6a).

### Management of Change
- **Purpose:** MOC formalized as a real entity ([11-safety-case-demonstration-model.md](../knowledge-graph/11-safety-case-demonstration-model.md) §7.2a), triggering safety re-assessment. As of v1.1, a `new_adh_identified` trigger can also flag linked `Competency` records for review, not just `safety_assessment`/`emergency_plan` ([07-inference-rules-catalogue.md](../knowledge-graph/07-inference-rules-catalogue.md) R21).
- **Dependencies:** Assets, Critical Controls.
- **Public interfaces:** `SafetyCase` tag, `/management-of-change` path.
- **Planned APIs:** `safety.management_of_change`, `safety.review_triggers`.
- **Planned database entities:** `safety.management_of_change`, `safety.review_triggers`.
- **Related ontology concepts:** review-trigger classification.

### Safety Assessment
- **Purpose:** ADH-level safety assessment — credible events, hazard coverage ([11-safety-case-demonstration-model.md](../knowledge-graph/11-safety-case-demonstration-model.md) §4).
- **Dependencies:** Assets, Hazard Library, Critical Controls, MOC.
- **Public interfaces:** `SafetyCase` tag.
- **Planned APIs:** `safety.safety_assessments`, `safety.credible_events`.
- **Planned database entities:** `safety.safety_assessments`, `safety.credible_events`, `safety.safety_assessment_hazards`.
- **Related ontology concepts:** SFAIRP/SFARP classification ([knowledge-graph/09](../knowledge-graph/09-regulatory-knowledge-model.md)).

### Safety Demonstration
- **Purpose:** covers the Demonstration Engine ([11-safety-case-demonstration-model.md](../knowledge-graph/11-safety-case-demonstration-model.md) §7), the terminal Safety Case Claim/Argument/Evidence/Requirement structure, and — **as of Design Baseline v1.1** — Emergency Planning ([ACR-002](../../.acr/ACR-002-emergency-planning-domain.md), approved 2026-08-04). Grouped as one user-facing module since IB3's dependency map treats Demonstration Engine and Safety Case as adjacent, tightly-coupled terminal nodes, and Emergency Planning is the structural home for Schedule 18B content that risk D4 previously had nowhere to attach (third strangler-fig-independent, net-new module set, R7).
- **Dependencies:** Knowledge Graph Sync, Safety Assessment, Verification, Performance Standards.
- **Public interfaces:** `SafetyCase`, `Requirements` tags.
- **Planned APIs:** `safety.demonstrations`, `/demonstrations`, `safety.safety_case_claims`, `safety.safety_arguments`, `regulatory.requirements`, `/parks/{parkId}/emergency-plan`, `/emergency-plans/{id}/credible-events`, `/emergency-plans/{id}/exercises`, `/emergency-plans/{id}/consultations`.
- **Planned database entities:** `safety.demonstrations`, `safety.safety_case_claims`, `safety.safety_case_claim_evidence`, `safety.safety_case_claim_requirements`, `safety.safety_arguments`, `safety.safety_argument_evidence`, `regulatory.requirements`, `safety.sms_sections`, `safety.sms_section_requirements`, `safety.emergency_plans`, `safety.emergency_plan_credible_events`, `safety.emergency_exercises`, `safety.emergency_service_consultations`.
- **Related ontology concepts:** ADH→ADI pathway; regulatory citation set (Schedule 18B confirmed and now structurally modelled via `emergency_plans`; Schedule 18C/19/ISO 45001/AS 3533/AS 4024/ISO 17842 partially `TO_BE_CONFIRMED` per [knowledge-graph/09](../knowledge-graph/09-regulatory-knowledge-model.md)); Emergency Service Organisation scheme ([knowledge-graph/01](../knowledge-graph/01-enterprise-knowledge-graph-specification.md) §6a). Risk D4 ([11-implementation-risk-register.md](11-implementation-risk-register.md)) is closed by this amendment.

### Knowledge Graph
- **Purpose:** Knowledge Graph Explorer UI + Graph Sync Service — instance graph and ontology graph in one viewer.
- **Dependencies:** Risk Register, Critical Controls, Incidents, Actions.
- **Public interfaces:** `KnowledgeGraph` tag; internal Graph Sync Service.
- **Planned APIs:** `/graph/query/{patternId}` (query patterns Q1–Q7, [EKG spec](../knowledge-graph/01-enterprise-knowledge-graph-specification.md) §5).
- **Planned database entities:** none new in Postgres — this module is the projection/query layer over Neo4j (§5).
- **Related ontology concepts:** ontology graph node labels ([02-neo4j-node-relationship-model.md](../knowledge-graph/02-neo4j-node-relationship-model.md) §2).

### AI Review Queue
- **Purpose:** human review UI for AI Extraction Service drafts — the confidence-routing "flag for review" path ([04-ai-extraction-specification.md](../knowledge-graph/04-ai-extraction-specification.md) §6). This is IB3's "AI Extraction" module surfaced as a user-facing queue, not a separate entity domain.
- **Dependencies:** Ontology, Hazard Library, Incidents.
- **Public interfaces:** `Documents`, `Extraction` tags.
- **Planned APIs:** `safety.documents`, extraction run/draft endpoints.
- **Planned database entities:** `safety.documents`; draft writes target Hazard Library/Risk Register/Critical Controls/Investigations tables directly, per [04-ai-extraction-specification.md](../knowledge-graph/04-ai-extraction-specification.md).
- **Related ontology concepts:** `ontology.extraction_rules` (`ExtractionRule.target_concept_id`).

### Competency (Design Baseline v1.1 — [ACR-003](../../.acr/ACR-003-competency-management-domain.md), approved 2026-08-04; renamed from the rejected Training placeholder, §2)
- **Purpose:** role-based competency management — Competency as the canonical claim, evidence-linked, superseding the originally-requested standalone Training module (ACR-001, rejected). Training, qualifications, licences, OEM certifications, authorisations, and officer information-briefing records are all `competency_type` values on one entity, not separate tables.
- **Dependencies:** People, Critical Controls (operator-competency as a control-assurance input), Ontology (Competency Category scheme).
- **Public interfaces:** `Competency` tag.
- **Planned APIs:** `/roles`, `/competencies`, `/competencies/{id}`, `/competencies/{id}/evidence`.
- **Planned database entities:** `safety.roles`, `safety.role_competency_requirements`, `safety.competencies`, `safety.competency_evidence`.
- **Related ontology concepts:** Competency Category scheme ([knowledge-graph/01](../knowledge-graph/01-enterprise-knowledge-graph-specification.md) §6a). "Experience" (cumulative, not a discrete record) explicitly deferred to a future baseline version, per the ACR's own scope decision — not implemented here.

### Administration
- **Purpose:** system administration surface — hosts the Ontology Curator UI (named separately in the architecture's Client subgraph) and People/user administration. Not itself a new entity domain; groups existing Ontology and People management under one admin-facing module.
- **Dependencies:** Authentication, Ontology.
- **Public interfaces:** `Ontology`, `People` tags.
- **Planned APIs:** `ontology.concepts`/`ontology.schemes` (curator workflow: draft → reviewed → approved → published), `safety.persons`.
- **Planned database entities:** `ontology.schemes`, `ontology.concepts`, `ontology.concept_aliases`, `ontology.concept_relations`, `ontology.relationship_types`, `ontology.extraction_rules`, `safety.persons`.
- **Related ontology concepts:** ontology governance model itself ([EKG spec](../knowledge-graph/01-enterprise-knowledge-graph-specification.md) §6). Role/permission model for administration access is **TO_BE_CONFIRMED** beyond "Entra ID provides AuthN/AuthZ" — the specific admin-role scoping is not detailed in any frozen document. Not to be confused with `safety.roles` (Competency module, above) — this is application-access role, an unrelated concept sharing an unfortunate name; if this becomes confusing in practice, renaming one of them is a candidate ADR, not an ACR (naming, not a domain-model change).

---

## 13. Open Items Carried Forward

Not duplicated in full — see the authoritative source for each, consistent with [12-deliverables-index.md](12-deliverables-index.md)'s existing practice:

- **Closed, 2026-08-04:** ACR-001 (rejected, superseded by ACR-003), ACR-002 (approved — Emergency Planning), ACR-003 (approved — Competency Management). Design Baseline is now v1.1. See [14-architecture-change-requests.md](14-architecture-change-requests.md) §6.
- Frontend routing/state/form/build-tool choices (§2) are working assumptions, not ADRs yet — five ADRs should be opened at R0 start.
- Dashboard aggregation endpoints (§12) — **TO_BE_CONFIRMED**, may require an OpenAPI ACR if client-side aggregation of existing endpoints proves insufficient.
- Stored procedure policy (§5) — placeholder folder only, zero procedures approved.
- Neo4j/Qdrant hosting (AuraDB vs. self-hosted) and Bicep-vs-alternative IaC confirmation — both already tracked as R0 exit items in [04-implementation-roadmap.md](04-implementation-roadmap.md) and [06-environment-strategy.md](06-environment-strategy.md); not re-opened here, only referenced.
- Feature-flag storage mechanism (§8) — not specified in [09-configuration-management.md](09-configuration-management.md).
- Administration module's specific admin-role scoping (§12) — beyond "Entra ID," not detailed anywhere in the frozen baseline. Naming collision with the new `safety.roles` (Competency module) noted in §12 — candidate ADR, not a blocker.
- Remaining regulatory `TO_BE_CONFIRMED` items (Schedule 18C sub-items — narrowed to contractor management §10.6 and incident management §10.7 only, since training/asset integrity are now read; Schedule 19 verbatim text; ISO/AS standards) remain exactly as tracked in [12-deliverables-index.md](12-deliverables-index.md). Risk D4 (`EmergencyPlan` entity) is **closed** — resolved by ACR-002.

No implementation code exists against this document. Phase 2.2 remains a planning artefact until approved.
