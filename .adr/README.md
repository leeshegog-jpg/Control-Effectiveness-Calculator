# Architecture Decision Records

Implementation-time decisions that don't change the frozen Design Baseline (v1.1) — tooling choices, library selections, internal code organisation. If a decision would change the ontology, schema, Neo4j model, OpenAPI contract, or module boundaries, it needs an [ACR](../.acr/README.md), not an ADR.

Use [TEMPLATE.md](TEMPLATE.md) for new entries.

## Decisions recorded

- **[ADR-001](ADR-001-baseline-tag-immutability.md)** — release tags (`vX.Y.Z-RN`) are immutable; defects are fixed forward, never by re-pointing a tag. Accepted 2026-08-05.
- **[ADR-002](ADR-002-branch-protection-model.md)** — branch protection model for `main`: PR + required CI checks, no minimum approval count while single-maintained ("Option A"), reserved for revisit once a second regular reviewer exists. Accepted 2026-08-07. Closes the merge deadlock discovered during the R0 merge (PR #11) — see [15-r0-exit-review.md](../docs/implementation-blueprint/15-r0-exit-review.md) §Release for the original investigation.

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
| [ADR-002](ADR-002-branch-protection-model.md) | Branch Protection Model — Option A (PR + CI, No Minimum Approval Count) | Accepted |
