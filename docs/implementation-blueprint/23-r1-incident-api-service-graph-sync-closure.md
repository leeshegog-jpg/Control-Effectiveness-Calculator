# R1 Incident Management — API, Service & Graph Synchronisation: Closure Record

**Status:** Closure record. Documentation only — no application code, schema, OpenAPI, ontology, or Neo4j model change is made by this document. No new implementation is authorised by this document.

## 1. Summary

```text
Implementation slice:
R1 Incident Management — API, Service & Graph Synchronisation

Status:
CLOSED

main:
fb1be8d

Merge CI:
12/12 green

Delivered:
9 files, +696/-10

Boundaries:
asset_id              relational-only
reporter_person_id    relational-only
hazard links          relational API only
REVEALS sync          excluded
Investigation sync    excluded
Action sync           excluded
Safety Case           excluded
osr_notified          TO_BE_CONFIRMED / excluded
```

## 2. Authorization Trail

- [22-r1-incident-reconciliation-decision-review.md](22-r1-incident-reconciliation-decision-review.md) — reconciliation establishing the safe implementation boundary; no new ADR/ACR required for this slice's scope.
- Pre-implementation scope inspection (chat, 2026-08-19, read-only, no code) — confirmed `sync_incident` viable as a self-contained bare-node `MERGE`; identified and reported the `asset_id`/`reporter_person_id` Neo4j-representation gap rather than resolving it by inference.
- Disposition on that gap (chat, 2026-08-19): both fields stay relational-only; no Neo4j edge invented for either; no ADR required to reach that disposition.
- Explicit implementation GO (chat, 2026-08-19): named scope "R1 Incident Management — API, Service & Graph Synchronisation," bounded in/out lists as recorded in that GO and reproduced in §4 below.

## 3. What Was Verified For This Closure

Re-verified directly against the live repository and GitHub, not assumed from any prior report:

| Check | Result |
|---|---|
| `main` HEAD | `fb1be8d` |
| Working tree | Clean (pre-existing untracked clutter — `.claude-flow/`, WHS/ISO source PDFs/md, html files, `ruvector.db` — unrelated to this or any prior slice, left untouched) |
| PR #21 state | `MERGED`, merge commit `fb1be8d2d184a36e14302de655db9d373007c946`, merged by `leeshegog-jpg` |
| Merge-commit CI | 12/12 `success` (7 PR-validation jobs + `build`, `deploy`, `report-build-status`, `Container build — api`, `Container build — web`) |
| Implementation diff scope (`343573a..fb1be8d`) | Exactly 9 files, +696/-10 — matches the authorized set with no extras |

## 4. Delivered, Within the Authorized Boundary

- `apps/api/app/dto/incidents.py` — `IncidentInput`/`IncidentOut`/`IncidentListOut`/`IncidentHazardLinkInput`, field-for-field against the frozen `Incident`/`IncidentInput` OpenAPI schema.
- `apps/api/app/routers/incidents.py` — `GET/POST /incidents`, `GET/PATCH /incidents/{id}`, `GET/POST /incidents/{id}/hazards`, `DELETE /incidents/{id}/hazards/{hazardId}`.
- `apps/api/app/services/incidents/service.py` — CRUD orchestration (create/update call `sync_incident`); hazard link/unlink (relational only, no graph call).
- `apps/api/app/repositories/incidents_repository.py` — extended with `list_incident_hazards`/`link_incident_hazard`/`unlink_incident_hazard`.
- `apps/api/app/models/safety.py` — new `IncidentHazard` ORM mapping (`safety.incident_hazards`, composite key only, ACR-004 Option A — no columns beyond `incident_id`/`hazard_id`).
- `apps/api/app/graph/sync_service.py` — new `sync_incident`/`get_incident_node`: bare `Incident` node `MERGE`, scalar properties only (`datetime`, `severity`, `vrtp_severity`, `location`, `description`, `immediate_cause`, `root_cause`, `whsq_notified`, `osr_notified`, `is_notifiable_incident`, `investigation_status`) — the exact property set specified in `02-neo4j-node-relationship-model.md` §3.3, no more.
- `tests/unit/test_incident_hazard_model.py` — `IncidentHazard` ORM mapping/composite-key coverage.
- `tests/unit/test_api_app_scaffold.py` — `IMPLEMENTED_ROUTERS` updated to include `incidents` (required consequence of the router gaining routes, not a separate change).
- `tests/integration/test_incidents_crud.py` — API CRUD, Neo4j bare-node sync, hazard link/unlink, and an explicit boundary assertion that hazard-linking writes **no** `REVEALS` edge.

