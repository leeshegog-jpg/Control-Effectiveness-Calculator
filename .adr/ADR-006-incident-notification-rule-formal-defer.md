# ADR-006: Incident Domain — Formal Defer of D6 (Notification-Rule Scope), Pending Compliance/Legal Determination

**Status:** Accepted (2026-08-12) — Deferred (not resolved)

## 1. Decision Statement

**D6 deferred pending Compliance/Legal determination of OSR meaning and R10 reportability scope. No interpretation of `whsq_notified` or R10 notification requirements is to be implemented by inference.**

This closes [19-r1-milestone-3b-incident-decision-register.md](../docs/implementation-blueprint/19-r1-milestone-3b-incident-decision-register.md) **D6** procedurally — the governance register no longer carries it as an undifferentiated "Pending" item — without resolving, guessing at, or implying an answer to its substance. This is a **controlled compliance decision gap**, not an engineering problem, and is recorded as such.

## 2. Context

[20-r1-milestone-3c-d6-notification-evidence-matrix.md](../docs/implementation-blueprint/20-r1-milestone-3c-d6-notification-evidence-matrix.md) built a cited evidence matrix (V1 source, frozen schema/OpenAPI/Neo4j, WHS Act 2011 Part 3 ss.35-39, WHS Regulation 2011 Chapter 9A §§608B/608J/608K/608L, `07-inference-rules-catalogue.md` R10, `09-regulatory-knowledge-model.md` §6, `04-ai-extraction-specification.md` §6-§7) and found:

