# Architecture Decision Records

Implementation-time decisions that don't change the frozen Design Baseline (v1.1) — tooling choices, library selections, internal code organisation. If a decision would change the ontology, schema, Neo4j model, OpenAPI contract, or module boundaries, it needs an [ACR](../.acr/README.md), not an ADR.

Use [TEMPLATE.md](TEMPLATE.md) for new entries.

## Open decisions flagged during R0/Phase 2.2 scaffolding

Per [docs/implementation-blueprint/13-application-foundation-scaffold.md](../docs/implementation-blueprint/13-application-foundation-scaffold.md) §2, these should become ADRs before R1 implementation begins:

- Frontend routing library (scaffold assumes React Router)
- Server-state library (scaffold assumes TanStack Query)
- Client-state library (scaffold assumes Zustand, UI-local state only)
- Form library (scaffold assumes React Hook Form + Zod)
- Build tool (scaffold uses Vite — this one is arguably already settled by having built the R0 scaffold with it; confirm and close out rather than re-litigate)

## Index

No ADRs recorded yet.
