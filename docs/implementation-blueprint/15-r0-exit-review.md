# 15 — R0 Exit Review

**Status: PASSED — 2026-08-05. Branch `feature/r0-repository-init` (5 commits) off tag `design-baseline-v1.1`. All required GitHub Actions checks green. Recommending merge to `main` and tag `v1.1.0-R0` once the required PR review is recorded.**

**Scope:** verifies R0 — Repository Initialisation against Design Baseline v1.1 and the R0 work order constraints (engineering foundation only — no business logic, no endpoints, no screens, no database population, no redesign).

---

## Checklist

| Criterion | Result | Evidence |
|---|---|---|
| Repository structure matches Design Baseline v1.1 | ✅ Pass | `apps/`, `packages/`, `database/`, `infrastructure/`, `tests/`, `scripts/`, `.github/`, `.adr/`, `.acr/` all present per [13-application-foundation-scaffold.md](13-application-foundation-scaffold.md) §1 |
| No architectural deviations introduced | ✅ Pass | `git diff design-baseline-v1.1..feature/r0-repository-init -- docs/ .acr/` = 2 new files only: `.acr/README.md`, `.acr/TEMPLATE.md` (governance index/template, not architecture). Zero changes to any knowledge-graph document or existing ACR. |
| CI passes | ✅ Pass — on GitHub Actions, not just locally (see §Post-review validation below) | All 6 `pr-validation.yml` jobs green on the PR |
| React builds successfully | ✅ Pass | `npm run build:web` — `tsc -b && vite build`, 0 errors |
| FastAPI starts successfully | ✅ Pass | `uvicorn app.main:app` started live, `GET /health` → `200 {"status":"ok","environment":"dev"}`, `GET /openapi.json` → `200` — with no live Postgres/Neo4j running (lazy DI confirmed) |
| TypeScript compiles | ✅ Pass | `apps/web` + all 4 `packages/*` compile via `tsc` with zero errors |
| Ruff passes | ✅ Pass | `ruff check app`: All checks passed. `ruff format --check app`: 168 files already formatted |
| MyPy passes | ✅ Pass | `mypy app`: Success, no issues found in 168 source files |
| Pytest passes | ✅ Pass | `pytest tests/unit -v`: 3 passed (app constructs, `/health` registered, all 20 routers carry zero live routes) |
| OpenAPI validation passes | ✅ Pass | `scripts/validate_openapi.py`: 64 paths, 76 schemas, 0 dangling `$ref`s |
| Ontology validation behaves as expected | ✅ Pass | `scripts/validate_ontology.py`: "no ontology seed concepts yet — nothing to validate" (correct — no ontology content exists at R0) |
| Graph validation behaves as expected | ✅ Pass | `scripts/run_graph_tests.py`: "no graph tests yet — nothing to run" (correct — no Neo4j instance graph exists at R0) |
| Docker Compose syntax validates | ✅ Pass | `docker compose -f docker-compose.dev.yml config` and `...test.yml config` both parse clean. **Caveat, not silently passed over:** Docker daemon was not running in this environment, so actual image builds (`docker build`) were not executed — compose/Dockerfile syntax is verified, runtime behavior is not. |
| No business logic exists | ✅ Pass | `grep -rn "class.*Base" apps/api/app/models/` → only `Base(DeclarativeBase)` itself, zero ORM tables defined |
| No API endpoints implemented | ✅ Pass | `grep -rn "@router\.(get\|post\|put\|patch\|delete)" apps/api/app/routers/` → 0 matches across all 20 routers |
| No database schema implemented | ✅ Pass | `database/postgres/migrations/versions/` contains only `.gitkeep` — zero migrations generated |
| No placeholder code pretending to be complete | ✅ Pass | `grep -rn "TODO\|FIXME\|XXX"` across `apps/web/src` and `apps/api/app` → 0 matches. Every placeholder file carries an explicit "R0 scaffold placeholder" docstring/comment stating what it is and where the real implementation lands (R1+), not a silent stub |

## Post-review validation (CI)

This review was first written against the branch as pushed, before the PR's checks had actually run on GitHub. That surfaced a real gap between local and CI verification, resolved before merge:

- **Issue identified:** the GitHub Actions Web job failed despite the equivalent build/lint/format sequence having passed locally on Windows.
- **Root cause:** a cross-platform dependency-resolution issue between the checked-in lockfile and the Linux CI runner, specific to Vite 8's newer native-binary-based bundler toolchain.
- **Investigation performed:**
  - Confirmed the failure was not a CI configuration mistake (job steps matched the local sequence exactly).
  - Confirmed the same underlying resolution issue persisted after switching the install step from `npm ci` to `npm install`, ruling out lockfile-strictness as the cause.
  - Confirmed the Docker build path (`apps/web/Dockerfile`) goes through the identical install step and would hit the same failure.
- **Corrective action:**
  - Downgraded `apps/web` to the stable Vite 6 toolchain (mature, cross-platform-proven dependency resolution), with a matching `@vitejs/plugin-react` version.
  - Applied the same install-step change to both the CI workflow and the Docker build path.
  - Removed a redundant per-package lockfile left over from before this repo used npm workspaces, leaving one authoritative root lockfile.
- **Verification evidence:**
  - Local lint, format, type-check, and production build all passed again after the change.
  - All 6 required checks on PR #11 completed successfully on GitHub Actions (not just locally).
- **Residual risk / follow-up:** `merge-main-build.yml`'s container build jobs have not yet executed against `main` — that workflow only triggers on push to `main`, so first real evidence of end-to-end container build success arrives with the first post-merge run. Flagging this for monitoring immediately after merge, not treating the untested path as verified.

## Known limitations carried forward (not blocking R0, tracked for R1+)

- Docker images not actually built locally (daemon unavailable this session), and `merge-main-build.yml` has not yet run against `main` — see Post-review validation above. First real build evidence arrives with the first post-merge run; monitor it before R1 relies on `docker compose up` for local dev.
- Five frontend tooling choices remain `TO_BE_CONFIRMED` pending ADRs: routing (React Router assumed), server-state (TanStack Query assumed), client-state (Zustand assumed), forms (React Hook Form + Zod assumed), — see [.adr/README.md](../../.adr/README.md).
- `infrastructure/bicep` only wires the Key Vault module; Container Apps, Postgres Flexible Server, Storage, Networking, Identity, and Monitoring modules remain unimplemented placeholders — full provisioning is a separate R0-exit/R1-entry activity, not scoped into this repository-initialisation pass.
- Neo4j/Qdrant managed-vs-self-hosted decision still open (tracked since Phase 2.1, [06-environment-strategy.md](06-environment-strategy.md)).

None of these block the merge — they are pre-existing open items or explicitly out of this pass's scope, not defects introduced by R0.

## Recommendation

**Merge `feature/r0-repository-init` → `main` via PR once the required review is recorded, then tag `v1.1.0-R0`.** This becomes the baseline commit implementation work builds from. Monitor the first post-merge run of `merge-main-build.yml` to confirm the container builds actually succeed end-to-end.
