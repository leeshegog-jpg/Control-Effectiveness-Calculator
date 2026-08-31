# ACR-008: OpenAPI Contract Completeness — Error-Response References for Implemented Operations

**Raised by:** Claude Code, on chat authorization (ADR-007 contract-defect discovery → "GO — implement ACR-A", ACR-A only), 2026-08-31
**Affected document(s):** [10-openapi.yaml](../docs/knowledge-graph/10-openapi.yaml) only. No other Design Baseline v1.1 artefact is proposed to change.

## 1. ACR Identifier

**ACR-008.**

## 2. Title

OpenAPI Contract Completeness — attach the existing `NotFound` (`404`) and `ValidationError` (`422`) response components to the implemented operations that already return them but do not document them.

## 3. Status

**Approved (2026-08-31) — Incorporated (2026-08-31), pending PR review.** `10-openapi.yaml` additively extended per §7 under a separate, explicit GO (ACR-A only). No application-code, test, CI, authentication, or ruleset change is authorized by this ACR.

## 4. Decision Requiring Change

The ADR-007 D4 report-only contract-test job produced its first DB-backed execution against `main @ 5f0af4c` (GitHub Actions run `33378169698`): `46 failed, 6 passed, 67 skipped`. The read-only contract-defect discovery / reconciliation that followed (register: `adr-007-contract-defect-register.md`, session scratchpad) classified every one of the 46 strict-operation failures against the implementation and the frozen contract. Two of the six systemic root causes are **frozen-contract discrepancies** — the implementation behaviour is defensible and framework-standard, but the frozen OpenAPI does not document it:

- **P1 — undocumented `404`.** 20 `{id}` operations raise an explicit `HTTPException(404, "<X> not found")` for a non-existent resource (correct REST). The frozen spec **already defines** `components.responses.NotFound` and **already references it** on some operations (`GET /assets/{id}:92`, `GET /incidents/{id}/investigation:579`, `POST /incidents/{id}/hazards:609`, …), but omits the reference on 20 implemented operations of the same shape.
- **P2 — undocumented `422`.** 6 operations return FastAPI/Pydantic's standard `422` on a malformed path/query UUID (e.g. `?park_id=`, `null,null` in a path segment). The frozen spec **already defines** `components.responses.ValidationError` and **already references it** on some operations (`POST /assets:84` as `400`, `PATCH /risks/{id}:402` as an inline `422`), but omits it on these 6.

This ACR reconciles those 26 operations. It does **not** address the API-defect root causes (P3 unhandled `IntegrityError` → `500`; P4 unconstrained `status` query param) or the test-methodology findings (P5 `AllowHeaderMismatch`; P6 unknown-query-param) or the known S4 authentication gap (P7) — each is a separate governance item (§5, §13).

## 5. Baseline Affected

- **In scope:** [10-openapi.yaml](../docs/knowledge-graph/10-openapi.yaml) — additive-only response-reference additions on 26 existing operations, plus the MINOR version bump (§7).
- **Explicitly not in scope, not touched, not proposed to change:** every other Design Baseline v1.1 artefact; all application code (`apps/api/**`); `tests/contract/**` and every other test; `.github/workflows/**`; the branch-protection ruleset; the `security` scheme and the S4 authentication gap; the `negative_data` Schemathesis check.
- **Explicitly excluded from this ACR, tracked as separate governance items:**
  - **P3** — unhandled `sqlalchemy.exc.IntegrityError` → `500` on 8 `POST` operations (`assets`, `hazards`, `risks`, `risks/{riskId}/controls`, `performance-standards/{id}/verification-activities`, `verification-activities/{id}/evidence`, `incidents`, `actions`). Requires an API-remediation ACR ("ACR-B" in the discovery register). The undocumented `422` those same operations return on a wrong-typed request-body scalar is deferred with them, not reconciled here.
  - **P4** — `status: str` query param on `GET /ontology/concepts` and `GET /actions` unvalidated → `500` (Postgres enum cast) or silent `200`. Requires an API-remediation ACR ("ACR-C").
  - **P5 / P6** — Schemathesis `AllowHeaderMismatch` (Starlette builds the `405` `Allow` header per-route) and `AcceptedNegativeData` for unknown query params (FastAPI ignores extras by design). Test-configuration decisions.
  - **P7 / S4** — contract declares global `security: [bearerAuth]`; R1 does not enforce. Governed as risk **S4** (`docs/implementation-blueprint/11-implementation-risk-register.md`); authentication enforcement is its own future slice, at which point ADR-007 D2's auth-conformance checks re-enable.