## 5. Boundaries Held (Verified, Not Merely Asserted)

- **`asset_id` / `reporter_person_id`:** both remain plain Postgres/API fields on `Incident`. `sync_incident`'s Cypher (`sync_service.py`) sets scalar properties only — no `MERGE`/`MATCH` referencing either FK, no edge creation of any kind for them. Confirmed by direct read of the merged diff.
- **Hazard links relational-only:** `link_incident_hazard`/`unlink_incident_hazard` (service + repository) touch `safety.incident_hazards` only — no call into `graph/sync_service.py` from either function. Confirmed by direct read of the merged diff, and by `test_incident_hazard_link_does_not_sync_reveals_to_neo4j` (passed in CI, `Integration tests (Postgres + Neo4j)` job) asserting zero `REVEALS` edges after a link operation.
- **`REVEALS`/`INVESTIGATED_AS`/`TRIGGERS` sync:** none of the three appears anywhere in `sync_service.py`'s new code. Only `sync_incident`/`get_incident_node` were added; no `sync_investigation`, `sync_action`, or hazard-link-sync function exists.
- **Investigation/Action:** no `Investigation` or `Action` ORM model, DTO, router, or service code was added. `/incidents/{id}/investigation` and `/incidents/{id}/evidence` remain unrouted.
- **Safety Case:** no `SafetyCaseClaim`/`Demonstration` reference anywhere in the merged diff.
- **`osr_notified`:** untouched — carried as a plain field through DTO/ORM/sync exactly as it already existed; no branching, defaulting, or propagation logic added. Still `TO_BE_CONFIRMED` per [ADR-006 §11](../../.adr/ADR-006-incident-notification-rule-formal-defer.md#11-residual-open-item--osr_notified--osr), unaffected by this slice.

## 6. What This Closure Does Not Do

- Does not create, modify, or migrate any schema, OpenAPI, ontology, or Neo4j model artefact.
- Does not raise or resolve any ADR or ACR.
- Does not resolve the `asset_id`/`reporter_person_id` Neo4j-representation question — the disposition (relational-only, no edge) stands as a scope decision for *this slice*, not a closure of the underlying question for all future work.
- Does not resolve `osr_notified`.
- Does not authorize Investigation, Action, hazard-link Neo4j sync, Evidence wiring, R23 propagation, `fReporterRole` resolution, `run-investigation-pipeline`, or Safety-Case linkage — all remain open, unclaimed by any slice.
- Does not name or number a next implementation slice.

## 7. What Remains Open

- Investigation API/service/Neo4j sync (`INVESTIGATED_AS`).
- Action API/service/Neo4j sync (`TRIGGERS`), including `safety.incident_actions`.
- Neo4j `REVEALS` sync for hazard links (relational persistence only exists as of this closure).
- `/incidents/{id}/evidence` wiring.
- R23 propagation logic (`is_notifiable_incident` → `whsq_notified` default-out) and `fReporterRole` resolution (D5) — service-rule work, not yet implemented.
- `shared-types` regeneration against the Incident OpenAPI surface — still stale (unaddressed by this slice; `packages/shared-types/src` still has zero `Incident` references, per the last direct check in [22 §10](22-r1-incident-reconciliation-decision-review.md#10-3d-1s-actual-delivered-scope--verified-directly), unchanged by this slice's scope).
- `osr_notified`/"OSR" — `TO_BE_CONFIRMED`, tracked in [12-deliverables-index.md](12-deliverables-index.md) Open Items.
- `run-investigation-pipeline`, Safety-Case linkage — both remain out of any CRUD-domain boundary, per [22 §12](22-r1-incident-reconciliation-decision-review.md#12-safe-boundary-for-the-next-implementation-scope).

## 8. Next Gate

No next implementation slice is named or numbered by this closure. Per the standing discipline this domain has followed since the reconciliation, the next bounded scope (whichever of §7's open items it covers) requires its own explicit, separately-issued GO.

## Acceptance Criteria

- [x] `main` HEAD, working-tree cleanliness, PR #21 merge status, and merge-commit CI independently re-verified against GitHub/the live repository, not assumed from any prior report.
- [x] Implementation diff scope re-confirmed as exactly the authorized 9 files.
- [x] Every excluded item (`asset_id`/`reporter_person_id` edges, hazard-link `REVEALS` sync, Investigation/Action sync, Safety Case, `osr_notified` logic) checked against the actual merged diff, not merely restated from the GO.
- [x] No schema, OpenAPI, ontology, Neo4j model, or further application-code change made in producing this document.
- [x] No new implementation slice named or numbered.
