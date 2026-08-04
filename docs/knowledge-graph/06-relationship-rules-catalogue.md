# Relationship Rules Catalogue
**Status: DRAFT — controlled design document. Requires approval before implementation.**
**Parent:** [01-enterprise-knowledge-graph-specification.md](01-enterprise-knowledge-graph-specification.md)
**Machine-enforced counterpart:** [03-postgresql-schema.sql](03-postgresql-schema.sql) `ontology.relationship_types` — every row in that table corresponds to one entry below. A relationship type must have an approved entry here **before** it is used anywhere in code (EKG spec §6).

---

## 1. Purpose

[02-neo4j-node-relationship-model.md](02-neo4j-node-relationship-model.md) §4 lists relationship types and cardinality. This document is the expansion: what each edge *means*, what makes an instance of it valid or invalid, and what enforces that — because cardinality alone doesn't stop nonsense like a `Control` claiming to mitigate a `Risk` it was never actually linked to through a `Hazard`. V1 has zero relationship integrity today (every cross-reference is a free-text string match); this catalogue is what a real foreign-keyed, graph-backed system needs instead.

## 2. Enforcement Levels

| Level | Where | Example |
|---|---|---|
| **Structural** | Postgres FK / Neo4j relationship existence | A `Control` row cannot reference a nonexistent `Risk` — the FK simply rejects it |
| **Cardinality** | Postgres unique constraint / join-table PK, Neo4j app-layer check | `CLASSIFIED_AS_CRITICAL` is 1:1 — `critical_controls.control_id` is itself the PK |
| **Semantic (chain consistency)** | Application service layer, validated at write time | A `SafetyCaseClaim`'s cited `Evidence` must trace back through the assurance chain to the same `Hazard`/`CriticalControl` the claim is about — not enforceable as a simple FK, requires a traversal check |

## 3. Catalogue — Instance Graph

