# ADR-002: Branch Protection Model — Option A (PR + CI, No Minimum Approval Count)

**Status:** Accepted (2026-08-07)
**Context:** Discovered during the R0 merge (PR #11) that the repository's ruleset restricted all writes to `main` to bypass-capable roles by construction (`update`/`creation`/`deletion` rule types), with no PR or CI requirement at all — merging required `--admin` regardless of review state, because there was nothing to satisfy other than bypass. Two models were considered (see [15-r0-exit-review.md](../docs/implementation-blueprint/15-r0-exit-review.md) §Release for the original investigation):

- **Option A** — PR + CI required, no minimum approval count, while the project has a single maintainer.
- **Option B** — PR + CI + ≥1 required approval.

Option B has a structural problem on a single-maintainer repo: GitHub blocks self-approval platform-wide, with no override. Setting a required-approval count with no second reviewer available makes `--admin` routine again — the exact problem this ADR exists to close — just with an unsatisfiable checkbox added on top.

**Decision:** Option A. The ruleset (`main` only, via `~DEFAULT_BRANCH` — previously scoped to all refs, which also blocked plain pushes to feature branches unnecessarily) now requires:
- A pull request (`pull_request` rule, `required_approving_review_count: 0`) — no direct pushes to `main`, but no minimum-reviewer deadlock either
- All 6 `pr-validation.yml` checks passing (`required_status_checks`, strict)
- Linear history (`required_linear_history`) — squash or rebase merges only, no merge commits
- No force-push (`non_fast_forward`)
- No deletion (`deletion`)

Bypass is retained for the admin role and the GitHub Actions integration only (narrowed from the broader write/maintain grant this ruleset originally had), reserved for genuine exceptions — not the normal merge path anymore.

**When to revisit:** once a second regular maintainer/reviewer exists, move to Option B — add `required_approving_review_count: 1`, and treat `--admin` bypass as an emergency-only path from that point on, per the standing governance policy in [CONTRIBUTING.md](../CONTRIBUTING.md).

**Consequences:** Normal PRs now merge via `gh pr merge --squash` (or `--rebase`) once CI is green, with no `--admin` needed — the deadlock discovered during the R0 merge is closed. PRs remain the permanent review/decision record even without a required approval count. Feature branches are no longer restricted by this ruleset at all (previously scoped to all refs), removing unrelated friction on day-to-day pushes.
