# R1 Incident Management — Investigation API & Hazard-Link Graph Sync: Closure Record

**Status:** Closure record. Documentation only — no application code, schema, OpenAPI, ontology, or Neo4j model change is made by this document. No new implementation is authorised by this document.

## 1. Summary

```text
Implementation slice:
R1 Incident Management — Investigation API & Hazard-Link Graph Sync

Status:
CLOSED (R23 explicitly excluded — see §5)

main:
e8c531b

Merge CI:
12/12 green

Delivered:
11 files, +440/-24

Delivered items:
Investigation ORM model / DTOs / repository / service
GET/POST/PATCH /incidents/{id}/investigation
sync_investigation / INVESTIGATED_AS
Hazard-link REVEALS synchronisation (link + unlink)

Explicit exclusions:
Action                          not implemented
Evidence wiring                 not implemented
fReporterRole                   not implemented
shared-types regeneration       not performed
osr_notified                    untouched, TO_BE_CONFIRMED
R23 propagation                 not implemented — specification gap, see §5
```

## 2. Authorization Trail

- [22-r1-incident-reconciliation-decision-review.md](22-r1-incident-reconciliation-decision-review.md) — established that Investigation API+sync, hazard-link `REVEALS` sync, and R23 required no new ADR/ACR.
- Pre-implementation reconciliation (chat, 2026-08-20, read-only): determined the seven remaining Incident-domain items did not form one coherent slice; identified Action's OpenAPI contract gap (`completion_date`/`notes`), Evidence's `verification_activity_id`-required service coupling, and `fReporterRole`'s missing exposure path as items needing separate scoping — none of which are part of this slice.
- Explicit implementation GO (chat, 2026-08-20): named scope "R1 Incident Management — Investigation API & Hazard-Link Graph Sync," in/out lists as recorded in that GO.
- Mid-implementation stop (chat, 2026-08-20): R23's target `whsq_notified` value found unspecified in the frozen `07-inference-rules-catalogue.md` entry; reported rather than resolved by inference, per the GO's explicit instruction. Confirmed by the user as the correct disposition — R23 excluded from this slice's scope, `services/incidents/rules.py` left untouched.

## 3. What Was Verified For This Closure

Re-verified directly against the live repository and GitHub, not assumed from any prior report:

| Check | Result |
|---|---|
| `main` HEAD | `e8c531b` |
| Working tree | Clean (pre-existing untracked clutter — `.claude-flow/`, WHS/ISO source PDFs/md, html files, `ruvector.db` — unrelated to this or any prior slice, left untouched) |
| PR #23 state | `MERGED`, merge commit `e8c531bec9112bd19a0b37f7e1cdd2e45cc7e053`, merged by `leeshegog-jpg` |
| Merge-commit CI | 12/12 `success` (7 PR-validation jobs + `build`, `deploy`, `report-build-status`, `Container build — api`, `Container build — web`) |
| Implementation diff scope (`c2372b5..e8c531b`) | Exactly 11 files, +440/-24 — matches the authorized set with no extras |
| `services/incidents/rules.py` present in diff? | **No** — confirmed absent from the merge-commit diff, consistent with R23 being unimplemented |

## 4. Delivered, Within the Authorized Boundary