| Relationship | Domain → Range | Cardinality | Semantics | Business rule |
|---|---|---|---|---|
| `HAS_HAZARD` | Asset → Hazard | 1:N | This asset has this hazard identified against it | `hazards.asset_id` nullable only for enterprise-wide hazards not yet asset-scoped (Major Hazard Register authoring stage); once scoped, immutable — re-scoping to a different asset is a new `Hazard`, not an edit, to preserve history |
| `GIVES_RISE_TO` | Hazard → Risk | 1:N | This hazard, under exposure, produces this risk | A `Risk` must always have exactly one `Hazard` (`risks.hazard_id NOT NULL`) — "risk with no hazard" is the exact conflation the briefing doc warns against (architecture §1.4 finding 6) and is structurally impossible here |
| `RESULTS_IN` | Risk → Consequence | 1:N | Possible outcomes if this risk materializes | At least one `Consequence` required before a `Risk` can leave `draft`/`Open` status with an assigned rating — enforced at the service layer, not the DB (a risk can exist mid-authoring with none yet) |
| `MITIGATED_BY` | Risk → Control | N:N | This control reduces this risk | A `Control` must be reachable from at least one `Risk` via this edge before it can be marked `critical` — a control floating with no risk it mitigates cannot be a *critical* control by definition (briefing doc §3.7: "decisive relationship with the unwanted event") |
| `CLASSIFIED_AS_CRITICAL` | Control → CriticalControl | 1:1 | This control passed the Critical Control Test ([08](08-critical-control-assurance-model.md) §3) | Only permitted when `controls.classification = 'Control'` (all 3 gates passed) — a `Support` or `Verification`-classified item can never carry this edge, matching V1's `bowtie-ccm-generator.html` logic exactly |
| `HAS_FAILURE_MODE` | Control → FailureMode | 1:N | Ways this control can fail to perform | Optional but strongly recommended for every `CriticalControl` — absence is a Gap Analysis finding ([07-inference-rules-catalogue.md](07-inference-rules-catalogue.md) R8), not a hard block |
| `GOVERNED_BY` | CriticalControl → PerformanceStandard | 1:N | The measurable requirement this critical control must meet | Every `CriticalControl` must have ≥1 — structurally required (briefing doc §3.10, a critical control without a performance standard is not verifiable, i.e. not actually critical-control-managed) |
| `VERIFIED_BY` | PerformanceStandard → VerificationActivity | 1:N | Scheduled/completed checks against this standard | `verification_activities.due_date` drives [07](07-inference-rules-catalogue.md) R3 (overdue detection) |
| `PRODUCES` | VerificationActivity → Evidence | 1:N | The record left behind by performing this verification | An `Evidence` row's `verification_activity_id` is nullable (evidence can be uploaded standalone) but a `VerificationActivity` marked `last_completed` with zero linked `Evidence` is a Gap Analysis finding ([07](07-inference-rules-catalogue.md) R6 — "superficial verification", briefing doc §11.3 "green-washing") |
| `SUPPORTS` | Evidence → SafetyCaseClaim | N:N | This evidence backs this claim | **Chain consistency rule:** every `Evidence` cited must be reachable from the claim's `hazard_id`/`critical_control_id` via `PRODUCES`⁻¹→`VERIFIED_BY`⁻¹→`GOVERNED_BY`⁻¹ — evidence for an unrelated control cannot be cited as support (application-layer check at claim save time, not a DB constraint) |
| `TRACES_TO` | SafetyCaseClaim → Requirement | N:N | This claim addresses this regulatory/standards obligation | See [09-regulatory-knowledge-model.md](09-regulatory-knowledge-model.md) — a claim citing a `Requirement` with `status = 'TO_BE_CONFIRMED'` is flagged, not blocked (the claim can be drafted, but cannot reach `assurance_status = 'approved'` while it cites an unconfirmed requirement) |
| `REVEALS` | Incident → Hazard | N:N | This incident showed this hazard was present/inadequately controlled | Many-to-many deliberately — one incident can reveal multiple hazards, one hazard can be revealed by multiple incidents over time |
| `INVESTIGATED_AS` | Incident → Investigation | 1:1 | `investigations.incident_id UNIQUE` enforces this structurally |
| `TRIGGERS` | Incident \| AuditFinding → Action | 1:N | This event required a corrective action | `actions.source_type_concept_id` + `source_id` must agree with which edge was used — an `Action` triggered by an `AuditFinding` cannot also claim `source_type = 'Incident'` |
| `REMEDIATES` | Action → Control | N:N | This action fixes/improves this control | Optional — not every action remediates a specific control (some are procedural/training actions with no single control target); when present, feeds [07](07-inference-rules-catalogue.md) R5 (control drift tracking) |
| `FOUND_DURING` | AuditFinding → Audit | N:1 | `audit_findings.audit_id NOT NULL` — a finding cannot exist without its parent audit |
| `EXTRACTED_FROM` | any instance node → Document | N:1 | Provenance shortcut mirrored from `provenance.records.document_id` for direct graph traversal (avoids a join through the provenance table for the common "show me the source doc" query) |
| `OWNS` / `ASSIGNED_TO` / `PERFORMED_BY` | Person → {Control \| CriticalControl \| Action \| VerificationActivity} | 1:N | Named accountability | A `CriticalControl` with no `OWNS` edge is a Gap Analysis finding (briefing doc §3.5, §11.4 "ownership without authority") |
| `LOCATED_AT` | Asset → Park | N:1 | | |
| `GOVERNS` | TriggerActionResponsePlan → CriticalControl | N:1 | This TARP applies to this critical control | Every `TriggerActionResponsePlan` requires exactly one `CriticalControl`; a `CriticalControl` may have several TARPs, one per distinct trigger condition ([08](08-critical-control-assurance-model.md) §5) |

## 4. Catalogue — Ontology Graph

| Relationship | Domain → Range | Cardinality | Semantics | Business rule |
|---|---|---|---|---|
| `IN_SCHEME` | Concept → OntologyScheme | N:1 | This concept belongs to this taxonomy | Structural, required on every `Concept` |
| `BROADER` | Concept → Concept | N:1 (tree, per scheme) | Parent concept | **Must be acyclic** — a concept cannot be its own ancestor. Enforced at write time by a path check before insert, since Postgres cannot express "no cycles" as a plain FK constraint |
| `RELATED_TO` | Concept → Concept | N:N | Cross-scheme association (e.g. a Control concept related to a Regulatory concept) | `relation_type` (broader/narrower/related/equivalent) must not duplicate what `BROADER` already expresses within the same scheme — `RELATED_TO` is for *cross-scheme* links only, `BROADER` is the intra-scheme hierarchy |
| `HAS_ALIAS` | Concept → Alias | 1:N | Synonyms/abbreviations for this concept | An `Alias.text` must be unique **within its scheme** — the same string can be an alias for different concepts in different schemes, but not two concepts in the same scheme (that would make extraction matching ambiguous) |
| `TARGETS` | ExtractionRule → Concept | N:1 | Which concept this extraction rule governs | — |

## 5. Cross-Chain Integrity Rules (beyond single-edge rules)

