# Neo4j Node and Relationship Model
**Status: DRAFT — controlled design document. Requires approval before implementation.**
**Parent:** [01-enterprise-knowledge-graph-specification.md](01-enterprise-knowledge-graph-specification.md)
**Companion:** [03-postgresql-schema.sql](03-postgresql-schema.sql) (system of record — every node below carries `pg_id` mapping back to its Postgres row), [06-relationship-rules-catalogue.md](06-relationship-rules-catalogue.md) (business rules per edge type)

---

## 1. Conventions

- Every instance-graph node has: `pg_id` (uuid, matches Postgres PK, unique constraint), `created_at`, `updated_at` (synced from Postgres), and a `provenance_id` linking to a `ProvenanceRecord` ([05-knowledge-provenance-model.md](05-knowledge-provenance-model.md)) — omitted from the property tables below for brevity, assume present on every node.
- Node labels: `PascalCase`, singular. Relationship types: `SCREAMING_SNAKE_CASE`, verb phrase, always defined in the ontology's `RelationshipTypeRegistry` before use (§1 EKG spec §6).
- Classification-style properties (`category`, `hierarchy`, `type`, `domain`) are **never string properties** on instance nodes — they are always `CLASSIFIED_AS` edges to a `Concept` node. Where a table below lists e.g. `category → Concept`, that denotes an edge, not a property.
- Soft-delete only: a `status` property of `retired`/`superseded` plus `superseded_by` edge, never a hard `DELETE` on published data.

## 2. Ontology-Graph Node Labels

| Label | Key properties | Notes |
|---|---|---|
| `OntologyScheme` | `id` (PK), `name`, `description`, `version` | One per taxonomy (§3.2 of parent architecture doc) |
| `Concept` | `id` (PK), `pref_label`, `definition`, `status` (`draft`\|`reviewed`\|`approved`\|`published`\|`deprecated`), `source_ref`, `effective_from`, `effective_to` | |
| `Alias` | `id` (PK), `text`, `alias_type` (`synonym`\|`abbreviation`\|`deprecated_term`) | e.g. "LOTO" |
| `RelationshipTypeEntry` | `id` (PK), `name` (matches an actual Neo4j relationship type string), `domain_scheme`, `range_scheme`, `description`, `cardinality` | Meta-node describing an allowed edge type — see [06](06-relationship-rules-catalogue.md) |
| `ExtractionRule` | `id` (PK), `pattern_type` (`regex`\|`embedding-similarity`\|`llm-prompt-instruction`), `confidence_threshold` (float), `action` (`auto-accept`\|`flag-for-review`\|`reject`), `example_positive`, `example_negative` | See [04-ai-extraction-specification.md](04-ai-extraction-specification.md) |

Ontology relationships: `(Concept)-[:IN_SCHEME]->(OntologyScheme)`, `(Concept)-[:BROADER]->(Concept)` (self-referential tree), `(Concept)-[:RELATED_TO {relation_type}]->(Concept)` (cross-scheme, e.g. Control concept related to Regulatory concept), `(Concept)-[:HAS_ALIAS]->(Alias)`, `(ExtractionRule)-[:TARGETS]->(Concept)`.

## 3. Instance-Graph Node Labels

### 3.1 Core hazard/risk/control chain

| Label | Key properties | Classification edges |
|---|---|---|
| `Asset` | `id`, `name`, `status` | `type → Concept` (Asset taxonomy), `LOCATED_AT → Park` |
| `Park` | `id`, `name` | (VRTP property — Movie World, Wet'n'Wild GC, etc.) |
| `Hazard` | `id`, `name`, `description`, `exposure_pathway`, `possible_consequence`, `date_identified` | `category → Concept` (Hazard taxonomy), `energy_source → Concept` (Energy Source taxonomy) |
| `Risk` | `id`, `description`, `cause`, `inherent_likelihood` (1-5), `inherent_consequence` (1-5), `inherent_rating`, `current_likelihood`, `current_consequence`, `current_rating`, `target_likelihood`, `target_consequence`, `sfarp_justification`, `status`, `review_date` | |
| `Consequence` | `id`, `description`, `severity`, `flag_608b` (bool) | `domain → Concept` (Consequence taxonomy) |
| `Control` | `id`, `description`, `type` (`Prevention`\|`Mitigation`), `classification` (`Control`\|`Support`\|`Verification`), `gate_1`, `gate_2`, `gate_3` (bool), `effectiveness_rating` | `hierarchy → Concept` (Control taxonomy) |
| `CriticalControl` | `id`, `farsi_functionality`, `farsi_availability`, `farsi_reliability`, `farsi_survivability`, `farsi_interdependency` (each 1-5 — corrected from "interaction", confirmed against the WHSQ Guide, [08-critical-control-assurance-model.md](08-critical-control-assurance-model.md) §4b), `farsi_score` (derived avg), `eia_effective`, `eia_independent`, `eia_auditable` (bool — [08](08-critical-control-assurance-model.md) §4a) | 1:1 with a `Control` where `critical = true` |
| `FailureMode` | `id`, `description` | `mode → Concept` (Failure Mode taxonomy) |

