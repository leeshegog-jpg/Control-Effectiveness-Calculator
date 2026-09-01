# ACR-009: OpenAPI Schema Nullability — Optional String Fields on the Implemented Surface

**Raised by:** Claude Code, on chat authorization ("GO — ACR-009", following the schema-nullability discovery/reconciliation GO), 2026-08-31
**Affected document(s):** [10-openapi.yaml](../docs/knowledge-graph/10-openapi.yaml) only. No other Design Baseline v1.1 artefact is proposed to change.

## 1. ACR Identifier

**ACR-009.**

## 2. Title

OpenAPI Schema Nullability — declare the nullability the implementation already exhibits on 30 optional string fields across the implemented 46-operation response surface.

## 3. Status

**Approved (2026-08-31) — Incorporated (2026-08-31); PR open, not merged.** `10-openapi.yaml` additively extended per §7 under a separate, explicit GO. No application-code, ORM, DTO, test, CI, authentication, or ruleset change is authorized by this ACR.

## 4. Decision Requiring Change

ACR-008 Round 3 (PR #51, `main @ 23f14ca`) cleared the last P1/P2 status-code discrepancy on `GET /ontology/concepts` and, by doing so, unmasked a `Schemathesis` `JsonSchemaError` on that operation's `200` body: `null is not of type "string"` at `ConceptInput/properties/definition` (run `33486221269`). `ontology.concepts.definition` is `text` (nullable) in the frozen schema, `Mapped[str | None]` in the ORM, and `str | None = None` in `ConceptOut`; only the frozen OpenAPI declared it `type: string` with no nullability.

The read-only schema-nullability discovery that followed (register: `schema-nullability-register.md`, session scratchpad) established this is **one systemic frozen-contract discrepancy**, not a `definition`-specific one:

```
DB column (nullable) → ORM (Mapped[str | None]) → DTO *Out (str | None = None) → OpenAPI (type: string)   ← sole outlier
```

**30 optional string fields** across 12 schemas (+ `ConceptRef`, nested in 7 of them) are declared bare `type: string` in the contract while the persisted column is nullable and the API returns `null`. The contract author applied `nullable: true` to optional **UUID/date** fields (`Concept.parent_concept_id`, `Hazard.asset_id`, `Hazard.device_boundary_id`, `Risk.hazard_id` via ACR-004, …) but uniformly missed optional **strings**. Only `Concept.definition` is `Schemathesis`-evidenced so far; the other 29 are the same deterministic class, latent behind earlier check failures until Rounds 1–3 cleared those.

This ACR corrects the contract to reflect the already-established data/API nullability. **It changes no application behaviour.**

## 5. Baseline Affected

- **In scope:** [10-openapi.yaml](../docs/knowledge-graph/10-openapi.yaml) — `nullable: true` added to 30 existing optional string properties (§7), plus the MINOR version bump.
- **Explicitly not in scope, not touched:** every other Design Baseline v1.1 artefact; `03-postgresql-schema.sql` (already correct — the source of truth for the nullability being documented); all application code, ORM models, and Pydantic DTOs (already correct); `tests/contract/**` and every other test; `.github/workflows/**`; the branch-protection ruleset; `ACR-008` and its Rounds 1–3.
- **Explicitly excluded, tracked separately:**
  - **The 19 "OK" fields** the discovery register §2b verified as correctly non-nullable (`NOT NULL` / `NOT NULL DEFAULT` columns, DTO `*Out: str`) — e.g. `Asset.name`, `Incident.status`, `Concept.pref_label`. Their bare `type: string` is accurate; **not changed**.
  - **The `TO BE CONFIRMED` status** of `Investigation.method` and `Asset.iso55000_class` (standing open items in the frozen DDL). This ACR documents their *nullability* only; it does not resolve what those fields ultimately are.
  - **The `ConceptRef.pref_label` resolver.** `_concept_ref` (`apps/api/app/routers/actions.py:26`, and the equivalents) returns `pref_label=None` when the referenced concept row is absent. This ACR declares the field nullable to match that behaviour; whether the resolver *should* always produce a non-null label is a separate API decision, not taken here.
  - **P3 / P4 / P5 / P6 / S4** — untouched; each its own governance item.

## 6. Current Representation and Evidence

All 30 fields: DB column carries no `NOT NULL`; ORM types it `Mapped[str | None]` ("Column shapes mirror [`03-postgresql-schema.sql`] exactly" — model docstring); DTO `*Out` returns `str | None = None`; OpenAPI declares `type: string` (no nullability). Full per-field table (DB column + DDL + DTO + evidence) in `schema-nullability-register.md` §2a.

| Schema (Input; response inherits via `allOf`) | Fields gaining `nullable: true` |
|---|---|
| `ConceptRef` | `pref_label` (readOnly; nested in `Asset.asset_type`, `Hazard.category`/`energy_source`, `Control.hierarchy`, `VerificationActivity.method`, `Evidence.type`, `Action.source_type`/`root_cause_category`) |
| `AssetInput` | `iso55000_class` |
| `HazardInput` | `exposure_pathway`, `possible_consequence` |
| `RiskInput` | `cause`, `sfarp_justification`, `serious_risk_justification` |
| `Risk` (response-only, derived) | `inherent_rating`, `current_rating` |
| `ControlInput` | `effectiveness_rating` |
| `Control` (response-only, derived) | `classification` |
| `PerformanceStandardInput` | `measurable_criteria` |
| `VerificationActivityInput` | `frequency`, `result` |
| `EvidenceInput` | `linked_entity_type` |
| `IncidentInput` | `vrtp_severity`, `location`, `injuries`, `witnesses`, `immediate_actions`, `immediate_cause`, `root_cause` |
| `InvestigationInput` | `method`, `findings`, `contributing_factors` |
| `ActionInput` | `priority`, `notes` |
| `OntologyScheme` | `description` |
| `ConceptInput` | `definition` (`JsonSchemaError`, run `33486221269`), `source_ref` |

Total: **30 fields**, 15 schema objects edited (`*Input` / standalone), response schemas inherit through their existing `allOf`.

## 7. Required Change

Additive-only. No property added, removed, renamed, or retyped; no `enum` changed; no `required` list changed; no endpoint, path, or component-structure change.

1. **`info.version`** — `0.8.0-draft` → `0.9.0-draft` (MINOR; additive, same convention as ACR-002..008).
2. **30 properties** each gain the key `nullable: true`. Six are also `enum` fields (`inherent_rating`, `current_rating`, `classification`, `frequency`, `vrtp_severity`, `priority`) — the `enum` value list is **unchanged**; `nullable: true` is added alongside it.

### Nullability syntax — `nullable: true` (decision, with the alternative recorded)

The spec is `openapi: 3.1.0`, where JSON Schema 2020-12 removes the `nullable` keyword; the strictly-correct 3.1 form is `type: ["string", "null"]`. **This ACR uses `nullable: true`** because:

- It is the **established convention in this file** — `10-openapi.yaml` already carries `nullable: true` on 5 properties (`ConceptRef.concept_id`, `HazardInput.asset_id`, `HazardInput.device_boundary_id`, `ConceptInput.parent_concept_id`, `RiskInput` via ACR-004). Introducing a second nullability convention for the string fields would leave the file internally inconsistent.
- It is **empirically honoured by the toolchain**: `Schemathesis` run `33446452156` generated and validated `null` values for `parent_concept_id` (seed roots have no parent) without raising `JsonSchemaError` — i.e. `nullable: true` is respected in this 3.1 document.
- `scripts/validate_openapi.py` accepts it (structural + `$ref` check).
- Migrating the whole file to the strict 3.1 form (`type: ["string","null"]` everywhere, including the 5 existing uses) is a **larger, separate spec-consistency decision** outside this ACR's "30 fields, structure preserved" boundary. It is recorded here as a candidate future item.

**The CI `contract-tests` run on the ACR-009 PR is the confirmation**: if `Concept.definition`'s `JsonSchemaError` clears, `nullable: true` is validated end-to-end for strings; if it does not, the ACR switches to `type: ["string","null"]` before merge.

## 8. Affected Endpoints

None added, renamed, or removed. Every implemented operation that returns one of the 12 affected schemas now documents that its optional string fields may be `null` — matching what the API already returns. Path count unchanged at **70**.

## 9. Affected Schemas / DTOs

- **OpenAPI:** 15 schema objects edited (`ConceptRef`, `AssetInput`, `HazardInput`, `Risk`, `RiskInput`, `Control`, `ControlInput`, `PerformanceStandardInput`, `VerificationActivityInput`, `EvidenceInput`, `IncidentInput`, `InvestigationInput`, `ActionInput`, `OntologyScheme`, `ConceptInput`) — one key added per affected property, nothing else. Schema **count** unchanged at 78.
- **Pydantic DTOs / ORM models:** **unchanged** — already `str | None`. This ACR brings the contract into line with them, not the reverse.

## 10. Relationship Semantics

None — property-level nullability documentation only.

## 11. Compatibility Impact

**Fully additive — no breaking change.** No path/schema/field removed or retyped; no `required` field becomes optional or vice-versa; no `enum` changes. A generated client regenerated against `v0.9.0-draft` gains `| null` on 30 optional string fields it previously (incorrectly) modelled as always-present strings — this makes the client match server reality; it cannot break a conformant existing consumer, which already had to tolerate absent/empty values on optional fields.

## 12. Migration Implications

None — no schema (Postgres or Neo4j) change. `03-postgresql-schema.sql` is unchanged and was already correct.

## 13. Traceability

- **ACR-008 Round 3** (PR #51, `main @ 23f14ca`) — the `JsonSchemaError` that triggered this.
- **`schema-nullability-register.md`** (session scratchpad) — the read-only discovery: 30-field inventory, 19 verified non-defects, one systemic root cause, five `TO BE CONFIRMED` points.
- **ACR-004..008** — precedent for the additive, contract-only, MINOR-bump pattern; ACR-004 is also the origin of the existing `nullable: true` uses this ACR follows.
- **Deferred, each its own governance item:** ACR-B (P3), ACR-C (P4), test-decisions (P5/P6), S4 (authentication), and a possible spec-wide OpenAPI-3.1 `nullable` → `type: [_, "null"]` migration.

## 14. Alternatives Considered

- **(a) Fix only `Concept.definition` (the one evidenced field).** Rejected — the discovery established a single systemic cause; a one-field fix guarantees a Round-4, Round-5, … as each remaining field surfaces in CI. Fixing the class in one pass is the point of running the discovery first.
- **(b) Use `type: ["string", "null"]` (strict 3.1).** Not chosen for this ACR — see §7. It would leave the file with two nullability conventions unless the 5 existing `nullable: true` uses were also migrated, which exceeds this ACR's boundary. Recorded as a candidate future spec-wide item.
- **(c) Tighten the implementation instead (make the fields non-null: `NOT NULL` + backfill, or non-null DTOs).** Rejected — these are genuinely optional fields (free-text notes, derived ratings not yet computed, TBC fields); the frozen DDL deliberately makes them nullable. The contract is wrong, not the data.
- **(d) Change the `ConceptRef` resolver so `pref_label` is never null.** Out of scope — an API behaviour change; §5 records it as a separate decision. ACR-009 documents current behaviour.

## 15. Risk of Not Implementing

The `contract-tests` job accumulates a `JsonSchemaError` per affected field as seed/test data grows to exercise each `null`, each masking the next and muddying the P3/P4/P5 signal. The contract continues to misrepresent 30 fields of the implemented surface as non-nullable. No safety or compliance risk — contract fidelity only.

## 16. Validation Requirements

**Satisfied.**
- `scripts/validate_openapi.py` → `OK: 70 paths, 78 schemas, 0 dangling $refs.` (unchanged counts).
- Semantic-additivity check (parse `HEAD` vs working tree, UTF-8): `paths` byte-identical; `title` / `description` identical; non-schema components (`securitySchemes`, `parameters`, `responses`) identical; schema **keyset** identical; the **only** per-schema diff is **`nullable: true` added to a `type: string` property that lacked it** — **30** such additions, **0** unexpected diffs (no property/enum/required/structure change).
- Raw diff: `31` insertions / `31` deletions = `info.version` + 30 single-line property redefinitions (each `- old` line re-appears verbatim with `, nullable: true` appended).
- `pytest tests/contract/test_contract_classification.py` → **6 passed** (population still 113 = 46 implemented + 67 deferred).
- `pytest tests/contract --collect-only` → **119 collected**, unchanged.
- DB-backed effect: the `contract-tests` job on this ACR's PR — expect `Concept.definition`'s `JsonSchemaError` to clear; `GET /ontology/concepts` stays failing on its unrelated P4/P5/P6/P7 findings.

## 17. Implementation Boundary

**`10-openapi.yaml` extended per §7. Nothing else is authorized.** No application-code, ORM, DTO, test, CI-workflow, authentication, or ruleset change. `ACR-008` is not modified. P3 (`IntegrityError` → `500`) and P4 (`status` query param) remediation each require their own separate GO. The `TO BE CONFIRMED` status of `Investigation.method` / `Asset.iso55000_class` and the `ConceptRef.pref_label` resolver question are unaffected by this incorporation.

## Outcome Paths

- **Approve** → `10-openapi.yaml` additively extended per §7 — **decision 2026-08-31 on chat GO ("GO — ACR-009"); incorporated 2026-08-31; PR open, not merged.**
- **Reject** → not taken.
- **Defer** → not taken.

---

## Current State (template field, restated for index consistency)

30 optional string fields across the implemented 46-operation surface are declared `type: string` (no nullability) in `10-openapi.yaml`, while the DB column is nullable, the ORM is `Mapped[str | None]`, and the DTO `*Out` is `str | None` — a systemic contract-vs-implementation gap, one instance of which (`Concept.definition`) is Schemathesis-evidenced.

## Proposed Change (template field, restated for index consistency)

Add `nullable: true` to those 30 properties; MINOR version bump `0.8.0-draft` → `0.9.0-draft`. No property/enum/structure change; no application/ORM/DTO change (§7, §9).

## Impact (template field, restated for index consistency)

Touches `10-openapi.yaml` only (§5). Fully additive, no breaking change (§11). No schema/Neo4j/ontology/code/test/CI/ruleset change. The 19 verified non-nullable fields, the `TO BE CONFIRMED` fields' status, the `ConceptRef` resolver, and P3/P4/P5/P6/S4 all remain separate, unaddressed items (§5, §13).
