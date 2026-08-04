# Implementation Blueprint — Phase 2.1 + 2.2 + ACR Review Pack
**Status: APPROVED. Design Baseline v1.1 (frozen 2026-08-04). R0 — Repository Initialisation AUTHORISED. No application code has been written yet — this remains planning + scaffold documentation only.**
**Baseline:** Design Baseline v1.1 ([../PLATFORM_ARCHITECTURE_V2.md](../PLATFORM_ARCHITECTURE_V2.md) + [../knowledge-graph/](../knowledge-graph/README.md), 11 documents, amended by [ACR-002](../../.acr/ACR-002-emergency-planning-domain.md)/[ACR-003](../../.acr/ACR-003-competency-management-domain.md)) — **frozen**. Any further change requires an Architecture Change Request ([02-development-standards.md](02-development-standards.md) §7), not a direct edit.

This document set answers "how do we build what Design Baseline v1.1 specifies" — Phase 2.1/2.2 did not redesign, extend, or simplify anything the v1.0 baseline had decided; the one controlled extension since (Emergency Planning + Competency Management) went through the full ACR process in doc 14, not a direct edit.

| # | Document |
|---|---|
| 1 | [Repository Structure](01-repository-structure.md) |
| 2 | [Development Standards](02-development-standards.md) |
| 3 | [Module Dependency Map](03-module-dependency-map.md) |
| 4 | [Implementation Roadmap](04-implementation-roadmap.md) |
| 5 | [Database Migration Strategy](05-database-migration-strategy.md) |
| 6 | [Environment Strategy](06-environment-strategy.md) |
| 7 | [CI/CD Architecture](07-cicd-architecture.md) |
| 8 | [Testing Strategy](08-testing-strategy.md) |
| 9 | [Configuration Management](09-configuration-management.md) |
| 10 | [Operational Readiness Checklist](10-operational-readiness-checklist.md) |
| 11 | [Implementation Risk Register](11-implementation-risk-register.md) |
| 12 | [Deliverables Index](12-deliverables-index.md) — master register of every document across all phases |
| 13 | [Application Foundation Scaffold](13-application-foundation-scaffold.md) — Phase 2.2, repository scaffolding detail |
| 14 | [Architecture Change Request Review Pack](14-architecture-change-requests.md) — consolidates ACR-001/002/003, impact assessment, recommendations, Board approval section |

## Reading order

**3 → 4** first (what the modules are and in what order they get built), then **1 → 2** (where the code lives and how it gets reviewed), then **5 → 6 → 7** (data, environments, pipelines), then **8 → 9 → 10** (quality, config, ops), then **11 → 12** (risk and full traceability).

## Key resolutions from the Phase 2.1 brief

- **Microsoft Entra ID** confirmed as the AuthN/AuthZ provider — resolves the "not yet decided" note in the architecture doc §8.
- **Schedule 18B — confirmed.** You provided the source PDF directly; full text read (5 parts: workplace hazard/detail, command structure, notifications, resources/equipment, procedures — [knowledge-graph/09 §5a](../knowledge-graph/09-regulatory-knowledge-model.md)). No `EmergencyPlan` entity exists yet in Design Baseline v1.0 to hold this content — flagged as an ACR candidate ([knowledge-graph/09](../knowledge-graph/09-regulatory-knowledge-model.md) §5a, risk D4 in [11-implementation-risk-register.md](11-implementation-risk-register.md)), not silently implemented.
- **There is no "Schedule 19C."** You corrected this directly: **Schedule 19 is the WHS Regulation's Dictionary** (defined terms), not a device-specific schedule. Corrected throughout this document set. The verbatim "amusement device" definition text (Schedule 19) is still `TO_BE_CONFIRMED` — WebFetch to the `legislation.qld.gov.au` URL you provided failed this session (tool infrastructure issue).
- **AS/NZS 4024** — partially grounded already: the WHSQ Guide's own footnotes cite AS/NZS 4024.1303 and 4024.1201 directly (clauses 5.4.1, 5.4.2, 5.5.2.2, 6.2.2.3, 6.2.3), transcribed in [knowledge-graph/09 §2](../knowledge-graph/09-regulatory-knowledge-model.md) — full standard text still not sourced locally.
- **Emergency Planning (ACR-002) and Competency Management (ACR-003) — approved, 2026-08-04.** Guide §12 and §10.8 read in full, Architecture Review Board decision recorded, Design Baseline updated to v1.1 and re-frozen. `EmergencyPlan` risk D4 is closed. Full record: [14-architecture-change-requests.md](14-architecture-change-requests.md).

**R0 — Repository Initialisation is authorised.** No application code has been written yet — that begins with R0 itself.