These span multiple relationship types and are the ones that actually deliver on "no gaps in the traceability chain" — each is implemented as a service-layer validation, and each corresponds directly to a Gap Analysis Service check ([07-inference-rules-catalogue.md](07-inference-rules-catalogue.md)):

1. **No orphan critical controls.** Every `CriticalControl` must be reachable from a `Risk` (via `MITIGATED_BY` → `CLASSIFIED_AS_CRITICAL`) — a critical control with no risk behind it cannot exist post-authoring.
2. **No unverifiable critical controls.** Every `CriticalControl` must have ≥1 `PerformanceStandard` with ≥1 `VerificationActivity` — required by §3 `GOVERNED_BY`/`VERIFIED_BY` rules above, restated here because it's the rule Gap Analysis actually queries for.
3. **No dangling Safety Case claims.** Every `SafetyCaseClaim` with `assurance_status = 'approved'` must have ≥1 `Evidence` (via `SUPPORTS`) and ≥1 `Requirement` (via `TRACES_TO`) satisfying the chain-consistency rule in §3.
4. **No self-contradicting classification.** A `Control` cannot carry `classification = 'Support'` or `'Verification'` and also carry a `CLASSIFIED_AS_CRITICAL` edge (see §3 row for that edge) — checked together because they're set at different times in the authoring workflow ([08-critical-control-assurance-model.md](08-critical-control-assurance-model.md)).

## 5a. Catalogue — Safety Case Demonstration ([11-safety-case-demonstration-model.md](11-safety-case-demonstration-model.md))

| Relationship | Domain → Range | Cardinality | Semantics | Business rule |
|---|---|---|---|---|
| `HAS_BOUNDARY` | Asset → DeviceBoundary | 1:1 | Defines the scope of an amusement device for Chapter 9A purposes | Only valid where `Asset.is_amusement_device = true`; a device without one is a gap finding once `is_adh` hazards exist against it |
| `HAS_INTERFACE` | DeviceBoundary → Interface | 1:N | A boundary consideration (pathway, entry/exit, fencing, utility, etc.) | — |
| `LOSS_OF_CONTROL` | Hazard → CredibleEvent | 1:N | The mechanism by which an ADH's control is lost, producing a scenario | Only valid where `Hazard.is_adh = true`; a non-ADH hazard keeps the direct `GIVES_RISE_TO` edge to `Risk` instead |
| `ASSESSES` | SafetyAssessment → DeviceBoundary | N:1 | This assessment's scope | — |
| `COVERS` | SafetyAssessment → Hazard | N:N | Hazards this assessment analyzes | Every `Hazard` with `is_adh = true` should be `COVERS`-linked from at least one `SafetyAssessment` — absence is a gap ([07](07-inference-rules-catalogue.md) R14) |
| `SUPPORTED_BY` | SafetyCaseClaim → SafetyArgument | 1:N | The reasoning chain(s) backing this claim | A `SafetyCaseClaim` with `assurance_status = 'approved'` must have ≥1 `SafetyArgument` — an evidence link alone (direct `SUPPORTS`, §3) is not sufficient for approval, only for draft |
| `GROUNDED_IN` | SafetyArgument → Evidence | N:N | The specific evidence this reasoning step relies on | Must be a subset of the evidence reachable from the claim's `SUPPORTS` chain (§3 chain-consistency rule) — an argument cannot cite evidence unrelated to its claim |
| `SUMMARIZES` | MonitoringSummary → VerificationActivity | N:N | Aggregates verification results over a period | `period_start`/`period_end` must not overlap another `MonitoringSummary` for the same `CriticalControl` |
| `DEMONSTRATES` | Demonstration → {SafetyAssessment\|Hazard\|CriticalControl\|Asset} | N:1 | What this generated narrative is about | Every `Demonstration.source_fact_refs` entry must correspond to a real graph node/edge reachable from the scope entity — a citation to a fact outside the scope traversal is a generation defect, not a valid demonstration |
| `PROPOSES_CHANGE_TO` | ManagementOfChange → {Asset\|Control\|SafetyAssessment} | N:1 | What this change affects | — |
| `TRIGGERS_REVIEW_OF` | ReviewTrigger → {SafetyAssessment\|SafetyCaseClaim} | N:1 | What must be re-reviewed | `requires_update_of` must be non-empty — a trigger that updates nothing isn't a trigger |

## 5b. Catalogue — Emergency Planning & Competency Management (Design Baseline v1.1 amendment — [implementation-blueprint/14-architecture-change-requests.md](../implementation-blueprint/14-architecture-change-requests.md), approved 2026-08-04)

