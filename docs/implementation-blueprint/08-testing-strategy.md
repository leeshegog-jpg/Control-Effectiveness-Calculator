# 08 — Testing Strategy
**Status: DRAFT — Phase 2.1 Implementation Blueprint. Baseline: Design Baseline v1.0 (frozen).**

---

## 1. Unit Testing

Per-module business logic — every rule in [07-inference-rules-catalogue.md](../knowledge-graph/07-inference-rules-catalogue.md) (R1–R18) gets a dedicated unit test with positive and negative cases, and every gate/test in [08-critical-control-assurance-model.md](../knowledge-graph/08-critical-control-assurance-model.md) (3-gate, EIA, FARSI banding) likewise. Located in `tests/unit`, mirroring `apps/api` module structure ([01-repository-structure.md](01-repository-structure.md)).

## 2. Integration Testing

API + database, ephemeral Postgres/Neo4j containers ([07-cicd-architecture.md](07-cicd-architecture.md) §3). Covers cross-entity writes (e.g. creating a `Risk` correctly cascades ontology FK validation) and the Graph Sync Service's Postgres→Neo4j propagation.

## 3. API Testing

Contract tests generated from [10-openapi.yaml](../knowledge-graph/10-openapi.yaml) (e.g. Schemathesis) — every one of the 56 paths exercised against its schema, confirming the implementation never silently diverges from the approved contract. Runs in PR validation ([07](07-cicd-architecture.md) §2).

## 4. Graph Validation

Every relationship rule in [06-relationship-rules-catalogue.md](../knowledge-graph/06-relationship-rules-catalogue.md) — §3 (instance graph), §4 (ontology graph), §5 (cross-chain integrity rules 1–4), §5a (Safety Case Demonstration relationships) — as an executable Cypher-backed test in `tests/graph`. Includes the acyclic `BROADER` check and the chain-consistency rule for `SUPPORTS`/`GROUNDED_IN` (§3, §5a).

## 5. Ontology Validation

`tests/ontology`: no orphan concepts (every `Concept` reachable from its `OntologyScheme`), no duplicate alias within one scheme ([06](../knowledge-graph/06-relationship-rules-catalogue.md) §4 `HAS_ALIAS` rule), no cycles, every `ExtractionRule.target_concept_id` resolves. Runs on every `ontology/` change ([07](07-cicd-architecture.md) §2) plus the weekly full-scope scan ([07](07-cicd-architecture.md) §5).

## 6. AI Extraction Validation

`tests/ai-extraction`: a golden set of real V1 source documents (the 108-row pilot register, sample procedures) with human-verified expected extraction output, tested against [04-ai-extraction-specification.md](../knowledge-graph/04-ai-extraction-specification.md) §4's schema and §6's confidence routing. Includes the worked example from that document ("Operator must isolate hydraulic pressure before maintenance" → hazard/risk/control/verification/evidence) as a permanent regression case. Weekly scheduled run ([07](07-cicd-architecture.md) §5) tracks accuracy drift over time — this is also the mechanism for calibrating the §6 confidence thresholds against real outcomes, per that document's own instruction that the starting defaults are not fixed.

## 7. Performance Testing

Load testing targets the query-pattern catalogue directly ([knowledge-graph/01](../knowledge-graph/01-enterprise-knowledge-graph-specification.md) §5, Q1–Q7) — these are the traversal shapes the platform's core objective depends on, so they're what gets performance-tested, not generic CRUD throughput. Executed against UAT-scale data volumes before go-live.

## 8. Security Testing

SAST/DAST per [07-cicd-architecture.md](07-cicd-architecture.md) §6, plus a pre-Prod penetration test covering: AuthN/AuthZ boundary enforcement, the Anthropic API key never being reachable client-side (direct regression test for architecture §1.4 finding 3), and Blob Storage access scoping for uploaded documents.

## 9. User Acceptance Testing

VRTP HSE and safety team sign-off, structured per release ([04-implementation-roadmap.md](04-implementation-roadmap.md)):
- **R1–R5** (strangler-fig cutovers): parity checklist against the corresponding V1 tool, signed off before the nav link repoints.
- **R6**: extraction accuracy review against the golden set (§6), Knowledge Graph Explorer usability review.
- **R7**: **the acceptance test that matters most** — a full generated `Demonstration` for a real ADH, reviewed against the Guide's own §7.3 standard ("a practical explanation of how something works," not "evidence of existence") by VRTP HSE, not just a developer confirming the API returns 200.

## Coverage Principle

Every layer above traces to a specific document/rule ID, not a generic "write tests for the code" instruction — this mirrors the traceability discipline the design baseline itself enforces (provenance model, [05-knowledge-provenance-model.md](../knowledge-graph/05-knowledge-provenance-model.md)) applied to the test suite.
