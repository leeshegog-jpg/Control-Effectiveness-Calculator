# ACR-006: Incident Domain — OpenAPI Extension for Incident-Scoped Action Linking (`incident_actions` / `TRIGGERS`)

**Raised by:** Claude Code, on chat authorization (Action reconciliation, ACR-drafting GO), 2026-08-21
**Affected document(s):** [10-openapi.yaml](../docs/knowledge-graph/10-openapi.yaml) only. No other Design Baseline v1.1 artefact is proposed to change.

## 1. ACR Identifier

**ACR-006.**

## 2. Title

Incident Domain — OpenAPI Extension for Incident-Scoped Action Linking (`incident_actions` / `TRIGGERS`).

## 3. Status

**Pending.** Drafted per explicit chat GO, scoped to governance/documentation only. Not approved. `10-openapi.yaml` remains unchanged; no schema/Neo4j/ontology/code change has been made. This ACR does not itself authorize implementation even if approved — see §17.

## 4. Decision Requiring Change

[29-action-mechanism-reconciliation-correction.md](../docs/implementation-blueprint/29-action-mechanism-reconciliation-correction.md) confirmed `safety.incident_actions` (`TRIGGERS`, Incident → Action) exists in the frozen PostgreSQL schema and Neo4j relationship model but has **zero representation in the frozen OpenAPI contract** — the same class of gap ACR-004 closed for Investigation/`incident_hazards`/incident-scoped Evidence, except ACR-004's scope never included `incident_actions` (confirmed directly against ACR-004 §5, §7-§9 above — Action is explicitly named as unaffected and unmentioned there, §10). A subsequent read-only reconciliation (chat, 2026-08-21) established this gap is functionally material, not cosmetic: generic `/actions` plus `source_type`/`source_id` filtering cannot reconstruct V1's `fCARs` behaviour (§6 below).

## 5. Baseline Affected

- **In scope:** [10-openapi.yaml](../docs/knowledge-graph/10-openapi.yaml) — proposed additive changes only (§7-§9 below).
- **Explicitly not in scope, not touched, not proposed to change:** [03-postgresql-schema.sql](../docs/knowledge-graph/03-postgresql-schema.sql), [02-neo4j-node-relationship-model.md](../docs/knowledge-graph/02-neo4j-node-relationship-model.md), `06`/`07`/`09` knowledge-graph docs, any ontology scheme, any application code. `safety.incident_actions` already exists, unmodified, in the frozen schema and graph model (§6).
- **Explicitly excluded from this ACR, tracked as separate governance items:** `safety.actions.completion_date`/`.notes` exposure on `ActionInput`/`Action` (§7 confirms these remain absent under this ACR); `safety.action_controls`/`REMEDIATES` exposure. Neither is addressed here — each requires its own ACR if pursued.

## 6. Current OpenAPI Representation and V1 Evidence

| Frozen artefact | Schema/graph status | Current OpenAPI status |
|---|---|---|
| `safety.incident_actions` (`03-postgresql-schema.sql:586-590`), `TRIGGERS` (`02-neo4j-node-relationship-model.md:112`) | Fully specified — composite PK `(incident_id, action_id)` join table | **No endpoint of any form.** |

**V1 evidence, verified directly** (`incident-report.html:110`): `fCARs` — "Linked CAR IDs," free text, placeholder `"e.g. C0001, C0002"` — a comma-separated list a user can populate with **any** existing CAR ID, including one originated elsewhere (an Audit finding, a different incident, a Risk Review). This is distinct from `openCAR()` (`incident-report.html:322-330`), which navigates to `corrective-actions.html?source=Incident&sourceRef=<incidentId>&...` — a single-value creation-origin flow, already fully represented by `actions.source_type_concept_id`/`source_id` and the existing generic `/actions` endpoints.

