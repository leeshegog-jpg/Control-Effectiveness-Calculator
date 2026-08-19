# R1 — Incident Management Reconciliation & Decision Review

**Status:** Governance/discovery pass only. No schema, OpenAPI, Neo4j, ontology, or application-code change was made to produce this document. No ADR or ACR is raised by this document. Authorized scope: reconciliation-and-routing pass only (chat GO, 2026-08-19), explicitly **not** an implementation authorization and explicitly **not** pre-labeled as any numbered slice ("3D-2" or otherwise) per the GO's own governance rule.

## 1. Purpose and Authority

3D-1 (persistence: `Incident` ORM model + repository CRUD + tests) is closed — [21 §12](21-r1-milestone-3d-incident-implementation-readiness.md#12-3d-1-closure-record-2026-08-19). Before any further Incident work is authorized, this document reconciles everything decided so far (3A/3B's D1–D7, ACR-004, ACR-005, ADR-003–006, 3D-1's actual delivered scope) against the current frozen baseline and the current verified code state, to establish where the **safe boundary** for the next implementation scope actually sits — and whether any ADR/ACR is required before it can be worked. It does not itself authorize that scope. Per the governing instruction, the next slice is not assumed to be "3D-2" — see §9.

## 2. Method

Two passes, both performed fresh for this document rather than assumed from prior docs:

1. **Documentary reconciliation** — re-read [18](18-r1-milestone-3a-incident-discovery-reconciliation.md), [19](19-r1-milestone-3b-incident-decision-register.md), [20](20-r1-milestone-3c-d6-notification-evidence-matrix.md), [21](21-r1-milestone-3d-incident-implementation-readiness.md), ADR-003/004/005/006, ACR-004/005 in full.
2. **Direct verification against the live repository** (`main` @ `5aed5bd`, 2026-08-19) — not inferred from any document's claims:
   - `apps/api/app/models/safety.py`, `repositories/incidents_repository.py`, `routers/incidents.py`, `services/incidents/{service,rules}.py`, `dto/incidents.py`, `graph/sync_service.py`
   - `tests/**/*incident*`, `packages/shared-types/src` for `Incident` references
   - `docs/knowledge-graph/03-postgresql-schema.sql`, `10-openapi.yaml`, `02-neo4j-node-relationship-model.md`, `07-inference-rules-catalogue.md`

Every finding below is tagged **[doc]** (drawn from and consistent with prior governance docs) or **[verified]** (re-checked directly against the live repository for this pass).

## 3. D1–D7 — What Was Actually Resolved vs. Merely Recommended

All seven 3A decision points now carry a recorded governance disposition — none remain "recommendation only." **[doc]**, cross-checked against [19 §8](19-r1-milestone-3b-incident-decision-register.md#8-outstanding-governance-decisions) and [12-deliverables-index.md](12-deliverables-index.md).

| # | Subject | Recommended (3B) | Actually resolved | Instrument | Baseline touched? |
|---|---|---|---|---|---|
| D1 | Canonical V1 source tree | Root SMS suite only | **Resolved by evidence** — no fresh choice existed | None (No Change) | No |
| D2 | Incident/Investigation/Action = sibling, not chain | Adopt sibling model | **Accepted** | [ADR-003](../../.adr/ADR-003-incident-investigation-action-sibling-structure.md) | No |
| D3 | `incident_type`/`root_cause_category` ontology | Defer | **Accepted** | [ADR-004](../../.adr/ADR-004-incident-ontology-scheme-deferral.md) | No |
| D4 | Investigation/hazards/Evidence OpenAPI surface | Extend additively | **Approved, contract-implemented** 2026-08-11 | [ACR-004](../../.acr/ACR-004-incident-openapi-extension.md) | **Yes** — `10-openapi.yaml` |
| D5 | Six orphan V1 fields | Non-port five; `fReporterRole` via `Person.role_title` | **Accepted** | [ADR-005](../../.adr/ADR-005-incident-orphan-v1-fields-disposition.md) | No |
| D6 | R10/notification scope | Formal defer → substantive resolution | **Resolved** (scope); **Approved + incorporated** 2026-08-15 | [ADR-006](../../.adr/ADR-006-incident-notification-rule-formal-defer.md) + [ACR-005](../../.acr/ACR-005-incident-general-notifiable-incident-rule.md) | **Yes** — `03-postgresql-schema.sql`, `10-openapi.yaml`, `02-neo4j-node-relationship-model.md`, `07-inference-rules-catalogue.md` (new R23; R10 itself untouched) |
| D7 | Governance status of `09`/`07` docs | Explicit sign-off pass | **Accepted** 2026-08-09 — this register itself the sign-off record | None (No formal instrument) | No |

**Finding:** every decision that required a baseline-artefact change (D4, D6) went through ACR and was incorporated. Every decision that didn't (D1, D2, D3, D5, D7) went through ADR or No Change only. No decision was silently converted from recommendation to fact without a named instrument — the discipline held across all seven.

**One residual substantive gap inside D6:** `osr_notified`/"OSR" meaning is explicitly `TO_BE_CONFIRMED` ([ADR-006 §11](../../.adr/ADR-006-incident-notification-rule-formal-defer.md#11-residual-open-item--osr_notified--osr)) — see §6.

## 4. Cross-Decision Dependencies

**[doc]**, re-verified against [19 §5](19-r1-milestone-3b-incident-decision-register.md#5-cross-decision-dependency-matrix): D4 depended on D2 (satisfied — ADR-003 recorded before ACR-004 drafted); D6 depended on D7 (satisfied — D7 accepted before ADR-006 written). Both dependency chains closed in the correct order. No dependency remains open. No new cross-decision dependency is introduced by 3D-1's closure or by this reconciliation.

## 5. Neo4j `sync_incident` — Currently Open

**[verified]** — `grep -n "incident\|Incident" apps/api/app/graph/sync_service.py` returns zero matches. The file implements `sync_hazard` and equivalent functions for `Asset`/`Risk` only. No `sync_incident`, `sync_investigation`, `sync_action`, or relationship-sync function for `REVEALS`/`INVESTIGATED_AS`/`TRIGGERS` exists.

**Governance assessment:** the Neo4j `Incident` node and all three relationships are **already fully specified** in `02-neo4j-node-relationship-model.md` (§3.3, line 56; relationships lines 110–112, including `is_notifiable_incident` per ACR-005 — verified present, §8 below). Writing `sync_incident` would be implementation code that calls the already-approved model, in the same shape as `sync_hazard` ([21 §4](21-r1-milestone-3d-incident-implementation-readiness.md#4-reference-implementation-pattern-hazards-domain)) — it does not add, remove, or reshape any node/relationship the model doesn't already declare. **No ADR or ACR is required to write it.**

## 6. Service/Orchestration Layer — Currently Open

**[verified]** — `services/incidents/service.py` and `rules.py` are both single-line placeholder docstrings; `routers/incidents.py` registers zero routes; `dto/incidents.py` is a placeholder docstring.

**Governance assessment:** the layer-dependency rule (`routers → services → repositories/graph → models`, [13 §3](13-application-foundation-scaffold.md)) is an already-approved architectural pattern, applied identically across every implemented domain (Hazards, Risk, Asset). Building `Incident`'s service/router/DTO layer to the same shape is implementation work over an already-frozen contract (`10-openapi.yaml` `/incidents`, `/incidents/{id}`, `/incidents/{id}/investigation`, `/incidents/{id}/hazards[/{hazardId}]`, `/incidents/{id}/evidence` — all present, verified §8 below). **No ADR or ACR is required.**

## 7. OSR / `osr_notified` — Status Confirmed Unchanged

**[doc, verified no drift]** — `03-postgresql-schema.sql:532` still carries `osr_notified varchar(40) NOT NULL DEFAULT 'Not applicable / under assessment'`, untouched by ACR-005's incorporation (which added `is_notifiable_incident` only, line 780). `ADR-006 §11` remains the authoritative record: **`TO_BE_CONFIRMED`**, one candidate ("Office of State Revenue") checked and ruled out, not to be renamed, merged, or reinterpreted by inference. Tracked as a controlled external dependency in [12-deliverables-index.md](12-deliverables-index.md) Open Items. This reconciliation makes no attempt to resolve it and finds no new evidence bearing on it. **It remains a non-blocking, explicitly out-of-scope item for whatever the next implementation boundary is** — confirmed again here because R23's propagation logic (see §11) sits immediately adjacent to it and must not accidentally absorb it.

## 8. Frozen Baseline Artefacts — Verified Current

**[verified]**, re-read directly rather than assumed from ACR-004/005's closure claims:

- `03-postgresql-schema.sql:515` — `CREATE TABLE safety.incidents` exists with all columns including `whsq_notified` (531), `osr_notified` (532); `:780` — `ALTER TABLE safety.incidents ADD COLUMN is_notifiable_incident boolean NOT NULL DEFAULT false` (ACR-005) present.
- `10-openapi.yaml` — `/incidents` (535), `/incidents/{id}` (544), `/incidents/{id}/run-investigation-pipeline` (553), `/incidents/{id}/investigation` (572), `/incidents/{id}/hazards` (594), `/incidents/{id}/hazards/{hazardId}` (610), `/incidents/{id}/evidence` (620) — full ACR-004 + ACR-005 surface present.
- `02-neo4j-node-relationship-model.md:56` — `Incident` node property list includes `is_notifiable_incident (bool, ACR-005)`; `:110–112` — `REVEALS`, `INVESTIGATED_AS`, `TRIGGERS` all present, sibling shape (no parent/child edge) confirmed.
- `07-inference-rules-catalogue.md:166` — **R23** present, titled "WHS Act s.38 / General Notifiable-Incident Propagation (Design Baseline v1.1 amendment — ACR-005, approved 2026-08-12)"; R10 itself unedited (confirmed by ADR-006 §5's own constraint, not re-verified line-by-line here as it is out of this reconciliation's touch scope).

**Finding: no drift.** Every baseline claim made in 3B/ACR-004/ACR-005/3D-readiness matches the live frozen artefacts exactly. This reconciliation surfaces no new baseline gap.

## 9. V1 Incident Business Logic — No New Gaps Found

**[doc]** — V1 field-shape reconciliation was already exhaustive in 3A (D1, D5) and 3C (D6's evidence matrix, reading WHS Act 2011 Part 3 and WHS Regulation 2011 Chapter 9A in full against V1's `incident-report.html`/`corrective-actions.html`). This reconciliation re-read that evidence and finds no field, rule, or workflow step referenced in V1 that is not already accounted for in the D1–D7 register: the sibling structure (D2), the ontology deferral (D3), the six orphan fields' individual dispositions (D5), and the notification rule (D6/R23) exhaust the V1 surface area 3A identified. No new V1 gap is introduced by 3D-1's closure.

## 10. 3D-1's Actual Delivered Scope — Verified Directly

**[verified]**, matching [21 §12.1](21-r1-milestone-3d-incident-implementation-readiness.md#121-what-was-authorized-and-built) exactly:

| Layer | State |
|---|---|
| `models/safety.py::Incident` | Present — all 21 columns, `class Incident` at line 321 |
| `repositories/incidents_repository.py` | Present — `list_incidents`, `get_incident`, `create_incident`, `update_incident`. No `delete` (correct — not contracted) |
| `routers/incidents.py` | **Placeholder** — zero routes |
| `services/incidents/service.py`, `rules.py` | **Placeholder** — both single-line docstrings |
| `dto/incidents.py` | **Placeholder** |
| `graph/sync_service.py` | **Zero** incident/Incident references |
| Tests | `tests/unit/test_incident_persistence_model.py`, `tests/integration/test_incidents_persistence.py` — persistence layer only |
| `packages/shared-types/src` | **Zero** `Incident` references — not regenerated against ACR-004/005's OpenAPI surface |

**No drift from the closure record.** 3D-1 delivered exactly persistence (model + repository + tests), nothing more, nothing less.

## 11. ADR/ACR Requirement — Applied to Every Remaining Piece of Work

Using the same single gate 3B established ([19 §3](19-r1-milestone-3b-incident-decision-register.md#3-decision-methodology)): *does the work modify a Design Baseline v1.1 artefact?* If no, and it's pure implementation-time interpretation of an already-frozen artefact, it needs no fresh governance instrument.

| Remaining work item | Modifies a baseline artefact? | Governance route |
|---|---|---|
| `Incident` DTO + `/incidents`, `/incidents/{id}` router endpoints | No — contract already frozen (§8) | **No Change** — implementation only |
| `Investigation` model/repo/service/DTO + `/incidents/{id}/investigation`, `sync_investigation` + `INVESTIGATED_AS` | No — ACR-004 already covers the contract; ADR-003 already covers the sibling shape | **No Change** — implementation only |
| `incident_hazards` join + `/incidents/{id}/hazards[/{hazardId}]`, `REVEALS` sync | No — ACR-004 Option A already covers the shape | **No Change** — implementation only |
| `/incidents/{id}/evidence` wiring | No — reuses existing generic Evidence, per ACR-004 §9 | **No Change** — implementation only |
| `sync_incident` (Neo4j) | No — node/relationships already fully specified (§5, §8) | **No Change** — implementation only |
| `Incident` service/orchestration layer | No — layer pattern already approved ([13 §3](13-application-foundation-scaffold.md)) | **No Change** — implementation only |
| R23 propagation logic (`is_notifiable_incident` → `whsq_notified` default-out) | No — R23 itself already incorporated (ACR-005); this is service-rule code implementing an existing rule | **No Change** — implementation only |
| `fReporterRole` resolution via `Person.role_title` | No — ADR-005 already specifies the resolution path | **No Change** — implementation only |
| Integration/unit tests, `shared-types` regeneration | No — test/tooling work over existing contract | **No Change** — implementation only |
| `run-investigation-pipeline` | N/A — **excluded from this boundary entirely** (§12) | Not assessed here — separate AI-layer subsystem |
| "Safety Case Demonstration evidence" (Incident ↔ `SafetyCaseClaim`/`Demonstration` linkage) | **Yes, if ever built** — no baseline artefact currently defines this relationship ([21 §9](21-r1-milestone-3d-incident-implementation-readiness.md#9-findings-that-adjust-the-proposed-scope)) | **ACR required** — not grounded in the frozen baseline, not part of any safe boundary until one is raised |
| Any logic reading, writing, or branching on `osr_notified` | Would require resolving `TO_BE_CONFIRMED` first — see §7 | **Blocked**, not routed — pending Compliance/Legal, out of scope |

**Finding:** the entire remaining CRUD/sync/service/rules surface for Incident, Investigation, hazard-linking, and Evidence is **already governed** — every baseline artefact it touches is already frozen and correct. **No new ADR or ACR is required** to proceed with any of it. The only two items requiring separate governance action before they could be pursued are the Safety Case linkage (needs its own ACR) and anything OSR-dependent (blocked pending Compliance/Legal).

## 12. Safe Boundary for the Next Implementation Scope

Everything in §11's "No Change — implementation only" rows sits inside the safe boundary: it requires no further ADR/ACR, is fully specified by the frozen schema/OpenAPI/Neo4j model, and follows an already-approved architectural pattern (the Hazards precedent). Explicitly **outside** the boundary, and not to be included in any GO drawn from this reconciliation without separate governance action first:

- `run-investigation-pipeline` — belongs to the AI Extraction Specification's Investigation Agent → Compliance Agent → Safety Case Trigger pipeline, a materially different subsystem ([21 §9](21-r1-milestone-3d-incident-implementation-readiness.md#9-findings-that-adjust-the-proposed-scope)).
- Any Incident ↔ Safety Case / Demonstration / `SafetyCaseClaim` linkage — ungrounded in the current baseline, needs its own ACR.
- Any automated logic reading, writing, or branching on `osr_notified` — blocked pending Compliance/Legal determination of "OSR."

## 13. Critical Governance Rule — Next Slice Naming

Per the GO's explicit instruction, this document does **not** designate the next implementation scope as "3D-2" or any other pre-assigned label. [21 §7](21-r1-milestone-3d-incident-implementation-readiness.md#7-proposed-slice-structure)'s original 8-slice breakdown already diverged once from what was actually GO'd and built (3D-1's own scope narrowed mid-execution — sync_incident and the service layer were named in that slice but not delivered under it, per [21 §12.1](21-r1-milestone-3d-incident-implementation-readiness.md#121-what-was-authorized-and-built)). Continuing to treat that original numbering as binding would repeat the exact drift this reconciliation exists to correct. The safe boundary in §12 describes **what may be worked**, not **how it will be sliced or ordered** — that remains a decision for whoever issues the next GO, made explicitly at that time, not inherited from a superseded proposal.

## 14. Decision Register — Updated Status

All of D1–D7: **closed**, no change from §3. No new decision point (D8+) is opened by this reconciliation — every item examined in §5–§11 resolved via the existing gate without requiring a fresh decision entry. The only tracked-open items after this pass:

- Neo4j `sync_incident` + Incident service/orchestration layer — open, ungated, no governance blocker (§5, §6, §11).
- `osr_notified`/"OSR" — `TO_BE_CONFIRMED`, external dependency, non-blocking (§7).
- Safety Case Demonstration linkage — ungrounded, would need its own ACR if pursued (§11, §12).
- `run-investigation-pipeline` — separate AI-layer subsystem, not part of this domain's CRUD boundary (§12).

## 15. What This Document Does Not Do

- Does not create, modify, or migrate any schema, model, contract, or code.
- Does not raise or resolve any ADR or ACR.
- Does not authorize any implementation work, including anything listed as "No Change" in §11 — "no governance instrument required" is not the same as "authorized to build."
- Does not name, number, or scope the next implementation slice.
- Does not resolve OSR.

## 16. Recommended Next Step

The governance authority reviews this reconciliation and, if it concurs with §11–§12's findings, issues an explicit, separately-scoped GO naming its own bounded piece of work from within the §12 boundary (e.g. "GO — Incident DTO + `/incidents`, `/incidents/{id}` router endpoints only," or "GO — `sync_incident` Neo4j sync only") — mirroring 3D-1's own bounded-GO discipline, not a single GO for the whole remaining boundary at once.

## Acceptance Criteria

- [x] D1–D7 reconciled against what was recommended vs. actually resolved, with instrument named for each (§3).
- [x] Cross-decision dependencies re-verified, none open (§4).
- [x] `sync_incident`, service/orchestration layer, and OSR status each independently assessed against the ADR/ACR gate (§5–§7, §11).
- [x] Frozen schema/OpenAPI/Neo4j artefacts verified directly against the live repository, not assumed from prior docs' claims (§8).
- [x] V1 business logic re-checked for gaps not already captured by D1–D7 (§9).
- [x] 3D-1's actual delivered code state verified directly (§10).
- [x] Every remaining piece of Incident-domain work assessed individually against the single stated ADR/ACR gate, not bulk-assumed (§11).
- [x] Safe boundary stated explicitly, with explicit exclusions (§12).
- [x] Next implementation slice explicitly left unnamed and unnumbered, per the governing rule (§13).
- [x] No ADR, ACR, schema, API, ontology, Neo4j, or code change made in producing this document.
