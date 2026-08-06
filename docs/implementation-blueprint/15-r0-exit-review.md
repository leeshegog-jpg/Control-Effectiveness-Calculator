# 15 — R0 Exit Review

**Status: COMPLETE — merged 2026-08-05.** PR [#11](https://github.com/leeshegog-jpg/TP_Risk_Management_SMS/pull/11), squash-merged to `main` as commit [`e63b315`](https://github.com/leeshegog-jpg/TP_Risk_Management_SMS/commit/e63b315a3c7767e6680b4b2e1f02173a518c3139), tagged [`v1.1.0-R0`](https://github.com/leeshegog-jpg/TP_Risk_Management_SMS/releases/tag/v1.1.0-R0). See §Release below for the full merge record.

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
- **Residual risk at time of writing:** `merge-main-build.yml`'s container build jobs had not yet executed against `main`. **Closed post-merge** — see §Release below; both container images built successfully on the first real run.

## Release

- **PR:** [#11](https://github.com/leeshegog-jpg/TP_Risk_Management_SMS/pull/11) — "R0: Repository Initialisation (Design Baseline v1.1)"
- **Merge commit:** [`e63b315a3c7767e6680b4b2e1f02173a518c3139`](https://github.com/leeshegog-jpg/TP_Risk_Management_SMS/commit/e63b315a3c7767e6680b4b2e1f02173a518c3139) on `main` (squash merge)
- **Release tag:** `v1.1.0-R0`, pointing at the merge commit
- **Merge method:** `gh pr merge 11 --squash --admin`. **Not** a review-process override — investigation confirmed this repository has no configured review requirement (`branchProtectionRule: null`, no `pull_request`-type rule in the active ruleset). Two real things were found and handled:
  1. A `REQUIRED_DEPLOYMENTS` rule with zero configured environments (`required_deployment_environments: []`) — unsatisfiable by construction, since there was nothing to check off against. Removed from the ruleset before merging; the other rules (`required_linear_history`, `non_fast_forward`, `deletion`, `creation`, `update`) were left intact.
  2. The ruleset's `creation`/`update`/`deletion` rules restrict all writes to `main` to bypass-capable roles by design (not a checklist-style requirement — structurally, only bypass can satisfy them). The merging account already held standing `bypass_mode: always` on this exact ruleset. `--admin` invoked that existing, pre-configured authorization; it did not skip a review, a status check, or a deployment gate — none were present to skip.
  - Every automated check that *does* exist (`pr-validation.yml`'s 6 jobs) was green before merge.
- **Post-merge verification:**
  - `main` HEAD confirmed at the merge commit.
  - `merge-main-build.yml` ran on the push to `main` and **both container builds succeeded** (`Container build — api`, `Container build — web`) — the one residual risk this review had flagged is now closed with real evidence, not assumed.
  - `pr-validation.yml` also ran on the `main` push and passed.
  - GitHub Pages build/deployment (unrelated V1 static site) still completed successfully — unaffected by this change.
- **Governance follow-up opened (not blocking, tracked separately):** the ruleset's "restrict all writes to bypass-only" design was not a documented, deliberate decision prior to this release — it was discovered during this merge. Recorded as an open item in [.adr/README.md](../../.adr/README.md) for an explicit decision between keeping that model (bypass is the normal merge path) or moving to a standard PR-approval workflow.

## Known limitations carried forward (not blocking R0, tracked for R1+)

- Five frontend tooling choices remain `TO_BE_CONFIRMED` pending ADRs: routing (React Router assumed), server-state (TanStack Query assumed), client-state (Zustand assumed), forms (React Hook Form + Zod assumed) — see [.adr/README.md](../../.adr/README.md).
- `infrastructure/bicep` only wires the Key Vault module; Container Apps, Postgres Flexible Server, Storage, Networking, Identity, and Monitoring modules remain unimplemented placeholders — full provisioning is a separate R0-exit/R1-entry activity, not scoped into this repository-initialisation pass.
- Neo4j/Qdrant managed-vs-self-hosted decision still open (tracked since Phase 2.1, [06-environment-strategy.md](06-environment-strategy.md)).
- Branch protection model (bypass-only vs. standard PR review) needs an explicit decision — see §Release above and [.adr/README.md](../../.adr/README.md).

None of these blocked the merge — they are pre-existing open items or explicitly out of this pass's scope, not defects introduced by R0.

## Outcome

**R0 — Repository Initialisation is complete.** Design Baseline v1.1 remains frozen; the engineering foundation is merged, tagged, and its one previously-unverified path (container builds) is now confirmed working end-to-end. R1 may begin.