### 3.2 Assurance chain

| Label | Key properties |
|---|---|
| `PerformanceStandard` | `id`, `requirement_text`, `measurable_criteria` |
| `VerificationActivity` | `id`, `frequency`, `due_date`, `last_completed`, `performed_by` (→ `Person`), `result` | `method → Concept` (Verification taxonomy) |
| `Evidence` | `id`, `uploaded_by` (→ `Person`), `uploaded_at`, `linked_entity_type`, `linked_entity_id` | `type → Concept` (Evidence taxonomy) |
| `SafetyCaseClaim` | `id`, `claim_text`, `assurance_status` | |
| `TriggerActionResponsePlan` | `id`, `trigger_condition`, `trigger_source_rule`, `required_action`, `escalation_level`, `status` | Net-new (briefing doc §5.7, no V1 equivalent) — see [08-critical-control-assurance-model.md](08-critical-control-assurance-model.md) §5 |

### 3.3 Incident / action chain

| Label | Key properties |
|---|---|
| `Incident` | `id`, `datetime`, `severity`, `vrtp_severity`, `location`, `description`, `immediate_cause`, `root_cause`, `whsq_notified`, `osr_notified`, `is_notifiable_incident` (bool, ACR-005), `investigation_status` | `type → Concept` |
| `Investigation` | `id`, `method`, `findings`, `contributing_factors` | *`method` — TO BE CONFIRMED: which methodology (ICAM or other) VRTP mandates* |
| `Action` | `id`, `description`, `priority`, `assigned_to` (→ `Person`), `due_date`, `status`, `effectiveness_review` | `source_type → Concept`, `root_cause_category → Concept` |
| `AuditFinding` | `id`, `severity`, `description` | |

### 3.4 Safety Case Demonstration (added — [11-safety-case-demonstration-model.md](11-safety-case-demonstration-model.md))

| Label | Key properties | Classification edges |
|---|---|---|
| `DeviceBoundary` | `id`, `boundary_description`, `includes_description`, `excludes_description` | One per `Asset` where `is_amusement_device = true` |
| `Interface` | `id`, `interface_type`, `description` | `interface_type → Concept` (Interface taxonomy — operationalized from Guide §7.4, not verbatim regulatory text) |
| `CredibleEvent` | `id`, `description`, `loss_of_control_description`, `is_adi` (bool) | Sits between `Hazard` (where `is_adh = true`) and `Risk` |
| `SafetyAssessment` | `id`, `scope_description`, `serious_risk_threshold_note`, `unmitigated_risk_method`, `status` | Owns/scopes a `DeviceBoundary`'s hazards, credible events, critical controls |
| `SafetyArgument` | `id`, `argument_text`, `sequence` | GSN Strategy-equivalent, connects `SafetyCaseClaim` to `Evidence` with stated reasoning |
| `MonitoringSummary` | `id`, `period_start`, `period_end`, `verification_count`, `pass_count`, `trend`, `indicator_class` (`leading`\|`lagging`) | Time-series rollup of `VerificationActivity` for one `CriticalControl` |
| `Demonstration` | `id`, `demonstration_type`, `generated_narrative`, `source_fact_refs`, `status` | Generated presentation, never the source of truth — see [11](11-safety-case-demonstration-model.md) §7.4 |
| `ManagementOfChange` | `id`, `change_description`, `change_type` (`minor`\|`major`), `risk_reassessment_required`, `status` | `change_category → Concept` |
| `ReviewTrigger` | `id`, `trigger_type`, `description`, `requires_update_of` (array), `status` | |

