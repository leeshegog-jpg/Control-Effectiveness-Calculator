# R1 Incident Management — Action API, Incident Linking & TRIGGERS Sync: Closure Record

**Status:** Closure record. Documentation only — no application code, schema, OpenAPI, ontology, or Neo4j model change is made by this document.

## 1. Summary

```text
Implementation slice:
R1 Incident Management — Action API, Incident Linking & TRIGGERS Sync

Status:
CLOSED

main:
021ec2b

Merge CI:
12/12 green

Delivered:
13 files, +748/-18

Boundaries:
completion_date          not exposed (ACR required to expose)
notes                    not exposed (ACR required to expose)
action_controls          not implemented (ACR required if pursued)
REMEDIATES               not implemented (ACR required if pursued)
Evidence wiring           untouched
fReporterRole             untouched
shared-types               not regenerated
osr_notified              TO_BE_CONFIRMED / untouched
```

## 2. Authorization Trail

- [29-action-mechanism-reconciliation-correction.md](29-action-mechanism-reconciliation-correction.md) — resolved the Incident↔Action relationship mechanism by evidence (origin vs. roster), withdrawing an earlier chat-only "genuine conflict" framing.
- [ACR-006](../../.acr/ACR-006-incident-action-openapi-extension.md) — raised, approved (Option A: link-existing, not create-and-link), and incorporated into `10-openapi.yaml` (v0.4.0-draft) across three sequential, separately-GO'd steps.
- Pre-implementation scope inspection (chat, 2026-08-22, read-only) — confirmed the file/function/endpoint list against the incorporated contract and current scaffold state before any code was written.
- Explicit implementation GO (chat, 2026-08-22): named scope "R1 Incident Management — Action API, Incident Linking & TRIGGERS Sync," in/out lists as recorded in that GO.

## 3. What Was Verified For This Closure

Re-verified directly against the live repository and GitHub, not assumed from any prior report:

