# R23 — Closure Record (No Implementation Required)

**Status:** Closure record. Documentation only — no application code, schema, OpenAPI, ontology, or Neo4j model change is made by this document. `services/incidents/rules.py` is not modified.

## 1. Relationship to Prior Records

[25](25-r23-decision-framing-record.md), [26](26-r23-operational-rule-update.md), and [27](27-r23-mechanism-decision.md) resolved R23's three open sub-questions by governance decision: closure/investigation independence from notification status, no invented interim `whsq_notified` value, and no automatic write on `is_notifiable_incident` trigger — the Safety Systems Manager records the final outcome through the existing Incident update mechanism. This record closes R23 following the read-only implementation-boundary inspection those decisions authorized.

## 2. Read-Only Verification Performed

Checked directly against the live repository (`main @ 66a6ca6`), following the GO'd sequence — inspection before any code change:

- `apps/api/app/services/incidents/rules.py` — confirmed unchanged, still the 3D-1 placeholder docstring, no logic of any kind.
- `apps/api/app/services/incidents/service.py:104-137` (`update_incident`, wired to `PATCH /incidents/{id}` via `routers/incidents.py:111/155`) — confirmed `whsq_notified` is accepted as a free-form optional field and persisted exactly as supplied by the caller, with no gating, no validation restriction, and no derivation from `is_notifiable_incident` or any other field.
- Confirmed no code path anywhere in the Incident domain (`create_incident`, `update_incident`, `sync_incident`, the router, or `rules.py`) writes to `whsq_notified` automatically on any trigger, including `is_notifiable_incident` transitioning to `true`.

## 3. Finding

**The approved R23 mechanism is already satisfied by the existing implementation, delivered under "R1 Incident Management — API, Service & Graph Synchronisation" (PR #21).** No application-code change is required to implement R23 as decided:

- `PATCH /incidents/{id}` accepts `whsq_notified`.
- The supplied value is persisted exactly as provided — no transformation, no default substitution beyond the column's own `NOT NULL DEFAULT 'Not yet assessed'`.
- No automatic write occurs when `is_notifiable_incident` becomes `true` — confirmed by absence, not by any explicit guard.
- The Safety Systems Manager can enter either approved outcome (`"Yes"` / `"No - assessed not required"`) through the existing endpoint today.
- Investigation (`services/investigations`) and incident closure (`Incident.status`) have no dependency on `whsq_notified` anywhere in the codebase — confirmed independent, consistent with [26 §2](26-r23-operational-rule-update.md#2-decision).

## 4. `rules.py` — Deliberately Unchanged

`services/incidents/rules.py` is not modified by this closure. No marker, comment, or docstring update was added. Writing a no-op reference into `rules.py` was considered and explicitly declined by the governance authority: it would be a code change with no functional purpose, and risks implying a rule exists in code where the approved behaviour is deliberately the *absence* of automatic behaviour. This record is the documentary trail instead.

## 5. Approved Mechanism (Preserved, Unchanged From 26/27)

```text
is_notifiable_incident = TRUE
        ↓
No automatic write to whsq_notified
        ↓
Safety Systems Manager records outcome via PATCH /incidents/{id}
        ├── "Yes"
        └── "No - assessed not required"

Investigation and incident closure: independent of whsq_notified, always.
```

## 6. Governance Sequence

| PR | Record | Disposition |
|---|---|---|
| #25 | [Decision Framing Record](25-r23-decision-framing-record.md) | Reframed the open question (write vs. gate vs. hybrid); withdrew the original "which enum value" framing |
| #26 | [Operational Rule Update](26-r23-operational-rule-update.md) | Removed the closure-gate option; narrowed to write-vs-record-only |
| #27 | [Mechanism Decision](27-r23-mechanism-decision.md) | Decided no automatic write; SSM records final outcome |
| this record | Closure | Confirms the decided mechanism requires no code; `rules.py` unchanged; R23 CLOSED |

## 7. Explicitly Out of Scope

This closure does not combine, scope, or advance: Action (including its own `completion_date`/`notes` OpenAPI gap), Evidence wiring, `fReporterRole`, `shared-types` regeneration, or `osr_notified`. Each remains open, tracked separately, each requiring its own reconciliation and GO.

## 8. Status

**R23 — CLOSED. No implementation required.**

## Acceptance Criteria

- [x] Read-only verification performed and recorded before any code-change decision, per the GO'd sequence.
- [x] Finding stated precisely: existing behaviour already satisfies the decided mechanism, confirmed by direct inspection of `service.py`/`router.py`, not assumed.
- [x] `rules.py`'s non-modification explicitly justified, not left implicit.
- [x] Approved mechanism restated for the permanent record.
- [x] Full governance sequence (PRs #25-#27 + this closure) cross-referenced.
- [x] No other Incident-domain item combined into this closure.
- [x] No code, schema, OpenAPI, ontology, Neo4j, ADR, or ACR change made in producing this document.
