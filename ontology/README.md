# Ontology Content

Governed data, not code — see [docs/knowledge-graph/01-enterprise-knowledge-graph-specification.md](../docs/knowledge-graph/01-enterprise-knowledge-graph-specification.md) §6 for the draft → reviewed → approved → published governance workflow.

- `schemes/` — one file per `OntologyScheme` (Hazard, Control, Consequence, Competency Category, Emergency Service Organisation, ...). Empty at R0.
- `seed-concepts/` — initial concept sets ported from V1 (`REF.controlHierarchy`, `REF.consequenceDomains`, energy-source list) plus the Design Baseline v1.1 additions. Empty at R0 — populated at R0 exit per [docs/implementation-blueprint/04-implementation-roadmap.md](../docs/implementation-blueprint/04-implementation-roadmap.md) R0 exit criteria.
- `validation/` — schema for concept files, acyclic-`BROADER` checker config.

No concepts are seeded yet. This is engineering-foundation scaffolding only — no database population per the R0 constraint.
