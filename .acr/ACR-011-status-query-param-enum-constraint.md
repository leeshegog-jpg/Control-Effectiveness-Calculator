# ACR-011: `status` Query-Parameter Enum Constraint (ACR-C / P4)

**Raised by:** Claude Code, on chat authorization ("GO — P4 status enum"), 2026-09-04
**Affected document(s):** application code (`apps/api/app/dto/ontology.py`, `apps/api/app/dto/actions.py`, `apps/api/app/routers/ontology.py`, `apps/api/app/routers/actions.py`) and [10-openapi.yaml](../docs/knowledge-graph/10-openapi.yaml). No other Design Baseline v1.1 artefact changes; `03-postgresql-schema.sql` is unchanged (its `status` columns are already correctly constrained — the gap was the API layer not validating against them before querying).

## 1. ACR Identifier

**ACR-011.**

## 2. Title

`status` Query-Parameter Enum Constraint — replace the unconstrained `str | None` query parameter on `GET /ontology/concepts` and `GET /actions` with a typed enum, so an out-of-range value fails FastAPI validation (422) instead of reaching the database.

## 3. Status

**Approved (2026-09-04) — Incorporated (2026-09-04); PR open, not merged.** Behavioural change (two `GET` operations only); no schema, authentication, or ruleset change.

## 4. Decision Requiring Change

The ADR-007 D4 report-only contract job's DB-backed runs, and the read-only contract-defect discovery register (`adr-007-contract-defect-register.md`, root cause P4), showed the `status` query parameter on two `GET` operations typed as plain `str | None` with no server-side constraint, producing two different failure modes from the same root cause:

- **`GET /ontology/concepts?status=<garbage>`** — `ontology.concepts.status` is a real Postgres `ENUM` type (`ontology.concept_status`: `draft`, `reviewed`, `approved`, `published`, `deprecated` — `models/ontology.py` `concept_status_enum`). An out-of-range value reaches `WHERE status = '<garbage>'` and Postgres raises `InvalidTextRepresentation`, uncaught → **500**.
- **`GET /actions?status=<garbage>`** — `safety.actions.status` is a plain `varchar(20)` with a `CHECK (status IN ('Open','In Progress','Closed'))` constraint (enforced on write, not on `SELECT`). An out-of-range value reaches `WHERE status = '<garbage>'`, matches zero rows, and the endpoint returns **200 with an empty list** — silent-accept, no signal to the caller that the filter value was invalid.

`docs/knowledge-graph/10-openapi.yaml` already documented both parameters as an `enum` (added in ACR-008 Round 3 for `GET /ontology/concepts`, and pre-existing on `GET /actions`) — the implementation simply did not enforce it. This ACR closes that spec/code gap; it is not a new contract decision.

## 5. Baseline Affected

