# Architecture Change Requests

Design Baseline v1.1 (the architecture doc + all 11 knowledge-graph documents) is **frozen**. Any change to it — a new entity, a changed relationship, a different tech-stack component — requires an ACR, not a PR against `docs/knowledge-graph/`. See [docs/implementation-blueprint/02-development-standards.md](../docs/implementation-blueprint/02-development-standards.md) §7.

No implementation work proceeds against a proposed change until the ACR is approved.

## Index

| ACR | Title | Status | Full review |
|---|---|---|---|
| [ACR-001](ACR-001-training-domain.md) | Training Domain | Rejected (2026-08-04) — superseded by ACR-003 | [14-architecture-change-requests.md](../docs/implementation-blueprint/14-architecture-change-requests.md) §2 |
| [ACR-002](ACR-002-emergency-planning-domain.md) | Emergency Planning Domain | Approved (2026-08-04) | [14-architecture-change-requests.md](../docs/implementation-blueprint/14-architecture-change-requests.md) §3, §3a |
| [ACR-003](ACR-003-competency-management-domain.md) | Competency Management Domain | Approved (2026-08-04) | [14-architecture-change-requests.md](../docs/implementation-blueprint/14-architecture-change-requests.md) §4, §4a |
| [ACR-004](ACR-004-incident-openapi-extension.md) | Incident Domain — OpenAPI Extension (Investigation, `incident_hazards`/`REVEALS`, incident-scoped Evidence) | **Approved (2026-08-11)** — raised 2026-08-09 | [19-r1-milestone-3b-incident-decision-register.md](../docs/implementation-blueprint/19-r1-milestone-3b-incident-decision-register.md) D4; basis: [ADR-003](../.adr/ADR-003-incident-investigation-action-sibling-structure.md) |

Design Baseline is currently **v1.1** as a result of ACR-002 and ACR-003. ACR-004 is approved but **not yet incorporated** — `10-openapi.yaml` is unchanged; per explicit governance instruction for this ACR, editing it requires a separate, further authorization beyond this approval (see ACR-004 §17–§18).
