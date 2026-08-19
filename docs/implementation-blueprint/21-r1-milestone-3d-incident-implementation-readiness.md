# R1 Milestone 3D — Incident Implementation Readiness & Scope

**Status:** Readiness section (§1-§11) is the original research/reconciliation pass — authorizes nothing to be built. Written 2026-08-15, PR #18, HEAD `1b3c2d2`. **Addendum, 2026-08-19: 3D-1 (§7) has since been GO'd, implemented, and closed — see §12.** The readiness content below is left as originally written; §12 records what actually happened.

## 1. Purpose

3A–3C settled *what the baseline says*. This document reconciles that baseline against *what the R0 scaffold actually contains* for the Incident domain, so the first implementation GO can be scoped precisely instead of discovered mid-build. No code, schema, contract, or test file is touched by this document.

## 2. Baseline decisions inventory (input to this reconciliation)

| Decision | Disposition | Effect on implementation |
|---|---|---|
| D1 — canonical V1 source | Resolved | `incident-report.html`, `corrective-actions.html` are the field-shape reference |
| D2 — Incident/Investigation/Action structure | [ADR-003](../../.adr/ADR-003-incident-investigation-action-sibling-structure.md) — **sibling**, not chain | `REVEALS`/`INVESTIGATED_AS`/`TRIGGERS` are three independent relationships off `Incident`, not a pipeline — implementation must not model Investigation as a stage Incident "becomes" |
| D3 — incident_type/root_cause_category ontology | [ADR-004](../../.adr/ADR-004-incident-ontology-scheme-deferral.md) — deferred, folded into standing Hazard Taxonomy deferral | `incident_type_concept_id`/`root_cause_category_concept_id` FKs exist in schema but resolve to `null` in the API, same pattern as `Hazard.category_concept_id` (see §4) |
| D4 — Investigation/hazards/Evidence OpenAPI surface | [ACR-004](../../.acr/ACR-004-incident-openapi-extension.md) — **Approved, contract-implemented 2026-08-11** | Full OpenAPI paths exist (§5); zero application code exists behind them |
| D5 — six orphan V1 fields | [ADR-005](../../.adr/ADR-005-incident-orphan-v1-fields-disposition.md) — `fReporterRole` resolves via `Person.role_title`; other five deferred, no columns added | No schema work needed; API layer must not silently drop `fReporterRole` intent — resolve via the reporter's linked `Person.role_title` at read time |
| D6 — R10/general-notification scope | [ADR-006](../../.adr/ADR-006-incident-notification-rule-formal-defer.md) + [ACR-005](../../.acr/ACR-005-incident-general-notifiable-incident-rule.md) — **Approved, incorporated 2026-08-15** | `is_notifiable_incident` column/field/property + **R23** now exist in the baseline docs; **zero application code implements R23's propagation** |
| D6 residual — `osr_notified`/OSR | **`TO_BE_CONFIRMED`** ([ADR-006](../../.adr/ADR-006-incident-notification-rule-formal-defer.md) §11) | Tracked as a controlled external dependency (§8) — does not block any Incident functionality that doesn't depend on it |
| D7 — governance status of 09§6/07 docs | Accepted | No implementation effect |

## 3. Current R0 code-state reconciliation

Verified directly against the repository (not inferred from prior docs) on 2026-08-15:

| Layer | File(s) | State |
|---|---|---|
| DTO | `apps/api/app/dto/incidents.py` | Placeholder docstring only — no Pydantic models |
| Router | `apps/api/app/routers/incidents.py` | `APIRouter(prefix="/incidents", tags=["incidents"])` — zero routes registered |
| Repository | `apps/api/app/repositories/incidents_repository.py` | Placeholder docstring only |
| Service | `apps/api/app/services/incidents/service.py`, `rules.py` | Both placeholder docstrings only |
| ORM model | `apps/api/app/models/safety.py` | **No `Incident`, `Investigation`, or `Action` class exists** — confirmed via grep, zero matches |
| Neo4j sync | `apps/api/app/graph/sync_service.py` | Handles `Asset`, `Hazard`, `Risk` only (`sync_hazard`, etc.) — no `sync_incident`/`sync_investigation`/incident-hazard-link/evidence sync function exists |
| Tests | `tests/**` | Zero files matching `*incident*` anywhere — no unit, integration, contract, or graph coverage |
| Generated types | `packages/shared-types/src` | Zero references to `Incident` — has not been regenerated against any of the Incident OpenAPI surface (ACR-004 or ACR-005). The PR's `openapi-validate` job has been emitting the (non-blocking) `shared-types stale` warning since ACR-004 landed; still unaddressed |