## 6. Current OpenAPI Representation and Behavioural Evidence

Every row below is evidenced by a `schemathesis.openapi.checks.UndefinedStatusCode` failure in job `99444250671` of run `33378169698`. "Current" = response codes documented at `main @ 5f0af4c`.

### P1 — add `'404': { $ref: '#/components/responses/NotFound' }` (20 operations)

| Operation | Current | Observed | Router evidence |
|---|---|---|---|
| `PATCH /assets/{id}` | `200` | `404 {"detail":"Asset not found"}` | `routers/assets.py:87` |
| `PATCH /hazards/{id}` | `200` | `404 {"detail":"Hazard not found"}` | `routers/hazards.py:107` |
| `GET /risks/{id}` | `200` | `404 {"detail":"Risk not found"}` | `routers/risks.py` |
| `PATCH /risks/{id}` | `200, 422` | `404 {"detail":"Risk not found"}` | `routers/risks.py` (existing inline `422` = R4 SFARP gate, unrelated, retained) |
| `GET /controls/{id}` | `200` | `404 {"detail":"Control not found"}` | `routers/controls.py:87` |
| `POST /controls/{id}/gate-test` | `200` | `404 {"detail":"Control not found"}` | `routers/controls.py:100` |
| `POST /controls/{id}/eia-test` | `200` | `404 {"detail":"Control not found"}` | `routers/controls.py:125` |
| `POST /controls/{id}/critical-control-test` | `201, 409` | `404 {"detail":"Control not found"}` | `routers/controls.py:147` |
| `GET /critical-controls/{id}` | `200` | `404 {"detail":"Critical control not found"}` | `routers/critical_controls.py:50` |
| `PATCH /critical-controls/{id}` | `200` | `404 {"detail":"Critical control not found"}` | `routers/critical_controls.py:63` |
| `GET /critical-controls/{id}/performance-standards` | `200` | `404 {"detail":"Critical control not found"}` | `routers/critical_controls.py:86` |
| `POST /critical-controls/{id}/performance-standards` | `201` | `404 {"detail":"Critical control not found"}` | `routers/critical_controls.py:104` |
| `GET /incidents/{id}` | `200` | `404 {"detail":"Incident not found"}` | `routers/incidents.py:142` |
| `PATCH /incidents/{id}` | `200` | `404 {"detail":"Incident not found"}` | `routers/incidents.py:155` |
| `POST /incidents/{id}/investigation` | `201, 409` | `404 {"detail":"Incident not found"}` | `routers/incidents.py:247` |
| `GET /incidents/{id}/hazards` | `200` | `404 {"detail":"Incident not found"}` | `routers/incidents.py` |
| `GET /incidents/{id}/evidence` | `200` | `404 {"detail":"Incident not found"}` | `routers/evidence.py:81` |
| `POST /incidents/{id}/evidence` | `201` | `404 {"detail":"Incident not found"}` | `routers/evidence.py:94` |
| `GET /incidents/{id}/actions` | `200` | `404 {"detail":"Incident not found"}` | `routers/incidents.py:289` |
| `PATCH /actions/{id}` | `200` | `404 {"detail":"Action not found"}` | `routers/actions.py:94` |

### P2 — add `'422': { $ref: '#/components/responses/ValidationError' }` (6 operations)

