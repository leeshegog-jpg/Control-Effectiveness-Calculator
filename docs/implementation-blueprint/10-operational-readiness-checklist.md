# 10 — Operational Readiness Checklist
**Status: DRAFT — Phase 2.1 Implementation Blueprint. Baseline: Design Baseline v1.0 (frozen).**

---

## Deployment

- [ ] Migration gate verified in CI/CD ([07-cicd-architecture.md](07-cicd-architecture.md) §4) — no container deploys ahead of its required schema migration
- [ ] Rollback path tested (container rollback automatic on smoke-test failure; Postgres rollback plan documented per migration, [05](05-database-migration-strategy.md) §5)
- [ ] Manual approval gate confirmed active for Prod deploys

## Backup

- [ ] Postgres: automated backups + point-in-time restore configured (Flexible Server built-in capability, finalized in R0)
- [ ] Neo4j: backup **secondary** to Postgres-rebuild capability ([05](05-database-migration-strategy.md) §2) — still backed up, but Postgres is the disaster-recovery source of truth
- [ ] Blob Storage: versioning/soft-delete enabled for uploaded documents and evidence files
- [ ] Ontology: concept history is inherently backed up via its own immutable versioning ([EKG spec](../knowledge-graph/01-enterprise-knowledge-graph-specification.md) §6) — confirm this isn't treated as a separate backup requirement, it's a design property already in place

## Restore

- [ ] Postgres restore drill performed (not just configured — tested end-to-end at least once before Prod go-live)
- [ ] Full Neo4j rebuild-from-Postgres drill performed and timed (this *is* the Neo4j restore procedure, [05](05-database-migration-strategy.md) §2)
- [ ] Document/evidence restore drill performed

## Monitoring

- [ ] Application Insights wired for all Prod services ([06-environment-strategy.md](06-environment-strategy.md))
- [ ] Alerting on: Graph Sync Service lag exceeding target ([EKG spec](../knowledge-graph/01-enterprise-knowledge-graph-specification.md) §4), extraction pipeline failure rate, R3/R5/R6/R18 gap-analysis rule execution failures (silent gap-detection failure is itself a gap)
- [ ] On-call rotation defined for Prod

## Logging

- [ ] Every write carries a provenance record ([05-knowledge-provenance-model.md](../knowledge-graph/05-knowledge-provenance-model.md)) — confirmed functioning as the platform's audit log, not a separate logging system bolted on afterward
- [ ] Application/infrastructure logs centralized, retention policy set

## Audit

- [ ] Provenance chain walkable end-to-end for a real record before go-live (the specific capability [05](../knowledge-graph/05-knowledge-provenance-model.md) §6 describes — tested, not assumed)
- [ ] Three-lines-of-assurance model ([08](../knowledge-graph/08-critical-control-assurance-model.md) §5) has real Audit records flowing by UAT

## Security

- [ ] Penetration test complete ([08-testing-strategy.md](08-testing-strategy.md) §8)
- [ ] Anthropic API key confirmed unreachable from any client bundle (direct regression test, architecture §1.4 finding 3)
- [ ] Entra ID roles/scopes reviewed — ontology curator role distinct from general user role ([EKG spec](../knowledge-graph/01-enterprise-knowledge-graph-specification.md) §6)

## Performance

- [ ] Query patterns Q1–Q7 ([EKG spec](../knowledge-graph/01-enterprise-knowledge-graph-specification.md) §5) load-tested at UAT-scale data volume
- [ ] Extraction pipeline throughput tested against realistic document upload volume

## Disaster Recovery

- [ ] RTO/RPO defined per environment (Prod values `TO_BE_CONFIRMED` — depends on VRTP's own business continuity requirements, not something to assume)
- [ ] Cross-region backup considered for Prod Postgres, decision recorded as an ADR ([02](02-development-standards.md) §6)

## Business Continuity

- [ ] Strangler-fig fallback confirmed functioning throughout migration — the live GitHub Pages site remains operable at every release boundary until its corresponding nav link is repointed ([04-implementation-roadmap.md](04-implementation-roadmap.md)), meaning V1 itself is the business-continuity fallback during the transition period, not a separate system to build
- [ ] Confirm VRTP has a documented manual/paper fallback for Safety Case demonstration in case of platform outage during a regulator audit — this is an operational question for VRTP, not a platform design gap, but should be explicitly answered before Prod go-live, not left implicit