- R10 currently propagates an assessment-required state onto `Incident.osr_notified` only. The general, penalty-backed WHS Act s.38 notifiable-incident duty (`whsq_notified`'s evident basis) has no rule representation anywhere in the platform.
- The acronym **"OSR"** is not defined or expanded anywhere in this repository, the WHS Act, or the WHS Regulation — three explanations were identified as *possible* (§5 of IB20) but none is adopted, preferred, or ruled in.
- Chapter 9A itself does not appear to impose a distinct per-incident regulator-notification duty separate from the general s.38 duty — §§608K/608L are proactive identification duties, §608J is a 14-day safety-case-material-change notice; neither matches "notify the regulator this specific incident occurred."

3B's own D6 entry already declined to offer a recommendation, explicitly routing the scope call to Compliance/Legal rather than implementation governance. This ADR does not change that routing — it formalizes the deferral so the governance register reflects a closed procedural state rather than an open-ended "Pending," and attaches the specific, narrow query Compliance/Legal needs to answer (§6).

## 3. Decision and Rationale

**Defer.** No default position is taken on any of D6's substantive questions (what OSR means; whether `whsq_notified` represents a statutory, internal, both, or other notification; which R10 events are reportable; who the responsible notifier is; timing/deadlines; evidence-retention requirements; whether the existing V1 rule is legally current or a stale historical business rule). Answering any of these by inference — from the frozen schema's field names, from V1's UI labels, or from the CCM/D3/D5 deferral precedents — would fabricate a compliance/legal position this project has no authority to assert. Deferring formally, with the query narrowed to specific answerable questions (§6), is the only option consistent with the standing project discipline against inventing structure the evidence doesn't support.

## 4. V1 Evidence — Preserved, Not Reinterpreted

The existing V1 fields and platform artefacts bearing on this question are recorded as **observed V1 behaviour — legal/compliance meaning not yet validated** — not deleted, not silently reinterpreted, not treated as authoritative:

- `incident-report.html:97-98` — "WHSQ Notified?" / "OSR (Chapter 9A) Notified?" form fields, VRTP's own UI labels, meaning not independently verified.
- `safety.incidents.whsq_notified`, `.osr_notified` (`03-postgresql-schema.sql:531-532`) — columns exist, carried from V1 verbatim per the schema's own "ports incident-report.html... near-verbatim" comment (`03:511-512`), not created or renamed by platform design.
- `07-inference-rules-catalogue.md` R10 (`:84-88`) — platform-authored rule, scope as currently written, not additionally extended or narrowed by this ADR.
- `local-automation/run-incident-pipeline.ps1:112` — V1's own informal ADI-signal detection (regex match against Compliance Agent LLM output), evidence of V1's *behaviour*, not a citable legal source.

None of these artefacts is modified by this ADR. All remain exactly as they were.

## 5. Consequences

- R10 remains exactly as specified in `07-inference-rules-catalogue.md` — scoped to `osr_notified` only. It is **not** extended to `whsq_notified`, and no notification-triggering logic is implemented, pending §6's answers.
- `whsq_notified` and `osr_notified` remain manually-set fields in any future Incident implementation — no automated propagation logic for either is built until D6 is substantively resolved.
- This defer does **not** block unrelated, already-approved work: Investigation (`ACR-004`), hazard-linking via `REVEALS` (`ACR-004`, Option A), and incident-scoped Evidence (`ACR-004`) all proceed under their existing approvals, none of which encode any notification semantics. Confirmed by inspection: the `10-openapi.yaml` extension implemented under ACR-004 touches `Investigation`, `/incidents/{id}/hazards`, and `/incidents/{id}/evidence` only — it does not reference, expose, or alter `whsq_notified`/`osr_notified`/R10 in any way.
- The single ongoing risk this defer accepts: any future Incident implementation that includes `whsq_notified`/`osr_notified` as plain, human-set fields (matching their current OpenAPI representation, unaffected by this ADR) does not need to wait for D6 — only *automated notification logic* is blocked. This distinction is deliberate and should not be collapsed in a future implementation GO.

## 6. Compliance/Legal Referral — Attached Query

The following is the **narrow, specific query** to be put to Compliance/Legal, with the evidence in [20-r1-milestone-3c-d6-notification-evidence-matrix.md](../docs/implementation-blueprint/20-r1-milestone-3c-d6-notification-evidence-matrix.md) attached. Per the governing instruction: *do not ask "can we implement this?" — ask these specific questions.*

1. **What does "OSR" mean** in the VRTP/business context, as used in V1's `incident-report.html` ("OSR (Chapter 9A) Notified?") and carried into the platform's `osr_notified` field?
2. Does **`whsq_notified`** represent: (a) a statutory notification (e.g. WHS Act 2011 s.38); (b) an internal/organisational notification; (c) both; or (d) something else?
3. **Which categories of incident/event are reportable or notifiable**, and under what specific rule (statutory citation, Safety Case commitment, or internal VRTP procedure)?
4. **Who is the responsible notifier** for each reportable category identified in Q3?
5. **What timing/deadline requirements apply** to each (e.g. WHS Act s.38's "immediately" / "fastest possible means," or any different internal or Chapter-9A-specific timeframe)?
6. **What evidence must be retained** to demonstrate that notification occurred (or that a "not required" determination was made), and for how long?
7. **Is the existing V1 `whsqNotified`/`osrNotified` field pair legally current**, or is it a historical VRTP business rule that predates or diverges from the applicable regulatory position today?

## 7. Explicit Scope Boundary

This ADR resolves **D6's governance status only** — it converts "Pending, no recommendation" to "Deferred, formally recorded, query attached." It does not:
- Answer any of the seven questions in §6.
- Authorize any notification-logic implementation, for either `whsq_notified` or `osr_notified`.
- Modify R10, `09-regulatory-knowledge-model.md`, the frozen schema, OpenAPI contract, Neo4j model, or ontology.
- Affect D1-D5 or D7, all independently closed.
- Block Investigation, hazard-linking, or incident-Evidence work already approved under ACR-004 (§5).

## 8. Status

**Accepted (2026-08-12) as a formal defer.** D6 is closed procedurally in the governance register; substantively it remains open pending Compliance/Legal's response to §6. A future ADR (or, if the answer requires a schema/API/ontology change, an ACR) will record the substantive resolution once that response is received — not before, and not by this document.