- **Application code (in scope):**
  - **new** `ConceptStatus(StrEnum)` in `apps/api/app/dto/ontology.py` — `draft`, `reviewed`, `approved`, `published`, `deprecated` (mirrors `concept_status_enum`).
  - **new** `ActionStatus(StrEnum)` in `apps/api/app/dto/actions.py` — `Open`, `In Progress`, `Closed` (mirrors the `safety.actions.status` `CHECK` constraint).
  - `apps/api/app/routers/ontology.py` — `get_concepts`'s `status` query parameter retyped `ConceptStatus | None`; converted to `.value` before calling `service.list_concepts`.
  - `apps/api/app/routers/actions.py` — `list_actions`'s `status` query parameter retyped `ActionStatus | None`; converted to `.value` before calling `service.list_actions`.
  - **Explicitly not touched:** `services/ontology/service.py`, `services/actions/service.py`, `repositories/ontology_repository.py`, `repositories/actions_repository.py` — all keep `status: str | None`; the enum boundary is the router only (validate at the edge, same layering discipline as ACR-010's `require_exists()` pre-checks).
- **Contract (in scope):** [10-openapi.yaml](../docs/knowledge-graph/10-openapi.yaml) — add `'422': { $ref: '#/components/responses/ValidationError' }` to `GET /actions` (the `enum` schema was already present, the `422` response was not); `GET /ontology/concepts` already carries both from ACR-008 Round 3 — **no change needed there**. `info.version` `0.10.0-draft` → `0.11.0-draft`.
- **Tests (in scope):** extended `tests/integration/test_ontology_seed.py` (+2: valid-value round trip, invalid-value 422) and `tests/integration/test_actions_crud.py` (+1: invalid-value 422; the valid-value round trip already existed as `test_action_list_filters_by_status`).
- **Explicitly not in scope, not touched:** `ConceptOut.status`, `ActionInput.status`, `ActionOut.status` (all remain plain `str` — this ACR constrains the *query filter*, not the persisted/returned value; broadening to body/response fields is a separate, larger decision about every `status` field in the API, not requested by the P4 finding); `03-postgresql-schema.sql`; ORM models; any other operation's `status` parameter or field; `ACR-008`, `ACR-009`, `ACR-010`.
- **Explicitly excluded, tracked separately:**
  - **P5 / P6** (`AllowHeaderMismatch`, unknown-query-parameter `negative_data`) — test-methodology decisions.
  - **NEW `RejectedPositiveData`×10** — test-methodology decision (create-op positive-phase fixtures).
  - **P7 / S4** (authentication not enforced) — authentication-enforcement slice.
  - **Latent PATCH-FK / `POST /incidents/{id}/hazards`** — ACR-010 fast-follow, unrelated defect class.
  - **D5** (promote contract job to required check) — separate ADR.

## 6. Behaviour: before → after

| | Before | After |
|---|---|---|
| `GET /ontology/concepts?status=<garbage>` | uncaught `InvalidTextRepresentation` (Postgres ENUM) → **500** | **422**, FastAPI/Pydantic enum validation, no query issued |
| `GET /actions?status=<garbage>` | **200**, empty list (silent-accept — CHECK constraint not enforced on read) | **422**, FastAPI/Pydantic enum validation, no query issued |
| `GET /ontology/concepts?status=published` (valid) | 200 | 200 (unchanged) |
| `GET /actions?status=Open` (valid) | 200 | 200 (unchanged) |

## 7. Design

Query-parameter validation only, at the router boundary — mirrors the repo's existing pattern of typed `Query()` parameters (`scheme_id: uuid.UUID | None`, `activity_id: uuid.UUID | None`, etc.) already producing 422 on a malformed value; `status` was the one parameter left as bare `str`. A `StrEnum` (not `str, Enum` — `ruff` `UP042` on this codebase's Python/ruff target) gives FastAPI's OpenAPI generation the same `enum: [...]` array already hand-written in the contract, so the generated schema and the frozen contract stay in lockstep. The enum member is unwrapped to its `.value` (a plain `str`) before crossing into the service/repository layer, so nothing downstream (SQL comparison, DB driver parameter binding) needs to know about the `Enum` type — kept identical to pre-ACR-011 behaviour once a valid value passes validation.

Two independent enums (`ConceptStatus`, `ActionStatus`) rather than one shared status enum — the two columns have disjoint value sets (`draft/reviewed/approved/published/deprecated` vs. `Open/In Progress/Closed`) and disjoint underlying constraint mechanisms (Postgres `ENUM` type vs. `varchar` + `CHECK`); a shared enum would either over-permit one endpoint or under-permit the other.

## 8. Affected Endpoints

| Operation | Query param | Enum | OpenAPI change |
|---|---|---|---|
| `GET /ontology/concepts` | `status` | `ConceptStatus` (draft, reviewed, approved, published, deprecated) | none — `enum` + `422` already documented (ACR-008 R3) |
| `GET /actions` | `status` | `ActionStatus` (Open, In Progress, Closed) | `+422` (enum was already documented) |

## 9. Affected Schemas / DTOs

**None.** No OpenAPI schema object added, removed, or restructured — the `422` addition reuses the existing `ValidationError` response component (same as ACR-008/ACR-010). Schema count 78, path count 70 — unchanged. `Concept` / `Action` response schemas untouched (§5 — their `status` property stays `type: string`, no `enum`, matching the DTOs staying `str`).

## 10. Relationship Semantics

None — query validation only. No Neo4j representation.

## 11. Compatibility Impact

- **Contract:** strictly additive — one `422` response added to `GET /actions`; `GET /ontology/concepts` unchanged (already correct since ACR-008 R3). A conformant client sending a documented enum value is unaffected; a client sending an undocumented value now gets an actionable 422 instead of a 500 (`/ontology/concepts`) or a misleading empty 200 (`/actions`).
- **Behaviour:** no previously-successful request changes outcome — the enum is a superset check only, and the query never executes for a rejected value (no partial side effects to consider, this is a read path).

## 12. Migration Implications

None — no schema change; no data migration.

## 13. Traceability

- **ADR-007 D4** report-only contract job — surfaced P4 (`GET /ontology/concepts` 500, `GET /actions` silent-accept).
- **`adr-007-contract-defect-register.md`** — P4 root-cause classification, systemic (2 ops, 1 cause: unconstrained `status` filter).
- **ACR-008 Round 3** (`main @ 23f14ca`) — already documented `enum` + `422` on `GET /ontology/concepts`'s `status` param; this ACR is the implementation catching up to that contract, not a new contract decision for that operation.
- **ACR-010** (`main @ ec55165`) — precedent for router-boundary validation before the query/write reaches the database; precedent for `.acr/README.md` incorporation-paragraph convention.
- **Deferred, each its own governance item:** P5/P6, NEW `RejectedPositiveData`×10, P7/S4, latent PATCH-FK fast-follow, D5 promotion ADR.

