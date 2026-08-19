# R1 Milestone 3C — D6 Notification-Rule Scope: Discovery & Evidence Matrix

**Status:** Discovery only. No ADR raised, no ACR raised, no decision made, no notification logic implemented, no code/schema/API/ontology/Neo4j change. Authorized scope: D6 evidence/discovery reconciliation only (chat authorization, 2026-08-12) — explicitly *not* an ADR-drafting pass.

**Scope of this pass:** reconcile [19-r1-milestone-3b-incident-decision-register.md](19-r1-milestone-3b-incident-decision-register.md) **D6** (whether/how R10, the `608B / Notifiable Incident Propagation` inference rule, is in scope for a future Incident implementation) against every source that bears on it — existing V1 behaviour, the WHS Act 2011 (Qld) and WHS Regulation 2011 (Qld) primary text (both now available locally in full), the frozen platform's own regulatory model and inference-rule catalogue, and the AI-extraction specification's human-override discipline. Output is an evidence matrix for Compliance/Legal, not a recommendation on what R10 should do.

---

## 1. Purpose

D6 was deliberately left with **no recommendation** at Milestone 3B ([19](19-r1-milestone-3b-incident-decision-register.md) D6: *"No default recommended... the scope call belongs with whoever holds compliance authority for notifiable-incident determinations, not with implementation governance alone"*). This pass does not change that. It exists to hand Compliance/Legal a **specific, cited evidence matrix** rather than an open-ended question — per the explicit instruction accompanying this GO: *"Do not ask Compliance/Legal a vague question such as 'what should R10 do?'"*

## 2. Method

Searched the repository and local primary-source files for every occurrence of: `R10`, `notification`, `notify`, `notifiable incident`, `regulator notification`, `WHSQ`, `OSR`, `reportable`, `escalation`, `Schedule 18C`, plus the full statutory text of WHS Act 2011 Part 3 (`WHS Act 2011.md`) and WHS Regulation 2011 Chapter 9A (`WHS Reg 2011.md`), both present locally in full (not previously read section-by-section for this specific question in 3A/3B). V1's `local-automation` PowerShell pipeline was inspected directly; its underlying LLM system prompts (`compliance-agent-prompt.txt`, `investigation-agent-prompt.txt`) live outside this repository, in an external Obsidian vault path (`local-automation/run-incident-pipeline.ps1:4-5`), and were **not accessible for this pass** — flagged as a limitation, not silently worked around.

---

## 3. Evidence Matrix

