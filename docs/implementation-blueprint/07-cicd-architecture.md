# 07 — CI/CD Architecture
**Status: DRAFT — Phase 2.1 Implementation Blueprint. Baseline: Design Baseline v1.0 (frozen).**

---

## 1. Pipeline Overview

**GitHub Actions**, workflows in `.github/workflows/` ([01-repository-structure.md](01-repository-structure.md)). Four pipeline classes:

| Pipeline | Trigger | Purpose |
|---|---|---|
| PR validation | Every PR | Fast feedback — lint, typecheck, unit tests, contract validation |
| Merge-to-main build | Push to `main` | Build + push container images, run integration tests |
| Environment deploy | Merge to `main` (→Dev), tag on `release/*` (→Test/UAT/Prod, gated) | Deploy containers + apply migrations |
| Scheduled | Nightly/weekly | Security scanning, Knowledge Graph drift check, dependency audit |

## 2. PR Validation Pipeline

1. Lint (frontend + backend)
2. Typecheck (TypeScript strict mode; Python via mypy)
3. Unit tests ([08-testing-strategy.md](08-testing-strategy.md) §1)
4. **OpenAPI validation** — `10-openapi.yaml` lints clean (already validated: 56 paths, 64 schemas, zero dangling `$ref`s as of Design Baseline v1.0) and, if changed, `packages/shared-types` regeneration is verified up to date (fails the PR if the generated types weren't committed alongside the spec change)
5. **Ontology validation** (only if `ontology/` changed) — no cycles in `BROADER` edges ([06-relationship-rules-catalogue.md](../knowledge-graph/06-relationship-rules-catalogue.md) §4), no duplicate alias within a scheme
6. **Database migration validation** (only if `database/postgres/migrations` changed) — migration applies cleanly to a fresh throwaway Postgres container, matches the SQLAlchemy models
7. **API contract tests** (only if `apps/api` changed) — generated from `10-openapi.yaml` (e.g. via Schemathesis), confirms implementation matches contract

## 3. Merge-to-Main Pipeline

1. Container builds — `apps/web`, `apps/api`, pushed to Azure Container Registry, tagged with commit SHA
2. Integration tests ([08-testing-strategy.md](08-testing-strategy.md) §2) against ephemeral Postgres + Neo4j containers
3. **Knowledge Graph validation** — after integration tests seed data, run the relationship-rule test suite ([06-relationship-rules-catalogue.md](../knowledge-graph/06-relationship-rules-catalogue.md)) and confirm Graph Sync Service produces a Neo4j projection matching Postgres (structural check, not full data diff)
4. Deploy to Dev automatically on success

## 4. Environment Deploy Pipeline (Test/UAT/Prod)

1. Triggered by `release/x.y` tag (per [02-development-standards.md](02-development-standards.md) §1)
2. Migration gate: Postgres migration applied first, verified, **then** new containers deployed — never the reverse (avoids a new container version running against an unmigrated schema)
3. Neo4j constraint script applied (idempotent, safe to re-run — [05-database-migration-strategy.md](05-database-migration-strategy.md) §2)
4. Smoke test suite runs post-deploy; automatic rollback to prior container tag on smoke-test failure (Postgres migration rollback is **not** automatic — per [05](05-database-migration-strategy.md) §5, handled manually per the migration's documented rollback plan)
5. Manual approval gate before Prod specifically (UAT sign-off is the gate, not a CI check — ties to [10-operational-readiness-checklist.md](10-operational-readiness-checklist.md))

## 5. Scheduled Pipelines

| Pipeline | Frequency | Purpose |
|---|---|---|
| Dependency/security scanning | Nightly | SAST, dependency vulnerability audit, container image scan |
| Knowledge Graph drift check | Daily | Confirms Neo4j instance graph matches Postgres system of record — surfaces Graph Sync Service failures before they become a gap-analysis blind spot |
| AI extraction golden-set regression | Weekly | Re-runs the golden-set documents ([08-testing-strategy.md](08-testing-strategy.md) §6) against the current extraction pipeline — catches silent accuracy regression from prompt/model changes |
| Ontology integrity check | Weekly | Acyclic check, orphan-concept check, unused-alias check across the full ontology (not just PR-diff scope) |

## 6. Security Scanning Detail

SAST on every PR (fast subset) + full scan nightly; dependency audit (`npm audit`/`pip-audit` equivalents) nightly; container image scan on every build; secrets-in-diff scan on every PR (catches an accidentally-committed API key before merge — directly relevant given V1's own client-side API key defect, architecture §1.4 finding 3, was a symptom of exactly this kind of oversight).
