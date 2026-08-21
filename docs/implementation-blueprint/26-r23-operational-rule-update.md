# R23 — Operational Rule Update (Closure Decoupled)

**Status:** Governance decision record. Documentation only — no application code, schema, OpenAPI enum, ontology, Neo4j model, ADR, or ACR is created or modified by this document.

## 1. Relationship to Prior Record

[25-r23-decision-framing-record.md](25-r23-decision-framing-record.md) reframed R23's open question as write-vs-gate-vs-hybrid, based on `09-regulatory-knowledge-model.md` §6's literal text ("...requiring explicit human determination **before closure**"). This record supersedes that framing's "before closure" premise with an explicit operational decision from the project governance authority (chat, 2026-08-20): **notification status must not gate incident closure or investigation continuation.**

**Provenance note, same treatment as [ADR-006](../../.adr/ADR-006-incident-notification-rule-formal-defer.md)'s determination:** this decision is recorded as received from the project sponsor/governance authority in chat. It is not independently sourced from Compliance/Legal, and it explicitly departs from §6's literal "before closure" language — that departure is the governance authority's call to make, not a reconciliation finding. §6's text is not amended by this record; this record documents that the platform's operational behaviour will not implement §6's closure-gate reading literally.

## 2. Decision

- `is_notifiable_incident` records the statutory classification (unchanged — already implemented, ACR-005).
- `whsq_notified` records the Safety Systems Manager's notification determination/outcome.
- **Investigation and incident closure proceed independently of `whsq_notified`'s value.** The earlier "block closure while `whsq_notified = 'Not yet assessed'`" option ([25 §4](25-r23-decision-framing-record.md#4-reframed-question) Option A, and the closure-gate half of Option B) is withdrawn. No validation gate on closure is authorized.

## 3. Narrowed Remaining Question

With the closure-gate option removed, R23's open question is narrower than [25 §4](25-r23-decision-framing-record.md#4-reframed-question)'s original three-way framing:

> When `is_notifiable_incident` becomes `true`, does the system automatically write an interim value into `whsq_notified`, or does it only route the notification assessment to the Safety Systems Manager and record whatever outcome they enter (`"Yes"` / `"No - assessed not required"`), with `whsq_notified` never machine-written to an interim state?

**Still no authoritative grounding found for an automatic interim write** — this conclusion from [25 §3](25-r23-decision-framing-record.md#3-evidence-gathered) is unchanged by this record; nothing in this decision supplies new evidence for or against a write.

## 4. R23 Disposition (Recommended by Governance Authority, Not Yet Finalized as an Implementation Instruction)

> When an incident is determined to be a notifiable incident, the system must identify/route the notification assessment to the Safety Systems Manager. The system must not prevent continuation or closure of the investigation based on `whsq_notified`.

`whsq_notified`'s exact write behaviour (system-written interim value vs. purely human-entered outcome) remains **TO BE CONFIRMED** until the authoritative workflow settles that specific point. This record fixes the closure-independence rule; it does not fix the write-mechanism question.

## 5. What Changed vs. What Remains Open

| Item | Status after this record |
|---|---|
| Closure/investigation gated on `whsq_notified` | **Removed as an option** — closure and investigation proceed independently |
| `is_notifiable_incident` vs `whsq_notified` roles | Clarified: classification vs. determination/outcome |
| Does the system write an interim `whsq_notified` value on trigger? | **Still open** — `TO_BE_CONFIRMED`, no grounding found either way |
| Safety Systems Manager as responsible notifier | Unchanged, [ADR-006 §9](../../.adr/ADR-006-incident-notification-rule-formal-defer.md#9-determination-received-2026-08-12) |
| `osr_notified`/"OSR" meaning | Unchanged, still `TO_BE_CONFIRMED`, out of scope here |

## 6. Explicit Governance Boundary

- No code change. No schema, OpenAPI enum, ontology, or Neo4j change.
- No ADR or ACR raised.
- `services/incidents/rules.py` remains untouched.
- §3's narrowed question is not answered by this record — an implementation GO for R23 still requires that answer first.

## 7. Status

**R23 — OPEN. Closure-independence rule fixed (§2). Write-mechanism question (§3) remains TO BE CONFIRMED.** No implementation GO may be issued for R23 until §3 is answered.

## Acceptance Criteria

- [x] Records the closure-independence decision with explicit provenance (chat governance authority, same treatment as ADR-006), not presented as a reconciliation finding.
- [x] States plainly that this decision departs from `09 §6`'s literal "before closure" text, without amending that text.
- [x] Narrows the remaining question precisely, without answering it.
- [x] No code, schema, OpenAPI, ontology, Neo4j, ADR, or ACR change made in producing this document.