**Confirmed by reconciliation, not assumed:** generic `/actions` filtering by origin cannot reconstruct `fCARs`'s roster behaviour — `source_type`/`source_id` records only where an Action was *created from* (one value per Action row), not an arbitrary set of Actions an Incident references. `safety.incident_actions` is the only mechanism in the frozen baseline capable of representing `fCARs`'s actual behaviour.

## 7. Required Extension

Additive-only. No existing path, schema object, or field in `10-openapi.yaml` is proposed to change or be removed. `completion_date`/`notes` remain absent from `ActionInput`/`Action` under this ACR — exposing them is a separate governance item (§5).

**No new schema object.** Proposed to reuse the existing `Action` schema unchanged for list responses, mirroring how `/incidents/{id}/hazards` (ACR-004, Option A) reuses `Hazard` rather than inventing a join-record schema — `safety.incident_actions` has no columns beyond its composite key, so a first-class resource schema would have nothing to carry.

## 8. Affected Endpoints (proposed, not yet added)

| Endpoint | Method(s) | Cardinality basis | Precedent pattern followed |
|---|---|---|---|
| `/incidents/{id}/actions` | `GET` | 1:N, per `TRIGGERS` | Direct structural copy of `/incidents/{id}/hazards` `GET` (ACR-004) |
| `/incidents/{id}/actions` | `POST` | Links (and, per §9, possibly creates) an Action | Modeled on `/incidents/{id}/hazards` `POST`, with the open design question in §9 not present in the hazard case |
| `/incidents/{id}/actions/{actionId}` | `DELETE` | Unlink | Direct structural copy of `/incidents/{id}/hazards/{hazardId}` `DELETE` (ACR-004) |

No changes proposed to `/incidents`, `/incidents/{id}`, `/actions`, `/actions/{id}`, `/incidents/{id}/investigation`, `/incidents/{id}/hazards[/{hazardId}]`, `/incidents/{id}/evidence`, or any other existing path.

## 9. Open Design Question — Not Resolved by This ACR Draft

**`POST /incidents/{id}/actions` — link an existing Action by ID, or also permit creating a new Action in the same call?**

Two readings are both plausible from the evidence and neither is picked here:

- **Link-existing (mirrors ACR-004 Option A exactly):** body is a bare `{action_id}` reference, matching `IncidentHazardLinkInput`'s shape. Simplest, most consistent with the existing hazard-link precedent.
- **Create-and-link:** body accepts the full `ActionInput` shape, creating a new Action with `source_type`/`source_id` implicitly set to this Incident and simultaneously writing the `incident_actions` row — closer to V1's `openCAR()` single-creation flow, but conflates two operations (`POST /actions` already exists for creation) into one endpoint.

This is presented as a fork for the approving authority to resolve, the same way ACR-004 §14(b)/§18 presented and then resolved the hazard-link shape question at approval time — not pre-decided in this draft.

## 10. Relationship Semantics

