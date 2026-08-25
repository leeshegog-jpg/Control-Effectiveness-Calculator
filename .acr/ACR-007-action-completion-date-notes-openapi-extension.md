# ACR-007: Action Domain — OpenAPI Extension for `completion_date` and `notes`

**Raised by:** Claude Code, on chat authorization (Incident-domain queue reconciliation, ACR-drafting GO), 2026-08-23
**Affected document(s):** [10-openapi.yaml](../docs/knowledge-graph/10-openapi.yaml) only. No other Design Baseline v1.1 artefact is proposed to change.

## 1. ACR Identifier

**ACR-007.**

## 2. Title

Action Domain — OpenAPI Extension for `completion_date` and `notes`.

## 3. Status

**Approved (2026-08-25).** Approved per explicit chat decision. `10-openapi.yaml` remains unchanged as of this approval record — the additive extension in §7 is authorized but not yet written; a separate GO is required before `10-openapi.yaml` is edited (§17), and a further separate GO is required before any application-code implementation against it.

## 4. Decision Requiring Change

[30-r1-incident-action-triggers-sync-closure.md](../docs/implementation-blueprint/30-r1-incident-action-triggers-sync-closure.md) and the preceding read-only Action reconciliation confirmed `safety.actions.completion_date` and `.notes` exist in the frozen PostgreSQL schema and are already mapped on the `Action` ORM model (for persistence fidelity), but are absent from the frozen `ActionInput`/`Action` OpenAPI schema — the same class of gap ACR-004/ACR-006 closed for other Incident-domain sub-resources.

## 5. Baseline Affected

- **In scope:** [10-openapi.yaml](../docs/knowledge-graph/10-openapi.yaml) — proposed additive changes only (§7 below).
- **Explicitly not in scope, not touched, not proposed to change:** [03-postgresql-schema.sql](../docs/knowledge-graph/03-postgresql-schema.sql), [02-neo4j-node-relationship-model.md](../docs/knowledge-graph/02-neo4j-node-relationship-model.md), `06`/`07`/`09` knowledge-graph docs, any ontology scheme, any application code. Both columns already exist, unmodified, in the frozen schema (§6).
- **Explicitly excluded from this ACR, tracked as separate governance items:** `safety.action_controls`/`REMEDIATES` exposure — requires its own ACR if pursued.

## 6. Current OpenAPI Representation and V1 Evidence

| Frozen artefact | Schema status | Current OpenAPI status |
|---|---|---|
| `safety.actions.completion_date` (`03-postgresql-schema.sql:570`) | `date`, nullable | **Absent from `ActionInput`/`Action`.** |
| `safety.actions.notes` (`03-postgresql-schema.sql:572`) | `text`, nullable | **Absent from `ActionInput`/`Action`.** |

**V1 evidence, verified directly** (`corrective-actions.html:81,83`): `fCompDate` ("Completion Date," date input) and `fNotes` ("Notes," textarea) are both real V1 fields on the corrective-action-record form, alongside every other `ActionInput`-mapped field (`fSource`, `fSourceRef`, `fDesc`, `fRCC`, `fPri`, `fAssigned`, `fDue`, `fStatus`, `fEffective` — all nine already contracted). These two are the only V1 corrective-action fields with a schema column but no OpenAPI representation.

## 7. Required Extension

Additive-only. No existing path, schema object, or field in `10-openapi.yaml` is proposed to change or be removed.

Add two optional properties to the existing `ActionInput` schema (inherited by `Action` via its `allOf`):

```yaml
completion_date: { type: string, format: date }
notes: { type: string }
```

No new schema object. No new endpoint. `GET/POST /actions`, `PATCH /actions/{id}`, and the Incident-scoped `/incidents/{id}/actions*` endpoints (ACR-006) all reuse `ActionInput`/`Action` automatically — no path-level change required.

## 8. Affected Endpoints

None added or modified. `completion_date`/`notes` become available on every existing endpoint that already accepts/returns `ActionInput`/`Action`: `GET/POST /actions`, `PATCH /actions/{id}`.

## 9. Affected Schemas / DTOs

- **Modified:** `ActionInput` (two new optional properties, inherited by `Action`).
- **Unchanged:** every other schema object, including `Incident`, `IncidentInput`, `Investigation`, `InvestigationInput`, `Evidence`, `EvidenceInput`.

