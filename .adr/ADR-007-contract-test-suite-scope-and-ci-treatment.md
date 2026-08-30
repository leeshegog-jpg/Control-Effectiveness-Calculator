# ADR-007: OpenAPI Contract Test Suite — Scope, Failure Semantics, and CI Treatment

**Status:** Proposed
**Context:** PR #44 (merged to `main` @ `150b571`) added a Schemathesis contract
suite at `tests/contract/`, validating the FastAPI app against the frozen
`docs/knowledge-graph/10-openapi.yaml`. It was merged **inactive** —
`.github/workflows/pr-validation.yml` does not execute `tests/contract`; branch
`ci/wire-contract-tests` (local, unpushed) holds the one-line activation.

Investigation established the suite cannot pass as written. It parametrizes all
**113** contracted operations; only **46** are implemented, the other **67** are
roadmap deferrals (consistent with `apps/api/app/main.py`'s own milestone-defer
docstring). Unimplemented operations return `404` → Schemathesis
`UndefinedStatusCode` failures (the frozen spec documents `404` on only 10 of
113 operations). The contract declares `security: [bearerAuth]` globally; the R1
implementation does not enforce authentication → `MissingHeaderNotRejected` on
all 113 operations. Both failure classes are DB-independent and reproducible.
Wiring the suite as-is would put a CI job permanently red on `main`.

A decision is needed on what the suite asserts, what counts as failure, what is
excluded, and how CI treats the result — before `ci/wire-contract-tests` is
touched. This ADR records that decision. It does not itself change
`tests/contract/`, the workflow, the OpenAPI contract, or the ruleset.

**Decision:**

*D1 — Population.* Strict pass/fail conformance is asserted against the **46
currently-implemented operations only**. The 67 unimplemented operations are
**not removed** from the suite — they are represented as explicit `skip` with
reason `deferred: not implemented (roadmap)`, classified at runtime by
introspecting the app's route table (no hand-maintained allowlist). This keeps
the full contracted surface visible in the test collection; implementing a
deferred operation then produces a visible follow-up — its `skip` must be
promoted to a strict assertion.

*D2 — Authentication.* The suite does **not** enforce `bearerAuth` and does
**not** supply a token. Schemathesis's auth-conformance checks
(`MissingHeaderNotRejected` / `ignored_auth`) are **disabled** for this suite,
with an inline reason referencing the risk-register entry below. The suite
reflects the current implementation; it is not the vehicle for an
authentication decision. The discrepancy — contract declares `bearerAuth`, R1
implementation does not enforce it — is recorded as a governed gap in
[11-implementation-risk-register.md](../docs/implementation-blueprint/11-implementation-risk-register.md)
(S4). When authentication enforcement is implemented (its own governed slice),
these checks are re-enabled.

*D3 — Deferred operations.* Per D1: `404` from an unimplemented operation is
**not a failure**. Deferred operations are skipped with a documented reason,
never asserted against, never silently dropped.

*D4 — CI treatment.* The suite runs as its **own non-required CI job** (not
folded into the `integration-tests` job), **report-only** — a red contract job
does not block a PR and does not mark `main` failing. It is diagnostic until
the promotion criteria below are met.

*D5 — Ruleset.* The branch-protection ruleset's required-status-checks set is
**not changed** by this decision. Promoting the contract job to a required
check is a separate ADR in the branch-protection domain (cf.
[ADR-002](ADR-002-branch-protection-model.md)), taken only after the promotion
criteria are met.

*Promotion criteria (report-only → blocking, future ADR):*
1. Suite green on the 46-operation population for 10 consecutive `main` builds,
   or 2 weeks, whichever is longer.
2. No Hypothesis/Schemathesis flakiness observed in that window.
3. Deferred-`skip` set reconciled against the actual unimplemented-operation set
   — no stale skips, no missing assertions.
4. Auth-conformance checks re-enabled (authentication enforcement implemented),
   or an explicit ADR carve-out if promotion precedes auth.

**Consequences:** The suite becomes a usable diagnostic as soon as it is wired
report-only — contract drift on implemented operations is caught in CI without
gating. `main` CI stays green; no permanently-red job. The 67 deferred
operations remain documented in the test surface, and implementing one surfaces
a required follow-up. The auth gap is explicit and tracked, not masked by a
token the app ignores. Activation still requires, each with its own GO: (a)
this ADR accepted; (b) an implementation slice for the D1–D3 behaviour plus its
own validation; (c) a CI-wiring change (own job, report-only). `ci/wire-contract-tests`
as it currently stands (one line appended to the `integration-tests` job) does
not match D4 and is superseded by this decision.
