# ACR-002: Emergency Planning Domain

**Raised by:** Project sponsor (leeshegog@icloud.com), 2026-08-04
**Affected document(s):** [09-regulatory-knowledge-model.md](../docs/knowledge-graph/09-regulatory-knowledge-model.md) §5a (Schedule 18B), [11-safety-case-demonstration-model.md](../docs/knowledge-graph/11-safety-case-demonstration-model.md), [03-postgresql-schema.sql](../docs/knowledge-graph/03-postgresql-schema.sql), [02-neo4j-node-relationship-model.md](../docs/knowledge-graph/02-neo4j-node-relationship-model.md), [10-openapi.yaml](../docs/knowledge-graph/10-openapi.yaml), [11-implementation-risk-register.md](../docs/implementation-blueprint/11-implementation-risk-register.md) (risk D4)

## Current state

Schedule 18B (Emergency Plan) content was confirmed and read in full this project (workplace hazard/detail, command structure, notifications, resources/equipment, procedures) and recorded into [knowledge-graph/09 §5a](../docs/knowledge-graph/09-regulatory-knowledge-model.md). **No `EmergencyPlan` entity exists in Design Baseline v1.0** to hold this content — no table, no node label, no OpenAPI tag. This gap is already tracked as risk D4 in [11-implementation-risk-register.md](../docs/implementation-blueprint/11-implementation-risk-register.md) and was carried forward, unresolved, through Phase 2.1 and Phase 2.2.

## Proposed change

Assess whether Emergency Planning becomes a first-class domain entity set in Design Baseline v1.1. Given Chapter 9A and Safety Case expectations (a safety case must demonstrate emergency response capability, not merely assert a plan exists on paper — the same "practical explanation of how something works" standard already applied to the Demonstration Engine, [11-safety-case-demonstration-model.md](../docs/knowledge-graph/11-safety-case-demonstration-model.md) §7.3), this is likely to become a significant evidence domain. Assessment must resolve entity-by-entity:

1. **Emergency Plan** — the Schedule 18B-derived document/record itself.
2. **Emergency Scenario** — credible emergency events requiring a response (relationship to existing `safety.credible_events`? — a scenario may be the same concept under a different name, or a distinct type; this ACR must determine which, not assume).
3. **Drill** and **Exercise** — are these the same entity with a `type` field, or genuinely distinct (a drill exercises one procedure; an exercise may be multi-agency and cross-scenario)?
4. **Emergency Equipment** — relationship to `safety.assets` (is equipment an `Asset` subtype, or a distinct entity?).
5. **Response Capability** — the claim being made; likely the `SafetyArgument`/`Claim` structure already in place ([11-safety-case-demonstration-model.md](../docs/knowledge-graph/11-safety-case-demonstration-model.md)) rather than a new entity — assessment must confirm or reject this reuse.
6. **Performance Standard** and **Verification** links — can an emergency response capability have its own performance standards, verified via the existing `safety.performance_standards`/`safety.verification_activities` model, or does it need domain-specific fields?
7. **Evidence** links — drill/exercise records as `safety.evidence` feeding `safety.safety_argument_evidence`.
8. **Safety Assessment** links — does an emergency scenario feed `safety.credible_events`/`safety.safety_assessments` directly, or sit alongside as a parallel input?
9. **Safety Case Demonstration** links — how an Emergency Plan's content surfaces in a generated `Demonstration` ([11-safety-case-demonstration-model.md](../docs/knowledge-graph/11-safety-case-demonstration-model.md) §7).

## Impact

Touches the PostgreSQL schema, Neo4j model, OpenAPI contract, and relationship/inference catalogues if approved. Directly affects R7 (Safety Assessment + Demonstration Engine + Safety Case, [04-implementation-roadmap.md](../docs/implementation-blueprint/04-implementation-roadmap.md)) — a `Demonstration` should not be assessed as complete against the Guide's §7.3 standard while Chapter 9A emergency-response evidence has nowhere to live. Resolves risk D4.

## Outcome paths

- **Approve** → Design Baseline updated to v1.1: schema, Neo4j model, OpenAPI, relationship/inference catalogues, and documentation index regenerated in a controlled pass. Risk D4 closed.
- **Reject** → Schedule 18B content remains reference material in [knowledge-graph/09 §5a](../docs/knowledge-graph/09-regulatory-knowledge-model.md) only, cited by narrative text in a `Demonstration` without structured entity backing — accepted as a documented limitation, not a silent gap. Risk D4 remains open and re-assessed at R7.

## Approval

**Approved** — Architecture Review Board (project sponsor), 2026-08-04, scoped to `emergency_plans` + `emergency_exercises` + `emergency_plan_credible_events` + `emergency_service_consultations` + FK links (Scenario/Equipment/Response Capability reuse existing entities, not new ones). Design Baseline updated to **v1.1**. Risk D4 closed. Full review and regeneration record: [implementation-blueprint/14-architecture-change-requests.md](../docs/implementation-blueprint/14-architecture-change-requests.md) §3, §3a, §6, §8.