**Conclusion: the Incident domain is genuinely greenfield.** Nothing above the schema/contract layer exists. This confirms [18](18-r1-milestone-3a-incident-discovery-reconciliation.md) §9 and ACR-005 §12's "no rows exist yet" premise still holds.

## 4. Reference implementation pattern (Hazards domain)

Hazards is the closest fully-implemented precedent and should be the structural template for Incident work:

- **Layer dependency rule** ([13](13-application-foundation-scaffold.md) §3): `routers → services → repositories/graph → models`. A router never imports a repository directly; a repository never contains a business rule (rules live in `services/<module>/rules.py`).
- **DTO** (`dto/hazards.py`, 52 lines): Pydantic `HazardInput`/`Hazard`, field-for-field match to the OpenAPI schema, with an explicit docstring flagging where a field is accepted but not yet resolved (their `category`/`energy_source` ontology deferral — the same shape D3's deferral will need for `incident_type`/`root_cause_category`).
- **Repository** (44 lines): thin Postgres/SQLAlchemy CRUD, no business logic.
- **Router** (124 lines): thin, delegates to service.
- **Service** (128 lines) + **rules** (5 lines): orchestration and rule evaluation split apart, per the layer rule above.
- **ORM model** (`models/safety.py::Hazard`): `Mapped[...]` SQLAlchemy 2.0 style, `__table_args__ = {"schema": "safety"}`, deferred-ontology FK columns left nullable with an explanatory comment rather than silently omitted.
- **Neo4j sync** (`graph/sync_service.py::sync_hazard`): explicit `MERGE` Cypher keyed on `pg_id`, called from the service layer after a Postgres write — Postgres remains source of truth, Neo4j is kept in sync via an explicit call, not a trigger or dual-write transaction.
- **Test** (`tests/integration/test_hazards_crud.py`, 93 lines): integration-level CRUD test against a real Postgres instance (per the `integration-tests` CI job's Postgres+Neo4j services).

Incident implementation should mirror this shape per entity (`Incident`, `Investigation`, `Action`), not invent a new pattern.

## 5. OpenAPI surface already contracted (§4 D4/D6 — nothing here needs a new ACR)

Verified against `10-openapi.yaml` directly:

| Path | Methods | Status |
|---|---|---|
| `/incidents` | GET, POST | Contracted, R0 (unimplemented) |
| `/incidents/{id}` | GET, PATCH | Contracted, R0 |
| `/incidents/{id}/investigation` | GET, POST, PATCH | Contracted (ACR-004), R0 |
| `/incidents/{id}/hazards` | GET, POST | Contracted (ACR-004), R0 |
| `/incidents/{id}/hazards/{hazardId}` | DELETE | Contracted (ACR-004), R0 |
| `/incidents/{id}/evidence` | GET, POST | Contracted (ACR-004), R0 |
| `/incidents/{id}/run-investigation-pipeline` | POST | Contracted — **out of 3D scope**, see §9 |
| `/actions` | (not incident-scoped — shared Actions module) | Out of 3D scope unless an Incident-sourced Action path is added |

No new OpenAPI path is required for `is_notifiable_incident` — it rides the existing `PATCH /incidents/{id}` via the extended `IncidentInput` (ACR-005 §8).

## 6. Field/relationship inventory to implement

- **Postgres → ORM models needed:** `Incident` (`safety.incidents`, including `is_notifiable_incident`, `whsq_notified`, `osr_notified` as a plain string column — not resolved, just carried), `Investigation` (`safety.investigations`, 1:1 via `UNIQUE incident_id`), `Action` (`safety.actions`, already partially shared with other action sources via `source_type_concept_id`/`source_id` — Incident is one polymorphic source), plus the two join tables `safety.incident_hazards` (`REVEALS`) and `safety.incident_actions` (`TRIGGERS`).
- **Six orphan V1 fields (D5):** only `fReporterRole` has representation work — resolve via `reporter_person_id → Person.role_title` at the DTO/service boundary, not a new column. The other five stay absent; do not silently re-add them as free columns during implementation.
- **R23 propagation:** currently doc-only (`07-inference-rules-catalogue.md`). Implementing it means: on `Incident` write where `is_notifiable_incident` transitions to `true`, default `whsq_notified` out of `'Not yet assessed'` — this is service-layer logic in `services/incidents/rules.py`, mirroring however R10's Chapter-9A equivalent gets implemented for `osr_notified` (R10 itself is not part of 3D — it was never in scope for D6/ACR-005, and has its own, separate, not-yet-assessed implementation status).
- **Neo4j:** `Incident`, `Investigation`, `Action` node sync functions (`sync_incident`, `sync_investigation`, `sync_action`) plus relationship sync for `REVEALS`/`INVESTIGATED_AS`/`TRIGGERS`, matching the sibling structure ADR-003 mandates — no parent/child nesting.
- **Evidence:** reuse existing generic `safety.evidence`/`Evidence` DTO with `linked_entity_type = 'incident'` — no new Evidence schema, per ACR-004 §9.

## 7. Proposed slice structure

Refining the proposed breakdown against what's actually verified above:

| Slice | Scope | Depends on | Notes |
|---|---|---|---|
| **3D-1** | `Incident` ORM model, repository, base CRUD | — | **CLOSED 2026-08-19 — see §12.** Neo4j `sync_incident` and a base CRUD *service* layer were not part of the GO'd scope in practice (see §12) — persistence only, per the actual GO issued. Those remain open for a later slice. |
| **3D-2** | `Incident` DTO + `/incidents`, `/incidents/{id}` router endpoints | 3D-1 | Wires 3D-1 to the existing OpenAPI contract |
| **3D-3** | `Investigation` model/repo/service/DTO + `/incidents/{id}/investigation`, Neo4j `sync_investigation` + `INVESTIGATED_AS` | 3D-1 | Sibling per ADR-003 — do not nest under Incident's service |
| **3D-4** | `incident_hazards` join, `/incidents/{id}/hazards[/{hazardId}]`, Neo4j `REVEALS` sync | 3D-1, existing Hazard implementation | Bare reference list (ACR-004 Option A) — no new schema object |
| **3D-5** | `/incidents/{id}/evidence` wiring to existing generic Evidence service | 3D-1 | Should be thin — Evidence itself is already generic |
| **3D-6** | R23 propagation logic (`is_notifiable_incident` → `whsq_notified` default-out), `fReporterRole` resolution (D5) | 3D-1, 3D-2 | Service-rule work, not schema work — schema/contract already done (this session) |
| **3D-7** | Integration tests (mirror `test_hazards_crud.py`), unit tests for R23/rules, `shared-types` regeneration, contract tests | 3D-1 through 3D-6 | Closes the zero-coverage gap in §3; also clears the standing `shared-types stale` CI warning |
| **3D-8** | *Not currently grounded in the baseline* — see §9 | — | Recommend deferring or dropping, not scoping yet |

`Action`/`safety.incident_actions` (`TRIGGERS`) is not its own slice above — it's the shared Actions module with an Incident-sourced variant. Recommend folding a thin `incident_actions` link into 3D-6 or a new 3D-6a if the shared Actions module isn't itself ready; flagging rather than pre-deciding.

## 8. OSR — controlled external dependency, not a blocker

`osr_notified`/"OSR" stays `TO_BE_CONFIRMED` (ADR-006 §11). None of 3D-1 through 3D-7 read, write, or branch on `osr_notified` — it's an existing column/field carried as-is (plain string, default `'Not applicable / under assessment'`), same as before this session. It should be tracked (e.g. a standing line item in [12-deliverables-index.md](12-deliverables-index.md)'s open-items section) as an external dependency on the Compliance/Legal referral, not folded into any 3D slice's exit criteria. R10 (the existing OSR-adjacent rule) is likewise not in 3D's scope.

## 9. Findings that adjust the proposed scope

- **`run-investigation-pipeline`** is contracted but belongs to the AI Extraction Specification's Investigation Agent → Compliance Agent → Safety Case Trigger pipeline ([04-ai-extraction-specification.md](../knowledge-graph/04-ai-extraction-specification.md) §7), a materially different (LLM-calling, isolated-key) subsystem per [13](13-application-foundation-scaffold.md)'s `ai/` layer note. Recommend explicitly excluding it from 3D — it is not CRUD/persistence work and would pull in AI-layer concerns this milestone hasn't scoped.
- **3D-8 "Safety Case Demonstration evidence"** — checked [11-safety-case-demonstration-model.md](../knowledge-graph/11-safety-case-demonstration-model.md) directly: it references incidents only conceptually (an "Amusement Device Incident" is a `CredibleEvent.is_adi = true` state, not `safety.incidents`). **No baseline artefact currently defines an `Incident` ↔ `Demonstration`/`SafetyCaseClaim` linkage.** Building one would be a new relationship, i.e. an ACR, not an implementation slice under the existing baseline. Recommend dropping 3D-8 from the near-term slice list, or explicitly routing it through its own ACR first if the user wants it pursued.
- **`shared-types` staleness** is already a live, if non-blocking, CI finding (§3) predating this document — it's cheapest to clear in 3D-7 alongside the rest of the Incident type surface, rather than as a separate cleanup pass.

## 10. What this document does not do

- Does not create, modify, or migrate any schema, model, or code.
- Does not authorize 3D-1 through 3D-7 (or any slice) to begin.
- Does not resolve OSR.
- Does not merge PR #18.

## 11. Recommended next step

Per the user's own framing: issue a scoped GO for one slice at a time, starting with **3D-1** (the only slice with no implementation dependency). Each subsequent slice's GO should name the slice explicitly (e.g. "GO — 3D-2 Incident API/DTOs only") rather than "GO — Incident implementation," consistent with this session's bounded-GO discipline.

## 12. 3D-1 Closure Record (2026-08-19)

**Milestone: CLOSED.**

### 12.1 What was authorized and built

`GO — R1 Milestone 3D-1: Incident persistence/model/repository implementation only`, explicitly bounded to the persistence layer and its tests, explicitly excluding router/service*-orchestration/DTO/Investigation/Action/hazard-link/Evidence/notification/OSR/AI-pipeline/Safety-Case work and unrelated refactoring.

Delivered, on `feature/r1-milestone-3a-incident-discovery`, squash-merged to `main` as `f115590`:

- `apps/api/app/models/safety.py` — `Incident` ORM mapping, all 21 frozen `safety.incidents` columns including `whsq_notified`, `osr_notified`, `is_notifiable_incident` (ACR-005), carried as plain columns with no business logic attached.
- `apps/api/app/repositories/incidents_repository.py` — `list_incidents`/`get_incident`/`create_incident`/`update_incident`. No `delete` — correctly absent, `10-openapi.yaml` contracts no `DELETE /incidents`.
- `tests/unit/test_incident_persistence_model.py` — ORM mapping/column/default assertions.
- `tests/integration/test_incidents_persistence.py` — create→read→update→list round-trip against real Postgres, via the pre-existing `db` fixture (unmodified).

*Correction against §7's original proposal: base CRUD **service** layer and Neo4j `sync_incident` were named in the original 3D-1 slice proposal but were not part of the GO actually issued or the work actually authorized — the GO narrowed to persistence (model + repository) only. Both remain open, unclaimed by any slice yet.

### 12.2 Provenance discrepancy, reconciled

The five persistence commits (`39d4e61`…`df854ee`) landed directly on the remote branch outside the session that had just delivered the 3D readiness document, without a GO visible in that session's own transcript. Per this project's standing rule that remote advancement is not itself authorization, the change was treated as unverified pending reconciliation (not auto-accepted): commit range inspected (`git log --decorate`, `git diff --stat`, full diffs), author verified (`leeshegog-jpg <leeshegog@icloud.com>` — the account this session runs under, not a third party), single-branch provenance confirmed (`git branch -a --contains`), content checked file-by-file against the 3D-1 exclusion list (clean — no router/service/DTO/Neo4j/notification/OSR/Investigation/Action/hazard-link/Evidence/AI/Safety-Case content), and two minor disclosure items were surfaced (a mechanical ruff-format collateral edit to unrelated ORM classes, zero semantic change; a stale module-docstring line still listing `incidents` as deferred). Classified **Category A — legitimate, in-scope** and reconciled into the governed record on that basis, not on the strength of the commit messages alone.

### 12.3 CI-gate closure sequence (each step separately GO'd)

Three defects surfaced only once full CI ran (`ruff check`, `ruff format --check`, `mypy` run sequentially in one job — each subsequent check is invisible until the prior one passes), and each was fixed under its own explicit, narrowly-scoped GO rather than bundled:

| # | Defect | File:line | Class | Commit | GO scope |
|---|---|---|---|---|---|
| 1 | `E501` line too long | `safety.py:334` (`report_date`) | Lint | `7dee896` | "fix `safety.py:334` only" |
| 2 | Formatter mismatch | `safety.py:360` (`status`) | Format | `c2be5f5` | "fix `safety.py:360` only" |
| 3 | `Incident.datetime` column shadows the `datetime` type within its own class body, breaking `Mapped[datetime]` on `created_at`/`updated_at` | `safety.py:361-362` | Type error | `ff11f5a` | "fix `safety.py:361–362` datetime type-shadow via import alias only" |

Fix 3 used a type-import alias (`from datetime import datetime as PyDT`, used only at the two affected annotations) rather than renaming the frozen `Incident.datetime` column — preserves the schema, OpenAPI contract, and ORM field name exactly. Each commit's diff was verified single-purpose before push (no bundling, no opportunistic cleanup); each discovery of a *further* failure after a fix landed was treated as a new, separately-classified item requiring its own GO, not an extension of the prior one.

### 12.4 Final validation, verified against the merge commit directly (not assumed from the last PR push)

`gh api .../commits/f115590/check-runs` — all 12 checks `success`, including the 7 PR-validation jobs and the merge-to-main jobs (`build`, `deploy`, `report-build-status`, `Container build — api`, `Container build — web`).

Local re-verification on `main` post-merge: `git status` clean, `Incident.datetime` column line unchanged (`safety.py:334` in the pre-fix numbering / current line — frozen name intact), squash-merge diff (`6deeb8e..f115590`, 22 files) contains exactly the expected file set — 3A/3B/3C/3D governance docs, ACR-004/005, ADR-003/004/005/006, the four baseline-artefact edits from ACR-005 incorporation, and the 3D-1 persistence files. No router/DTO/service/Neo4j-sync/OSR/AI/Safety-Case file present.

### 12.5 Status table

| Item | Status |
|---|---|
| 3D-1 implementation | ✅ Complete |
| E501 fix | ✅ `7dee896` |
| Formatting fix | ✅ `c2be5f5` |
| `datetime` type-shadow fix | ✅ `ff11f5a` |
| Unit validation | ✅ (49 passed locally, and in CI) |
| Integration validation | ✅ CI (Postgres+Neo4j service containers) |
| 7/7 PR CI | ✅ |
| Merge-to-main CI (12/12) | ✅ |
| PR #18 | ✅ Merged |
| Merge commit | `f115590` |
| Schema/OpenAPI/ontology/architecture altered by closure | **No** — closure is documentation only |
| Milestone | **CLOSED** |

### 12.6 What remains open (not implied complete by this closure)

- 3D-2 through 3D-7 (API/DTO, Investigation, hazard-links, Evidence, R23 propagation + `fReporterRole`, tests/shared-types) — none started.
- Neo4j `sync_incident` and an `Incident` service/orchestration layer — named in §7's original 3D-1 proposal but not delivered under the GO actually issued (§12.1) — unclaimed by any slice.
- OSR (`osr_notified`) — `TO_BE_CONFIRMED`, untouched, tracked in [12-deliverables-index.md](12-deliverables-index.md)'s open items.
- No automatic progression to 3D-2 or any other slice is authorized by this closure. The next bounded GO is a separate decision.
