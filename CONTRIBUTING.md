# Contributing

Full standards: [docs/implementation-blueprint/02-development-standards.md](docs/implementation-blueprint/02-development-standards.md). This file is the quick-start version.

## Before you start

The Design Baseline (architecture, ontology, PostgreSQL schema, Neo4j model, OpenAPI contract, Safety Case model) is **frozen at v1.1**. Do not implement against a `TO_BE_CONFIRMED` marker, and do not add an entity, relationship, or endpoint that isn't already in `docs/knowledge-graph/`. If your change needs one, open an [ACR](.acr/README.md) first — see [.acr/TEMPLATE.md](.acr/ACR-001-training-domain.md) for the shape a real one takes.

## Workflow

1. Branch from `main` (or the current integration branch): `feature/<short-description>` or `fix/<short-description>`.
2. Write the test first where practical (unit → integration → contract, per [08-testing-strategy.md](docs/implementation-blueprint/08-testing-strategy.md)).
3. Implement against the Design Baseline entity/relationship/rule ID, not a paraphrase of it (Definition of Ready, [02-development-standards.md](docs/implementation-blueprint/02-development-standards.md) §8).
4. Run locally before opening a PR:
   - Web: `npm run build:web && npm run lint:web && npm run format:check:web`
   - API: `ruff check apps/api/app && ruff format --check apps/api/app && mypy apps/api/app && pytest tests/unit -v`
5. If you touched `docs/knowledge-graph/10-openapi.yaml`, regenerate `packages/shared-types` in the same PR.
6. If you touched the PostgreSQL schema or Neo4j model, include the migration in the same PR — see [05-database-migration-strategy.md](docs/implementation-blueprint/05-database-migration-strategy.md).
7. Open the PR using the template — the checklist there is not optional for schema/ontology/regulatory-citation changes (2 approving reviews required).

## Commit messages

Conventional commits: `feat:`, `fix:`, `refactor:`, `docs:`, `test:`, `chore:`, `perf:`, `ci:`. See [docs/implementation-blueprint/02-development-standards.md](docs/implementation-blueprint/02-development-standards.md) for the full convention.

## Local dev environment

See [DEVELOPMENT.md](DEVELOPMENT.md).
