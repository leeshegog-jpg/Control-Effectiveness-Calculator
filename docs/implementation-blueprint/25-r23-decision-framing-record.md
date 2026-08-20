# R23 — Decision Framing Record

**Status:** Decision-framing record. Documentation only — no application code, schema, OpenAPI enum, ontology, Neo4j model, ADR, or ACR is created or modified by this document. This document narrows the open R23 question; it does not answer it.

## 1. Why This Record Exists

During implementation of "R1 Incident Management — Investigation API & Hazard-Link Graph Sync" ([24 §5](24-r1-incident-investigation-hazard-graph-sync-closure.md#5-r23--specification-gap-not-resolved)), R23 propagation was found to have an unspecified target: the frozen catalogue entry names R23's trigger and target field but not the literal `whsq_notified` value it should write. A subsequent read-only reconciliation (chat, 2026-08-20) found that the underlying grounding text does not describe a value-write mechanism at all — it describes a validation gate. This record captures that finding and reframes the open question accordingly, so a future decision is made against the corrected question rather than the original (and now withdrawn) "which enum value" framing.

## 2. Original Framing — Withdrawn

The question as originally posed — *"What exact `whsq_notified` enum value does R23 require when `is_notifiable_incident` transitions to `true`?"* ([24 §5](24-r1-incident-investigation-hazard-graph-sync-closure.md#5-r23--specification-gap-not-resolved)) — presupposed that R23 is a field-mutation rule: on trigger, write some specific value into `whsq_notified`. That presupposition is not supported by the evidence gathered in this reconciliation (§3). It is withdrawn, not answered.

## 3. Evidence Gathered

**3.1 Frozen grounding text** (`09-regulatory-knowledge-model.md:123`, §6 — the authoritative regulatory-determination source both R10's and R23's catalogue entries summarize):

> "An `Incident` REVEALS a `Hazard` whose `Risk` has `is_serious_risk = true` (or a `Consequence` with `flag_608b = true`) → `osr_notified` is **forced out of** any 'not yet assessed' default, **requiring explicit human determination before closure**."

This describes a constraint on what state is allowed to persist through to closure, not an instruction to write a specific replacement value. "Forced out of the default" reads as *may not remain at the default*, not *must become value X*.

**3.2 R10's catalogue paraphrase** (`07-inference-rules-catalogue.md:84-88`) already compresses §6's language to "propagates a 'notification assessment required' state onto `Incident.osr_notified` (defaults it to `'Not applicable / under assessment'`...)" — notably, R10's paraphrase *does* name a literal target value, and that value happens to equal `osr_notified`'s own column default. Whether R10's implementation (itself still unbuilt — `services/incidents/rules.py` has no R10 logic either) should mirror §6's gate language or its own catalogue's paraphrase is not resolved by this record; flagged only as a related open question, not decided here.

**3.3 R23's catalogue entry** (`07-inference-rules-catalogue.md:166-170`) states it "mirrors R10's structure exactly, applied to the sibling field" and describes moving `whsq_notified` "out of `'Not yet assessed'`" — but, unlike R10's paraphrase, does not name a target value at all.

**3.4 V1 evidence** — no automation found writing to `whsqNotified`:
- `incident-report.html:97` — `fWhsq` is a plain manual `<select>`, four options, no default-changing script logic found in the surrounding form handlers.
- `local-automation/run-incident-pipeline.ps1:97` — V1's own Compliance Agent automation writes `notification-decision: [PENDING GATE 1]` into a generated compliance-assessment document — a literal gate/placeholder marker, not any of the four `whsqNotified` enum values. This is V1's own precedent for how it represents "notification decision pending," and it is a gate marker, not a value assignment.

**3.5 ADR-006 §9** — the Safety Systems Manager responsible-notifier determination and the 48-hour/10-year timing/retention determinations. This governs *who* and *by when*, not *what the field's interim state should be* or *whether the mechanism is a write or a gate*. Not used to infer either.

## 4. Reframed Question

> **Does R23 require the platform to write a value into `Incident.whsq_notified` on trigger, or does R23 require the platform to enforce a validation gate — blocking incident closure while `is_notifiable_incident = true` and `whsq_notified = "Not yet assessed"` — with the field's actual value set only by explicit human determination?**

Three candidate mechanisms, none selected by this record:

- **Option A — Validation gate only.** No automatic field write. `PATCH /incidents/{id}` (or whichever operation represents "closure") rejects a transition to a closed state while `is_notifiable_incident = true` and `whsq_notified = "Not yet assessed"`. The Safety Systems Manager's explicit determination is the only thing that ever changes `whsq_notified` away from its default.
- **Option B — Hybrid.** An interim value is written on trigger (the original "which enum value" question, now understood to still require textual grounding this reconciliation did not find) *and* the closure-time gate from Option A still applies.
- **Option C — Other, explicitly authorised mechanism.** Only if a source not yet examined provides one; not identified in this reconciliation.

## 5. What This Decision Must Be Checked Against

1. `09-regulatory-knowledge-model.md` §6 (§3.1 above).
2. R10 and R23's catalogue entries (§3.2, §3.3 above), including whether R10's own eventual implementation should be reconciled with this same question.
3. V1 `incident-report.html` (§3.4 above).
4. V1 automation behaviour, `run-incident-pipeline.ps1` (§3.4 above).
5. The existing `Incident` state/closure model — `safety.incidents.status` (`Open`/`Under Investigation`/`Closed`) and whatever operation is understood to represent "closure" for this purpose.
6. ADR-006 §9's Safety Systems Manager / 48-hour / 10-year determination — as the *responsible-authority and timing* answer only, explicitly not a source for the write-vs-gate mechanism question (§3.5 above).

## 6. Explicit Governance Boundary

- ADR-006 §9's responsible-notifier determination is retained exactly as recorded — it answers "who," not "what mechanism." This record does not touch, reinterpret, or extend it.
- No enum value is selected by this record, including in Option A/B's illustrative text above — none of it is authorized for implementation.
- No OpenAPI, schema, ontology, or Neo4j change is made.
- No ADR or ACR is raised. If the eventual decision determines a new column, state value, or contract change is required (e.g. Option A's closure-gate needing a distinct rejection response, or Option B needing a genuinely new enum value not currently in `10-openapi.yaml:1174`), that assessment is a separate, not-yet-performed step — not pre-judged here.
- `services/incidents/rules.py` remains untouched.

## 7. Status

**R23 — OPEN / SPECIFICATION FRAMING DECISION REQUIRED.**

The question in §4 is now the governing question, superseding the original "which value" framing (§2, withdrawn). No implementation GO may be issued for R23 until this reframed question is answered by the governance/Compliance authority.

## Acceptance Criteria

- [x] Original "which enum value" framing explicitly withdrawn, not silently carried forward.
- [x] Evidence re-traced directly to source text (`09 §6`, V1 HTML, V1 PowerShell automation) rather than reasoned from the catalogue paraphrases alone.
- [x] Reframed question stated precisely, with three candidate mechanisms named and none selected.
- [x] ADR-006 §9's responsible-authority determination explicitly kept separate from the mechanism question.
- [x] No code, schema, OpenAPI, ontology, Neo4j, ADR, or ACR change made in producing this document.