| Operation | Current | Observed | Evidence |
|---|---|---|---|
| `GET /assets` | `200` | `422` on `?park_id=` (`uuid_parsing`, `loc: ["query","park_id"]`) | `park_id` typed `uuid.UUID` in `routers/assets.py` |
| `PATCH /incidents/{id}/investigation` | `200, 404` | `422` on bad path `incident_id` (`uuid_parsing`) | shared `parameters/id` typed UUID |
| `POST /incidents/{id}/hazards` | `201, 404` | `422` on bad path `incident_id` | same |
| `DELETE /incidents/{id}/hazards/{hazardId}` | `204, 404` | `422` on bad path `hazard_id` | `hazardId` typed `{type: string, format: uuid}` → UUID |
| `POST /incidents/{id}/actions` | `201, 404` | `422` on bad path `incident_id` | shared `parameters/id` |
| `DELETE /incidents/{id}/actions/{actionId}` | `204, 404` | `422` on bad path `action_id` | `actionId` typed UUID |

## 7. Required Change

Additive-only. No existing path, operation, schema object, field, parameter, or response is proposed to change or be removed.

1. **`info.version`** — `0.5.0-draft` → `0.6.0-draft` (MINOR bump; additive, no removed/changed paths or schemas — same convention as ACR-002/003/004/005/006/007, per `02-development-standards.md §2`).
2. **26 operations** each gain **one** response entry, referencing a **pre-existing** `components.responses` object — no new response component, no new schema:
   - 20 × `'404': { $ref: '#/components/responses/NotFound' }`
   - 6 × `'422': { $ref: '#/components/responses/ValidationError' }`

Ten operations written in the single-line `responses: { … }` form were expanded to the multi-line block form to carry the second entry. This is a formatting change only; the pre-existing `'200'`/`'201'`/`'204'` entry is byte-for-byte preserved in every case (verified — §16).

## 8. Affected Endpoints

None added, renamed, or removed. 26 existing operations gain one documented error response each (§6). Path count unchanged at **70**.

## 9. Affected Schemas / DTOs

**None.** Schema count unchanged at **78**; `components.schemas` byte-identical. Both referenced response components (`NotFound`, `ValidationError`) already exist and are unchanged; both resolve to the existing `Error` schema.

## 10. Relationship Semantics

No relationship implication — response documentation only. No Neo4j representation.

## 11. Compatibility Impact

**Fully additive — no breaking change to any existing consumer of `10-openapi.yaml`.** No path modified/renamed/removed. No schema's required fields change. No existing response entry changed or removed — only new `404`/`422` entries added. A generated client regenerated against v0.6.0-draft gains error-branch types it did not previously have; no existing success-path type changes.

## 12. Migration Implications

None — no schema (Postgres or Neo4j) change; `03-postgresql-schema.sql` untouched.

## 13. Traceability

- **ADR-007** (`.adr/ADR-007-contract-test-suite-scope-and-ci-treatment.md`) — D4 report-only CI job, merged as PR #48 (`main @ 056f7d4`); its first DB-backed run is the evidence base for this ACR.
- **Contract-defect discovery register** (`adr-007-contract-defect-register.md`, session scratchpad) — the read-only classification of all 46 strict-operation failures; §2 rows 1, 4, 8, 11, 12, 15–22, 29, 30, 32–41, 44 are the 26 reconciled here ("ACR-A").
- **ACR-004 / ACR-006 / ACR-007** — precedent for the additive-only, contract-only, MINOR-bump extension pattern this ACR follows.
- **Deferred, each its own governance item:** ACR-B (P3 — `IntegrityError` handling), ACR-C (P4 — query-param validation), test-decision-1 (P5), test-decision-2 (P6), S4 (P7).

## 14. Alternatives Considered

