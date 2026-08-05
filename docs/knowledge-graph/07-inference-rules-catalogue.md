# Inference Rules Catalogue
**Status: DRAFT — controlled design document. Requires approval before implementation.**
**Parent:** [01-enterprise-knowledge-graph-specification.md](01-enterprise-knowledge-graph-specification.md)
**Referenced by:** [03-postgresql-schema.sql](03-postgresql-schema.sql), [05](05-knowledge-provenance-model.md), [06](06-relationship-rules-catalogue.md), [08](08-critical-control-assurance-model.md)

---

## 1. Purpose

Facts the platform *derives* rather than stores as direct input — risk ratings, overdue flags, drift/degradation signals, duplicate candidates, regulatory gaps. Each rule below states its trigger, its logic (ported from V1 where V1 already implements it — nothing here is invented where a working implementation exists), its output, and where that output surfaces. Illustrative Cypher/SQL is given for precision, not as implementation code to ship verbatim.

Every rule's output is tagged `system_derived` in the provenance model ([05](05-knowledge-provenance-model.md) §3) and re-evaluated whenever its inputs change (event-driven, not nightly-batch, for anything feeding the Executive Dashboard or Gap Analysis).

## 2. Rule Catalogue

### R1 — Risk Rating Derivation
**Trigger:** `likelihood`/`consequence` set or changed on a `Risk` (inherent, current, or target).
**Logic:** ported verbatim from `sms-shared.js` — `score = likelihood × consequence` (1–25), banded per VRTP Risk Matrix (GOHS2.1.2): Extreme 15–25, High 10–14, Medium 5–9, Low 1–4.
**Output:** `risks.inherent_rating` / `current_rating` (stored, not computed-on-read, so historical ratings survive a future matrix-threshold change without silently rewriting history).
**Surfaces:** Risk Register, Executive Dashboard.

### R2 — Critical Control Effectiveness Multiplier
**Trigger:** any `critical_controls.farsi_*` score set/changed, or a `Control`'s hierarchy concept changes.
**Logic:** ported verbatim from `GOHS4.1.8.X_FARSI_Control_Effectiveness_Calculator_v0.2.html` — FARSI score = average(F,A,R,S,I); band → multiplier (High ≥4.0→100%, Moderate 3.0–3.9→60%, Low 2.0–2.9→30%, Very Low <2.0→10%); combined with a hierarchy cap (Elimination 100% → PPE 20%); floored by a residual-likelihood floor (20% general, 10–15% for ADI/high-consequence hazards); independence check prevents double-counting non-independent controls in sequence.
**Output:** contributes to `risks.current_likelihood` suggestion (human-confirmed, per AI Extraction Spec §6 critical-item override — never auto-applied to a critical risk without review).
**Surfaces:** Critical Control Management module, feeds R1.

### R3 — Verification Overdue Detection
**Trigger:** scheduled (daily) + on-demand.
**Logic:** `verification_activities.due_date < current_date AND (last_completed IS NULL OR last_completed < due_date)`.
```sql
SELECT * FROM safety.verification_activities
WHERE due_date < current_date AND (last_completed IS NULL OR last_completed < due_date);
```
**Output:** overdue flag, age in days.
**Surfaces:** Executive Dashboard "Verification compliance", Critical Control Management, drives escalation in [08-critical-control-assurance-model.md](08-critical-control-assurance-model.md) §5.

### R4 — SFARP Gate Enforcement
**Trigger:** `risks.sfarp_justification` written/changed while `current_rating IN ('Extreme','High')`.
**Logic:** ported from `bowtie-ccm-generator.html`'s `validateDraft()` — rejects a justification matching `/risk is acceptable/i` with no further substantiation. **Flagged in the parent architecture doc as weak (regex-only) — recommend upgrading to a required-fields check (specific SFARP factors addressed) rather than pattern-blocklisting a phrase, before this becomes the sole gate in a regulator-facing system.**
**Output:** blocks save (validation, not silent inference) until justification substantiates the SFARP determination.
**Surfaces:** Risk Register authoring flow.

