# ACR-004: Incident Domain — OpenAPI Extension for Investigation, `incident_hazards` (`REVEALS`), and Incident-Scoped Evidence

**Raised by:** Claude Code, on chat authorization (R1 Milestone 3B, D4 ACR drafting GO), 2026-08-09
**Affected document(s):** [10-openapi.yaml](../docs/knowledge-graph/10-openapi.yaml) only. No other Design Baseline v1.1 artefact is proposed to change.

## 1. ACR Identifier

**ACR-004.**

## 2. Title

Incident Domain — OpenAPI Extension for Investigation, `incident_hazards` (`REVEALS`), and Incident-Scoped Evidence.

## 3. Status

**Pending Approval.** Not approved, not rejected, not deferred by this document. Raising this ACR is not implementation authorization for anything it describes.

## 4. Decision Requiring Change

[19-r1-milestone-3b-incident-decision-register.md](../docs/implementation-blueprint/19-r1-milestone-3b-incident-decision-register.md) **D4**: `safety.investigations`, `safety.incident_hazards`, and incident-scoped `Evidence` all exist in the frozen PostgreSQL schema and Neo4j relationship model but have **zero representation in the frozen OpenAPI contract**. D4 was routed to ACR at 3A Review (2026-08-08) and confirmed at 3B (2026-08-09): `10-openapi.yaml` is a named Design Baseline v1.1 artefact, and additive-only, low-risk changes are not exempt from the ACR process ([02-development-standards.md](../docs/implementation-blueprint/02-development-standards.md) §7).

## 5. Baseline Affected

- **In scope:** [10-openapi.yaml](../docs/knowledge-graph/10-openapi.yaml) — proposed additive changes only (§7 below).
- **Explicitly not in scope, not touched, not proposed to change:** [03-postgresql-schema.sql](../docs/knowledge-graph/03-postgresql-schema.sql), [02-neo4j-node-relationship-model.md](../docs/knowledge-graph/02-neo4j-node-relationship-model.md), `06`/`07`/`09` knowledge-graph docs, any ontology scheme, any application code. Every table, column, and relationship this ACR's proposed extension would expose **already exists**, unmodified, in the frozen schema and graph model (§6).

## 6. Current OpenAPI Representation

Exhaustively confirmed absent at [18-r1-milestone-3a-incident-discovery-reconciliation.md](../docs/implementation-blueprint/18-r1-milestone-3a-incident-discovery-reconciliation.md) §4, §8:

| Frozen artefact | Schema/graph status | Current OpenAPI status |
|---|---|---|
| `safety.investigations` (`03:548-558`), `INVESTIGATED_AS` (`02:111`) | Fully specified — `incident_id UNIQUE`, `method`/`findings`/`contributing_factors` columns | **No `Investigation` schema object. No endpoint of any form.** |
| `safety.incident_hazards` (`03:542-546`), `REVEALS` (`02:110`) | Fully specified — composite PK join table | **No endpoint.** |
| Incident-scoped `safety.evidence` (`03:272-281`, `linked_entity_type` comment explicitly names `'incident'`) | Fully specified — polymorphic, generic `Evidence`/`EvidenceInput` schema already exists (`10:1055-1061` area) | **No `/incidents/{id}/evidence` endpoint.** Only `/verification-activities/{id}/evidence` (`10:502`) and `/competencies/{id}/evidence` (`10:822`) exist as concrete nested-evidence endpoints. |

## 7. Required Extension

Additive-only. No existing path, schema object, or field in `10-openapi.yaml` is proposed to change or be removed.

