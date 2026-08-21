# R23 — Mechanism Decision

**Status:** Governance decision record. Documentation only — no application code, schema, OpenAPI, ontology, or Neo4j model change is created or modified by this document. **No implementation authorization is implied by this record.**

## 1. Relationship to Prior Records

[25-r23-decision-framing-record.md](25-r23-decision-framing-record.md) reframed R23's open question as write-vs-gate-vs-hybrid. [26-r23-operational-rule-update.md](26-r23-operational-rule-update.md) removed the closure-gate option by governance decision and narrowed the remaining question to write-vs-record-only. This record answers that narrowed question.

## 2. Decision

**Approved mechanism:**

```text
is_notifiable_incident = TRUE
        ↓
No automatic write to whsq_notified
        ↓
Safety Systems Manager determines outcome
        ├── "Yes"
        └── "No - assessed not required"
```

- **No interim `whsq_notified` value is generated.** `whsq_notified` is not written by any system-triggered logic when `is_notifiable_incident` transitions to `true`.
- **R23 does not modify `whsq_notified`** at the point `is_notifiable_incident` becomes `true`. The field remains at whatever value it already holds (`"Not yet assessed"` by column default, or any prior value) until a human sets it.
- **The Safety Systems Manager enters the final outcome through the existing Incident update mechanism** — i.e. whatever the already-implemented `PATCH /incidents/{id}` endpoint provides for `whsq_notified`, not a new endpoint or a new automated pathway.
- **Investigation and incident closure remain independent of notification status**, unchanged from [26 §2](26-r23-operational-rule-update.md#2-decision).

## 3. Provenance

This is a **governance decision**, not a conclusion drawn from the enum or inferred from the frozen text. It is grounded in the evidence reconciled in [25 §3](25-r23-decision-framing-record.md#3-evidence-gathered) and [26](26-r23-operational-rule-update.md) — no V1 automation was found writing an interim value; V1's own automation (`run-incident-pipeline.ps1`) represents "pending" as a gate marker, not a field value — but the decision itself, that the platform will not invent an interim value either, is the governance authority's determination, recorded from chat (2026-08-20), consistent with the same provenance treatment applied to ADR-006 and to [26 §1](26-r23-operational-rule-update.md#1-relationship-to-prior-record).

## 4. What This Record Does Not Do

- Does not modify `services/incidents/rules.py`.
- Does not modify any ORM model or schema.
- Does not modify `10-openapi.yaml` or any other contract artefact.
- Does not modify any router, service, or test.
- Does not modify ontology or the Neo4j model.
- Does not raise or resolve any ADR/ACR.
- Does not authorize implementation. A separate, explicit implementation GO is required before any code reflecting this decision is written.

## 5. Status

**R23 — Mechanism decided.** All three of R23's open sub-questions (closure-independence, target-value framing, write-vs-record mechanism) are now resolved by governance decision across [26](26-r23-operational-rule-update.md) and this record. R23 remains **unimplemented** — `services/incidents/rules.py` is still the placeholder from 3D-1, and no application code has been written reflecting this decision. Implementation requires its own bounded GO.

## Acceptance Criteria

- [x] Records the approved mechanism precisely, with no ambiguity about what is and is not written.
- [x] Explicitly labeled a governance decision, with provenance traced to docs 25/26's evidence without claiming that evidence alone dictated the answer.
- [x] Explicitly states no implementation authorization is implied.
- [x] No code, schema, OpenAPI, ontology, Neo4j, ADR, or ACR change made in producing this document.
