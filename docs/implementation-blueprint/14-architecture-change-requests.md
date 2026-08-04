# 14 — Architecture Change Request Review Pack

**Status: CLOSED — Architecture Review Board decision recorded 2026-08-04 (§6). Baseline: Design Baseline v1.1 (Approved, 2026-08-04) + Phase 2.1 Blueprint (Approved) + Phase 2.2 Application Foundation Scaffold (Approved, 2026-08-04). R0 authorised (§10).**

**Purpose:** consolidate [ACR-001](../../.acr/ACR-001-training-domain.md), [ACR-002](../../.acr/ACR-002-emergency-planning-domain.md), and [ACR-003](../../.acr/ACR-003-competency-management-domain.md) into a single review package — impact assessment, options, and a recommendation per ACR — with a formal approval section. This document does not itself approve or implement anything; it is the audit-trail artefact between "gap identified" and "Architecture Review Board decision." R0 remains blocked until the approval section below is completed.

---

## 1. Review Methodology

Each ACR is assessed against three lenses, consistently:

1. **Regulatory requirement** — does Chapter 9A / the WHSQ Guide / an existing confirmed citation actually require this content to exist as structured data, or only as narrative evidence?
2. **Domain model consistency** — does the proposed entity duplicate something that already exists elsewhere in Design Baseline v1.0 (the exact failure mode the platform exists to fix — architecture §1.4 finding 1), or is it genuinely new?
3. **Implementation impact** — which artefacts change (schema, Neo4j model, ontology, OpenAPI, relationship catalogue, inference rules), and at what size (S/M/L/XL, same scale used in [04-implementation-roadmap.md](04-implementation-roadmap.md)).

A recommendation is given per ACR. **A recommendation is not a decision** — the Approval section (§6) is where the Architecture Review Board records the actual decision, and nothing downstream of this document treats a recommendation as authorization to implement.

**Sourcing status — updated 2026-08-04:** Guide §10.8 (Training and competency) and §12 (Emergency plans, all sub-sections 12.1–12.4) have now been read in full from the source PDF (`Guide for major amusement parks Safety Case 2021.pdf`, pages 38–50 of 53). The findings below in §3a and §4a are marked **Verification-driven** and are additive to the original design-driven recommendations in §3/§4 — nothing in the original analysis was found wrong, but two genuinely new structural requirements surfaced that the design-only pass could not have anticipated. Still unread: §10.6–10.7 (contractor management, incident management) and the companion *Guide for Developing Major Amusement Parks Safety Case Outline* and *ICMM Critical Control Management Practical Guide* — neither bears on ACR-001/002/003, so this does not block the Board decision below.

---

## 2. ACR-001 — Training Domain

**Full text:** [.acr/ACR-001-training-domain.md](../../.acr/ACR-001-training-domain.md)

| Lens | Assessment |
|---|---|
| Regulatory requirement | Not yet confirmed structurally — Guide §10.8 (training) unread (§1 caveat above). No existing confirmed citation mandates a specific data structure, only that competence/training records exist as evidence. |
| Domain model consistency | **Fails in isolation.** A standalone `Training` entity duplicates the concept ACR-003 raises (Competency) — the Safety Case claim is "competent," training is one evidence path to it. Modelling Training first risks exactly the V1 pattern this platform was built to fix: an entity invented independently that later needs a parent concept retrofitted around it. |
| Implementation impact (if approved standalone) | M — one table, one ontology scheme, one OpenAPI tag, no relationship-catalogue changes beyond new edges. |

**Recommendation: do not approve ACR-001 as an independent entity.** Fold into ACR-003 — see §4 consolidated recommendation.

---

## 3. ACR-002 — Emergency Planning Domain

**Full text:** [.acr/ACR-002-emergency-planning-domain.md](../../.acr/ACR-002-emergency-planning-domain.md)

| Lens | Assessment |
|---|---|
| Regulatory requirement | **Strong, on what's already confirmed.** Schedule 18B content (workplace hazard/detail, command structure, notifications, resources/equipment, procedures) is fully read and sitting in [knowledge-graph/09 §5a](../knowledge-graph/09-regulatory-knowledge-model.md) with nowhere to attach structurally — risk D4. Guide §12 itself is unread (§1 caveat), so the *full* regulatory shape is not yet confirmed, but the confirmed Schedule 18B content alone already justifies action. |
| Domain model consistency | **Mostly reuse, not net-new.** Per entity requested in the ACR: |

