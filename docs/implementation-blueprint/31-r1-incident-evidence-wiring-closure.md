# R1 Incident Management — Evidence API Wiring & Incident-Scoped Evidence: Closure Record

**Status:** Closure record. Documentation only — no application code, schema, OpenAPI, ontology, or Neo4j model change is made by this document.

## 1. Summary

```text
Implementation slice:
R1 Incident Management — Evidence API Wiring & Incident-Scoped Evidence

Status:
CLOSED

main:
2d0e270

Merge CI:
12/12 green

Delivered:
5 files, +145/-7 (2 commits squashed: implementation + a CI-discovered fix)

Boundaries:
Schema change                  none
OpenAPI contract change        none
Ontology change                none
Neo4j Incident→Evidence edge   none — bare node only
EvidenceOut contract drift     pre-existing, unresolved, separately noted
completion_date / notes        untouched
action_controls / REMEDIATES   untouched
fReporterRole                  untouched
osr_notified                   untouched
```

## 2. Authorization Trail

- Read-only Evidence reconciliation (chat, 2026-08-22) — established every governance-level artifact (OpenAPI, schema, Neo4j model) was already sufficient; classified Evidence implementation as **READY**, no ACR/ADR required.
- Explicit implementation GO (chat, 2026-08-22): named scope "R1 Incident Management — Evidence API Wiring & Incident-Scoped Evidence."
- Mid-implementation CI failure and its own separate, narrowly-scoped GO (chat, 2026-08-22): the reconciliation's "zero Neo4j work needed" finding was corrected after `test_incident_evidence_syncs_as_bare_node_no_incident_edge` failed in CI — `sync_evidence` was found to return before creating any node for standalone evidence, not merely skip an edge as the reconciliation had assumed. Fixed under its own GO, committed separately (`642dab4`) on the same PR branch, re-validated before merge.

## 3. What Was Verified For This Closure

Re-verified directly against the live repository and GitHub, not assumed from any prior report:

| Check | Result |
|---|---|
| `main` HEAD | `2d0e270` |
| Working tree | Clean (pre-existing untracked clutter — `.claude-flow/`, WHS/ISO source PDFs/md, html files, `ruvector.db` — unrelated to this or any prior slice, left untouched) |
| PR #35 state | `MERGED`, merge commit `2d0e270ef2aa463ea0e2eb6bade92f44594081d0` |
| Merge-commit CI | 12/12 `success` (7 PR-validation jobs + `build`, `deploy`, `report-build-status`, `Container build — api`, `Container build — web`) — confirmed on the merge commit itself, not just the pre-merge PR head |
| Previously-failing test | `test_incident_evidence_syncs_as_bare_node_no_incident_edge` confirmed `PASSED` by name, both on the fixed PR head and on the merge commit |
| Implementation diff scope (`d3b0c02..2d0e270`) | Exactly 5 files, +145/-7 — matches the authorized set (4 implementation files + the one-file `sync_evidence` fix), no extras |
| Local validation (recorded at PR time) | 56/56 unit tests, `ruff check`/`ruff format --check`/`mypy` clean, `scripts/validate_openapi.py` → `OK: 70 paths, 78 schemas, 0 dangling $refs` (unaffected) |

## 4. Delivered, Within the Authorized Boundary

