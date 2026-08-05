# Neo4j — Constraints, Indexes & Sync

Instance data is **not** migrated here — Postgres is the system of record and Neo4j is a rebuildable projection synced at runtime by the Graph Sync Service (see [docs/knowledge-graph/01-enterprise-knowledge-graph-specification.md](../../docs/knowledge-graph/01-enterprise-knowledge-graph-specification.md) §4). This folder stays small by design.

- `schema/` — reference copy of node label definitions for scripting convenience; [docs/knowledge-graph/02-neo4j-node-relationship-model.md](../../docs/knowledge-graph/02-neo4j-node-relationship-model.md) remains authoritative.
- `constraints/`, `indexes/` — versioned Cypher DDL (§5 of the model doc). Empty at R0.
- `ontology-import/` — scripts loading `ontology/schemes` + `ontology/seed-concepts` into the ontology graph. Not implemented yet.
- `inference-rules/` — Cypher implementations of R1–R22 ([docs/knowledge-graph/07-inference-rules-catalogue.md](../../docs/knowledge-graph/07-inference-rules-catalogue.md)). Not implemented yet.
- `migrations/` — versioned, idempotent constraint/index changes (not instance-data migrations).