| Requested entity | Recommendation | Rationale |
|---|---|---|
| `EmergencyPlan` | **New entity.** No existing table represents a plan document/record. | Genuinely novel — nothing today models a plan-level container. |
| `EmergencyScenario` | **Reuse `safety.credible_events`** with a `scenario_type` or boolean discriminator, not a parallel table. | `safety.credible_events` already models "things that could happen requiring a response" — an emergency scenario is that concept under Chapter 9A framing, not a different concept. |
| `Drill` / `Exercise` | **Single new entity** `safety.emergency_exercises` with an `exercise_type` enum (`drill`\|`exercise`), not two tables. | The ACR's own question ("are these the same entity with a type field?") — yes, per the reuse-over-invent principle; splitting prematurely violates YAGNI. |
| `Emergency Equipment` | **Reuse `safety.assets`** via `is_amusement_device`-style specialization flag, not a parallel entity. | Directly mirrors the precedent already set for Device Boundary: "an amusement device is a specialized `Asset`, not a different kind of thing" ([11-safety-case-demonstration-model.md](../knowledge-graph/11-safety-case-demonstration-model.md) §2). Emergency equipment is the same pattern. |
| `Response Capability` | **Reuse `safety.safety_arguments`/Claim structure**, no new entity. | The ACR's own assessment question already suspected this; a "capability" is a claim supported by evidence, which is exactly what `safety_case_claims`/`safety_arguments` already model. |
| Performance Standard / Verification / Evidence links | **Reuse existing tables** (`safety.performance_standards`, `safety.verification_activities`, `safety.evidence`) via new foreign keys only. | No new entity needed — these are link-only changes. |