Consistent with ADR-003 and ACR-004 §10: `/incidents/{id}/actions` is scoped only to Incident's `TRIGGERS` edge. It does not affect, nest under, or depend on `/incidents/{id}/investigation` or `/incidents/{id}/hazards`. `source_type`/`source_id` on `actions` (Action's origin) and `incident_actions` (Incident's linked-CAR roster) are confirmed independent, non-competing concepts (§6, [29 §2](../docs/implementation-blueprint/29-action-mechanism-reconciliation-correction.md#2-corrected-finding)) — this ACR adds API surface for the roster only; the origin mechanism already has full representation via generic `/actions`.

## 11. Compatibility Impact

**Fully additive — no breaking change to any existing consumer of `10-openapi.yaml`.** No existing path is modified, renamed, or removed. No existing schema object's required/optional fields change.

## 12. Migration Implications

None at the schema level — `03-postgresql-schema.sql` is unchanged; `safety.incident_actions` already exists, unmodified, at its current DDL.

## 13. Traceability

- [29-action-mechanism-reconciliation-correction.md](../docs/implementation-blueprint/29-action-mechanism-reconciliation-correction.md) — origin of this ACR; resolves the Incident↔Action mechanism question this ACR builds on.
- [18-r1-milestone-3a-incident-discovery-reconciliation.md](../docs/implementation-blueprint/18-r1-milestone-3a-incident-discovery-reconciliation.md) §3 (line 76), §11 (line 188) — prior reconciliation establishing `incident_actions` as the `fCARs`-backing mechanism.
- [06-relationship-rules-catalogue.md:37](../docs/knowledge-graph/06-relationship-rules-catalogue.md) — `TRIGGERS`/`source_type`/`source_id` consistency rule.
- [ACR-004](ACR-004-incident-openapi-extension.md) §14(b), §18 — precedent for the bare-reference-list design pattern this ACR proposes to follow (§7, §9).

## 14. Alternatives Considered

- **(a) Do nothing — leave `incident_actions` with no API surface.** Viable as a temporary posture (Base Action CRUD against generic `/actions` proceeds regardless, per [29 §5](../docs/implementation-blueprint/29-action-mechanism-reconciliation-correction.md#5-updated-disposition)), but leaves V1's `fCARs` behaviour permanently unreproducible via the API.
- **(b) Model `incident_actions` as a first-class schema object.** Rejected for the same reason ACR-004 §14(b) rejected it for `incident_hazards` — no columns beyond the composite key, no precedent elsewhere in the frozen contract for exposing a bare join table as its own resource.
- **(c) Represent the link solely via `actions.source_type`/`source_id`, no new endpoint.** Rejected — confirmed insufficient by evidence (§6); cannot reproduce `fCARs`'s roster behaviour.

## 15. Risk of Not Implementing

If this ACR is rejected or left indefinitely pending: any future Incident Action implementation is limited to origin-tracking only (`source_type`/`source_id` via generic `/actions`), unable to reproduce V1's `fCARs` linked-CAR roster. This is a completeness/data-fidelity risk relative to V1, not a compliance or safety-critical risk — no statutory notification logic or safety-critical control depends on this extension.

## 16. Validation Requirements

Not yet applicable — no OpenAPI change has been made under this draft. If approved, `scripts/validate_openapi.py` must confirm 0 dangling `$ref`s and a strictly additive diff before commit, per the ACR-004/005 precedent.

## 17. Implementation Boundary

**Nothing implemented by this ACR draft.** Raising this ACR does not authorize:
- Any edit to `10-openapi.yaml`.
- Any application-code implementation (routers, services, repositories, models) against these proposed endpoints.
- Any Postgres schema, Neo4j, or ontology change.
- Resolution of §9's open design question — that resolution, if this ACR is approved, is itself a governance act, mirroring how ACR-004 §18 resolved its own Option A/B fork at approval time, not before.

A separate, explicit GO is required before this ACR's proposed `10-openapi.yaml` extension is written, and a further separate GO is required before any application-code implementation against it.

## Outcome Paths

- **Approve** → `10-openapi.yaml` additively extended per §7-§9, with §9's design question resolved at approval time (mirroring ACR-004 §18) — not yet taken.
- **Reject** → not taken.
- **Defer** → not taken.

---

## Current State (template field, restated for index consistency)

`safety.incident_actions` is fully specified in Design Baseline v1.1's PostgreSQL schema and Neo4j model but has no OpenAPI representation — see §6.

## Proposed Change (template field, restated for index consistency)

Additively extend `10-openapi.yaml` with the endpoints in §7-§9, reusing the existing `Action` schema, with one open design question (§9) left for the approving authority.

## Impact (template field, restated for index consistency)

Touches `10-openapi.yaml` only (§5). Fully additive, no breaking change (§11). No schema/Neo4j/ontology/code change (§5, §12). `completion_date`/`notes` and `action_controls`/`REMEDIATES` remain separate, unaddressed governance items (§5).
