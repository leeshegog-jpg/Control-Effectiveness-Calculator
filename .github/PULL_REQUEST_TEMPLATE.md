## Summary

<!-- What changed and why -->

## Linked work item

<!-- Issue/ticket referencing a specific module from docs/implementation-blueprint/03-module-dependency-map.md -->

## Checklist — docs/implementation-blueprint/02-development-standards.md §4–§5

- [ ] CI green: lint, typecheck, unit tests
- [ ] If this touches `docs/knowledge-graph/10-openapi.yaml`: `packages/shared-types` regenerated in this PR
- [ ] If this touches `docs/knowledge-graph/03-postgresql-schema.sql` or the Neo4j model: a migration file is included in this PR
- [ ] Respects the relationship rules in `06-relationship-rules-catalogue.md` (no bypassing a business rule, e.g. writing `Control.classification` without running the 3-gate test)
- [ ] Respects critical-item overrides (`04-ai-extraction-specification.md` §6, `11-safety-case-demonstration-model.md` §7.3) — nothing touching a critical control, SFAIRP/serious-risk justification, or regulatory notification auto-publishes
- [ ] Does not introduce a new relationship type or ontology concept without an approved entry
- [ ] Does not silently resolve a `TO_BE_CONFIRMED` marker without evidence
- [ ] No architecture deviation without an approved ACR (`.acr/`)

## Review requirement

1 approving review for standard changes. **2 approving reviews** required for: schema changes, ontology scheme changes, any change touching a regulatory citation or `TO_BE_CONFIRMED` marker, or anything in the Safety Case Demonstration Engine's narrative-generation path.

## Test evidence

<!-- Paste relevant test output, screenshots, or CI run links -->
