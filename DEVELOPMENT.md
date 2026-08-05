# Local Development Setup

R0 scaffold — no endpoints, no screens, no seeded databases. This gets the toolchain running so R1 implementation has somewhere to land.

## Prerequisites

- Node.js 24+, npm 12+
- Python 3.12+ (pinned in `.python-version`)
- Docker Desktop (for Postgres/Neo4j/Qdrant — not required just to build/lint)

## Frontend (`apps/web`)

```bash
npm install                  # installs the whole npm workspace: apps/web + packages/*
npm run build:web            # tsc -b && vite build
npm run lint:web             # oxlint
npm run format:check:web     # prettier --check
npm run dev:web               # local dev server
```

Shared packages build independently:

```bash
npm run build --workspace packages/shared-types
npm run build --workspace packages/api-client
npm run build --workspace packages/ontology-client
npm run build --workspace packages/ui-components
```

## Backend (`apps/api`)

```bash
cd apps/api
python -m venv .venv
./.venv/Scripts/activate      # Windows; source .venv/bin/activate on macOS/Linux
pip install -e ".[dev]"
```

Verify the scaffold (no live database needed — engine/driver construction is lazy):

```bash
python -c "from app.main import app; print(len(app.routes))"
ruff check app
ruff format --check app
mypy app
pytest ../../tests/unit -v
```

Run it:

```bash
uvicorn app.main:app --reload
curl http://localhost:8000/health
```

## Database migrations

Alembic is configured at the repo root (`alembic.ini`), pointing at `database/postgres/migrations` — not `apps/api/`, to avoid two migration histories (see [13-application-foundation-scaffold.md](docs/implementation-blueprint/13-application-foundation-scaffold.md) §5). No migrations exist yet — `app.models.Base` has no tables defined (R0: no business logic).

```bash
alembic revision --autogenerate -m "description"
alembic upgrade head
```

## Full stack via Docker

```bash
docker compose -f docker-compose.dev.yml up
```

Brings up Postgres, Neo4j, Qdrant, the API, and the web dev server. See [docker-compose.dev.yml](docker-compose.dev.yml) for ports and credentials (dev-only, never real secrets).

For CI-style ephemeral integration testing: `docker-compose.test.yml` (tmpfs-backed, no persistent volumes).

## Validation scripts

```bash
python scripts/validate_openapi.py     # docs/knowledge-graph/10-openapi.yaml, zero dangling $refs
python scripts/validate_ontology.py    # ontology/seed-concepts/*.yaml acyclic + no duplicate aliases
python scripts/run_graph_tests.py      # tests/graph/*.py
```

All three report "OK, nothing to validate yet" honestly when their target content doesn't exist yet, rather than silently passing or failing.

## Environment variables

Copy `.env.example` to `.env` and fill in local values — see [09-configuration-management.md](docs/implementation-blueprint/09-configuration-management.md). Never commit `.env`.
