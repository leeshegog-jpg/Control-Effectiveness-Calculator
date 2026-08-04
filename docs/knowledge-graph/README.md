# Foundation Artefacts — Safety Knowledge Graph Platform
**Status: APPROVED — Design Baseline v1.1 (2026-08-04). Frozen — any change requires an Architecture Change Request ([implementation-blueprint/02-development-standards.md](../implementation-blueprint/02-development-standards.md) §7). Amended from v1.0 by [ACR-002](../../.acr/ACR-002-emergency-planning-domain.md) (Emergency Planning) and [ACR-003](../../.acr/ACR-003-competency-management-domain.md) (Competency Management) — see [implementation-blueprint/14-architecture-change-requests.md](../implementation-blueprint/14-architecture-change-requests.md).**
**Parent:** [../PLATFORM_ARCHITECTURE_V2.md](../PLATFORM_ARCHITECTURE_V2.md)

| # | Document | Covers |
|---|---|---|
| 1 | [Enterprise Knowledge Graph Specification](01-enterprise-knowledge-graph-specification.md) | Purpose, two-layer (ontology + instance) model, system-of-record/graph sync, query pattern catalogue, governance |
| 2 | [Neo4j Node and Relationship Model](02-neo4j-node-relationship-model.md) | Every node label + properties, every relationship type, Cypher constraints/indexes, worked example |
| 3 | [PostgreSQL Schema](03-postgresql-schema.sql) | Full DDL — ontology, safety, regulatory, provenance schemas |
| 4 | [AI Extraction Specification](04-ai-extraction-specification.md) | Pipeline stages, extraction JSON schema, prompt construction, confidence routing, incident pipeline, security |
| 5 | [Knowledge Provenance Model](05-knowledge-provenance-model.md) | Source tracing, confidence propagation, immutable history, corrections |
| 6 | [Relationship Rules Catalogue](06-relationship-rules-catalogue.md) | Domain/range/cardinality/semantics/business rules per edge type, cross-chain integrity rules |
| 7 | [Inference Rules Catalogue](07-inference-rules-catalogue.md) | R1–R18: risk rating, FARSI multiplier, overdue/drift/gap detection, SFAIRP-aware serious-risk checks, ADH boundary completeness, monitoring trend, demonstration staleness |
| 8 | [Critical Control Assurance Model](08-critical-control-assurance-model.md) | 3-gate classification test, EIA test (Guide Table 2), FARSI scoring, three lines of defence (Schedule 18C(7)/(8)), control health state machine, TARPs |
| 9 | [Regulatory Knowledge Model](09-regulatory-knowledge-model.md) | Confirmed WHS Regulation/Schedule 18C citation map, ADI/serious-risk determination, SMS-section mapping |
| 10 | [OpenAPI 3.1 Specification](10-openapi.yaml) | Full REST contract — 56 paths, 64 schemas, validated (all `$ref`s resolve) |
| 11 | [Safety Case Demonstration Model](11-safety-case-demonstration-model.md) | SMS ≠ Safety Case layering, device boundary, ADH→ADI pathway, Safety Assessment, Claim→Argument→Evidence, Monitoring, Demonstration Engine, Management of Change |

## Reading order

For a first read: **1 → 2 → 3** (the graph/schema foundation), then **11** (the Safety Case philosophy correction — read this before 6–9, it changes how to read them), then **6 → 7** (the rules that make the graph trustworthy), then **8 → 9** (the two domain models that matter most for a regulator-facing Safety Case), then **4 → 5** (how AI-extracted facts enter the system with provenance), then **10** (the resulting API contract).

## Revision history

- **2026-08-04, Design Baseline v1.1:** Architecture Review Board approved [ACR-002](../../.acr/ACR-002-emergency-planning-domain.md) (Emergency Planning) and [ACR-003](../../.acr/ACR-003-competency-management-domain.md) (Competency Management, superseding rejected [ACR-001](../../.acr/ACR-001-training-domain.md) — Training), after reading the Guide's §10.8 and §12 in full. Added: `safety.emergency_plans`, `emergency_exercises`, `emergency_plan_credible_events`, `emergency_service_consultations`, `safety.competencies`, `roles`, `role_competency_requirements`, `competency_evidence` (doc 3); corresponding Neo4j labels/relationships (doc 2 §3.6/§4/§5); relationship rules §5b (doc 6); inference rules R19–R22 (doc 7); `Competency` OpenAPI tag + emergency-plan/competency paths, v0.2.0-draft (doc 10); 3 new ontology schemes (doc 1 §6a). Full record: [implementation-blueprint/14-architecture-change-requests.md](../implementation-blueprint/14-architecture-change-requests.md).
- **2026-08-03, second pass:** added doc 11 (Safety Case Demonstration Model) after review against the WHSQ *Guide for major amusement parks: Preparing a safety case* (2021) — read in full text directly (§7–11), not secondhand. This corrected several things a first pass got wrong by relying on V1 alone: **FARSI's fifth letter is Interdependency, not Interaction** (V1's calculator has the typo); the Guide's own Effective/Independent/Auditable control test (Table 2, LOPA-derived) is distinct from V1's 3-gate Control/Support/Verification test and needed its own fields, not a merge; **SFAIRP**, not SFARP, is the correct term for anything Chapter 9A/ADI-facing; Management of Change is a fully specified requirement (§10.5, §10.12), not a gap. See [11 §0](11-safety-case-demonstration-model.md#0-sourcing-status) for exactly what was and wasn't verified this pass.

## Open items carried forward from this document set

- **ISO 45001, AS/NZS 3533, ISO 17842 clause text** — not sourced locally; the Chapter 9A safety case itself is assessed against **Schedule 18C**, not ISO 45001 ([09](09-regulatory-knowledge-model.md) §7) — an ISO 45001 mapping remains useful for separate internal conformance tracking only, and stays `TO_BE_CONFIRMED` until that source is obtained.
- **Copyright constraint** on AS/NZS/ISO standards once sourced — paraphrase + clause reference, not verbatim reproduction. The WHSQ Guide itself is CC BY 4.0 and safe to quote directly, which is why doc 9 and doc 11 now cite it verbatim in places.
- **Two Schedule 18C sub-item numbers unconfirmed** (change management, contractor management/incident management — §10.6–10.7 not yet read; training and asset integrity, §10.8–10.9, are now confirmed as of 2026-08-04) — [09](09-regulatory-knowledge-model.md) §5.
- **Guide for Developing Major Amusement Parks Safety Case Outline** and the **ICMM Critical Control Management Practical Guide** — both provided this session, neither read yet. The main Guide (§7.2) says the safety case must follow the Outline document specifically — recommend reading it before this document set is finalized.
- **Investigation methodology** (`investigations.method`) — not specified by any source read so far; left `TO BE CONFIRMED`.
- **VRTP audit cycle policy** — third-line-of-assurance minimum frequency ([08](08-critical-control-assurance-model.md) §5) needs confirming against actual VRTP policy; the Guide requires the safety case to state a frequency but doesn't prescribe one.
- **AuthN/AuthZ provider** — **confirmed: Microsoft Entra ID** ([implementation-blueprint/README.md](../implementation-blueprint/README.md) Phase 2.1 key resolutions) — this line was stale, corrected 2026-08-04.
- **SFARP gate (R4)** — flagged as weak (regex-only in V1); recommend a required-fields redesign before this is the sole gate in a regulator-facing system. Applies to the general (non-ADI) `Risk.sfarp_justification` path — the ADI-specific path now also has R13 (serious risk justification completeness).

No implementation work (application code, infrastructure provisioning, or database deployment) proceeds against this document set until you approve it.