### R5 — Control Drift / Degradation Detection
**Trigger:** scheduled (weekly).
**Logic:** flags a `CriticalControl` where any of: (a) ≥2 linked `Action`s via `REMEDIATES` opened in the trailing 90 days, (b) the two most recent `VerificationActivity.result` entries trend negative/declining, (c) `effectiveness_rating` has been downgraded at the last two review cycles. Realizes briefing doc §5.9 "Critical Control Drift and Degradation" as a queryable signal instead of a narrative concept.
**Output:** drift flag + contributing signal(s).
**Surfaces:** Executive Dashboard, Critical Control Management, feeds TARP escalation ([08](08-critical-control-assurance-model.md) §5).

### R6 — Superficial Verification Detection
**Trigger:** scheduled (daily) + on write of `verification_activities.last_completed`.
**Logic:** a `VerificationActivity` marked complete with zero linked `Evidence` (no `PRODUCES` edge). Realizes briefing doc §11.3 "Superficial Verification ('Green-Washing')" as a mechanical check.
```cypher
MATCH (v:VerificationActivity) WHERE v.last_completed IS NOT NULL
AND NOT (v)-[:PRODUCES]->(:Evidence)
RETURN v;
```
**Output:** flag — "verification marked complete, no evidence attached."
**Surfaces:** Gap Analysis, Critical Control Management.

### R7 — Unresolved Low-Confidence Chain Detection
**Trigger:** on `SafetyCaseClaim` save/read.
**Logic:** per [05-knowledge-provenance-model.md](05-knowledge-provenance-model.md) §4 — effective confidence is the minimum across the evidence chain; any chain segment still `flag-for-review` and unreviewed is reported as **unresolved**, distinct from a genuinely low (but reviewed/accepted) confidence score.
**Output:** claim confidence + unresolved-segment list.
**Surfaces:** Safety Case Workspace.

### R8 — Missing Failure Mode Detection
**Trigger:** scheduled (weekly).
**Logic:** `CriticalControl` with zero linked `FailureMode`.
**Output:** flag — recommendation, not a hard block (a control can be legitimately new/not-yet-fully-analyzed).
**Surfaces:** Gap Analysis, Critical Control Management.