| # | Source | Requirement | Authority | Mandatory / Discretionary | Trigger | Recipient | Timeframe | Existing V1 implementation | Current platform representation | Gap / Status |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | WHS Act 2011 (Qld) s.35 | Defines "notifiable incident" = death, serious injury/illness (s.36), or dangerous incident (s.37) | Statute | N/A — definitional | N/A | N/A | N/A | V1 has no explicit s.35 test; `vrtp_severity` (First Aid/MTI/LTI/Serious Injury/Dangerous Incident/Near Miss) is a VRTP-internal severity taxonomy, not a direct restatement of the statutory test | `incidents.vrtp_severity` (schema), `incidents.severity` (1-5 int) — neither is programmed against the s.35/36/37 definitions | **GAP** — no rule anywhere maps `vrtp_severity`/`severity` to the statutory s.35 test. `TO_BE_CONFIRMED` whether the operator's severity taxonomy is intended to *be* that test or is a separate internal scale |
| 2 | WHS Act 2011 (Qld) s.38 | "A person who conducts a business or undertaking must ensure that the regulator is notified **immediately** after becoming aware that a notifiable incident... has occurred", by phone or in writing, fastest possible means. Record retained 5 years. Penalty 100 units (notify) / 50 units (record-keeping) | Statute — **generally applicable, not Chapter-9A-specific** | **Mandatory**, penalty-backed | An event meeting s.35's definition has occurred | "the regulator" (WHSQ, Qld's WHS regulator) | Immediate (phone) / 48hr written follow-up if requested | None found | `incidents.whsq_notified` (enum: Not yet assessed / Yes / No - assessed not required / No - under assessment) exists in schema+OpenAPI (`03-postgresql-schema.sql:531`, `10-openapi.yaml:1104`); **no rule anywhere (R10 or otherwise) sets, defaults, or propagates this field.** [09-regulatory-knowledge-model.md](../knowledge-graph/09-regulatory-knowledge-model.md) §6 formalizes `osr_notified` only — its own heading names both fields, its numbered logic addresses only one | **GAP — the general, generally-applicable statutory notification duty (arguably the more legally consequential of the two fields, given the penalty) has zero rule/logic representation anywhere in the platform.** R10 as currently specified does not touch `whsq_notified` at all |
| 3 | WHS Act 2011 (Qld) s.39 | Duty to preserve incident sites once a notifiable incident has occurred, until an inspector arrives or directs otherwise | Statute | Mandatory, penalty-backed | Same as s.38 | N/A (site preservation, not a notification) | N/A | None found | None | Out of scope for D6 (not a notification rule) — noted for completeness only, not a gap requiring resolution here |
| 4 | WHS Regulation 2011 (Qld) s.608B(1) | Defines "amusement device incident" (ADI): involves an amusement device **and** exposes/potentially exposes a person to serious risk to health/safety | Subordinate legislation, Chapter 9A (major amusement parks) | N/A — definitional | N/A | N/A | N/A | V1's Compliance Agent pipeline detects an "ADI signal" via regex (`ADI\|608B\|attributable dangerous\|s 608Z\|Chapter 9A\|safety case`) in its own LLM output (`local-automation/run-incident-pipeline.ps1:112`) — informal, not a codified rule | [09-regulatory-knowledge-model.md](../knowledge-graph/09-regulatory-knowledge-model.md) §6 point 1-2 — "confirmed, not inferred" per prior citation work; R10's trigger (`Risk.is_serious_risk`/`Consequence.flag_608b`) is built on this | Already reconciled in 3A/3B — not new to this pass |
| 5 | WHS Regulation 2011 (Qld) Chapter 9A, §608K/608L (read in full this pass) | Operator must **identify** (so far as reasonably practicable) all ADIs/ADHs that *could occur*, and conduct a safety assessment | Subordinate legislation | Mandatory, penalty-backed (60 units) | Ongoing/systematic — not incident-triggered | N/A — an identification/assessment duty, not a per-incident notification duty | N/A | Not directly implemented; this is the general Hazard/Risk domain's job (Milestone 1), not Incident's | N/A | Confirms (§4 below) that Chapter 9A does **not** itself impose a distinct "notify the regulator that *this* ADI occurred" duty — 608K/L are prospective identification duties, not reactive notification |
| 6 | WHS Regulation 2011 (Qld) Chapter 9A, §608J (read in full this pass) | Operator must give the regulator **written notice within 14 days** of a **material change to the safety case outline** | Subordinate legislation | Mandatory, penalty-backed | A material particular of the *safety case outline* changes | The regulator | 14 days | None found | None | Distinct trigger (safety-case-content change) from "an incident occurred" — does not match either `whsq_notified` or `osr_notified`'s apparent intent. Noted as a candidate explanation ruled out, not adopted |
| 7 | "OSR (Chapter 9A) Notified?" — V1 label (`incident-report.html:98`) and `osr_notified` field (schema/API/Neo4j) | Unknown — the acronym "OSR" is **not defined or expanded anywhere** in: this repository's controlled docs, `WHS Act 2011.md` (full text, searched), `WHS Reg 2011.md` (full text, searched), or the V1 source itself | **Unconfirmed** | Unconfirmed | Unconfirmed | Unconfirmed | Unconfirmed | Field exists, unexplained, since V1; carried into `03-postgresql-schema.sql:532`, `10-openapi.yaml:1105` ("Chapter 9A — see 09-regulatory-knowledge-model.md §4"), and `02-neo4j-node-relationship-model.md:56` without ever being expanded | **CONFLICT/GAP — this repository has never established what "OSR" stands for or what specific obligation it represents.** §4's Chapter 9A search (rows 4-6 above) found no distinct per-incident regulator-notification duty in Chapter 9A that "OSR" could textually correspond to, beyond the general s.38 duty already tracked separately as `whsq_notified`. **This is the single most material open question for Compliance/Legal in this matrix** — see §5 |
| 8 | [07-inference-rules-catalogue.md](../knowledge-graph/07-inference-rules-catalogue.md) R10 (`608B / Notifiable Incident Propagation`) | Platform-internal rule, not a legal source | Platform design | N/A (a design artefact, not a duty) | `Consequence.flag_608b = true`, or `Incident REVEALS` a flagged `Hazard`/`Risk` | N/A — sets a flag, does not notify anyone | N/A | N/A | Propagates a "notification assessment required" state onto `Incident.osr_notified` only (defaults out of "not yet assessed") — never sets `whsq_notified`, never auto-determines notifiability, never sends an actual notification to anyone | R10's proposed scope is conservative by design — it flags for human assessment, consistent with row 10 below. Confirms R10 as currently specified is **incomplete relative to the full notification picture** (row 2) — it silently omits the s.38 general duty entirely, not by any documented decision, just by never having been extended to it |
| 9 | [09-regulatory-knowledge-model.md](../knowledge-graph/09-regulatory-knowledge-model.md) §6 | "formalizes V1's `whsqNotified`/`osrNotified` fields" (its own heading) | Platform design, citing s.608B(1) | N/A | N/A | N/A | N/A | N/A | Despite the heading naming both fields, all four numbered points address only the Chapter 9A/ADI/`osr_notified` side. No point addresses the general `whsq_notified`/s.38 duty at all | Confirms row 2/8's gap directly at the source document — this is not a new discovery contradicting 09, it is 09 itself never having covered `whsq_notified` |
| 10 | [04-ai-extraction-specification.md](../knowledge-graph/04-ai-extraction-specification.md) §6, §7 | "Any extraction touching a critical control, SFARP justification, or a **regulatory notification determination (WHSQ/OSR/Chapter 9A)** is always flag-for-review regardless of confidence score" | Platform design | N/A | Any AI-extracted content touching notification determination | N/A | N/A | N/A | Compliance Agent step (§7) "evaluates WHSQ/OSR (Chapter 9A) notification obligations against 09... always flag-for-review" | Confirms platform-wide design intent: **notification determination is a human decision point everywhere it appears, never an automated action.** This bounds what R10 could ever safely do even before D6 is resolved — it cannot become an auto-notify feature regardless of Compliance/Legal's answer |
| 11 | [11-implementation-risk-register.md](11-implementation-risk-register.md) REG3 | Schedule 18C sub-item "Incident management, investigation, reporting, improvement" (Guide §10.7) unread/unconfirmed | Platform governance tracking | N/A | N/A | N/A | N/A | N/A | Already tracked, cited in 3A §7 and 3B — not new | Still open; relevant context for Compliance/Legal (the SMS-section-level regulatory citation for this whole domain is itself incomplete), but not new evidence produced by this pass |
| 12 | Schedule 18B (Emergency Plan, `03` `safety.emergency_plans` et al., ACR-002) | Notifications to **emergency service organisations** (QFES/QPS/QAS) during/after an emergency | Subordinate legislation, s.608N | Mandatory | An emergency requiring response | Emergency services, not the WHS regulator | Per emergency plan procedures | N/A | Separate, already-approved domain (`EmergencyServiceConsultation` etc., ACR-002) | **Explicitly out of scope for D6** — a different recipient (emergency services, not WHSQ/regulator) and a different trigger (emergency response, not incident notification). Noted only to rule out conflation, per the user's own category table distinguishing "Emergency notification" from "Statutory notification" |