## 10. Relationship Semantics

No relationship implication — both fields are scalar properties on `Action` itself, not FKs or polymorphic pointers. No Neo4j representation is proposed; `Action`'s Neo4j node properties (`02-neo4j-node-relationship-model.md:58`) already list `effectiveness_review` but not `completion_date`/`notes` — whether to add them to the graph node is a separate question, not addressed by this ACR (contract-only scope, §5).

## 11. Compatibility Impact

**Fully additive — no breaking change to any existing consumer of `10-openapi.yaml`.** No existing path is modified, renamed, or removed. No existing schema object's required fields change (both new properties are optional). No existing enum changes.

## 12. Migration Implications

None — `03-postgresql-schema.sql` is unchanged; both columns already exist, unmodified, at their current DDL.

## 13. Traceability

- [22-r1-incident-reconciliation-decision-review.md](../docs/implementation-blueprint/22-r1-incident-reconciliation-decision-review.md) — original identification of the `completion_date`/`notes` gap as requiring its own ACR.
- [29-action-mechanism-reconciliation-correction.md](../docs/implementation-blueprint/29-action-mechanism-reconciliation-correction.md) §4 — re-confirmed the gap during the Action mechanism reconciliation.
- [30-r1-incident-action-triggers-sync-closure.md](../docs/implementation-blueprint/30-r1-incident-action-triggers-sync-closure.md) §6 — recorded as an open item after the Action implementation slice closed, explicitly not claimed by that slice.
- [ACR-006](ACR-006-incident-action-openapi-extension.md) — precedent for the additive-extension pattern this ACR follows.

## 14. Alternatives Considered

- **(a) Do nothing — leave `completion_date`/`notes` unexposed.** Viable indefinitely; Action CRUD functions fully without them (already implemented, PR #33). No V1-parity urgency beyond the two fields themselves.
- **(b) Model `completion_date`/`notes` as part of a broader "close out an Action" workflow endpoint** (e.g. a dedicated `POST /actions/{id}/complete`) rather than plain `ActionInput` fields. Rejected — no evidence (V1 or frozen baseline) supports a distinct completion workflow; V1 treats both as ordinary form fields alongside `status`, edited the same way as any other field. Adding a bespoke endpoint would invent structure the evidence doesn't support.

## 15. Risk of Not Implementing

If this ACR is rejected or left indefinitely pending: Action records remain unable to capture completion date or free-text notes via the API, despite both existing in the frozen schema and both being genuine V1 fields. This is a completeness/data-fidelity gap relative to V1, not a compliance or safety-critical risk.

## 16. Validation Requirements

Not yet applicable — no OpenAPI change has been made under this draft. If approved, `scripts/validate_openapi.py` must confirm 0 dangling `$ref`s and a strictly additive diff before commit, per the ACR-004/005/006 precedent.

## 17. Implementation Boundary

**Nothing implemented by this ACR draft.** Raising this ACR does not authorize:
- Any edit to `10-openapi.yaml`.
- Any application-code implementation (DTO/router/service changes) to expose the new fields.
- Any Postgres schema, Neo4j, or ontology change.

A separate, explicit GO is required before this ACR's proposed `10-openapi.yaml` extension is written, and a further separate GO is required before any application-code implementation against it.

## Outcome Paths

- **Approve** → `10-openapi.yaml` additively extended per §7 — **decision taken 2026-08-25**; the extension itself remains pending a separate GO (§17).
- **Reject** → not taken.
- **Defer** → not taken.

---

## Current State (template field, restated for index consistency)

`safety.actions.completion_date` and `.notes` are fully specified in Design Baseline v1.1's PostgreSQL schema and are both genuine V1 fields, but have no OpenAPI representation — see §6.

## Proposed Change (template field, restated for index consistency)

Additively extend `ActionInput`/`Action` with two optional scalar properties (§7). No new endpoint, no new schema object.

## Impact (template field, restated for index consistency)

Touches `10-openapi.yaml` only (§5). Fully additive, no breaking change (§11). No schema/Neo4j/ontology/code change (§5, §12). `action_controls`/`REMEDIATES` remains a separate, unaddressed governance item (§5).