### R9 — Duplicate Hazard / Concept Collision Detection
**Trigger:** scheduled (weekly) + on new `Hazard` creation.
**Logic:** `Hazard` nodes sharing the same `CLASSIFIED_AS → Concept` edge (same category *and* same energy source), with description text-similarity above a configurable threshold (embedding cosine similarity via Qdrant — architecture §2) but distinct `id`s and, ideally, distinct or unclear `asset_id` scoping.
```cypher
MATCH (h1:Hazard)-[:CLASSIFIED_AS]->(c:Concept)<-[:CLASSIFIED_AS]-(h2:Hazard)
WHERE h1.pg_id < h2.pg_id
RETURN h1, h2, c;  // candidate set — similarity scoring happens in the Gap Analysis Service, not Cypher
```
**Output:** duplicate-candidate pair + similarity score — **surfaced for human merge/dismiss decision, never auto-merged.**
**Surfaces:** Gap Analysis (your spec's worked example: "Asset A has hydraulic isolation + annual verification; Asset B, same hazard, no verification identified → CONTROL ASSURANCE GAP" — this rule plus R3 together produce exactly that finding).

### R10 — 608B / Notifiable Incident Propagation
**Trigger:** `consequences.flag_608b = true` set on a `Consequence`, or a new `Incident` created with `REVEALS` pointing at a `Hazard` whose `Risk` has a `flag_608b` `Consequence`.
**Logic:** propagates a "notification assessment required" state onto the `Incident.osr_notified` field (defaults it to `'Not applicable / under assessment'` rather than leaving it unset), per [09-regulatory-knowledge-model.md](09-regulatory-knowledge-model.md).
**Output:** notification-assessment-required flag.
**Surfaces:** Incident module, drives AI Extraction Spec §7 Compliance Agent / Safety Case Trigger check.

### R11 — Regulatory Coverage Gap Detection
**Trigger:** scheduled (monthly).
**Logic:** `Requirement` rows with zero inbound `TRACES_TO` edges from any `SafetyCaseClaim`.
**Output:** coverage gap list, grouped by regulatory source.
**Surfaces:** Executive Dashboard "Safety Case readiness", Safety Case Workspace.

### R12 — Conflicting Control Requirement Detection
**Trigger:** scheduled (weekly).
**Logic:** two `PerformanceStandard`s attached (directly or via shared `CriticalControl`) to the same `Hazard`/`Asset` pairing with contradictory `measurable_criteria` (e.g. different required chlorine ppm ranges for the same pool system) — detected via ontology-concept co-occurrence (same taxonomy target, same asset) plus a numeric-range overlap check where criteria are structured, otherwise flagged for human read where criteria are free text.
**Output:** conflict candidate pair.
**Surfaces:** Gap Analysis.

### R13 — Serious Risk Justification Completeness
**Trigger:** on `Risk` save where `is_serious_risk = true`.
**Logic:** validation, not automated determination — per [09-regulatory-knowledge-model.md](09-regulatory-knowledge-model.md) §6, "serious risk" is deliberately operator-defined, not a fixed numeric threshold, so this rule only checks that `serious_risk_justification` is populated with a substantive interpretation, not merely present.
**Output:** blocks save (like R4) until justification is substantive.
**Surfaces:** Risk Register / Safety Assessment authoring flow.

### R14 — ADH Boundary/Coverage Completeness
**Trigger:** scheduled (weekly) + on `Hazard` save where `is_adh = true`.
**Logic:** flags a `Hazard` with `is_adh = true` and either (a) no `device_boundary_id`, or (b) not `COVERS`-linked from any `SafetyAssessment` ([06-relationship-rules-catalogue.md](06-relationship-rules-catalogue.md) §5a).
**Output:** gap flag, per hazard.
**Surfaces:** Gap Analysis, Major Hazard Register, Safety Assessment authoring flow.

### R15 — Monitoring Trend Computation
**Trigger:** scheduled (monthly, per `CriticalControl`).
**Logic:** aggregates the trailing period's `VerificationActivity` records into a new `MonitoringSummary` row — `pass_count`/`verification_count` from completed activities, `trend` computed by comparing this period's pass rate to the prior period's (declining if pass rate drops ≥1 band, improving if it rises, else stable), `indicator_class` set per the source indicator's nature (leading if the verification method is predictive per its ontology concept, lagging otherwise — [08-critical-control-assurance-model.md](08-critical-control-assurance-model.md) §5.1).
**Output:** new `MonitoringSummary` row.
**Surfaces:** Executive Dashboard, Critical Control Management, feeds R5 (control drift).

### R16 — Demonstration Staleness Detection
**Trigger:** scheduled (daily) + on any write to an entity referenced in a `Demonstration.source_fact_refs`.
**Logic:** a `Demonstration` with `status IN ('approved','published')` whose cited facts have been updated since `generated_at` is flagged stale — it is not un-published automatically (a human decides whether the change is material), but the staleness is surfaced, never silently hidden.
**Output:** stale flag + list of changed source facts.
**Surfaces:** Safety Case Demonstration Engine, Safety Case Workspace.

### R17 — EIA / FARSI Consistency Cross-Check
**Trigger:** on `CriticalControl` save.
**Logic:** per [08-critical-control-assurance-model.md](08-critical-control-assurance-model.md) §4c — a `Control` with `eia_independent = false` or `eia_auditable = false` should not be the sole FARSI-scored barrier for a `CriticalControl` (i.e. should not be the only control reaching `CLASSIFIED_AS_CRITICAL` for a given `Risk` without at least one other independent control in the chain).
**Output:** cross-check flag.
**Surfaces:** Critical Control Management, Gap Analysis.

### R18 — Lagging-Only Indicator Gap
**Trigger:** scheduled (monthly, per `CriticalControl`).
**Logic:** a `CriticalControl` whose linked `MonitoringSummary` history contains only `indicator_class = 'lagging'` entries, with no `leading` indicator ever recorded — mirrors the Guide's own point (§11.1) that lagging indicators alone "will not give an early indication that a failure is imminent."
**Output:** gap flag — recommendation to add a leading indicator, not a hard block.
**Surfaces:** Gap Analysis, Critical Control Management.

### R19 — Competency Currency Lapse Detection (Design Baseline v1.1 amendment — ACR-003, approved 2026-08-04)
**Trigger:** scheduled (daily) + on read of any `Competency`.
**Logic:** `competencies.currency_expiry_date < current_date AND status = 'current'` — mirrors R3's overdue-verification shape exactly, applied to competency currency instead of verification scheduling.
```sql
SELECT * FROM safety.competencies
WHERE currency_expiry_date < current_date AND status = 'current';
```
**Output:** lapse flag, transitions `status` to `'lapsed'` (system-derived, not silently deleted — the historical claim remains queryable).
**Surfaces:** AI Review Queue / Administration (Competency), Executive Dashboard.

### R20 — Critical Control Operator Competency Gap (ACR-003, approved 2026-08-04)
**Trigger:** scheduled (daily) + on `Competency.status` change + on `Person → CriticalControl` `ASSIGNED_TO` edge change.
**Logic:** flags a `CriticalControl` where a `Person` holding an `ASSIGNED_TO`/`OWNS` edge to it has no `Competency` row with `critical_control_id` matching, `status = 'current'` — i.e. an operator assigned to a critical control without a current, linked competency record. This is the direct structural realization of §10.8's own framing: the regulator's question is whether workers operating/maintaining/testing the device are competent, not merely whether training occurred somewhere unlinked.
**Output:** gap flag, per critical control + assigned person.
**Surfaces:** Gap Analysis, Critical Control Management, AI Review Queue / Administration (Competency).

### R21 — ADH/ADI Change Re-Triggers Competency Review (ACR-003, approved 2026-08-04)
**Trigger:** a `ReviewTrigger` created with `trigger_type = 'new_adh_identified'` (existing type, [03-postgresql-schema.sql](03-postgresql-schema.sql) `review_triggers.trigger_type`) where the affected `Hazard`/`SafetyAssessment` has linked `Competency` records via `DEMONSTRATES_COMPETENCY → CriticalControl`.
**Logic:** currency is not purely time-based per Guide §10.8 ("review and revision of training needs and information in line with changes or new ADHs and ADIs") — a new/changed ADH affecting a critical control a person is competent-linked to appends `'competency'` to that `ReviewTrigger.requires_update_of` (already extended to include this value, [03-postgresql-schema.sql](03-postgresql-schema.sql)), rather than leaving competency review to wait for the next `currency_expiry_date`.
**Output:** `requires_update_of` inclusion — does not itself lapse the `Competency` (R19 owns that), only flags it for human review ahead of its stated expiry.
**Surfaces:** Management of Change, AI Review Queue / Administration (Competency), Gap Analysis.

### R22 — Emergency Plan Exercise Currency (ACR-002, approved 2026-08-04)
**Trigger:** scheduled (weekly, per `EmergencyPlan`).
**Logic:** flags an `EmergencyPlan` with no `EmergencyExercise` where `status = 'conducted'` and `conducted_date` within the trailing 12–18 months — mirrors the Guide's own framing of exercise planning as a rolling window (§12: "the emergency exercises/drills planned for the MAP over the next 12–18 months"), not a one-off pre-licence event.
**Output:** staleness flag.
**Surfaces:** Management of Change / Safety Demonstration (Emergency Planning), Executive Dashboard.

## 3. Rule Governance

New inference rules follow the same approval gate as relationship types ([06](06-relationship-rules-catalogue.md) §6) — a rule is documented here, reviewed, and approved before it runs against production data, particularly for anything that could auto-populate a field a regulator might later rely on (R1, R2 explicitly excluded from auto-write on critical-rated risks, per R2's note).
