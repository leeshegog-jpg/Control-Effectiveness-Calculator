# ACR-010: Referential-Integrity Error Handling for the Implemented Write Operations

**Raised by:** Claude Code, on chat authorization ("GO — ACR-010 implementation", following the ACR-B discovery + decision record), 2026-08-31
**Affected document(s):** application code (`apps/api/app/**`) and [10-openapi.yaml](../docs/knowledge-graph/10-openapi.yaml). No other Design Baseline v1.1 artefact is proposed to change; the frozen PostgreSQL schema is **unchanged** (it is already correct — its foreign keys are the constraints this ACR handles gracefully).

## 1. ACR Identifier

**ACR-010.**

## 2. Title

Referential-Integrity Error Handling — turn the uncaught `sqlalchemy.exc.IntegrityError` / HTTP 500 that the 8 implemented POST operations return for a bad client-supplied foreign key into a documented HTTP 404 / 422 with no database detail in the response.

## 3. Status

**Approved (2026-08-31) — Incorporated (2026-08-31); PR open, not merged.** Behavioural change per the locked decision record; no schema, authentication, or ruleset change.

## 4. Decision Requiring Change

The ADR-007 D4 report-only contract job's DB-backed runs showed 8 implemented POST operations answering a foreign-key violation with an **uncaught `IntegrityError` → HTTP 500**. The read-only ACR-B discovery (`acr-b-p3-reconciliation-register.md`) and the accepted decision record (`acr-b-implementation-decision-record.md`) established:

- **one systemic cause** — no layer catches or pre-empts `IntegrityError`; no global handler; the repo already applies the correct pattern (router pre-existence check → `HTTPException`, e.g. `POST /incidents/{id}/investigation`) but not to these 8;
- **the fix** — path-parameter parents pre-checked in the router → **404**; body foreign keys pre-checked in the service → typed `ReferentialIntegrityError` → **422** at the router; a sanitised global `IntegrityError` handler (**409**) as defence-in-depth;
- **the security finding** — client-facing leakage is limited to a bare 500 (the app runs `debug=False`), but the server log discloses the INSERT, bound parameters, and the psycopg `DETAIL` on routine client-error traffic (CWE-209). **Medium**.

## 5. Baseline Affected

- **Application code (in scope):**
  - **new** `apps/api/app/services/referential.py` — `ReferentialIntegrityError` + `require_exists()`.
  - `apps/api/app/main.py` — global `IntegrityError` exception handler (409, sanitised).
  - routers `assets`, `hazards`, `risks`, `controls`, `verification`, `evidence`, `incidents`, `actions` — `try/except ReferentialIntegrityError → HTTPException(422)` on the create handlers; path-parent `HTTPException(404)` guards on the 3 nested-POST operations.
  - services `assets`, `hazards`, `risks`, `controls`, `verification`, `evidence`, `incidents`, `actions` — `require_exists(...)` calls in each `create_*` before the ORM object is built.