### 3.5 Regulatory & organizational

| Label | Key properties |
|---|---|
| `Requirement` | `id`, `clause_ref`, `text`, `applies_to_entity_type` | `source → Concept` (Regulatory ontology) — see [09-regulatory-knowledge-model.md](09-regulatory-knowledge-model.md) |
| `Person` | `id`, `name`, `role_title`, `email` | Represents a named accountable owner (control owner, risk owner, action assignee) — V1 stored these as free-text strings; modeled as nodes here because officer/owner accountability (WHS s 27 due diligence, briefing doc §3.5 "control ownership") is itself a query VRTP needs to run ("every critical control owned by X"), which free text cannot support |
| `Document` | `id`, `filename`, `mime_type`, `uploaded_at`, `extraction_status`, `source_hash` | Blob storage pointer + extraction status; the document *content* lives in Blob Storage, not Neo4j |

### 3.6 Emergency Planning & Competency Management (Design Baseline v1.1 amendment — [implementation-blueprint/14-architecture-change-requests.md](../implementation-blueprint/14-architecture-change-requests.md), approved 2026-08-04)

| Label | Key properties | Classification edges |
|---|---|---|
| `EmergencyPlan` | `id`, `title`, `summary`, `max_persons_normal_day`, `max_persons_peak_season`, `warning_system_description`, `corporate_response_plan_description`, `status`, `effective_date`, `sent_to_regulator_at` | One per `Park` (Guide §12.4 — "a MAP is regarded as having one amusement device emergency plan") |
| `EmergencyExercise` | `id`, `exercise_type` (`drill`\|`scenario_test`\|`desktop_exercise`\|`evacuation_exercise`\|`corporate_response_exercise`), `planned_date`, `conducted_date`, `status`, `learnings`, `learnings_implemented` (bool) | |
| `EmergencyServiceConsultation` | `id`, `consultation_date`, `recommendation_text`, `incorporation_description`, `plan_sent_at` | `organisation → Concept` (Emergency Service Organisation taxonomy — QFES/QPS/QAS/other) |
| `Role` | `id`, `name`, `role_category` (`operator`\|`technical_services`\|`supervisor`\|`management`\|`officer`\|`contractor`\|`security`) | Guide §10.8 skills-matrix categories |
| `Competency` | `id`, `description`, `assessment_date`, `currency_expiry_date`, `status` (`current`\|`lapsed`\|`pending_assessment`\|`revoked`) | `competency_type → Concept` (Competency category taxonomy: training/qualification/licence/oem_certification/authorisation/information_briefing) — the claim ("Person X is competent for Role/Control Y"), distinct from the `Evidence` supporting it |

No standalone `Training` node — training is one `competency_type` classification value on `Competency`, per ACR-003 superseding ACR-001. No standalone `EmergencyScenario` node — an emergency scenario reuses `CredibleEvent` (§3.4) via the `ADDRESSED_BY` edge below, per ACR-002's reuse-over-invent recommendation. Emergency equipment reuses `Asset` (an `is_emergency_equipment`-style specialization, mirroring how `DeviceBoundary` already specializes `Asset` rather than introducing a parallel entity).

## 4. Relationship Types (summary — full business rules in [06-relationship-rules-catalogue.md](06-relationship-rules-catalogue.md))