- `apps/api/app/routers/evidence.py` — `GET/POST /incidents/{id}/evidence`, added to the existing Evidence router (tagged `[Evidence]` in the frozen contract, consistent with where `/verification-activities/{id}/evidence` already lives). Reuses `EvidenceInput`/`EvidenceOut` and the existing `_to_out` helper unchanged. `POST` passes `verification_activity_id=None`, `linked_entity_type="incident"` explicitly.
- `apps/api/app/services/evidence/service.py` — `create_evidence`'s `verification_activity_id` parameter loosened from required `uuid.UUID` to `uuid.UUID | None` (the underlying column was already nullable — a backward-compatible type change, not a redesign). New `list_incident_evidence`.
- `apps/api/app/repositories/evidence_repository.py` — new `list_incident_evidence`, querying by `linked_entity_type='incident'`/`linked_entity_id`, mirroring the existing `list_evidence` query shape.
- `apps/api/app/graph/sync_service.py` — `sync_evidence` fixed to `MERGE` a bare `Evidence` node (scalar properties only) when `verification_activity_id` is `None`, rather than returning without syncing anything. The `PRODUCES` edge path (verification-activity-linked evidence) is unchanged and still gated on `verification_activity_id` being present.
- `tests/integration/test_incidents_evidence.py` — empty-list-before-creation, create+list round trip, `404` on missing incident (both `GET` and `POST`), and an explicit boundary check confirming the `Evidence` node exists in Neo4j **and** no `Incident→Evidence` edge exists of any kind.

## 5. Boundaries Held (Verified, Not Merely Asserted)

- **No schema, OpenAPI, or ontology change:** `03-postgresql-schema.sql`, `10-openapi.yaml`, and every ontology scheme untouched — confirmed by diff scope (§3).
- **No `Incident→Evidence` Neo4j edge:** `test_incident_evidence_syncs_as_bare_node_no_incident_edge` asserts both the node's existence (`count == 1`) and the absence of any edge from `Incident` to that `Evidence` node (`count == 0`), passing in CI on the merge commit.
- **Existing `VerificationActivity→Evidence` `PRODUCES` behaviour preserved:** `sync_evidence`'s verification-activity path is untouched by the fix — only the standalone (`None`) branch gained node creation. No change to `list_evidence`, the verification-activity router endpoints, or their tests, all of which remained in the passing CI suite (e.g. `test_critical_control_management.py`'s evidence coverage) throughout.
- **Pre-existing `EvidenceOut` contract drift left unresolved, as instructed:** `EvidenceOut` still exposes `verification_activity_id`, a field absent from the frozen `Evidence` OpenAPI schema — a Milestone-2-era drift, confirmed still present and untouched by this slice.
- **`completion_date`/`notes`, `action_controls`/`REMEDIATES`, `fReporterRole`, `osr_notified`:** none referenced anywhere in the merged diff.

## 6. What Remains Open

- `completion_date`/`notes` exposure on `ActionInput`/`Action` — requires its own ACR.
- `action_controls`/`REMEDIATES` — requires its own ACR if pursued.
- `fReporterRole` — no exposure path in the frozen contract yet; needs its own scoping (new API field → ACR, or defer to a future People surface).
- `shared-types` regeneration — still stale against the full Incident/Investigation/Action/Evidence OpenAPI surface.
- `osr_notified`/"OSR" — `TO_BE_CONFIRMED`, tracked in [12-deliverables-index.md](12-deliverables-index.md) Open Items.
- The pre-existing `EvidenceOut`/`Evidence`-schema field drift (§5) — noted, not resolved, no slice currently owns it.

## 7. Next Gate

No next implementation slice is named or numbered by this closure. Per the standing discipline this domain has followed throughout, the next bounded scope (whichever of §6's open items it covers) requires its own explicit, separately-issued GO.

## Acceptance Criteria

- [x] `main` HEAD, working-tree cleanliness, PR #35 merge status, and merge-commit CI independently re-verified against GitHub/the live repository, not assumed from any prior report.
- [x] The specific CI-discovered defect and its fix traced explicitly, including that the fix was validated on both the PR head and the merge commit by test name, not just by overall job status.
- [x] Implementation diff scope re-confirmed as exactly the authorized 5 files.
- [x] Every excluded item (schema/OpenAPI/ontology, Incident→Evidence edge, `completion_date`/`notes`, `action_controls`/`REMEDIATES`, `fReporterRole`, `osr_notified`) checked against the actual merged diff, not merely restated from the GO.
- [x] Pre-existing `EvidenceOut` contract drift explicitly noted as unresolved, not silently absorbed into "done."
- [x] No schema, OpenAPI, ontology, Neo4j model, or further application-code change made in producing this document.
- [x] No new implementation slice named or numbered.
