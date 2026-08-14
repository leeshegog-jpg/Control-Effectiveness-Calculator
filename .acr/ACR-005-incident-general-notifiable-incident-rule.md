# ACR-005: Incident Domain — New Rule Extending Notification Propagation to General WHS Act Notifiable-Incident Categories

**Raised by:** Claude Code, on chat authorization (D6 ACR-raising GO), 2026-08-12
**Affected document(s):** [03-postgresql-schema.sql](../docs/knowledge-graph/03-postgresql-schema.sql), [10-openapi.yaml](../docs/knowledge-graph/10-openapi.yaml), [02-neo4j-node-relationship-model.md](../docs/knowledge-graph/02-neo4j-node-relationship-model.md), [07-inference-rules-catalogue.md](../docs/knowledge-graph/07-inference-rules-catalogue.md).

## 1. ACR Identifier

**ACR-005.**

## 2. Title

Incident Domain — New Rule (R23) Extending Notification-Assessment Propagation to the General WHS Act Notifiable-Incident Categories (`whsq_notified`).

## 3. Status

**Pending Approval.** Not approved, not rejected, not deferred by this document. Raising this ACR is not implementation authorization for anything it describes.

## 4. Decision Requiring Change

[ADR-006](../.adr/ADR-006-incident-notification-rule-formal-defer.md) §9-§10 (D6 determination, 2026-08-12): `whsq_notified` classified as an internal notification; R10's scope determined to extend to the general WHS Act incident categories (not Chapter-9A/`osr_notified` only); §10 concluded this requires an ACR because it edits `07-inference-rules-catalogue.md`, a Design Baseline v1.1 artefact, and likely needs a new trigger-flag column.

## 5. Baseline Affected

- **`03-postgresql-schema.sql`** — one new column proposed (§7).
- **`10-openapi.yaml`** — one new field on `IncidentInput`/`Incident` proposed (§7); additive only.
- **`02-neo4j-node-relationship-model.md`** — one new `Incident` node property proposed (§7), mirroring how `flag_608b` is already a `Consequence` node property.
- **`07-inference-rules-catalogue.md`** — **one new rule added (R23)**, following the exact precedent of R19-R22 (added for ACR-002/003, "Design Baseline v1.1 amendment" tags). **R10 itself is not edited, renamed, or reinterpreted** — it stays exactly as ADR-006 §9 committed to ("R10 remains exactly as specified... scoped to `osr_notified` only").
- **Explicitly not touched:** ontology, application code, any other schema table/column, any other OpenAPI path or schema object.

## 6. Current Representation

- `07-inference-rules-catalogue.md` R10 (`:84-88`) triggers only on `Consequence.flag_608b`/`Risk.is_serious_risk` — the Chapter 9A/ADI-specific test — and only sets `Incident.osr_notified`.
- `whsq_notified` (`03-postgresql-schema.sql:531`, `10-openapi.yaml:1104`) exists but has zero rule logic anywhere.
- No column, field, or property anywhere represents "this incident meets the WHS Act s.35 notifiable-incident test" — unlike the Chapter 9A path, which has `is_serious_risk`/`flag_608b` as dedicated, already-existing trigger flags.

## 7. Required Extension

Additive only, mirroring the existing `is_serious_risk` pattern exactly (`03-postgresql-schema.sql:383`, `10-openapi.yaml:1036` — "operator-defined threshold... see 09-regulatory-knowledge-model.md §6"):

