# ADR-006: Incident Domain — D6 (Notification-Rule Scope) Formal Defer, then Resolved

**Status:** Accepted (2026-08-12) — **Resolved (2026-08-12)**. §1–§7 below are the original formal-defer record, unchanged, preserved for the audit trail. §9–§11 record the determination subsequently received and its consequences. One item from the original referral (§6 Q1, "OSR" meaning) remains **unanswered** and is carried forward as a residual open item, not silently closed — see §9.

**Provenance note:** the determination in §9 was provided directly in chat by the project sponsor/governance authority — the same authority that has approved every ACR/ADR in this project to date (ACR-002/003/004, D2/D7 acceptance). It is recorded as that, not represented as a separately-sourced, independently-documented Compliance/Legal sign-off. This distinction is preserved deliberately, per this project's own evidence-provenance discipline — see §9.

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

## 8. Status (original defer — superseded by §9–§11 below)

**Accepted (2026-08-12) as a formal defer.** D6 was closed procedurally in the governance register; substantively it remained open pending Compliance/Legal's response to §6.

---

## 9. Determination Received (2026-08-12)

Answers to §6's referral, provided in chat by the project sponsor/governance authority (see provenance note, top of document):

| # | Question | Determination |
|---|---|---|
| 1 | What does "OSR" mean? | **Not answered — remains open.** Carried forward as a residual item (§11). Not guessed at, not defaulted. |
| 2 | `whsq_notified` classification | **Internal** notification (not statutory, not "both," not "other" per the §6 Q2 option set). |
| 3 | Reportable categories under R10 | **Extended** — R10 is to also cover the general WHS Act incident categories (i.e. the s.35/36/37 notifiable-incident test), not remain scoped to the Chapter 9A/`osr_notified` trigger alone. |
| 4 | Responsible notifier | Safety Systems Manager. |
| 5 | Notification timeframe | 48 hours. |
| 6 | Evidence retention | 10 years. |
| 7 | Is the V1 rule legally current? | **Yes** — confirmed current, no revision required. |

**Reconciling Q2 and Q3:** Q2 classifies `whsq_notified` as an *internal* notification, while the evidence matrix (IB20 row 2) identified WHS Act s.38 as a statutory, penalty-backed duty. Q3's determination — extend R10 to the general WHS Act categories — is the more operative instruction for scope purposes: R10 is authorized to propagate an assessment-required state for the s.35/36/37 test, addressed to an internally-designated responsible party (Safety Systems Manager) on a 48-hour/10-year cycle, regardless of whether that internal process is itself the s.38 statutory notification or sits alongside it. This ADR does not resolve which — that nuance is not necessary to specify the R10 extension's mechanics, and is noted rather than adjudicated.

**`osr_notified` is explicitly not touched by this determination.** Q1 (OSR meaning) is unanswered, so `osr_notified`/R10's existing Chapter-9A behaviour is left exactly as `07-inference-rules-catalogue.md` currently specifies it (§4/§5 above) — no new timeframe, notifier, or retention rule is applied to it. Applying Q3–Q6's answers to `osr_notified` as well, without knowing what "OSR" represents, would repeat exactly the invented-semantics risk this whole D6 track exists to prevent.

## 10. Impact Assessment — Is an ACR Required?

Per the governing instruction: assess against OpenAPI, PostgreSQL, notification workflow, incident state model, regulatory reporting fields, and automated rules.