| Relationship | Domain → Range | Cardinality | Semantics | Business rule |
|---|---|---|---|---|
| `HAS_EMERGENCY_PLAN` | Park → EmergencyPlan | 1:1 | The one amusement device emergency plan for this MAP | `emergency_plans.park_id UNIQUE` enforces this structurally, mirroring Guide §12.4's "a MAP is regarded as having one amusement device emergency plan" — not one per asset or per ADI |
| `ADDRESSED_BY` | CredibleEvent → EmergencyPlan | N:1 | This ADI's response is covered by (combined into) the park's plan | Every `CredibleEvent` where `is_adi = true` should be `ADDRESSED_BY`-linked to the park's `EmergencyPlan` — absence is a gap finding, mirroring the §5a `COVERS` rule pattern for `SafetyAssessment`/`Hazard` |
| `TESTED_BY` | EmergencyPlan → EmergencyExercise | 1:N | Exercises conducted or planned against this plan | At least one `EmergencyExercise` with `status = 'conducted'` and `exercise_type != 'evacuation_exercise'` required before an `EmergencyPlan` can leave `draft` status — Guide §12.3: "you must, prior to applying for a licence, have tested your emergency plan... more than an evacuation exercise" |
| `EXERCISES` | EmergencyExercise → CredibleEvent | N:1, nullable | The specific ADI this exercise tested | Nullable only for `desktop_exercise` and `corporate_response_exercise` types, where the Guide allows covering a scenario class rather than one specific ADI (§12.1, §12.3) — every `drill`/`scenario_test`/`evacuation_exercise` must specify one |
| `CONSULTED` | EmergencyPlan → EmergencyServiceConsultation | 1:N | Emergency service organisations consulted in preparing this plan | An `EmergencyPlan` cannot move to `status = 'current'` (i.e. be finalised) without ≥1 `EmergencyServiceConsultation` recorded — Guide §12.3: consultation with emergency services is mandatory before licence application, and the finalised plan must be sent to them (`plan_sent_at`, s.608N(4)) |
| `REQUIRES_COMPETENCY` | Role → Concept (Competency category) | N:N | The competency types this role must hold | Feeds the currency-lapse inference rule ([07-inference-rules-catalogue.md](07-inference-rules-catalogue.md)) — a `Person` assigned a `Role` without a matching current `Competency` is a gap finding, the direct structural equivalent of §5a's `COVERS` gap check |
| `HOLDS_COMPETENCY` | Person → Competency | 1:N | This person's competency claims | — |
| `DEMONSTRATES_COMPETENCY` | Competency → Role \| CriticalControl | N:1 | What this competency claim qualifies the person for | A `Competency` linked to a `CriticalControl` feeds the critical-control operator-assurance check — an operator without a current, linked `Competency` on a `CriticalControl` they are `ASSIGNED_TO` is a gap finding, not merely a training-records gap |
| `ASSESSED_BY` | Competency → Person | N:1 | The trainer/assessor who validated this competency | Self-referential via `Person` — Guide §10.8: "management of the trainer's competency and validation of their assessment processes" means an assessor's *own* competency is tracked the same way, not a separate concept |
| `GROUNDED_IN` | Competency → Evidence | N:N | The specific evidence (training record, licence, assessment result, etc.) this competency claim relies on | Same relationship type and same chain-consistency discipline as §5a's `SafetyArgument → Evidence` row — reused deliberately, not duplicated as a new type, per EKG spec §6 governance |

**No `Training` relationship set.** Training is a `competency_type` classification value reached via the existing `CLASSIFIED_AS` edge (§3) on `Competency` — ACR-001 (standalone Training domain) was rejected by the Architecture Review Board specifically to avoid inventing a parallel relationship set here. **No `EmergencyScenario` relationship set** — `ADDRESSED_BY` above operates directly on the existing `CredibleEvent` label (§3.4 of [02-neo4j-node-relationship-model.md](02-neo4j-node-relationship-model.md)), not a new node type.

## 6. Change Control

Adding a new relationship type requires: (1) a new approved row in `ontology.relationship_types`, (2) a new entry in this catalogue with domain/range/cardinality/semantics/business rule, (3) the corresponding Neo4j constraint if one applies. No relationship type is used in application code, extraction output, or manual data entry ahead of these three existing — this is the same governance gate the Enterprise Knowledge Graph Specification (§6) applies to ontology concepts, applied to edges.