## 14. Alternatives Considered

- **(a) Application-level validation inside the service (`if status not in {...}: raise HTTPException(422)`).** Rejected — FastAPI's typed-`Query()` + `Enum` mechanism already does this declaratively, generates the matching OpenAPI `enum` for free, and matches every other typed query parameter in the codebase (`uuid.UUID`, `int`).
- **(b) A single shared `Status` enum with the union of both value sets.** Rejected — would let `GET /actions?status=published` pass validation and then silently match zero rows again (reintroducing the P4 symptom for values valid for the other operation); the two columns are genuinely disjoint domains.
- **(c) Also constrain `ConceptOut`/`ActionInput`/`ActionOut`'s `status` field to the enum.** Rejected as out of this ACR's scope — the P4 finding is specifically about the query *filter*; the response/body fields are a separate, larger surface (every write path, every other `status`-bearing schema in the contract) that was not raised in the P4 finding and deserves its own governance decision if pursued.
- **(d) Add a Postgres `CHECK`-to-`ENUM` migration for `safety.actions.status`** (matching `ontology.concepts.status`'s stronger DB-level guarantee). Rejected — out of scope for an API-layer ACR; `03-postgresql-schema.sql` is the frozen Design Baseline artefact and any change to it needs its own ACR against the schema, not a side effect of a query-parameter fix.

## 15. Risk of Not Implementing

The contract job keeps 2 permanent findings (1 `500`, 1 silent-accept) that mask other signal in the report-only job's output; `GET /actions?status=` degrades from a filter to a de-facto no-op for any value a caller mistypes, with no error to indicate why the result set came back empty. No safety or compliance risk (read-only endpoints).

## 16. Validation Requirements

**Local (satisfied):**
- `ruff check apps/api/app` → All checks passed; `ruff format --check` → clean (173 files); `mypy apps/api/app` → Success, no issues in 173 files.
- `pytest tests/unit` → 60 passed.
- `pytest tests/contract/test_contract_classification.py` → 6 passed (wiring only, DB-free; population unchanged, 113 = 46 + 67).
- `scripts/validate_openapi.py` → `OK: 70 paths, 78 schemas, 0 dangling $refs`.
- Semantic-additivity (spec, `HEAD` vs tree): `components`/`schemas` byte-identical; **0 responses removed**; exactly 1 operation (`GET /actions`) gained a response (`422`); only `info.version` changed in `info`.

**DB-backed (CI, no local Docker daemon available this session):**
- `pytest tests/integration/test_ontology_seed.py` + `tests/integration/test_actions_crud.py` — the 3 new/extended cases.
- Report-only `contract-tests` job — expect the P4 finding cleared from the `main @ ec55165` baseline (`25 failed / 27 passed / 67 skipped`); actual post-push counts to be confirmed against the CI run and recorded in the PR.

## 17. Implementation Boundary

Two DTO files (new enum only), two router files (query-parameter retyping + `.value` unwrap), `10-openapi.yaml` (`+422` on one operation), two test files. **Nothing else.** No service, repository, ORM, schema, transaction, Neo4j, authentication, or ruleset change. `ACR-008`/`ACR-009`/`ACR-010` untouched. P5/P6, NEW `RejectedPositiveData`, P7/S4, the latent PATCH-FK fast-follow, and D5 each require their own separate GO.

## Outcome Paths

- **Approve** → application + contract change per §5 — **decision 2026-09-04 on chat GO ("GO — P4 status enum"); incorporated 2026-09-04; PR open, not merged.**
- **Reject** → not taken.
- **Defer** → not taken.

---

## Current State (template field, restated for index consistency)

`GET /ontology/concepts?status=` and `GET /actions?status=` accept any string. An out-of-range value produces an uncaught Postgres `InvalidTextRepresentation` → 500 on the former (a real DB `ENUM` column) and a silently-empty 200 on the latter (a `varchar` + `CHECK` column, not enforced on read) — see §4, §6.

## Proposed Change (template field, restated for index consistency)

Retype both `status` query parameters from `str | None` to a `StrEnum | None` (`ConceptStatus`, `ActionStatus`) matching each column's actual constrained value set; unwrap to `.value` at the router boundary before calling the (unchanged) service/repository layer. Add the one missing `422` response (`GET /actions`) to the contract; `info.version` `0.10.0-draft` → `0.11.0-draft`. No schema/DTO(body)/ORM/service/repository change (§7, §9).

## Impact (template field, restated for index consistency)

Two DTO files, two router files, `10-openapi.yaml`, two test files (§5). Contract change fully additive (§11). No schema/Neo4j/ontology/auth/ruleset change. P5/P6, NEW `RejectedPositiveData`, P7/S4, the latent PATCH-FK fast-follow, and D5 remain separate, unaddressed items (§5, §13).
