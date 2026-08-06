# Architecture Decision Records

Implementation-time decisions that don't change the frozen Design Baseline (v1.1) — tooling choices, library selections, internal code organisation. If a decision would change the ontology, schema, Neo4j model, OpenAPI contract, or module boundaries, it needs an [ACR](../.acr/README.md), not an ADR.

Use [TEMPLATE.md](TEMPLATE.md) for new entries.

## Open decisions flagged during R0 release (2026-08-05)

- **Branch protection / merge model for `main`.** Discovered during the R0 merge (PR #11), not previously a documented decision: the repository's active ruleset restricts all writes to `main` (`creation`/`update`/`deletion` rules) to bypass-capable roles by construction — there is no configured review or status-check requirement. That made `gh pr merge --admin` the only way to merge, for anyone, regardless of approvals. Two models, either valid, need an explicit choice recorded here before it becomes an accidental default:
  - **Option A — Locked main (current behaviour):** only bypass-authorized roles can update `main`; `--admin` is the expected, normal merge command, not an exception.
  - **Option B — Standard PR workflow:** configure an actual required-review/status-check rule so normal (non-bypass) merges succeed once requirements are met; reserve `--admin`/bypass for genuine exceptions.
  - See [15-r0-exit-review.md](../docs/implementation-blueprint/15-r0-exit-review.md) §Release for the full investigation (a separate, now-fixed issue — an unsatisfiable `REQUIRED_DEPLOYMENTS` rule with zero environments — was found and removed in the same pass, unrelated to this decision).
  - **Sub-question still open on Option B specifically:** GitHub blocks self-approval platform-wide, no setting overrides it. A required-review count ≥1 on a single-maintainer repo makes `--admin` routine again (same deadlock, just with an unsatisfiable checkbox added), unless either a second reviewer/collaborator is added, or the review requirement is left unset (0) while still requiring PR + passing CI + no direct pushes. Pick one before configuring Option B, not after.

## Decisions recorded

- **[ADR-001](ADR-001-baseline-tag-immutability.md)** — release tags (`vX.Y.Z-RN`) are immutable; defects are fixed forward, never by re-pointing a tag. Accepted 2026-08-05.

## Open decisions flagged during R0/Phase 2.2 scaffolding

Per [docs/implementation-blueprint/13-application-foundation-scaffold.md](../docs/implementation-blueprint/13-application-foundation-scaffold.md) §2, these should become ADRs before R1 implementation begins:

- Frontend routing library (scaffold assumes React Router)
- Server-state library (scaffold assumes TanStack Query)
- Client-state library (scaffold assumes Zustand, UI-local state only)
- Form library (scaffold assumes React Hook Form + Zod)
- Build tool (scaffold uses Vite — this one is arguably already settled by having built the R0 scaffold with it; confirm and close out rather than re-litigate)

## Index

| ADR | Title | Status |
|---|---|---|
| [ADR-001](ADR-001-baseline-tag-immutability.md) | Release Tags Are Immutable | Accepted |