- **(a) Do nothing — leave the 26 operations under-documented.** Rejected for this slice: the D4 job is now a live diagnostic, and ~26 of its 46 failures are pure contract-reporting noise that masks the genuine API/test/S4 findings. Removing that noise first gives a clean baseline for the ACR-B/ACR-C decisions, changing one variable at a time.
- **(b) Also reconcile the undocumented `422` on the 8 P3 `POST` operations (wrong-typed request body → `422`) in this ACR.** Rejected — those operations' headline failure is the unhandled `500` (P3); documenting one of their two discrepancies while the other is unresolved would muddy the "one variable at a time" intent. Their `422` is deferred to ACR-B with the `500`.
- **(c) Also add `422` to every `{id}` operation with a typed path param (not just the 6 evidenced).** Rejected — the GO scopes this to "where the current API behaviour has been evidenced". The next D4 run will surface any further per-operation `422` discrepancy on the P1 operations; those become an evidenced follow-up rather than a guess now.
- **(d) Introduce a richer error-response body schema (RFC 7807 / match the actual `{"detail": …}` shape).** Rejected — out of scope; the existing loose `Error` schema (`{code?, message?, details?}`, no `required`, `additionalProperties` default-true) already validates the API's `{"detail": …}` body, which is why the existing `NotFound`-referencing operations pass response-schema conformance. The `Error`-schema-vs-actual-body looseness is noted as a separate observation (§17), not fixed here.

## 15. Risk of Not Implementing

The D4 contract job stays at 46 failures, ~26 of which are contract-documentation gaps rather than behavioural defects. The genuine findings (8 × `500`, S4, test-methodology) stay buried in the noise, and the ACR-B / ACR-C / promotion decisions have to reason about a mixed signal. No safety or compliance risk — this is contract-fidelity only.

## 16. Validation Requirements

**Satisfied.**
- `scripts/validate_openapi.py` → `OK: 70 paths, 78 schemas, 0 dangling $refs.` (paths/schemas unchanged).
- Semantic-additivity check (parse `HEAD` vs working tree, UTF-8): `components` byte-identical; `paths` key set identical; **0 responses removed** on any operation; exactly **26** operations gained a response; every added code ∈ {`404`, `422`}; every pre-existing response code retained in order; only `info.version` changed in `info`.
- `pytest tests/contract/test_contract_classification.py` → **6 passed** (population still 113 = 46 implemented + 67 deferred; wiring unchanged).
- `pytest tests/contract --collect-only` → **119 collected** (113 parametrised + 6 wiring), unchanged.
- Full DB-backed effect: demonstrated by the `contract-tests` job on this ACR's PR — see the PR body for the before/after failure counts.

## 17. Implementation Boundary

**`10-openapi.yaml` extended per §7. Nothing else is authorized.** This incorporation does not authorize any application-code, DTO, router, service, repository, model, test, CI-workflow, authentication, or ruleset change. P3 (`IntegrityError` → `500`) and P4 (`status` query param) remediation each require their own separate, explicit GO.

**Separate observation, not addressed here:** the documented error-response body (`components.schemas.Error` = `{code?, message?, details?}`) does not match the API's actual FastAPI error body (`{"detail": …}`). The loose `Error` schema still validates the actual body (no `required`, `additionalProperties` default-true), so this causes no response-schema-conformance failure and is pre-existing on every operation that already references `NotFound`/`ValidationError`. Whether to tighten `Error` to the real shape is a separate contract decision.

## Outcome Paths

- **Approve** → `10-openapi.yaml` additively extended per §7 — **decision taken 2026-08-31 on chat GO (ACR-A only); incorporated 2026-08-31; PR open, not merged.**
- **Reject** → not taken.
- **Defer** → not taken.

---

## Current State (template field, restated for index consistency)

26 implemented operations return a `404` (20) or `422` (6) that the frozen `10-openapi.yaml` does not document, despite the spec already defining and partially using the `NotFound` and `ValidationError` response components — see §6.

## Proposed Change (template field, restated for index consistency)

Additively reference the existing `NotFound` / `ValidationError` components on those 26 operations; MINOR version bump `0.5.0-draft` → `0.6.0-draft`. No new endpoint, schema, or response component (§7).

## Impact (template field, restated for index consistency)

Touches `10-openapi.yaml` only (§5). Fully additive, no breaking change (§11). No schema/Neo4j/ontology/code/test/CI/ruleset change. P3, P4, P5/P6 and S4 remain separate, unaddressed governance items (§5, §13).