- **PostgreSQL:** `incidents.whsq_notified` already exists (`03:531`), no new column strictly required to *store* a notification-required state — it's the same enum already in the schema. **However:** R10's `osr_notified` mechanism is driven by a dedicated upstream trigger flag (`Risk.is_serious_risk` / `Consequence.flag_608b`, `03:383`, `:197`). No equivalent trigger flag exists for the general WHS Act s.35/36/37 test — nothing on `incidents` currently marks "this event meets the general notifiable-incident definition." Without one, R10 cannot mirror its existing pattern for `whsq_notified`. **This is very likely a new column** (e.g. a boolean or derived-state field), which would require an ACR.
- **OpenAPI:** No change needed for `whsq_notified` itself (already represented, `10-openapi.yaml:1104`). A new trigger field (previous bullet), if added, would need OpenAPI representation too.
- **Notification workflow / automated rules:** **Yes.** Extending R10's actual scope is an edit to `07-inference-rules-catalogue.md`, a named, approved Design Baseline v1.1 artefact (`docs/implementation-blueprint/12-deliverables-index.md` Phase 1 table: "7 | Inference Rules Catalogue | ... | Approved — Design Baseline v1.1"). This is the same class of artefact D4 encountered with `10-openapi.yaml` — additive-only or not, editing it requires the ACR process (`02-development-standards.md` §7), not a direct edit and not an ADR alone.
- **Incident state model / regulatory reporting fields:** No new state values proposed for `whsq_notified` itself; the question is entirely about what triggers and drives it, covered above.

**Conclusion: an ACR is required** before R10's definition in `07-inference-rules-catalogue.md` can be extended, and before any new trigger-flag column (if confirmed necessary during that ACR's drafting) is added to `incidents`. **This ACR has not been raised by this document.** Consistent with D4's precedent, raising it is a separate, not-yet-authorized action.

## 11. Residual Open Item — `osr_notified` / "OSR"

**Status: `TO_BE_CONFIRMED`** — formally tagged, not merely "unanswered," per this project's standard convention for unresolved-but-tracked items (matching `requirements.status` enum, `10-openapi.yaml:1191`, and the WHS Reg Schedule 19/18C precedents in `09-regulatory-knowledge-model.md`).

**One candidate explanation checked and ruled out (2026-08-12):** "Office of State Revenue" — a real Queensland Government body (Queensland Treasury), but a payroll-tax/duties/royalties function with no plausible connection to WHS major-amusement-park incident notification. Checked against external web sources by the project sponsor; found no credible source connecting it to this context. **Ruled out, not adopted.** This does not narrow the remaining candidate set meaningfully — it removes one specific wrong guess, it does not supply the right answer. The three candidates originally listed in [20-r1-milestone-3c-d6-notification-evidence-matrix.md](../docs/implementation-blueprint/20-r1-milestone-3c-d6-notification-evidence-matrix.md) §5 remain equally open.

**Explicit implementation constraint:** `osr_notified` is **not** to be renamed, merged into, or reinterpreted as `whsq_notified` (or any expanded terminology) on the strength of this ADR or ACR-005. The two fields represent separately identified, non-conflated concerns:
- `whsq_notified` — WHS Act 2011 s.38, general notifiable-incident duty. Previously had zero rule representation; now resolved (§9) and implemented via [ACR-005](../.acr/ACR-005-incident-general-notifiable-incident-rule.md) (Pending Approval).
- `osr_notified` — meaning `TO_BE_CONFIRMED`. Untouched by §9's determination and by ACR-005. R10's existing Chapter-9A behaviour (`07-inference-rules-catalogue.md:84-88`) stays exactly as specified — no new timeframe, notifier, or retention rule applied to it.

This is not blocking for the `whsq_notified`/general-WHS-Act extension (§9, ACR-005), and not blocking for Investigation/hazard-linking/incident-Evidence (ACR-004, unaffected throughout). It does block ever extending Q3–Q6's parameters to `osr_notified`, and blocks fully closing D6 end-to-end — resolution requires primary-source or V1-provenance evidence establishing what "OSR" actually means, not a plausible guess.

## 12. Status

**Resolved (2026-08-12) for `whsq_notified`'s scope, with `osr_notified`/"OSR" carried forward as `TO_BE_CONFIRMED` (§11).** D6's governance disposition: determination received and recorded (§9); scope decision made and implemented as a proposal via [ACR-005](../.acr/ACR-005-incident-general-notifiable-incident-rule.md) (raised 2026-08-12, Pending Approval); `osr_notified`/OSR meaning explicitly carved out, tagged `TO_BE_CONFIRMED`, one wrong-guess candidate ruled out, not to be renamed or reinterpreted by inference. No schema/OpenAPI/code change made by this ADR — ACR-005 proposes, does not itself implement. Implementation remains separately gated — this ADR authorizes a requirement, not a build.
