# PostgreSQL — Migrations & Seeds

System of record. Schema source of truth: [docs/knowledge-graph/03-postgresql-schema.sql](../../docs/knowledge-graph/03-postgresql-schema.sql) — a migration that drifts from it is a bug, not a valid change (see [docs/implementation-blueprint/05-database-migration-strategy.md](../../docs/implementation-blueprint/05-database-migration-strategy.md)).

- `migrations/` — Alembic migration history. Tooling wired (`alembic.ini` at repo root, `env.py`/`script.py.mako` here), **zero migrations generated yet** — no ORM models are populated (R0 constraint: no database population).
- `seeds/dev-fixtures/` — synthetic data, Dev/Test only.
- `seeds/pilot-register/` — V1's 108-row/14-hazard pilot register migration script. Real reference data, not disposable.
- `seeds/views/` — read-optimized SQL views (e.g. control-health rollups feeding the Dashboard module).
- `procedures/` — placeholder only. No stored procedure is approved in Design Baseline v1.1; any addition requires an ACR (business logic in the database layer bypasses the `services/` rule-enforcement point).