| Check | Result |
|---|---|
| `main` HEAD | `021ec2b` |
| Working tree | Clean (pre-existing untracked clutter — `.claude-flow/`, WHS/ISO source PDFs/md, html files, `ruvector.db` — unrelated to this or any prior slice, left untouched) |
| PR #33 state | `MERGED`, merge commit `021ec2b278b27340f5f4f160f3e12e17a621f74a` |
| Merge-commit CI | 12/12 `success` (7 PR-validation jobs + `build`, `deploy`, `report-build-status`, `Container build — api`, `Container build — web`) |
| Implementation diff scope (`be05c8d..021ec2b`) | Exactly 13 files, +748/-18 — matches the authorized set with no extras |
| Local validation (recorded at PR time) | 56/56 unit tests, `ruff check`/`ruff format --check`/`mypy` clean, `scripts/validate_openapi.py` → `OK: 70 paths, 78 schemas, 0 dangling $refs` (unaffected — contract already incorporated in #32) |

## 4. Delivered, Within the Authorized Boundary

- `apps/api/app/models/safety.py` — new `Action` ORM mapping (all 14 frozen `safety.actions` columns, including `completion_date`/`notes` for persistence fidelity — neither exposed via DTO/API); new `IncidentAction` ORM mapping (`safety.incident_actions`, ACR-006 Option A composite key only).
- `apps/api/app/dto/actions.py` — `ActionInput`/`ActionOut`/`IncidentActionLinkInput`, field-for-field against the frozen `Action`/`ActionInput` OpenAPI schema, deliberately omitting `completion_date`/`notes`.
- `apps/api/app/repositories/actions_repository.py` — base Action CRUD (`list_actions`, `get_action`, `create_action`, `update_action`).
- `apps/api/app/repositories/incidents_repository.py` — extended with `list_incident_actions`/`link_incident_action`/`unlink_incident_action`, mirroring the `incident_hazards` functions exactly (kept in the Incident repository, not the Action repository, matching where `incident_hazards` already lives).
- `apps/api/app/services/actions/service.py` — Action CRUD orchestration + `sync_action` call.
- `apps/api/app/services/incidents/service.py` — `link_incident_action`/`unlink_incident_action`, mirroring `link_incident_hazard`/`unlink_incident_hazard` exactly — relational `incident_actions` rows remain the source of truth, `TRIGGERS` sync follows.
- `apps/api/app/routers/actions.py` — `GET/POST /actions`, `PATCH /actions/{id}`.
- `apps/api/app/routers/incidents.py` — `GET/POST /incidents/{id}/actions`, `DELETE /incidents/{id}/actions/{actionId}`. `POST` links an existing Action by ID only (ACR-006 §9a) — does not create one.
- `apps/api/app/graph/sync_service.py` — new `sync_action`/`get_action_node` (bare `Action` node `MERGE`, scalar properties only); new `sync_incident_action_link`/`unsync_incident_action_link` (`TRIGGERS`), mirroring `REVEALS` exactly.
- `tests/unit/test_api_app_scaffold.py` — `IMPLEMENTED_ROUTERS` updated to include `actions` (required consequence of the router gaining routes, not a separate change).
- `tests/unit/test_action_model.py` — `Action`/`IncidentAction` ORM mapping and composite-key coverage.
- `tests/integration/test_actions_crud.py` — Action CRUD, status filter, Neo4j bare-node sync.
- `tests/integration/test_incidents_actions.py` — Incident-Action link/unlink, `TRIGGERS` sync verification, 404 boundary checks (missing link, missing incident).

## 5. Boundaries Held (Verified, Not Merely Asserted)

- **`completion_date`/`notes`:** present as ORM columns (persistence fidelity, matching how `osr_notified` was carried on `Incident` before its own ACR resolved its exposure), but confirmed absent from `ActionInput`/`ActionOut` and from every router/service function signature. Checked directly against the merged diff — zero functional reference to either field anywhere outside docstrings explaining the exclusion.
- **`action_controls`/`REMEDIATES`:** no ORM model, no repository function, no router, no service, no sync function — confirmed absent from the merged diff entirely.
- **No schema, OpenAPI, or ontology change:** `03-postgresql-schema.sql`, `10-openapi.yaml`, and every ontology scheme untouched by this slice — the contract was already incorporated in [#32](https://github.com/leeshegog-jpg/TP_Risk_Management_SMS/pull/32), a separate, already-closed step.
- **ACR-006 Option A held exactly:** `POST /incidents/{id}/actions` requires an existing `action_id` (`IncidentActionLinkInput`) — no code path creates an Action as a side effect of linking.
- **Evidence wiring, `fReporterRole`, `shared-types`, `osr_notified`:** none touched — confirmed absent from the merged diff.

## 6. What Remains Open

- `completion_date`/`notes` exposure on `ActionInput`/`Action` — requires its own ACR.
- `action_controls`/`REMEDIATES` — requires its own ACR if pursued.
- Evidence wiring (the `verification_activity_id`-required service coupling identified in [22](22-r1-incident-reconciliation-decision-review.md)) — needs its own implementation-approach decision.
- `fReporterRole` — no exposure path in the frozen contract yet; needs its own scoping (new API field → ACR, or defer to a future People surface).
- `shared-types` regeneration — still stale against the full Incident/Investigation/Action OpenAPI surface.
- `osr_notified`/"OSR" — `TO_BE_CONFIRMED`, tracked in [12-deliverables-index.md](12-deliverables-index.md) Open Items.

## 7. Next Gate

No next implementation slice is named or numbered by this closure. Per the standing discipline this domain has followed since the reconciliation, the next bounded scope (whichever of §6's open items it covers) requires its own explicit, separately-issued GO.

## Acceptance Criteria

- [x] `main` HEAD, working-tree cleanliness, PR #33 merge status, and merge-commit CI independently re-verified against GitHub/the live repository, not assumed from any prior report.
- [x] Implementation diff scope re-confirmed as exactly the authorized 13 files.
- [x] Every excluded item (`completion_date`/`notes`, `action_controls`/`REMEDIATES`, Evidence/`fReporterRole`/`shared-types`/`osr_notified`) checked against the actual merged diff, not merely restated from the GO.
- [x] No schema, OpenAPI, ontology, Neo4j model, or further application-code change made in producing this document.
- [x] No new implementation slice named or numbered.
