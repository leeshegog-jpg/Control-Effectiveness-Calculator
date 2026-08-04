# 02 — Development Standards
**Status: DRAFT — Phase 2.1 Implementation Blueprint. Baseline: Design Baseline v1.0 (frozen).**

---

## 1. Branching Strategy

Trunk-based development with short-lived branches.

| Branch | Purpose | Lifetime |
|---|---|---|
| `main` | Always deployable to Dev. Protected — no direct pushes, PR + passing CI + review required. | Permanent |
| `release/x.y` | Cut from `main` for UAT/Prod promotion. Only fixes cherry-picked, no new features. | Until superseded |
| `feature/<ticket>-<slug>` | One module/story per branch. | Days, not weeks |
| `fix/<ticket>-<slug>` | Bug fixes. | Days |
| `chore/<slug>` | Tooling, CI, non-functional changes. | Days |

No long-lived per-developer or per-module branches — the strangler-fig migration ([PLATFORM_ARCHITECTURE_V2.md](../PLATFORM_ARCHITECTURE_V2.md) §8) already means the codebase and the live V1 site coexist for a long period; the repository itself should not add a second axis of long-lived divergence on top of that.

## 2. Semantic Versioning

Three independently-versioned artefacts, because they change at different rates and a change to one does not imply a change to the others:

| Artefact | Versioning | Bump trigger |
|---|---|---|
| Platform release | `MAJOR.MINOR.PATCH` | MAJOR: breaking API contract change. MINOR: new module/feature. PATCH: fix, no contract change |
| OpenAPI contract (`10-openapi.yaml`) | Its own `MAJOR.MINOR.PATCH` (already `0.1.0-draft`) | MAJOR: breaking path/schema removal or type change. MINOR: additive endpoint/field. PATCH: description/doc fix |
| Ontology scheme | Per-scheme version (`ontology.schemes.version`, [03-postgresql-schema.sql](../knowledge-graph/03-postgresql-schema.sql)) | Incremented on any published `Concept` change within that scheme — independent of platform releases entirely, since ontology governance ([01-enterprise-knowledge-graph-specification.md](../knowledge-graph/01-enterprise-knowledge-graph-specification.md) §6) is a curator process, not a dev release process |

## 3. Commit Conventions

[Conventional Commits](https://www.conventionalcommits.org/): `<type>(<scope>): <description>`.

Types: `feat`, `fix`, `docs`, `chore`, `refactor`, `test`, `perf`, `ci`. Scope: module name (`hazard`, `critical-control`, `ontology`, `demonstration-engine`, etc.) or `repo` for cross-cutting changes. Breaking changes: `!` after type/scope + `BREAKING CHANGE:` footer — required whenever the OpenAPI contract's MAJOR version bumps.

## 4. Pull Request Requirements

- Linked to a tracked work item referencing a specific module from [03-module-dependency-map.md](03-module-dependency-map.md).
- CI green: lint, typecheck, unit tests, and — where the change touches schema/API/ontology — the corresponding validation pipeline ([07-cicd-architecture.md](07-cicd-architecture.md)).
- If the change touches `10-openapi.yaml`: `packages/shared-types` regenerated in the same PR, not a follow-up.
- If the change touches `03-postgresql-schema.sql` or the Neo4j model: a migration file included in the same PR.
- **1 approving review** for standard changes. **2 approving reviews** for: schema changes, ontology scheme changes, any change touching a regulatory citation or `TO_BE_CONFIRMED` marker, and anything in the Safety Case Demonstration Engine's narrative-generation path ([11-safety-case-demonstration-model.md](../knowledge-graph/11-safety-case-demonstration-model.md) §7.3).
- No direct pushes to `main` or `release/*`.

## 5. Code Review Checklist

Beyond standard code quality, every reviewer checks against the frozen baseline:

- Does this respect the relationship rules in [06-relationship-rules-catalogue.md](../knowledge-graph/06-relationship-rules-catalogue.md), or does it bypass a business rule (e.g. writing a `Control.classification` without running the 3-gate test)?
- Does this respect the critical-item overrides ([04-ai-extraction-specification.md](../knowledge-graph/04-ai-extraction-specification.md) §6, [11](../knowledge-graph/11-safety-case-demonstration-model.md) §7.3) — nothing touching a critical control, SFAIRP/serious-risk justification, or regulatory notification auto-publishes?
- Does this introduce a new relationship type or ontology concept without an approved entry ([06](../knowledge-graph/06-relationship-rules-catalogue.md) §6, [01](../knowledge-graph/01-enterprise-knowledge-graph-specification.md) §6)?
- Does this silently resolve a `TO_BE_CONFIRMED` marker without evidence, or does it correctly leave it open?

## 6. Architecture Decision Record (ADR) Process

For decisions made *during implementation* that the frozen baseline doesn't already specify (e.g. "Alembic vs. raw SQL migration runner," "which Azure Container Apps scaling policy"). Template:

```
# ADR-NNN: <Title>
Status: Proposed | Accepted | Superseded by ADR-NNN
Context: <what decision is needed and why>
Decision: <what was decided>
Consequences: <what this makes easier/harder>
```

Stored in `.adr/`, numbered sequentially, never deleted (superseded, not removed — same immutable-history principle as [05-knowledge-provenance-model.md](../knowledge-graph/05-knowledge-provenance-model.md)).

## 7. Architecture Change Request (ACR) Process

Design Baseline v1.0 (the architecture doc + all 11 knowledge-graph documents) is **frozen**. Any change to it — a new entity, a changed relationship, a different tech-stack component — requires an ACR, not a PR against `docs/knowledge-graph/`.

```
# ACR-NNN: <Title>
Raised by: <name>, <date>
Affected document(s): <e.g. 03-postgresql-schema.sql, 08-critical-control-assurance-model.md>
Current state: <what the baseline currently says>
Proposed change: <what would change and why>
Impact: <what else in the 12-document set / codebase this touches>
Approval: <pending | approved by <you> on <date> | rejected>
```

Stored in `.acr/`, sequentially numbered. **No implementation work proceeds against a proposed change until the ACR is approved** — this is the mechanism that stops the "architecture drift during implementation" failure mode, mirroring exactly what the ontology's own concept-governance workflow does for vocabulary (EKG spec §6), applied here to the architecture itself.

## 8. Definition of Ready

A work item is ready to start when:
- It references a specific entity/relationship/rule ID from the Design Baseline (e.g. "implement R14" or "implement the `HAS_BOUNDARY` relationship" — not "build the boundary feature").
- Acceptance criteria are traceable to a specific document/section.
- No unresolved `TO_BE_CONFIRMED` marker blocks it — if one does, the item is blocked, not started with an assumption substituted in.
- Dependencies per [03-module-dependency-map.md](03-module-dependency-map.md) are met (prerequisite modules merged to `main`).

## 9. Definition of Done

- Code merged to `main`, CI green.
- Tests exist per [08-testing-strategy.md](08-testing-strategy.md) for the relevant layer(s).
- OpenAPI/schema/ontology docs updated in the same PR if the contract changed (§4).
- Deployed and smoke-tested in Dev.
- No new `TO_BE_CONFIRMED` introduced silently — if the work surfaced a new open question, it's logged in the relevant document's open-items list, not left implicit in code.
- No architecture deviation without an approved ACR (§7).