- `apps/api/app/models/safety.py` — new `Investigation` ORM mapping (`safety.investigations`, 1:1 via `incident_id UNIQUE`, `method` carried as free text exactly as the frozen schema specifies — not resolved, not defaulted).
- `apps/api/app/dto/investigations.py` — `InvestigationInput`/`InvestigationOut`, field-for-field against the frozen `Investigation`/`InvestigationInput` OpenAPI schema.
- `apps/api/app/repositories/investigations_repository.py` — `get_investigation_by_incident`/`create_investigation`/`update_investigation`.
- `apps/api/app/services/investigations/service.py` — new, deliberately separate module from `services/incidents` (ADR-003 sibling structure — Investigation is not nested under Incident's service).
- `apps/api/app/routers/incidents.py` — `GET/POST/PATCH /incidents/{id}/investigation`, including the contracted `409` on double-create (`investigations.incident_id UNIQUE`).
- `apps/api/app/graph/sync_service.py` — new `sync_investigation`/`get_investigation_node` (`MATCH`es the existing `Incident` node, `MERGE`s `Investigation` + `INVESTIGATED_AS`); new `sync_incident_hazard_link`/`unsync_incident_hazard_link` (`REVEALS`, both endpoint nodes `MATCH`ed rather than `MERGE`d to avoid creating a partial node from a stale sync).
- `apps/api/app/services/incidents/service.py` — `link_incident_hazard`/`unlink_incident_hazard` extended to call the new `REVEALS` sync functions; relational `incident_hazards` rows remain the source of truth, the graph edge follows them.
- `tests/unit/test_investigation_model.py` — `Investigation` ORM mapping/unique-constraint coverage.
- `tests/integration/test_incidents_investigation.py` — Investigation CRUD, `409` conflict, `INVESTIGATED_AS` sync.
- `tests/integration/test_incidents_crud.py` — prior slice's `test_incident_hazard_link_does_not_sync_reveals_to_neo4j` inverted to `test_incident_hazard_link_syncs_reveals_to_neo4j`, reflecting that this slice explicitly moved `REVEALS` sync from excluded to in-scope.

## 5. R23 — Specification Gap, Not Resolved

**Finding, unchanged from the mid-implementation stop:** R23's catalogue entry (`07-inference-rules-catalogue.md:166-170`) specifies the trigger (`is_notifiable_incident` transitions to `true`), the target field (`Incident.whsq_notified`), and that the field moves away from `"Not yet assessed"` — but does not name the literal value it moves *to*. R10, which R23 claims to mirror, names its literal target value explicitly; R23 does not. `whsq_notified`'s enum (`"Not yet assessed"`, `"Yes"`, `"No - assessed not required"`, `"No - under assessment"`) contains no value matching R23's descriptive phrase "notification assessment required."

**Explicitly not conflated with this gap:** [ADR-006 §9](../../.adr/ADR-006-incident-notification-rule-formal-defer.md#9-determination-received-2026-08-12) determined the *responsible notifier* for R23-driven notifications is the Safety Systems Manager. That is a distinct question from the *target enum value* `whsq_notified` should hold — the responsible-notifier determination does not supply, imply, or narrow the missing value. No inference was drawn from one to the other.

**Disposition:** R23 remains unimplemented. `services/incidents/rules.py` is untouched (placeholder). No value was selected, no ADR/ACR was raised to legitimise an inferred value, and no OpenAPI enum change was made. Resolving the target value requires an explicit governance/Compliance determination, tracked as an open item — not resolved by this closure.

## 6. Boundaries Held (Verified, Not Merely Asserted)

- **Action:** no `Action` ORM model, DTO, router, or service code exists in the merged diff. Confirmed by direct read.
- **Evidence wiring:** `services/evidence/service.py` (the existing Milestone-2 `verification_activity_id`-required implementation) is untouched by this diff — no incident-scoped Evidence path was added.
- **`fReporterRole`:** no new field added to `IncidentOut` or any other schema; `/people` remains unrouted.
- **`shared-types`:** not regenerated by this slice.
- **`osr_notified`:** untouched — carried exactly as it already existed, no branching or propagation logic added.
- **R23:** confirmed absent from the diff (§3, §5).

## 7. What Remains Open

- R23's target `whsq_notified` enum value — requires a separate, explicit governance/Compliance determination (§5). Blocks R23 propagation logic only; does not block anything else in this domain.
- Action — API/service/sync, plus the `completion_date`/`notes` OpenAPI contract gap and the `incident_actions`/`TRIGGERS`-has-no-OpenAPI-surface gap, both identified in the pre-implementation reconciliation and not resolved.
- Evidence wiring — the `verification_activity_id`-required service coupling identified in the pre-implementation reconciliation; needs its own implementation-approach decision before it can be scoped.
- `fReporterRole` — no exposure path in the frozen contract yet; needs its own scoping (new API field → ACR, or defer to a future People surface).
- `shared-types` regeneration — still stale against the full Incident/Investigation OpenAPI surface.
- `osr_notified`/"OSR" — `TO_BE_CONFIRMED`, tracked in [12-deliverables-index.md](12-deliverables-index.md) Open Items.

## 8. Next Gate

No next implementation slice is named or numbered by this closure. R23's target-value determination is its own governance item, separate from any future Incident-domain implementation slice — resolving it does not itself authorize implementation, and implementation of anything else in §7 does not require R23 to be resolved first.

## Acceptance Criteria

- [x] `main` HEAD, working-tree cleanliness, PR #23 merge status, and merge-commit CI independently re-verified against GitHub/the live repository, not assumed from any prior report.
- [x] Implementation diff scope re-confirmed as exactly the authorized 11 files; `services/incidents/rules.py` confirmed absent.
- [x] R23's specification gap restated precisely, with the responsible-notifier determination (ADR-006 §9) explicitly distinguished from the unresolved target-value question.
- [x] Every excluded item (Action, Evidence wiring, `fReporterRole`, `shared-types`, `osr_notified`, R23) checked against the actual merged diff, not merely restated from the GO.
- [x] No schema, OpenAPI, ontology, Neo4j model, or further application-code change made in producing this document.
- [x] No new implementation slice named or numbered.