1. **New schema object `Investigation`** (analogous in form to existing 1:1 extension objects, e.g. `CriticalControl`'s relationship to `Control`) — fields: `id`, `incident_id` (readOnly, implied by nesting), `method`, `findings`, `contributing_factors`, `created_at`, `updated_at`. `InvestigationInput` — `method`, `findings`, `contributing_factors` (all optional, matching the nullable/free-text schema columns).
2. **No new schema object for `incident_hazards`** — proposed to reuse the existing generic `ConceptRef`/id-list pattern already used elsewhere (e.g. `hazard_ids` array on request, `Hazard` refs on response) rather than invent a new join-record schema, consistent with how the frozen contract treats other pure link tables. This is a **design option flagged for approval, not a foregone conclusion** — see §14 Alternatives.
3. **No new schema object for incident-scoped Evidence** — reuses the existing generic `Evidence`/`EvidenceInput` schema unchanged, mirroring the two existing nested-evidence endpoints exactly.

## 8. Affected Endpoints (proposed, not yet added)

| Endpoint | Method(s) | Cardinality basis | Precedent pattern followed |
|---|---|---|---|
| `/incidents/{id}/investigation` | `GET`, `POST` (create-if-absent), `PATCH` | 1:1, per `INVESTIGATED_AS` and `investigations.incident_id UNIQUE` (ADR-003 §3) | Singular resource path — distinct from every other nested endpoint in the contract, which are all 1:N/N:N collections; this is deliberate, matching the confirmed 1:1 cardinality, not a copy-paste of the 1:N pattern |
| `/incidents/{id}/hazards` | `GET`, `POST`, `DELETE` (or `POST`/`DELETE` on `/incidents/{id}/hazards/{hazardId}`) | N:N, per `REVEALS` | No exact N:N precedent exists elsewhere in the frozen contract (§14) — modeled on the nearest analog, `/risks/{riskId}/controls` (`10:400`), adapted for true many-to-many |
| `/incidents/{id}/evidence` | `GET`, `POST` | Polymorphic, per `linked_entity_type = 'incident'` | Direct structural copy of `/verification-activities/{id}/evidence` (`10:502`) and `/competencies/{id}/evidence` (`10:822`) |

No changes proposed to `/incidents`, `/incidents/{id}`, `/incidents/{id}/run-investigation-pipeline`, `/actions`, `/actions/{id}`, or any other existing path.

## 9. Affected Schemas / DTOs

- **New:** `Investigation`, `InvestigationInput`.
- **Reused unchanged:** `Evidence`, `EvidenceInput` (for incident-scoped evidence); `ConceptRef` or a `Hazard` reference array (for hazard-linking — exact shape is the open design question in §14).
- **Unchanged:** `Incident`, `IncidentInput`, `Action`, `ActionInput`, and every other existing schema object.

## 10. Relationship Semantics

Endpoint shapes above are drafted directly against **ADR-003** ([D2](../docs/implementation-blueprint/19-r1-milestone-3b-incident-decision-register.md), Accepted 2026-08-09): Investigation and Action are independent siblings of Incident, not a chain. Accordingly:

- `/incidents/{id}/investigation` is scoped only to Incident — it carries no reference to, and no dependency on, any `Action`.
- Nothing in this ACR nests Action under Investigation, or requires an Investigation to exist before an Action can be created. `Action` creation/linkage (`/actions`, `incident_actions`) is unaffected and unmentioned by this ACR — it already has full OpenAPI representation and needs none of this extension.
- `/incidents/{id}/hazards` (`REVEALS`) is likewise independent of both `/incidents/{id}/investigation` and `/actions` — three parallel, non-sequential relationships off `Incident`, matching `02-neo4j-node-relationship-model.md:110-112` exactly.

## 11. Compatibility Impact

**Fully additive — no breaking change to any existing consumer of `10-openapi.yaml`.** No existing path is modified, renamed, or removed. No existing schema object's required/optional fields change. No existing enum changes. A client that only uses today's contract is unaffected. This is stated as an impact-assessment finding, not as an argument that additive changes bypass ACR review (they do not — §4, per the 3A Review correction).

## 12. Migration Implications

None at the schema level — `03-postgresql-schema.sql` is unchanged by this ACR; every table referenced already exists, unmodified, at its current DDL. No Alembic/database migration is implied by approving this ACR in isolation. (A migration would only become relevant if this ACR's approval is followed by a separately-authorized implementation pass — not addressed here.)

## 13. Traceability to ADR-003 / D2

- [ADR-003](../.adr/ADR-003-incident-investigation-action-sibling-structure.md) — accepted basis for §10's relationship semantics; this ACR does not restate ADR-003's evidence, it inherits its conclusion.
- [19-r1-milestone-3b-incident-decision-register.md](../docs/implementation-blueprint/19-r1-milestone-3b-incident-decision-register.md) D4 — origin of this ACR; D2→D4 dependency recorded there is satisfied by ADR-003's acceptance, which is why this ACR can now be drafted.
- [18-r1-milestone-3a-incident-discovery-reconciliation.md](../docs/implementation-blueprint/18-r1-milestone-3a-incident-discovery-reconciliation.md) §4, §5, §8 — original evidence for the OpenAPI-surface gap this ACR proposes to close.

## 14. Alternatives Considered

- **(a) Do nothing — leave Investigation/hazard-linking/incident-Evidence with no API surface.** Rejected as a permanent position (it was 3A/3B option (b), "implement Incident/Action CRUD only, explicitly excluding these sub-resources") — viable as a *temporary* posture but does not close the gap D4 exists to resolve; recorded here as the fallback if this ACR is rejected (§15, §18).
- **(b) Model `incident_hazards` as a first-class schema object** (an `IncidentHazard` record with its own `id`, timestamps, etc.) rather than a bare reference list. More consistent with how `safety.action_controls`-style join tables *could* be modeled, but no existing frozen-contract precedent does this for any join table — every existing many-relationship in the contract is expressed as a nested collection under the "one" side of a 1:N relationship, not as its own addressable resource. Flagged as a genuine open design question for the approving authority, not resolved by this ACR.
- **(c) Expose Investigation as a full nested collection (`/incidents/{id}/investigations`, plural) instead of a singular resource.** Rejected — would misrepresent the confirmed 1:1 cardinality (`investigations.incident_id UNIQUE`, ADR-003) and invite exactly the "looks like a chain/multiplicity" misreading ADR-003 exists to prevent.
- **(d) Add a single combined `/incidents/{id}/full` or similar aggregate endpoint instead of three separate additions.** Rejected — inconsistent with the contract's existing convention of one focused endpoint per relationship (e.g. `CriticalControl`'s performance-standards/verification-activities/evidence are each separately nested, not aggregated).

## 15. Risk of Not Implementing

If this ACR is rejected or left indefinitely pending: any future Incident implementation is structurally limited to Incident/Action CRUD only (3A §14, 3B §7 implementation-boundary finding). `safety.investigations` and `safety.incident_hazards` would remain populated, if at all, only by direct database access or a future migration script — not through the application's own API — undermining the schema's own stated purpose (`03:511-512`: incident/action/audit chain is "the richest, most complete entities in V1" and intended to be ported "near-verbatim"). Incident-scoped Evidence would have no way to be attached via the API despite the schema explicitly naming `'incident'` as a supported target. This is a completeness/usability risk, not a compliance or data-integrity risk — no statutory notification logic (D6) or safety-critical control (CCM) depends on this extension.

## 16. Validation Requirements

If approved and later implemented: the extended `10-openapi.yaml` would need to pass the existing `openapi-validation` CI job (confirmed present and green throughout this PR's history) plus, per repository convention ([02-development-standards.md](../docs/implementation-blueprint/02-development-standards.md)), `scripts/validate_openapi.py`. No new validation tooling is proposed by this ACR. Any implementation would additionally need `configure_mappers()`/SQLAlchemy model parity checks per the established Milestone 0–2 quality-gate pattern — not performed here, as no code is written by this ACR.

## 17. Implementation Boundary

**This ACR authorizes nothing to be built.** If approved, the boundary it would open is: `10-openapi.yaml` may then be edited (in a separate, subsequent action) to add the schema objects and endpoints in §7–§9, following the exact shapes recorded here or a revision of them made during approval. Approval of this ACR is **not** approval of an implementation GO for the Incident domain generally — D3, D5, D6 remain independently gating whatever a future Incident implementation scope document defines, per [19](../docs/implementation-blueprint/19-r1-milestone-3b-incident-decision-register.md) §7's standing implementation-implications note.

## 18. Approval / Disposition

**Pending Approval.** No disposition recorded. Per the governing instruction for this pass, approval is not inferred by this document's existence, completeness, or internal consistency — it requires an explicit act by the designated governance authority (Architecture Review Board / project sponsor, per ACR-001/002/003 precedent).

## Outcome Paths (for the approving authority's reference)

- **Approve** → `10-openapi.yaml` may be additively extended per §7–§9 in a subsequent, separately-tracked action; §9's open design question (list-schema vs. first-class `IncidentHazard` object) should be settled as part of that approval, not left implicit.
- **Reject** → Investigation, hazard-linking, and incident-scoped Evidence remain without API representation; any Incident implementation proceeds on the Incident/Action-CRUD-only boundary (3A §14) until this ACR is revisited.
- **Defer** → Same practical effect as Reject in the near term; distinguished only by an explicit intent to revisit, e.g. alongside a future Incident implementation-scope document.

---

## Current State (template field, restated for index consistency)

`safety.investigations`, `safety.incident_hazards`, and incident-scoped `safety.evidence` are fully specified in Design Baseline v1.1's PostgreSQL schema and Neo4j model but have no OpenAPI representation — see §6.

## Proposed Change (template field, restated for index consistency)

Additively extend `10-openapi.yaml` with the schema objects and endpoints in §7–§9, drafted against the ADR-003 sibling structure — see §7, §10.

## Impact (template field, restated for index consistency)

Touches `10-openapi.yaml` only (§5). Fully additive, no breaking change (§11). No schema/Neo4j/ontology/code change (§5, §12). Unblocks a future, separately-authorized Incident implementation to expose Investigation/hazard-linking/incident-Evidence — does not itself authorize that implementation (§17).
