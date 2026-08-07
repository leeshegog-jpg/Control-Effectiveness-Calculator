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
7. Open the PR using the template — the checklist there is not optional for schema/ontology/regulatory-citation changes (2 approving reviews recommended by convention for those; no minimum approval count is machine-enforced while the project is single-maintained, see Branch Governance below and [ADR-002](.adr/ADR-002-branch-protection-model.md)).
8. **Merge with `--squash` or `--rebase`, not `--merge`.** The repo's ruleset requires linear history — a merge commit will be rejected. All 6 required checks must pass before merge; once they do, `gh pr merge --squash` succeeds normally, no `--admin` needed. See [ADR-002](.adr/ADR-002-branch-protection-model.md).

## Branch Governance

- All changes are developed on feature branches.
- All changes are merged through Pull Requests — direct pushes to `main` are rejected by the repo's ruleset.
- Pull Requests provide the permanent review and decision record.
- CI must pass before merge (6 required checks — see `.github/workflows/pr-validation.yml`).
- Architectural changes require an approved [ACR](.acr/README.md); implementation-time decisions are recorded as [ADRs](.adr/README.md).
- Release tags are immutable ([ADR-001](.adr/ADR-001-baseline-tag-immutability.md)).
- While the project has a single maintainer, no minimum PR approval count is configured ([ADR-002](.adr/ADR-002-branch-protection-model.md)) — GitHub cannot enforce self-review, so a required-approval count with no second reviewer would just force routine `--admin` bypass instead of adding real assurance.
- When additional maintainers are appointed, a minimum of one independent approval will be introduced and `--admin` reserved for emergencies only.

## Commit messages

Conventional commits: `feat:`, `fix:`, `refactor:`, `docs:`, `test:`, `chore:`, `perf:`, `ci:`. See [docs/implementation-blueprint/02-development-standards.md](docs/implementation-blueprint/02-development-standards.md) for the full convention.

## Local dev environment

See [DEVELOPMENT.md](DEVELOPMENT.md).
