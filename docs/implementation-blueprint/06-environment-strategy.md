# 06 — Environment Strategy
**Status: DRAFT — Phase 2.1 Implementation Blueprint. Baseline: Design Baseline v1.0 (frozen — Azure hosting, [PLATFORM_ARCHITECTURE_V2.md](../PLATFORM_ARCHITECTURE_V2.md) §8).**

---

| | **Development** | **Test** | **UAT** | **Production** |
|---|---|---|---|---|
| **Purpose** | Active feature development, ephemeral per-PR previews | Automated CI test execution | VRTP HSE/safety team sign-off before go-live | Live system |
| **Infrastructure** | Azure Container Apps, minimum tier; shared or per-branch ephemeral | Azure Container Apps, ephemeral per CI run where practical | Azure Container Apps, production-equivalent sizing | Azure Container Apps, full HA/scaling config (finalized in R0 using Azure's own current best-practice tooling, not assumed here) |
| **Authentication** | Entra ID — dedicated Dev app registration, test accounts only | Entra ID — dedicated Test app registration, service-principal auth for CI | Entra ID — dedicated UAT app registration, real VRTP HSE user accounts | Entra ID — Prod app registration, real organizational accounts, MFA enforced |
| **PostgreSQL** | Azure Database for PostgreSQL Flexible Server, Burstable tier | Ephemeral container (or Burstable tier) — reset per run | Flexible Server, General Purpose tier, production-like data volume | Flexible Server, production tier with HA + point-in-time restore |
| **Neo4j** | Self-hosted container (per architecture §8, decision pending: AuraDB vs. self-hosted) | Ephemeral container | Matches Prod's hosting decision | Per architecture §8 decision — AuraDB or self-hosted with persistent storage, finalized in R0 |
| **Qdrant** | Self-hosted container | Ephemeral container | Matches Prod's hosting decision | Per architecture §8 decision |
| **AI services** | Anthropic API, dedicated Dev key, **usage-capped** to bound cost during iterative extraction development | Anthropic API, dedicated Test key, capped; extraction tests may mock the LLM call for pure-logic tests ([08-testing-strategy.md](08-testing-strategy.md)) | Anthropic API, dedicated UAT key, uncapped but monitored | Anthropic API, Prod key, server-side only (never client-side — architecture §1.4 finding 3), full monitoring |
| **Storage** | Azure Blob Storage, Dev container, short retention | Azure Blob Storage, Test container, purged per run | Azure Blob Storage, UAT container, production-like retention | Azure Blob Storage, Prod container, full retention per [10-operational-readiness-checklist.md](10-operational-readiness-checklist.md) |
| **Monitoring** | Basic logs, no alerting | CI pass/fail only | Application Insights, alerting to a UAT channel | Application Insights, full alerting, on-call rotation |

## Cross-Environment Rules

- **Secrets never shared across environments** — a Dev Anthropic key must not be reused in Test/UAT/Prod, enforced via Azure Key Vault scoping ([09-configuration-management.md](09-configuration-management.md)).
- **No production data in Dev/Test** — UAT is the first environment permitted production-scale/production-like data (synthetic where real data isn't available), consistent with the V1 `localStorage` export only happening at Prod cutover ([05-database-migration-strategy.md](05-database-migration-strategy.md) §4).
- **Feature flags** ([09-configuration-management.md](09-configuration-management.md)) allow a feature to reach Dev/Test before Prod without a code branch divergence — the environment strategy and the branching strategy ([02](02-development-standards.md) §1) are deliberately decoupled.
