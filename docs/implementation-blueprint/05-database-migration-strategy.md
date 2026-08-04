# 05 — Database Migration Strategy
**Status: DRAFT — Phase 2.1 Implementation Blueprint. Baseline: Design Baseline v1.0 (frozen).**

---

## 1. PostgreSQL Migrations

**Tool: Alembic** (SQLAlchemy's migration tool — standard pairing with FastAPI, not a new architectural decision, a tooling choice within the frozen backend stack).

- One migration per schema change, auto-generated from SQLAlchemy models then hand-reviewed against [03-postgresql-schema.sql](../knowledge-graph/03-postgresql-schema.sql) — the design doc is authoritative; a migration that drifts from it is a bug, not a valid change (fix the migration, or raise an ACR if the schema doc itself needs to change).
- Every migration reviewed like code (PR requirements, [02](02-development-standards.md) §4).
- Forward-only preferred; a `down_revision` is required for every migration but is only a promise of *technical* reversibility (DDL rollback) — not a promise that reversing is *safe* once real data exists. Migrations that drop columns/tables get an explicit "irreversible past this point" note and a documented manual rollback plan instead of relying on the auto-generated down-migration.
- Tested in CI against a throwaway Postgres container on every PR ([07-cicd-architecture.md](07-cicd-architecture.md)).

## 2. Neo4j Migrations

**Constraints/indexes** ([02-neo4j-node-relationship-model.md](../knowledge-graph/02-neo4j-node-relationship-model.md) §5) are versioned Cypher scripts, applied in order, tracked in a `graph_schema_version` node (self-tracking, no external migration tool required for this small a surface).

**Instance data is not migrated in the traditional sense** — this is a property of the architecture worth stating explicitly because it materially reduces Neo4j migration risk: the Graph Sync Service ([01-enterprise-knowledge-graph-specification.md](../knowledge-graph/01-enterprise-knowledge-graph-specification.md) §4) treats Postgres as the system of record and Neo4j as a rebuildable projection. A full Neo4j rebuild from Postgres is always a valid recovery path, which means:
- Neo4j schema changes (new node label, new relationship type) don't need a data-migration step — new writes populate the new shape, and a backfill job (not a "migration") can walk Postgres and re-sync historical rows if needed.
- This is *not* true of Postgres, which remains the actual system of record requiring careful migration discipline.

## 3. Ontology Versioning

Deliberately **not** a schema migration concern — adding/changing a `Concept` is a content change through the Ontology Service API (draft → reviewed → approved → published, [EKG spec](../knowledge-graph/01-enterprise-knowledge-graph-specification.md) §6), performed by the ontology curator, not a deploy-time migration. The `ontology/` repo folder ([01-repository-structure.md](01-repository-structure.md)) holds the *seed* concept set only (V1-ported: control hierarchy, consequence domains, energy sources) — loaded once per environment via a seed script, not re-applied as a migration on every deploy.

## 4. Seed Data

| Seed set | Source | Target environment(s) |
|---|---|---|
| Ontology seed concepts | `ontology/seed-concepts/` (ported from V1 `REF.controlHierarchy`, `REF.consequenceDomains`, energy-source list — [PLATFORM_ARCHITECTURE_V2.md](../PLATFORM_ARCHITECTURE_V2.md) §6) | All environments |
| Ontology seed concepts — v1.1 amendment | Emergency Service Organisation, Competency Category schemes — net-new, no V1 source to port ([knowledge-graph/01](../knowledge-graph/01-enterprise-knowledge-graph-specification.md) §6a; ACR-002/ACR-003) | All environments |
| V1 pilot register (108 rows / 14 hazards) | `bowtie-ccm-generator.html` seed data, migrated via a one-time script mapping V1's 55-column schema to the canonical model | Dev, Test, UAT (real reference data — do not treat as disposable fixtures) |
| Live V1 `localStorage` data | Exported via the Hub's "Backup All Data" button (architecture §8 decision 4) — **must happen before R1 cutover**, not automatable, depends on physical access to the browser(s) that have been using the live site | Prod, migrated once at cutover |
| Dev/test fixtures | Synthetic, generated | Dev, Test only — never UAT/Prod |

## 5. Rollback

- **Postgres:** migration-per-PR with tested down-migration where reversible (§1); irreversible migrations require sign-off in the PR description and a documented manual recovery procedure.
- **Neo4j:** rollback = re-run the constraint script for the prior version + trigger a re-sync from Postgres (§2) — simpler than Postgres rollback precisely because of the system-of-record/projection split.
- **Ontology:** never rolled back via deploy — a bad concept is deprecated (`status = 'deprecated'`, `effective_to` set) and superseded, per the immutable-history governance model already specified ([EKG spec](../knowledge-graph/01-enterprise-knowledge-graph-specification.md) §6). This is a content correction, not a migration rollback.

## 6. Environment Promotion

```
Dev → Test → UAT → Prod
```

Migrations applied **only** via the CI/CD pipeline ([07-cicd-architecture.md](07-cicd-architecture.md)) — never manually against Test/UAT/Prod. Promotion gate: migration applied and smoke-tested in the lower environment before the same migration is promoted. No environment ever receives a migration that skipped a lower environment, including hotfixes (a hotfix still flows Dev→Test→UAT→Prod, compressed in time, not skipped in sequence).