---

## 4. Category Mapping (per the six categories requested in the authorizing instruction)

| Category | Applicable here? | Finding |
|---|---|---|
| Statutory notification (legally notifiable incident) | **Yes** | WHS Act s.35/s.38 (rows 1-2) — mandatory, penalty-backed, generally applicable. This is `whsq_notified`'s evident basis, though no rule currently implements it |
| Safety Case / MAP obligation | **Partially, unconfirmed** | Chapter 9A (rows 4-6) imposes proactive identification (608K/L) and safety-case-change notice (608J) duties, but **no distinct per-incident regulator-notification duty was found**. Whether `osr_notified`/"OSR" is meant to represent this category, or something else, is unresolved (row 7) |
| Internal escalation | **Not evidenced** | No V1 or platform document describes an internal (non-regulator) escalation notification distinct from the two fields already tracked |
| Investigation trigger | **Adjacent, not D6** | `investigation_status`/`safety.investigations` (D2/ADR-003) already covers this; not a notification concern |
| Emergency notification | **Out of scope, separate domain** | Row 12 — Schedule 18B/ACR-002, different recipient and trigger |
| Advisory / information-only notification | **Not evidenced** | No source found describing a non-mandatory, informational-only notification concept distinct from rows 1-7 |

---

## 5. The Material Open Question for Compliance/Legal