1. **New column** `safety.incidents.is_notifiable_incident boolean NOT NULL DEFAULT false` — a human-set flag recording the operator's determination that the incident meets the WHS Act 2011 s.35 test (death, s.36 serious injury/illness, or s.37 dangerous incident). Not auto-derived from `vrtp_severity` or `severity` — see §14 for why.
2. **New OpenAPI field** on `IncidentInput`/`Incident`: `is_notifiable_incident: { type: boolean, default: false, description: "WHS Act 2011 s.35 notifiable-incident determination (death / s.36 serious injury / s.37 dangerous incident) — operator-determined, see ADR-006 §9" }`.
3. **New Neo4j property** on the `Incident` node: `is_notifiable_incident` (bool), joining the existing property list (`whsq_notified`, `osr_notified`, etc., `02-neo4j-node-relationship-model.md:56`).
4. **New rule R23** in `07-inference-rules-catalogue.md`, added after R22 (next available number), tagged `(Design Baseline v1.1 amendment — ACR-005, pending)`:
   > **R23 — WHS Act s.38 / General Notifiable-Incident Propagation**
   > **Trigger:** `Incident.is_notifiable_incident = true`.
   > **Logic:** propagates a "notification assessment required" state onto `Incident.whsq_notified` (defaults it out of `'Not yet assessed'` rather than leaving it unset), per [ADR-006](../.adr/ADR-006-incident-notification-rule-formal-defer.md) §9 — mirrors R10's structure exactly, applied to the sibling field.
   > **Output:** notification-assessment-required flag on `whsq_notified`.
   > **Surfaces:** Incident module. Responsible notifier: Safety Systems Manager (ADR-006 §9). Timeframe: 48 hours (ADR-006 §9, consistent with WHS Act s.38(2) "fastest possible means"). Evidence retention: 10 years (ADR-006 §9 — exceeds WHS Act s.38(7)'s 5-year minimum; the longer VRTP-determined period governs).

## 8. Affected Endpoints

None new. The existing `PATCH /incidents/{id}` (already in `10-openapi.yaml`) carries the new `is_notifiable_incident` field via the extended `IncidentInput` schema, same as any other field addition.

## 9. Affected Schemas / DTOs

`IncidentInput`/`Incident` extended with one new boolean field. No new schema object. `ActionInput`/`Action` unaffected.

## 10. Relationship Semantics

Independent of [ADR-003](../.adr/ADR-003-incident-investigation-action-sibling-structure.md)'s sibling structure — `is_notifiable_incident` is a scalar property of `Incident` itself, not a relationship. No interaction with `Investigation`, hazard-linking, or Evidence (all ACR-004).

## 11. Compatibility Impact

Fully additive — no existing path, schema field, column, or Neo4j property is modified or removed. A client using today's contract is unaffected by the new optional field. R10 is untouched (§7 point 4) — this is a genuinely separate, parallel rule, not a modification.

## 12. Migration Implications

New column requires an Alembic migration (`ALTER TABLE safety.incidents ADD COLUMN is_notifiable_incident boolean NOT NULL DEFAULT false`), same shape as the existing `is_serious_risk`/`flag_608b` migrations already executed. No backfill complexity: the R0 placeholder state means no `safety.incidents` rows exist yet in any deployed environment (`apps/api/app/dto/incidents.py` etc. remain empty stubs, confirmed in [18](../docs/implementation-blueprint/18-r1-milestone-3a-incident-discovery-reconciliation.md) §9) — `DEFAULT false` is uncomplicated here, not a retrofit onto live data.

## 13. Traceability to ADR-006 / D6

- [ADR-006](../.adr/ADR-006-incident-notification-rule-formal-defer.md) §9 — the determination this ACR implements (scope, notifier, timeframe, retention).
- [ADR-006](../.adr/ADR-006-incident-notification-rule-formal-defer.md) §10 — the impact assessment that concluded this ACR was required.
- [ADR-006](../.adr/ADR-006-incident-notification-rule-formal-defer.md) §11 — explicitly **not** addressed by this ACR: "OSR" meaning and `osr_notified` remain untouched; this ACR proposes nothing for either.
- [20-r1-milestone-3c-d6-notification-evidence-matrix.md](../docs/implementation-blueprint/20-r1-milestone-3c-d6-notification-evidence-matrix.md) — underlying evidence (WHS Act ss.35-39 verbatim).

## 14. Alternatives Considered

- **(a) New human-set boolean column, mirroring `is_serious_risk`** — adopted (§7). Consistent with the existing pattern for exactly this kind of operator-judgement flag, and with `09-regulatory-knowledge-model.md` §6 point 3's standing principle: "This automated flag is still never a substitute for human judgement on notifiability."
- **(b) Auto-derive from `vrtp_severity`** (e.g. treat `vrtp_severity IN ('Serious Injury','Dangerous Incident')` as equivalent to the s.35 test). **Rejected.** `vrtp_severity`'s six values are VRTP's own internal severity taxonomy (confirmed against V1 `incident-report.html:93`, no statutory citation anywhere) — their legal equivalence to WHS Act s.36's specific injury list (amputation, serious head/eye injury, serious burn, degloving, spinal injury, loss of bodily function, serious lacerations, or 48hr-exposure medical treatment) or s.37's specific dangerous-incident list has never been verified. Adopting this mapping would fabricate exactly the kind of unverified legal equivalence D6's entire discovery/defer/resolve track exists to prevent. Also note: `vrtp_severity`'s enum has no explicit "Death" option, while s.35(a) is a standalone notifiable category — a severity-based derivation would silently miss it.
- **(c) No new column — derive the trigger from existing `severity` (1-5 int) threshold.** **Rejected**, same reasoning as (b): `severity` is an unvalidated numeric scale with no confirmed mapping to the s.35/36/37 test either.
- **(d) Edit R10 in place to add the new trigger, rather than adding R23.** **Rejected** — contradicts ADR-006 §9's explicit commitment that R10 stays exactly as specified, and departs from the established v1.1-amendment precedent (R19-R22 were additions, not edits to R1-R18, for ACR-002/003).

## 15. Risk of Not Implementing

If this ACR is rejected or left pending: `whsq_notified` remains entirely unautomated indefinitely — every incident's general-notifiability assessment stays a fully manual field with no platform support, even though the underlying determination (D6, ADR-006 §9) has already been made. This is a lower-severity risk than D6 itself being unresolved (the scope question is answered; only its mechanical implementation awaits this ACR) — closer to a completeness gap than an open compliance question.

## 16. Validation Requirements

If approved and implemented: `scripts/validate_openapi.py` must pass (0 dangling `$ref`s) after the `IncidentInput` extension, same as ACR-004's validation. `configure_mappers()`/SQLAlchemy parity check applies once a model column is added (no model exists yet for `Incident` at all — greenfield, per [18](../docs/implementation-blueprint/18-r1-milestone-3a-incident-discovery-reconciliation.md) §9). No new CI job proposed.

## 17. Implementation Boundary

**This ACR authorizes nothing to be built.** If approved, it opens the boundary for a subsequent, separately-authorized action to: add the migration (§12), extend `IncidentInput`/`Incident` and the Neo4j `Incident` node property (§7), and add R23's text to `07-inference-rules-catalogue.md`. It does **not** authorize implementing R23's actual propagation logic in application code, nor any UI/form change to capture `is_notifiable_incident`. D3, D5 (both closed) do not gate this; D6's "OSR" residual item (ADR-006 §11) is explicitly out of this ACR's scope and remains separately open.

## 18. Approval / Disposition

**Pending Approval.** No disposition recorded. Approval is not inferred by this document's existence or internal consistency — it requires an explicit act by the designated governance authority, per ACR-001/002/003/004 precedent.

## Outcome Paths

- **Approve** → §7's four changes may be additively made in a subsequent, separately-authorized action (schema migration, OpenAPI field, Neo4j property, R23 text).
- **Reject** → `whsq_notified` remains fully manual; D6's scope determination (ADR-006 §9) stands recorded but unimplemented; may be revisited later without re-litigating the underlying determination.
- **Defer** → same practical effect as Reject, distinguished by an explicit intent to revisit alongside a future Incident implementation-scope milestone.

---

## Current State (template field, restated for index consistency)

`whsq_notified` has zero rule representation anywhere in the platform, and no trigger flag exists for the WHS Act s.35/36/37 general notifiable-incident test — see §6.

## Proposed Change (template field, restated for index consistency)

Add `incidents.is_notifiable_incident` (new column), its OpenAPI and Neo4j representations, and a new inference rule R23 (not an edit to R10) that propagates an assessment-required state onto `whsq_notified` when set — see §7.

## Impact (template field, restated for index consistency)

Touches `03-postgresql-schema.sql`, `10-openapi.yaml`, `02-neo4j-node-relationship-model.md`, `07-inference-rules-catalogue.md` (§5). Fully additive (§11). R10/`osr_notified`/"OSR" explicitly untouched (§7, §13). Does not itself authorize implementation (§17).