- **Contract (in scope):** [10-openapi.yaml](../docs/knowledge-graph/10-openapi.yaml) — add the `404` / `422` responses ACR-010's behaviour produces (§8); `info.version` `0.9.0-draft` → `0.10.0-draft`.
- **Tests (in scope):** `tests/integration/test_referential_integrity.py` (new), `tests/unit/test_referential_integrity_handler.py` (new).
- **Explicitly not in scope, not touched:** `03-postgresql-schema.sql` and every other Design Baseline artefact; ORM models; Pydantic DTOs; `db.commit()` / `db.flush()` placement and transaction boundaries; Neo4j sync; the `security` scheme / S4; the branch-protection ruleset; `tests/contract/**` and the report-only Schemathesis configuration; `ACR-008`, `ACR-009`.
- **Explicitly excluded, tracked separately:**
  - **P4** (`status` query param → 500 / silent accept) — ACR-C.
  - **P5 / P6** (`AllowHeaderMismatch`, unknown-query-parameter `negative_data`) — test-methodology decisions.
  - **P7 / S4** (authentication not enforced) — authentication-enforcement slice.
  - **`PATCH` FK-setting paths** (`update_asset`, `update_hazard`, `update_incident`, `update_action`) and **`POST /incidents/{id}/hazards`** — same defect class, not in the P3 8-POST set, **not** remediated here (the GO's hard boundary). Latent-risk inventory item; the `require_exists` helper would cover them in a fast-follow.
  - **Non-FK constraints** (`CHECK`, `UNIQUE` other than the already-handled `investigations.incident_id`, `NOT NULL` on non-FK columns) — the global 409 handler incidentally backstops them against leakage; their correct status codes are not analysed here.
  - **`POST /assets`'s existing documented `400`** — an unreachable R0 contract slot; left as-is (not removed, not re-pointed).

## 6. Behaviour: before → after

| | Before | After |
|---|---|---|
| Body FK UUID names no row | uncaught `IntegrityError` → **500**; log leaks INSERT + params + `DETAIL` | **422** `{"detail": "<field> references a <entity> that does not exist"}`; pre-checked in the service, no INSERT attempted |
| URL-path parent named in the route does not exist | **500** (same) | **404** `{"detail": "<Parent> not found"}`; pre-checked in the router (mirrors `POST /incidents/{id}/investigation`) |
| Any constraint violation that slips past the pre-checks | **500** with SQL/`DETAIL` | global handler → **409** `{"detail": "The request could not be completed due to a data constraint."}` — no SQL, no `DETAIL`, no constraint name, no parameters, no traceback |
| Valid references | 201 | 201 (unchanged; the pre-check is one indexed PK `SELECT` per supplied FK) |

## 7. Design — layered, pre-check first (locked decisions A–E)

- **A** — body FK missing → **422** (semantically invalid body; mirrors `SfarpJustificationError → 422`). Not `400`.
- **B** — `POST /risks` `hazard_id` (required, NOT NULL FK) → **422** (a body value, not a URL resource).
- **C** — (1) router pre-existence check on path parents → `HTTPException(404)`; (2) service `require_exists()` per body FK → `ReferentialIntegrityError` → router `HTTPException(422)`; (3) global `@app.exception_handler(IntegrityError)` in `main.py` → sanitised **409**, defence-in-depth only; (4) no constraint-name parsing on the business path; (5) pre-checks run before `flush()`, so the session is never left in a failed state — `get_db()`'s `close()` already rolls back the unforeseen path; **no `get_db` change** (implementation confirmation #2).
- **D** — the OpenAPI response additions are part of ACR-010, limited to ACR-010's behaviour.
- **E** — reuse `#/components/responses/ValidationError` (422) and `#/components/responses/NotFound` (404); the runtime body is `{"detail": "<message>"}`, which the loose `Error` schema already validates. **No new error model.**

`ReferentialIntegrityError.__init__(field, entity)` produces `f"{field} references a {entity} that does not exist"` — names the field, never SQL (implementation confirmation #3). `require_exists(db, target, id_, *, field, entity)`: no-op when `id_` is `None`; `db.get(model, id_)` for ORM-mapped targets; a parameterised `SELECT 1 FROM <schema.table>` for the two frozen-schema tables not yet ORM-mapped (`safety.documents`, `safety.device_boundaries`) — the table name is always a code constant, never client input. Global handler status = **409** (implementation confirmation #1). `services/critical_controls/service.py` is **unchanged** — its `create_performance_standard` carries no client body FK, and `create_verification_activity` lives in `services/verification` (implementation confirmation #5).

## 8. Affected Endpoints / Foreign Keys

25 client-supplied foreign-key inputs across the 8 operations: **3 path** (→ 404) + **22 body** (→ 422). `actions.source_id` is a polymorphic `uuid` with no `REFERENCES` — not validated.

| Operation | Path FK → 404 | Body FKs → 422 | OpenAPI adds |
|---|---|---|---|
| `POST /assets` | — | `park_id`, `asset_type.concept_id` | `422` |
| `POST /hazards` | — | `asset_id`, `category`, `energy_source`, `owner_person_id`, `device_boundary_id` | `422` |
| `POST /risks` | — | `hazard_id` | `422` |
| `POST /risks/{riskId}/controls` | `riskId` → risks | `hierarchy.concept_id`, `owner_person_id` | `404`, `422` |
| `POST /performance-standards/{id}/verification-activities` | `standard_id` → performance_standards | `method.concept_id`, `performed_by_person_id` | `404`, `422` |
| `POST /verification-activities/{id}/evidence` | `activity_id` → verification_activities | `type.concept_id`, `source_document_id`, `uploaded_by_person_id` | `404`, `422` |
| `POST /incidents` | — | `incident_type.concept_id`, `asset_id`, `reporter_person_id` | `422` |
| `POST /actions` | — | `source_type`, `root_cause_category`, `assigned_to_person_id` | `422` |

`POST /incidents/{id}/evidence` shares the `create_evidence` service function, so it also gains the `try/except ReferentialIntegrityError` for correctness; its contract already documents `404` and `422` (ACR-008 Round 2), so **no contract change** is needed there.

## 9. Affected Schemas / DTOs

**None.** No OpenAPI schema object, no Pydantic DTO, no ORM model changed. Schema count 78, path count 70 — unchanged.

## 10. Relationship Semantics

None — error handling only. No Neo4j representation.

## 11. Compatibility Impact

- **Contract:** strictly additive — `404` / `422` added to 8 operations, no response removed or changed, `POST /assets`'s `400` untouched. A conformant client is unaffected; a client that was (incorrectly) treating the 500 as retryable now gets an actionable 4xx.
- **Behaviour:** a request that previously received a 500 for a bad reference now receives 404 or 422. No previously-successful request changes outcome (the pre-check only rejects references that would have failed at the database anyway).

## 12. Migration Implications

None — no schema change.

## 13. Traceability

- **ADR-007 D4** report-only contract job — surfaced the 8 `IntegrityError` → 500 cases (`ForeignKeyViolation`, runs `33387238415`, `33494743190`).
- **`acr-b-p3-reconciliation-register.md`** — discovery: one systemic cause, per-operation FK evidence, security assessment.
- **`acr-b-implementation-decision-record.md`** — locked decisions A–E, the 25-FK audit, the exception architecture, the file list, the six implementation confirmations.
- **Precedent reused:** `POST /incidents/{id}/investigation` / `POST /incidents/{id}/evidence` router pre-check → 404; `SfarpJustificationError` / `ControlNotClassifiedError` typed-exception → `HTTPException` mapping.
- **Deferred, each its own governance item:** ACR-C (P4), test-decisions (P5/P6), S4 (authentication), a PATCH-FK / `POST /incidents/{id}/hazards` fast-follow.

## 14. Alternatives Considered

- **(a) Global `IntegrityError` handler as the only mechanism.** Rejected — cannot choose 404 vs 422 vs 409 without brittle `constraint_name` parsing, cannot produce a per-field body, breaks the repo's explicit-pre-check idiom. Kept only as the sanitised backstop.
- **(b) Catch `IntegrityError` inside the service and map it.** Rejected — after the failed `flush()` the session is in a failed state and `get_db()` does not `rollback()`; continuing to use it in-request is unsafe. Pre-checking before `flush()` avoids the failed state entirely.
- **(c) `400` for the body-FK case (matching `POST /assets`'s documented `400`).** Rejected per decision A — `422` matches the repo's semantic-validation precedent; `POST /assets`'s `400` is an unreachable R0 slot, not a requirement.
- **(d) Add `NOT NULL` + tighten the schema so bad references can't be submitted.** Rejected — these are genuinely optional FKs; the schema is correct, the handling was missing.

## 15. Risk of Not Implementing

The contract job keeps 8 permanent `500`s that mask other findings; the server log keeps disclosing schema + submitted payloads on routine client-error traffic; a caller can trivially generate unbounded `500`s with random UUIDs. No safety or compliance risk.

## 16. Validation Requirements

**Satisfied.**
- `ruff check apps/api/app` → All checks passed; `ruff format --check` → clean; `mypy apps/api/app` → Success, no issues in 173 files.
- `pytest tests/unit` → passed (includes the new global-handler / message / no-op tests).
- `pytest tests/contract/test_contract_classification.py` → 6 passed; `--collect-only` → 119 (population unchanged: 113 = 46 + 67).
- `scripts/validate_openapi.py` → `OK: 70 paths, 78 schemas, 0 dangling $refs`.
- Semantic-additivity (spec, `HEAD` vs tree): `components` / `schemas` byte-identical; **0 responses removed**; exactly 8 operations gained a response; every added code ∈ {`404`, `422`}; only `info.version` changed in `info`.
- DB-backed: `pytest tests/integration/test_referential_integrity.py` + the report-only `contract-tests` job on the ACR-010 PR — expect the 8 P3 `ForeignKeyViolation`/`UndefinedStatusCode` `500`s cleared; reconciled against the `f716294` baseline (`28 failed / 24 passed / 67 skipped`) in the PR.

## 17. Implementation Boundary

Application code + `10-openapi.yaml` + the two new test files per §5. **Nothing else.** No schema, ORM, DTO, transaction-architecture, Neo4j, authentication, or ruleset change. `ACR-008` / `ACR-009` untouched. P4/P5/P6/S4, the PATCH-FK paths, and `POST /incidents/{id}/hazards` each require their own separate GO.

## Outcome Paths

- **Approve** → application + contract change per §5 — **decision 2026-08-31 on chat GO ("GO — ACR-010 implementation"); incorporated 2026-08-31; PR open, not merged.**
- **Reject** → not taken.
- **Defer** → not taken.

---

## Current State (template field, restated for index consistency)

8 implemented POST operations answer a client-supplied foreign key that references no existing row with an uncaught `sqlalchemy.exc.IntegrityError` → HTTP 500 that leaks the INSERT, bound parameters, and the psycopg `DETAIL` to the server log — see §4, §6.

## Proposed Change (template field, restated for index consistency)

Pre-check path-parent FKs in the router (→ 404) and body FKs in the service (→ 422 via `ReferentialIntegrityError`); add a sanitised global `IntegrityError` handler (409); document the `404` / `422` responses on the 8 operations; `info.version` `0.9.0-draft` → `0.10.0-draft`. No schema / DTO / ORM / transaction change (§7, §9).

## Impact (template field, restated for index consistency)

Application code + `10-openapi.yaml` + two new test files (§5). Contract change fully additive (§11). No schema/Neo4j/ontology/auth/ruleset change. P4/P5/P6/S4, the PATCH-FK paths, and `POST /incidents/{id}/hazards` remain separate, unaddressed items (§5, §13).