This pass could not determine, from any source available in this repository (including the full text of the WHS Act and WHS Regulation), **what "OSR" stands for or what specific obligation `osr_notified` is meant to represent**, beyond the already-reconciled ADI/`flag_608b` trigger mechanics (row 4, already settled in 3A/3B). Three non-exclusive possibilities are visible in the evidence but **none is adopted or preferred by this document**:

1. `osr_notified` is intended as the Chapter 9A-specific tracking field, but the actual underlying duty is the *same* general s.38 duty as `whsq_notified` (i.e., an ADI that also meets the s.35 definition triggers s.38 once, and both fields are tracking facets of one duty, not two duties) — in which case the two fields may be redundant rather than distinct.
2. "OSR" refers to a body, process, or requirement not found in the WHS Act/Regulation text searched here — possibly a VRTP-internal process (matching the pattern of `GOHS4.1.8` and similar internal-standard citations already flagged `TO_BE_CONFIRMED` in [09](../knowledge-graph/09-regulatory-knowledge-model.md) §2) or a different Queensland regulatory instrument not yet sourced.
3. "OSR" is a V1 labeling artefact that was never fully grounded by its original author and has been carried forward through the platform's design documents without independent verification — consistent with `09`'s own heading naming both fields while only ever substantively addressing one.

**This is the specific question this evidence matrix exists to put to Compliance/Legal — not "what should R10 do?"**

---

## 6. What D6 Still Needs, Restated (not resolved here)

Per [19](19-r1-milestone-3b-incident-decision-register.md) D6, restated with this pass's findings folded in — genuinely still open, no position taken:

1. Confirm what "OSR" represents (§5) — a prerequisite to scoping R10 sensibly, since R10 currently only touches `osr_notified` and is silent on `whsq_notified`.
2. Confirm whether R10 should be extended to also propagate an assessment-required state onto `whsq_notified` (the general, penalty-backed, generally-applicable duty — arguably the more legally load-bearing of the two) — currently **completely unaddressed** by any platform rule.
3. Confirm the operator's own documented "serious risk" threshold interpretation (already correctly identified as a human, not automated, decision — `09` §6 point 2, `SafetyAssessment.serious_risk_threshold_note`) extends coherently to the s.35/36/37 general-notifiable-incident test, or whether a separate threshold interpretation is needed for that test.
4. Whether VRTP's existing internal incident-notification/escalation procedure (requested first in the authorizing instruction's source-priority list) already answers any of the above — **not obtainable from this repository**; this remains an external-document dependency, same limitation noted for the Compliance Agent prompt file (§2).

---

## 7. Explicit Boundary

- No ADR was drafted or proposed. No recommendation is offered on any of §6's four points.
- No ACR was raised, no schema/OpenAPI/Neo4j/ontology/code change was made.
- D1-D5, D7 are unaffected and unchanged by this pass.
- Item 4 in §6 (VRTP's own internal procedure, and the Guide's own remaining unread sections per REG3) could not be sourced from this repository — this pass is bounded by what's available locally, not a claim that no such document exists.

---

## Acceptance Criteria

- [x] Reconciled against V1 source representation — `incident-report.html`, `local-automation/*.ps1` (§3 rows 1, 4, 8).
- [x] Reconciled against the frozen PostgreSQL schema — `whsq_notified`/`osr_notified` columns (§3 row 2, 7).
- [x] Reconciled against the OpenAPI contract — `IncidentInput` enums (§3 row 2, 7).
- [x] Reconciled against the Neo4j model — `Incident` node properties (§3 row 7).
- [x] Reconciled against existing D1-D4 decisions — ADR-003 (structure), ADR-004 (ontology), ACR-004 (OpenAPI surface) checked for interaction; none found to affect D6.
- [x] Reconciled against relevant business logic — R10 (§3 row 8), 04-ai-extraction-specification.md's human-override discipline (§3 row 10).
- [x] Primary statutory text read directly, not paraphrased at a distance — WHS Act 2011 ss.35-39, WHS Regulation 2011 Chapter 9A §§608B, 608J, 608K, 608L, all quoted/cited by section and, where useful, verbatim.
- [x] No replacement semantics invented where evidence did not support them — the "OSR" question is presented as unresolved, not guessed at.
- [x] No decision made; evidence matrix only, formatted per the authorizing instruction's exact column spec.