| Relationship | From → To | Cardinality |
|---|---|---|
| `HAS_HAZARD` | `Asset → Hazard` | 1:N |
| `GIVES_RISE_TO` | `Hazard → Risk` | 1:N |
| `RESULTS_IN` | `Risk → Consequence` | 1:N |
| `MITIGATED_BY` | `Risk → Control` | N:N |
| `CLASSIFIED_AS_CRITICAL` | `Control → CriticalControl` | 1:1 |
| `HAS_FAILURE_MODE` | `Control → FailureMode` | 1:N |
| `GOVERNED_BY` | `CriticalControl → PerformanceStandard` | 1:N |
| `VERIFIED_BY` | `PerformanceStandard → VerificationActivity` | 1:N |
| `PRODUCES` | `VerificationActivity → Evidence` | 1:N |
| `SUPPORTS` | `Evidence → SafetyCaseClaim` | N:N |
| `TRACES_TO` | `SafetyCaseClaim → Requirement` | N:N |
| `REVEALS` | `Incident → Hazard` | N:N |
| `INVESTIGATED_AS` | `Incident → Investigation` | 1:1 |
| `TRIGGERS` | `Incident \| AuditFinding → Action` | 1:N |
| `REMEDIATES` | `Action → Control` | N:N |
| `FOUND_DURING` | `AuditFinding → Audit` *(Audit node — see note)* | N:1 |
| `EXTRACTED_FROM` | any instance node → `Document` | N:1 |
| `OWNS` / `ASSIGNED_TO` / `PERFORMED_BY` | `Person → {Control\|CriticalControl\|Action\|VerificationActivity}` | 1:N |
| `CLASSIFIED_AS` | any instance node → `Concept` | N:1 |
| `LOCATED_AT` | `Asset → Park` | N:1 |
| `GOVERNS` | `TriggerActionResponsePlan → CriticalControl` | N:1 |
| `HAS_BOUNDARY` | `Asset → DeviceBoundary` | 1:1 |
| `HAS_INTERFACE` | `DeviceBoundary → Interface` | 1:N |
| `LOSS_OF_CONTROL` | `Hazard → CredibleEvent` | 1:N (only where `Hazard.is_adh = true`) |
| `ASSESSES` | `SafetyAssessment → DeviceBoundary` | N:1 |
| `COVERS` | `SafetyAssessment → Hazard` | N:N |
| `SUPPORTED_BY` | `SafetyCaseClaim → SafetyArgument` | 1:N |
| `GROUNDED_IN` | `SafetyArgument → Evidence` | N:N |
| `SUMMARIZES` | `MonitoringSummary → VerificationActivity` | N:N (aggregation over a period) |
| `DEMONSTRATES` | `Demonstration → {SafetyAssessment\|Hazard\|CriticalControl\|Asset}` | N:1 |
| `PROPOSES_CHANGE_TO` | `ManagementOfChange → {Asset\|Control\|SafetyAssessment}` | N:1 |
| `TRIGGERS_REVIEW_OF` | `ReviewTrigger → {SafetyAssessment\|SMS section\|SafetyCaseClaim}` | N:1 |
| `HAS_EMERGENCY_PLAN` | `Park → EmergencyPlan` | 1:1 |
| `ADDRESSED_BY` | `CredibleEvent → EmergencyPlan` | N:1 (via the response-linkage; multiple credible events may combine into one plan per Guide §12) |
| `TESTED_BY` | `EmergencyPlan → EmergencyExercise` | 1:N |
| `EXERCISES` | `EmergencyExercise → CredibleEvent` | N:1, nullable (desktop exercises may cover a scenario class rather than one specific ADI) |
| `CONSULTED` | `EmergencyPlan → EmergencyServiceConsultation` | 1:N |
| `REQUIRES_COMPETENCY` | `Role → Concept` (Competency category) | N:N |
| `HOLDS_COMPETENCY` | `Person → Competency` | 1:N |
| `DEMONSTRATES_COMPETENCY` | `Competency → Role \| CriticalControl` | N:1 |
| `ASSESSED_BY` | `Competency → Person` | N:1 (self-referential via `Person`; trainer/assessor's own competency uses the same label) |
| `GROUNDED_IN` | `Competency → Evidence` | N:N (reuses the same relationship type already defined for `SafetyArgument → Evidence`, §4 above — same "claim grounded in evidence" semantic, not a new type) |

*Note: `Audit` (the parent audit/inspection event, distinct from `AuditFinding`) is a Postgres entity carried into the graph for `FOUND_DURING` traversal — see [03-postgresql-schema.sql](03-postgresql-schema.sql) `audits` table.*

## 5. Constraints & Indexes (Cypher — illustrative DDL for the design review, not an implementation artifact)

```cypher
// Uniqueness on every node's Postgres-sourced ID
CREATE CONSTRAINT asset_pg_id IF NOT EXISTS FOR (n:Asset) REQUIRE n.pg_id IS UNIQUE;
CREATE CONSTRAINT hazard_pg_id IF NOT EXISTS FOR (n:Hazard) REQUIRE n.pg_id IS UNIQUE;
CREATE CONSTRAINT risk_pg_id IF NOT EXISTS FOR (n:Risk) REQUIRE n.pg_id IS UNIQUE;
CREATE CONSTRAINT control_pg_id IF NOT EXISTS FOR (n:Control) REQUIRE n.pg_id IS UNIQUE;
CREATE CONSTRAINT criticalcontrol_pg_id IF NOT EXISTS FOR (n:CriticalControl) REQUIRE n.pg_id IS UNIQUE;
CREATE CONSTRAINT concept_id IF NOT EXISTS FOR (n:Concept) REQUIRE n.id IS UNIQUE;
CREATE CONSTRAINT person_pg_id IF NOT EXISTS FOR (n:Person) REQUIRE n.pg_id IS UNIQUE;
// (repeat pattern for every remaining label in §3)

// v1.1 amendment — §3.6
CREATE CONSTRAINT emergencyplan_pg_id IF NOT EXISTS FOR (n:EmergencyPlan) REQUIRE n.pg_id IS UNIQUE;
CREATE CONSTRAINT competency_pg_id IF NOT EXISTS FOR (n:Competency) REQUIRE n.pg_id IS UNIQUE;
CREATE CONSTRAINT role_pg_id IF NOT EXISTS FOR (n:Role) REQUIRE n.pg_id IS UNIQUE;
CREATE INDEX competency_expiry IF NOT EXISTS FOR (n:Competency) ON (n.currency_expiry_date);

// Indexes supporting the query patterns in EKG spec §5
CREATE INDEX risk_rating IF NOT EXISTS FOR (n:Risk) ON (n.current_rating);
CREATE INDEX verification_due IF NOT EXISTS FOR (n:VerificationActivity) ON (n.due_date);
CREATE INDEX concept_scheme IF NOT EXISTS FOR (n:Concept) ON (n.pref_label);
CREATE FULLTEXT INDEX hazard_text IF NOT EXISTS FOR (n:Hazard) ON EACH [n.name, n.description];
```

## 6. Worked Example (illustrative subgraph, not seed data)

Using the pattern from V1's pilot register (chlorine dosing hazard) translated into the new model:

```cypher
CREATE (a:Asset {pg_id:'A-001', name:'Pool water treatment system'})-[:LOCATED_AT]->(:Park {name:'Wet\'n\'Wild GC'})
CREATE (h:Hazard {pg_id:'H-001', name:'Over-chlorinated pool water'})
CREATE (a)-[:HAS_HAZARD]->(h)
CREATE (h)-[:CLASSIFIED_AS]->(:Concept {pref_label:'Chemical exposure'})
CREATE (r:Risk {pg_id:'R-001', inherent_rating:'High'})
CREATE (h)-[:GIVES_RISE_TO]->(r)
CREATE (c:Control {pg_id:'C-001', description:'Automated dosage controller', classification:'Control'})
CREATE (r)-[:MITIGATED_BY]->(c)
CREATE (c)-[:CLASSIFIED_AS]->(:Concept {pref_label:'Engineering'})  // Control taxonomy — control hierarchy
CREATE (cc:CriticalControl {pg_id:'CC-001', farsi_functionality:5, farsi_availability:4, farsi_reliability:5, farsi_survivability:3, farsi_interdependency:4})
CREATE (c)-[:CLASSIFIED_AS_CRITICAL]->(cc)
CREATE (ps:PerformanceStandard {pg_id:'PS-001', requirement_text:'Free chlorine maintained 1-3ppm, continuous monitoring'})
CREATE (cc)-[:GOVERNED_BY]->(ps)
CREATE (v:VerificationActivity {pg_id:'V-001', frequency:'Daily', last_completed:date('2026-07-30')})
CREATE (ps)-[:VERIFIED_BY]->(v)
CREATE (e:Evidence {pg_id:'E-001', type:'record'})
CREATE (v)-[:PRODUCES]->(e)
```

This is the shape every real record populates through automatically once the extraction pipeline and CRUD API are implemented — shown here purely to validate the model reads naturally end-to-end.