| Lens | Assessment |
|---|---|
| Implementation impact | M — one genuinely new table (`EmergencyPlan`) plus one new table (`emergency_exercises`), a handful of new FKs on existing tables, one new Neo4j relationship set, no new OpenAPI tag required (fits under `SafetyCase`, consistent with MOC's precedent), ontology: one new scheme for emergency scenario/exercise classification. |

**Recommendation (design-driven, pre-verification): approve**, scoped narrowly to `EmergencyPlan` + `emergency_exercises` + FK links, explicitly rejecting the wider entity list in favour of reuse. This resolves risk D4 without duplicating `credible_events`, `assets`, or `safety_arguments`.

### 3a. Verification findings — Guide §12 read in full, 2026-08-04

The design-driven modelling above is **confirmed correct in shape**; §12 does not overturn any of it. It does surface refinements and one genuinely new entity, all **Verification-driven**:

| Finding | Guide reference | Effect on ACR-002 |
|---|---|---|
| A MAP has exactly **one** amusement device emergency plan, not one per asset or per ADI ("In the WHS Regulation, a MAP is regarded as having one amusement device emergency plan," §12.4). Individual ADIs/scenarios link *into* it. | §12, §12.4 | `EmergencyPlan` cardinality is one-per-`safety.parks`, not one-per-asset. Confirms the many-to-many join was the right shape, not a per-asset FK — the ACR text's phrasing ("EmergencyPlan") already implied this; now confirmed rather than assumed. |
| Plan must show explicit **linkage from each ADI/credible event to the plan** ("you will need to include linkages from your ADIs to the corresponding amusement device emergency plans," §12) — combining plans across similar ADIs is expected and must itself be demonstrable ("it is effective to combine those plans... a table which links the emergency plans back to the ADIs"). | §12 | Confirms a join table `emergency_plan_credible_events` (many-to-many), not a single FK on `credible_events`. Reuse of `credible_events` for the scenario concept stands. |
| Exercises are more varied than a binary drill/exercise split: scenario tests, desktop exercises (for scenarios impractical to physically test), evacuation exercises, and a distinct **corporate emergency response exercise** are all separately named (§12.1, §12.3). | §12.1, §12.3 | `emergency_exercises.exercise_type` enum widened to `{drill, scenario_test, desktop_exercise, evacuation_exercise, corporate_response_exercise}` — still one table, per the original YAGNI rationale; only the enum's cardinality changes, not the schema shape. |
| **Mandatory consultation with emergency services (QFES/QPS/QAS)** before licence application, with their recommendations recorded and a documented account of how each was incorporated ("note this in your emergency plan summary... provide information on how those recommendations were incorporated," §12.3); the finalised plan must be sent to those organisations (s.608N(4)). | §12.2, §12.3 | **Genuinely new, not previously identified in the ACR's own entity list.** Recommend a new lightweight table `safety.emergency_service_consultations` (organisation, consultation date, recommendation text, incorporation description, plan-sent date), FK to `emergency_plans`. This was not anticipated by the design-only pass — it is a consultation/response-tracking pattern with no existing analogue in the schema (`safety_argument_evidence` is claim-evidence, not consultation-response). |
| Emergency equipment requirement is explicit and two-tier: general systems (e.g. extinguisher systems) and specialised/incident-specific equipment (e.g. height-rescue gear), each needing a stated maintenance owner and a design-standard basis ("principles or standards on which particular items... have been designed," §12.4). | §12.4 | Confirms the Asset-reuse recommendation, and confirms it needs an FK to `regulatory.requirements` for the standards-basis field — already anticipated generically in §3's Performance Standard/Verification/Evidence row, now specifically required for equipment. |
| Training in the emergency plan is explicitly cross-referenced from §10.8 ("emergency planning for ride operators and all other staff... could be written into your summary of the emergency planning," §10.8) and from §12.1 ("How often will you train workers in the plan?"). | §10.8, §12.1 | Confirms the cross-ACR link already anticipated in §4: emergency-response training is one `evidence_type` under ACR-003's `competency_evidence`, not a duplicate concept inside ACR-002. No schema change to ACR-002 from this — it's a modelling constraint on ACR-003's evidence taxonomy. |

**Updated recommendation: approve**, scope widened by one table (`emergency_service_consultations`) and the `exercise_type` enum broadened — both additive to, not a reversal of, the original design-driven recommendation. **Confidence: Very High** (sourcing gap that was the only stated reason for withholding it is now closed).

---

## 4. ACR-003 — Competency Management Domain (joint with ACR-001)

**Full text:** [.acr/ACR-003-competency-management-domain.md](../../.acr/ACR-003-competency-management-domain.md)

| Lens | Assessment |
|---|---|
| Regulatory requirement | Guide §10.8 unread (§1 caveat) — the specific structural requirement is not yet confirmed, only the general principle that competence evidence must exist. |
| Domain model consistency | Competency-as-canonical avoids the V1-pattern refactor risk both ACRs themselves already identify. Recommend **not** one table per evidence type (Qualification, Licence, OEM certification, Assessment, Authorisation) — reuse `safety.evidence` (already a generic evidence table serving Verification) for the *evidence artefact* itself, with a new `safety.competencies` table for the *claim* ("Person X is competent for Role/Control Y") and a join table `safety.competency_evidence` linking claim to evidence, mirroring the existing `safety_argument_evidence` join-table pattern exactly. |
| Implementation impact | L — two new tables (`competencies`, `competency_evidence`), reuse of `safety.evidence`, new FKs to `safety.persons`, `safety.critical_controls` (operator-competency-as-assurance-input), `regulatory.requirements`; one new ontology scheme (competency category/currency taxonomy); relationship-catalogue additions for `REQUIRES_COMPETENCY` / `DEMONSTRATES_COMPETENCY` edge types; new OpenAPI tag `Competency`. |

**Scope explicitly deferred, not silently dropped:** "Experience" (cumulative, not a discrete record) — recommend v1.2, out of scope for this ACR. Currency/refresher — recommend reuse `safety.review_triggers` (already the MOC pattern) rather than a new state-tracking mechanism.

**Recommendation (design-driven, pre-verification): approve ACR-003, supersede ACR-001.** Training becomes an `evidence_type` value within `safety.evidence`/`competency_evidence`, not its own table. This is the single largest-impact recommendation in this pack and the one most directly preventing a future refactor.

### 4a. Verification findings — Guide §10.8 read in full, 2026-08-04

The Competency-as-canonical shape is **confirmed correct**; §10.8 does not overturn it. One genuinely new entity surfaces, plus several refinements to the evidence taxonomy, all **Verification-driven**:

| Finding | Guide reference | Effect on ACR-003 |
|---|---|---|
| Training is explicitly **role-based**: "the skills necessary for all positions (e.g. skills matrix)... training needs analysis (gap between skills and those required for a role)." Managers, senior management, and company officers are named as *distinct role categories* with distinct competency obligations (officers' s.27 duty-of-care information is explicitly "not `training`" but must still be tracked). | §10.8 | **Genuinely new — "Role" is structurally required, not just implied.** ACR-001's own text flagged "Roles (not currently modelled anywhere in the baseline)" as a possible second gap; §10.8 confirms it directly. Recommend a new lightweight table `safety.roles` (name, category — e.g. operator/technical/management/officer) and a join `safety.role_competency_requirements` (role → required competency type). `safety.competencies` gains an FK to `safety.roles` alongside the existing FK to `safety.persons`. |
| Refresher/currency is **not purely time-based** — it is explicitly re-triggered by new or changed ADHs/ADIs ("review and revision of training needs and information in line with changes or new ADHs and ADIs," §10.8). | §10.8 | Confirms (does not change) the recommendation to reuse `safety.review_triggers` — this is exactly the same pattern already governing MOC, now confirmed to apply here for the same reason (a safety-assessment change, not just elapsed time, invalidates currency). |
| **Trainer/assessor competency and validation is itself in scope**: "management of the trainer's competency and validation of their assessment processes" (§10.8). | §10.8 | No new entity — `safety.competencies.assessed_by` (FK to `safety.persons`) already covers this by self-reference: an assessor's own competency record uses the same table. Confirms the join-table design rather than requiring a separate "Assessor" entity. |
| Officer duty-of-care information acquisition is explicitly **not training** but must still be evidenced ("This may not be in the form of `training` however it is a duty under the WHS Act that this information is acquired," §10.8). | §10.8 | Confirms `evidence_type` must be a broad enum, not narrowly training-shaped — e.g. `{training, assessment, qualification, licence, oem_certification, authorisation, information_briefing}` — no schema change beyond enum breadth. |
| Explicit links required to: ADI history, incident reporting process, and control measures ("the inclusion of information pertaining to ADHs and ADIs... controls used to minimise the occurrence of ADIs," §10.8). | §10.8 | Confirms the already-recommended FKs to `safety.critical_controls`; adds a recommended FK from `safety.competencies` (or `competency_evidence`) to `safety.incidents` where a competency requirement arose from incident learning — additive, not structural. |
| Emergency-response training is explicitly folded into the training system's scope, cross-referencing §12 (see ACR-002 §3a). | §10.8 | Confirms `evidence_type` includes an emergency-response-training value, and that ACR-002's `emergency_exercises` records can be one *source* feeding a `competency_evidence` row — the two ACRs share this edge, cross-referenced, not duplicated. |

**Updated recommendation: approve ACR-003, supersede ACR-001**, scope widened by one table pair (`roles`, `role_competency_requirements`) beyond the original design-driven pass. **Confidence: Very High** (sourcing gap closed).

---

## 5. Cross-ACR Impact Matrix (updated post-verification)

| Artefact | ACR-002 (Emergency Planning) | ACR-003 (Competency, supersedes ACR-001) |
|---|---|---|
| PostgreSQL schema | +`emergency_plans` (one per `safety.parks`), +`emergency_exercises` (widened `exercise_type` enum), +`emergency_plan_credible_events` (join), +`emergency_service_consultations` **(verification-driven)**, FKs on `assets`/`credible_events`/`safety_arguments`/`regulatory.requirements` | +`competencies`, +`competency_evidence`, +`roles`, +`role_competency_requirements` **(verification-driven)**, FKs on `persons`/`critical_controls`/`requirements`/`incidents` |
| Neo4j model | New relationship types (e.g. `HAS_EMERGENCY_PLAN`, `EXERCISES`, `CONSULTED`) — no new node label beyond `EmergencyPlan`/`EmergencyExercise` | New relationship types (`REQUIRES_COMPETENCY`, `DEMONSTRATES_COMPETENCY`) — new node labels `Competency`, `Role` |
| Ontology | +1 scheme (emergency scenario/exercise classification, widened taxonomy) | +1 scheme (competency category/currency), role taxonomy folded into same scheme |
| OpenAPI | Fits under existing `SafetyCase` tag | +1 new tag: `Competency` |
| Relationship catalogue | +rules for new edges, §6-style entries | +rules for new edges, §6-style entries |
| Inference rules | Possible new rule: emergency-exercise currency lapse (parallel to existing review-trigger pattern) | Possible new rule: competency-lapse blocking critical-control operator assignment; new rule: ADH/ADI change re-triggers refresher requirement (§4a) |
| Documentation index | [12-deliverables-index.md](12-deliverables-index.md) update | [12-deliverables-index.md](12-deliverables-index.md) update |

Both ACRs, if approved, are sized to fit inside a single controlled Design Baseline v1.0 → v1.1 pass — neither requires re-opening the frozen architecture doc (`PLATFORM_ARCHITECTURE_V2.md`) itself, only the knowledge-graph document set. The verification-driven additions (2 tables per ACR) do not change either ACR's overall size band (still M for ACR-002, L for ACR-003) — they refine shape within the same order of magnitude, not scope creep into a larger band.

---

## 6. Approval Section

**Completed by the Architecture Review Board (project sponsor), 2026-08-04. All sourcing gaps against these three ACRs were closed first (§10.8, §12 read in full, 2026-08-04) — the Board's own stated precondition.**

| ACR | Recommendation (post-verification) | Confidence | Decision | Approved by | Date | Baseline impact |
|---|---|---|---|---|---|---|
| ACR-001 | Do not approve independently — superseded by ACR-003 | Very High | **Rejected** — superseded by ACR-003 | Project sponsor | 2026-08-04 | None — no standalone Training entity created |
| ACR-002 | Approve, scoped to `emergency_plans` + `emergency_exercises` + `emergency_plan_credible_events` + `emergency_service_consultations` + FK links only | Very High | **Approved**, as scoped | Project sponsor | 2026-08-04 | Design Baseline v1.0 → v1.1 |
| ACR-003 | Approve as canonical entity; Training folded in as evidence type; `roles` + `role_competency_requirements` added per §10.8 | Very High | **Approved**, as scoped | Project sponsor | 2026-08-04 | Design Baseline v1.0 → v1.1 |

**Board rationale (recorded verbatim intent):** ACR-001 rejected because the verified Guide confirms competency, not training, is the governing concept — training is an input to and evidence of competence, and approving a standalone Training domain would duplicate the model and increase refactor risk. ACR-002 approved because Guide §12 confirms Emergency Planning requires capabilities the baseline didn't represent, while the canonical-reuse modelling (Scenario→CredibleEvent, Equipment→Asset, Response Capability→SafetyArgument, emergency-response training→Competency) preserves the same modelling discipline already established elsewhere. ACR-003 approved because Guide §10.8 validates a role-based competency model, consistent with ISO 45001's competence-vs-training distinction and Safety Case evidence principles; Experience is explicitly deferred to a future baseline version, not silently dropped.

## 7. Resulting Design Baseline

**Design Baseline v1.0 → Design Baseline v1.1 (Approved, 2026-08-04).** The architecture itself was not redesigned — the approved ACRs extend the baseline in a controlled manner, per the reuse-over-invent discipline applied throughout §3a/§4a.

## 8. Regeneration — Completed

| Artefact | Action | Where |
|---|---|---|
| PostgreSQL schema | Updated | [knowledge-graph/03-postgresql-schema.sql](../knowledge-graph/03-postgresql-schema.sql) — new "DESIGN BASELINE v1.1 AMENDMENT" section |
| Neo4j model | Updated | [knowledge-graph/02-neo4j-node-relationship-model.md](../knowledge-graph/02-neo4j-node-relationship-model.md) §3.6, §4, §5 |
| Relationship catalogue | Updated | [knowledge-graph/06-relationship-rules-catalogue.md](../knowledge-graph/06-relationship-rules-catalogue.md) §5b |
| Inference rules | Updated | [knowledge-graph/07-inference-rules-catalogue.md](../knowledge-graph/07-inference-rules-catalogue.md) R19–R22 |
| OpenAPI specification | Updated | [knowledge-graph/10-openapi.yaml](../knowledge-graph/10-openapi.yaml) — `Competency` tag, `/parks/{parkId}/emergency-plan` + related paths, v0.2.0-draft |
| Enterprise ontology | Updated | [knowledge-graph/01-enterprise-knowledge-graph-specification.md](../knowledge-graph/01-enterprise-knowledge-graph-specification.md) §6a — 3 new schemes |
| Documentation index | Updated | [12-deliverables-index.md](12-deliverables-index.md) |
| Safety Case Demonstration Model | Cross-reference update only | [knowledge-graph/11-safety-case-demonstration-model.md](../knowledge-graph/11-safety-case-demonstration-model.md) §0 |
| Regulatory Knowledge Model | Cross-reference update only | [knowledge-graph/09-regulatory-knowledge-model.md](../knowledge-graph/09-regulatory-knowledge-model.md) §5/§5a |
| Implementation risk register | Updated | [11-implementation-risk-register.md](11-implementation-risk-register.md) — risk D4 closed |
| Application Foundation Scaffold | Updated | [13-application-foundation-scaffold.md](13-application-foundation-scaffold.md) — Training→Competency module rename, Safety Demonstration/MOC entries extended |

Existing identifiers preserved throughout — no renamed or removed tables/columns/paths/schemas, only additions, per the Board's regeneration guidance.

## 9. Freeze

> **Design Baseline v1.1 is declared the controlled architectural baseline, effective 2026-08-04.**
> No further architectural changes are permitted except through the Architecture Change Request process ([02-development-standards.md](02-development-standards.md) §7).

## 10. Release Gate

| Gate | Status |
|---|---|
| Design Baseline v1.1 | ✅ Approved |
| Implementation Blueprint | ✅ Approved |
| Application Foundation | ✅ Approved |
| ACR Review Pack | ✅ Closed |
| R0 — Repository Initialisation | **Authorised** |

**R0 is authorised as of 2026-08-04.** See [12-deliverables-index.md](12-deliverables-index.md) for the updated master gate record.
