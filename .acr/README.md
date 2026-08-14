# Architecture Change Requests

Design Baseline v1.1 (the architecture doc + all 11 knowledge-graph documents) is **frozen**. Any change to it — a new entity, a changed relationship, a different tech-stack component — requires an ACR, not a PR against `docs/knowledge-graph/`. See [docs/implementation-blueprint/02-development-standards.md](../docs/implementation-blueprint/02-development-standards.md) §7.

No implementation work proceeds against a proposed change until the ACR is approved.

## Index

| ACR | Title | Status | Full review |
|---|---|---|---|
| [ACR-001](ACR-001-training-domain.md) | Training Domain | Rejected (2026-08-04) — superseded by ACR-003 | [14-architecture-change-requests.md](../docs/implementation-blueprint/14-architecture-change-requests.md) §2 |
| [ACR-002](ACR-002-emergency-planning-domain.md) | Emergency Planning Domain | Approved (2026-08-04) | [14-architecture-change-requests.md](../docs/implementation-blueprint/14-architecture-change-requests.md) §3, §3a |
| [ACR-003](ACR-003-competency-management-domain.md) | Competency Management Domain | Approved (2026-08-04) | [14-architecture-change-requests.md](../docs/implementation-blueprint/14-architecture-change-requests.md) §4, §4a |
| [ACR-004](ACR-004-incident-openapi-extension.md) | Incident Domain — OpenAPI Extension (Investigation, `incident_hazards`/`REVEALS`, incident-scoped Evidence) | **Approved (2026-08-11) — Implemented (contract only)** — raised 2026-08-09 | [19-r1-milestone-3b-incident-decision-register.md](../docs/implementation-blueprint/19-r1-milestone-3b-incident-decision-register.md) D4; basis: [ADR-003](../.adr/ADR-003-incident-investigation-action-sibling-structure.md) |
| [ACR-005](ACR-005-incident-general-notifiable-incident-rule.md) | Incident Domain — New Rule (R23) Extending Notification Propagation to General WHS Act Notifiable-Incident Categories | **Approved (2026-08-12) — Not yet incorporated** — raised 2026-08-12 | [19-r1-milestone-3b-incident-decision-register.md](../docs/implementation-blueprint/19-r1-milestone-3b-incident-decision-register.md) D6; basis: [ADR-006](../.adr/ADR-006-incident-notification-rule-formal-defer.md) |

`10-openapi.yaml` bumped to **v0.3.0-draft** — ACR-004's additive extension incorporated (`Investigation` schema, `/incidents/{id}/investigation`, `/incidents/{id}/hazards[/{hazardId}]`, `/incidents/{id}/evidence`; Option A for the hazard-link shape, per ACR-004 §18). Validated: `scripts/validate_openapi.py` → 0 dangling `$ref`s; diff confirmed strictly additive (88 insertions, 1 deletion — the version bump only). **Contract-only** — no application code was written; the Incident domain's R0 placeholder stubs are unchanged and a separate GO is required before any implementation against these new endpoints. Design Baseline remains **v1.1** — this ACR extends the OpenAPI contract additively, per the same "MINOR bump, no removed/changed paths or schemas" convention ACR-002/003 used; it does not itself constitute a new baseline version.

**ACR-005 is approved but not yet incorporated** — `03-postgresql-schema.sql`, `10-openapi.yaml`, `02-neo4j-node-relationship-model.md`, and `07-inference-rules-catalogue.md` all remain exactly as they stood before this ACR. Per explicit instruction accompanying this approval, editing those four artefacts requires a separate, further GO — same treatment ACR-004 received between its approval and its contract implementation. `osr_notified`/"OSR" remains `TO_BE_CONFIRMED` (ADR-006 §11), untouched by this ACR either way.
