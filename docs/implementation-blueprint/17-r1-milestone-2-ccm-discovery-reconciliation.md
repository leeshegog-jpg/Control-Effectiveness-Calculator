# R1 Milestone 2A — CCM Discovery & Reconciliation Findings

**Status:** Research only. No code, schema, migration, API, or ontology changes were made to produce this document. Authorized scope: discovery/reconciliation pass only (see chat authorization, R1 Milestone 2A).

**Scope of this pass:** reconcile V1 (`bowtie-ccm-generator.html`, `GOHS4.1.8.X_FARSI_Control_Effectiveness_Calculator_v0.2.html`), the frozen PostgreSQL schema, the frozen OpenAPI contract, and the existing (unimplemented) CCM design docs (`06-relationship-rules-catalogue.md`, `07-inference-rules-catalogue.md`, `08-critical-control-assurance-model.md`) against the proposed Critical Control = Control + Support + Verification (with Owner/Frequency/Parameter mandatory on Verification) framing.

---

## 1. Executive Finding

The core CCM object model is **internally consistent across V1, the frozen schema, the frozen OpenAPI contract, and the existing design docs** — and all four converge on **Option A** (classification as a value on sibling rows), not Option B (Control/Support/Verification as subordinate children of a single Critical Control parent). This is not a fresh decision to make; it is already the built, executed, and cross-referenced reality of the frozen baseline. Adopting Option B would mean overriding the frozen schema, which is out of scope for this authorization and would require an ACR.

Two genuine structural gaps were found (§6d, §6e below), and three areas of the user's proposed Owner/Frequency/Parameter triad don't map cleanly onto the frozen model as literally proposed (§6a–§6c). None of these require a schema change to begin Milestone 2 implementation — they are implementation-time interpretation decisions, addressed as Decision Points in §7, each recommended for a short ADR rather than a full ACR (§9), because none of them, as recommended, changes the frozen schema.

A procedural finding, not a content defect: `06` and `08` carry the same "DRAFT — requires approval before implementation" boilerplate header as `02`/`03`/`10` — a header on *every* knowledge-graph doc, not a marker specific to `08`. Milestones 0–1 already implemented directly against `02`/`03`/`06`/`07`/`10` despite that boilerplate. The real gap is narrower: unlike Training/Emergency Planning/Competency Management (ACR-001/002/003), `08`'s CCM content was never explicitly listed in the v1.1 Board Approval Table in [14-architecture-change-requests.md](14-architecture-change-requests.md). See Decision Point D6.

---

## 2. V1 Behaviour (source-cited)

CCM has no home in `risk-register.html` — that file only ever captured "Existing Controls" as free text (confirmed during Milestone 1). V1's actual CCM logic lives in two separate, standalone tools:

### `bowtie-ccm-generator.html` — classification, gates, performance, verification
- **Gate assignment (the exact 3-gate test):** `setGate()`, lines 1505–1507 — `c.gates[gi]=val`; `if(c.gates.every(g=>g===true)) c.classification='Control'`; else `c.classification = c.followup==='verification' ? 'Verification' : (c.followup==='support' ? 'Support' : null)`. `setFollowup()`, line 1510, sets `classification` to `'Verification'` or `'Support'` directly from the follow-up answer. **All of this operates on one control object per candidate** — there is no parent/child structure in the V1 source.
- **Gate questions and critical-control test text:** `REF.controlGateTests` (3 entries) and `REF.criticalControlTest`, both in the `REF` object at line 398 — verbatim source for `08 §2`/`§3`.
- **Owner (closest V1 analog):** `verifByWhom` — a free-text name field, set once per control (line 1354 init, line 1550 UI, line 1584 handler). V1 does **not** distinguish a standing "verification owner" from "whoever performed the check" — it is one field, reused. There is no V1 concept of an owner distinct from the control's own author/owner.
- **Frequency:** `verifFrequency` (line 1354 init, default `'Monthly'`), driven by `FREQ_DAYS` (line 533): `{'Daily':1,'Weekly':7,'Fortnightly':14,'Monthly':30,'Quarterly':91,'Annual':365,'Biennial':730,'Other':null}`.
- **Parameter (no single V1 field):** V1 splits what the user's proposal calls "Parameter" across **four separate free-text fields**, all on the control object itself, not on a separate verification record: `perfFunctionality`, `perfAvailability`, `perfReliability`, `perfResponse` (lines 1353, 1538–1543). Note the fourth dimension is **"Response [time]"**, not "Survivability" or "Interdependency" — a third naming variant alongside FARSI's five and EIA's three. Additionally `verifMethod` (how it's checked, line 1546) and `verifRecordLoc` (line 1551 — e.g. "Mobaro / Maximo / Figtree", the external system of record) are captured, neither of which has any frozen-schema equivalent.
- **A third V1 effectiveness concept, not just EIA/FARSI:** `REF.effectivenessLevels` (line 398) — a 5-level qualitative scale (Highly Effective → Not Effective), each with a `reduce{}` lookup table that maps an inherent likelihood level directly to a residual likelihood level. Used in `strongestControl()` (line 1358) and the effectiveness picker (lines 1554, 1589). This is wired into real generation logic, not decorative. **Neither `07-inference-rules-catalogue.md` nor `08` account for this mechanism** — `08 §4` frames EIA and FARSI as "two tools, not one," but V1 itself runs a third, independent effectiveness calculation. See §6e / D5.

### `GOHS4.1.8.X_FARSI_Control_Effectiveness_Calculator_v0.2.html` — FARSI
- Verified independently (not just trusting `08`'s citation): the file labels the fifth FARSI dimension **"Interaction"** (lines 252, 483–487, 834, 847), not "Interdependency." This confirms `08 §4b`'s stated correction — the Guide (WHSQ 2021 §9.2.2.1, Table 3) uses "Interdependency," V1's calculator has it wrong, and the frozen schema/OpenAPI correctly use "Interdependency" (`farsi_interdependency`), not V1's term. Correctly *not* ported verbatim on this one point — the only deliberate deviation from V1 found anywhere in this reconciliation, and it's already documented as such.
- No Owner/Frequency/Parameter concept anywhere in this file — it is a pure scoring calculator, unconnected to authoring/scheduling.

---

## 3. Frozen Schema — what currently exists ([03-postgresql-schema.sql](../knowledge-graph/03-postgresql-schema.sql))

| Table | Lines | Key columns | Notes |
|---|---|---|---|
| `safety.controls` | 200–218 | `id`, `risk_id` (FK, NOT NULL), `description`, `control_type` (Prevention\|Mitigation), `hierarchy_concept_id` (FK ontology), `classification` (CHECK IN Control\|Support\|Verification), `gate_1/2/3` (bool), `eia_effective/independent/auditable` (bool), `effectiveness_rating` (varchar(30), free text), `owner_person_id` (FK persons) | One row per authored candidate control. **No status/retired column.** |
| `safety.critical_controls` | 220–236 | `control_id` (PK **and** FK to `controls.id` — 1:1, not a separate entity), `farsi_functionality/availability/reliability/survivability/interdependency` (1–5), `farsi_score` (GENERATED, average of the five) | 1:1 extension table, exists only for rows that passed Stage 2. **No status/retired column.** |
| `safety.failure_modes` | 238–243 | `id`, `control_id` (FK), `description`, `mode_concept_id` | 1:N per Control. |
| `safety.performance_standards` | 245–252 | `id`, `critical_control_id` (FK, NOT NULL), `requirement_text`, `measurable_criteria` | 1:N per CriticalControl. **This is where "Parameter" lives today**, one level above Verification. |
| `safety.verification_activities` | 256–267 | `id`, `performance_standard_id` (FK, NOT NULL), `method_concept_id` (FK ontology), `frequency` (varchar(30)), `due_date`, `last_completed`, `performed_by_person_id` (FK persons), `result` | 1:N per PerformanceStandard. `frequency` lives here — matches V1 exactly. No dedicated "parameter" field; inherits its acceptance criterion from the parent PerformanceStandard. |
| `safety.evidence` | 272–281 | `id`, `type_concept_id`, `verification_activity_id` (nullable FK), `source_document_id`, `uploaded_by_person_id`, `linked_entity_type`/`linked_entity_id` (polymorphic) | Evidence can stand alone (nullable FK to verification activity). |
| `safety.trigger_action_response_plans` | 324–338 | `id`, `critical_control_id` (FK, NOT NULL), `trigger_condition`, `trigger_source_rule`, `required_action`, `response_owner_person_id`, `escalation_level` (supervisor\|manager\|executive), `status` (active\|triggered\|resolved\|retired) | Already exists, executed. Net-new vs V1 (no V1 equivalent, per its own comment at line 322). |
| `safety.monitoring_summaries` | 436–447 | `id`, `critical_control_id` (FK), `period_start/end`, `verification_count`, `pass_count`, `trend`, `indicator_class` (leading\|lagging) | Time-series rollup; `indicator_class` added by ALTER at line 444. |

**Confirms Option A structurally:** `classification` is a single-value CHECK-constrained column on one `controls` row. `critical_controls.control_id` is simultaneously its primary key and its foreign key to `controls.id` — a 1:1 extension, not a nested child collection. There is no table anywhere that represents "Critical Control" as a parent object distinct from a classified `controls` row.

**Confirmed absence:** no `status`, `is_retired`, or equivalent column on `controls` or `critical_controls`. `08 §6`'s state diagram includes a `Critical --> Retired` transition with nowhere to persist it.

---

## 4. OpenAPI — what currently exists ([10-openapi.yaml](../knowledge-graph/10-openapi.yaml))

| Path | Purpose | Lines |
|---|---|---|
| `GET/POST /risks/{riskId}/controls` | List/create control candidates for a risk | 400–412 |
| `GET /controls/{id}` | Get a control | 413–419 |
| `POST /controls/{id}/gate-test` | Submit `gate_1/2/3` (+ `is_verification_check` follow-up) → server returns computed `classification` | 420–444 |
| `POST /controls/{id}/eia-test` | Record EIA (distinct from the gate test) | 445–452 |
| `POST /controls/{id}/critical-control-test` | Submit `is_critical` → creates `CriticalControl`; **409 if not already `classification = 'Control'`** | 453–470 |
| `GET/PATCH /critical-controls/{id}` | Get (incl. derived `farsi_score`/`health_state`) / update FARSI scores | 471–483 |
| `GET/POST /critical-controls/{id}/performance-standards` | | 484–492 |
| `GET/POST /performance-standards/{id}/verification-activities` | | 493–501 |
| `GET/POST /verification-activities/{id}/evidence` | | 502–511 |
| `GET/POST /critical-controls/{id}/tarps`, `POST /tarps/{id}/resolve` | | 512–527 |

**Schema fields (lines 969–1068):**
- `Control`/`ControlInput`: `risk_id`, `description`, `control_type`, `hierarchy`, `owner_person_id`, `effectiveness_rating` — plus **readOnly** `classification`, `is_critical`. Classification/criticality are never client-settable; they're workflow outputs of the gate-test/critical-control-test endpoints. This matches V1's `setGate()` exactly and matches `06`'s invariant that classification is set at a specific point in the authoring workflow, not free-edited.
- `CriticalControl`: `farsi_*` ×5, `farsi_score` (readOnly), `eia_*` ×3, and **`health_state`** (readOnly, enum `[Verified, Healthy, Degraded, Overdue, Unverified]`) — a computed field, consistent with `08 §6`'s explicit statement that these states aren't stored. Note the enum only covers the *post-critical, ongoing-assurance* sub-states from `08`'s full diagram — `Draft`/`Gated`/`ControlClassified`/`Critical`/`TARP_Triggered`/`Retired` aren't represented here (the first four are derivable from existing data without a dedicated field; `TARP_Triggered` surfaces via the TARP entity's own `status`; **`Retired` has no representation anywhere**, matching the schema-level gap in §3).
- `PerformanceStandardInput`: `requirement_text`, `measurable_criteria` — this is the API-level confirmation that "Parameter" is a Performance Standard concept, not a Verification Activity concept.
- `VerificationActivityInput`: `method`, `frequency` (enum matches `FREQ_DAYS` keys exactly), `due_date`, `last_completed`, `performed_by_person_id`, `result` — no parameter/threshold field. `performed_by_person_id` is per-activity, not a standing owner.

---

## 5. Control / Support / Verification Analysis

`classification` means: **which of three roles does this one authored control candidate play, for the risk it was created against.** It is assigned once, via the 3-gate test (`08 §2`, `bowtie-ccm-generator.html:1505-1510`), and is not re-assignable except by re-running the workflow. A `Risk` can have many `Control`-table rows attached via `MITIGATED_BY` (N:N per [02-neo4j-node-relationship-model.md](../knowledge-graph/02-neo4j-node-relationship-model.md) §4 and [06-relationship-rules-catalogue.md](../knowledge-graph/06-relationship-rules-catalogue.md) §3 line 27) — some classified `'Control'`, some `'Support'`, some `'Verification'`. Only rows classified `'Control'` are eligible for the Stage 2 critical-control test and the resulting 1:1 `CLASSIFIED_AS_CRITICAL` edge to a `CriticalControl` row (`06` line 28: *"Only permitted when `controls.classification = 'Control'`"*). `06`'s explicit invariant #4 (line 62): *"No self-contradicting classification. A `Control` cannot carry `classification = 'Support'` or `'Verification'` and also carry a `CLASSIFIED_AS_CRITICAL` edge."*

**"Critical Control" in the frozen architecture = a `controls` row (classification='Control') plus its 1:1 `critical_controls` extension row.** Support and Verification rows are **not** subordinate components of that object — they are separate, independent `controls` rows tied to the same `Risk`, playing a different role. The user's proposed Option B (Critical Control as a parent with Control/Support/Verification as children) does not match V1, the schema, the OpenAPI contract, or `06`/`08` at any point. This is Option A, confirmed four ways independently.

---

## 6. Structural Gap Analysis

| # | Gap | V1 | Frozen schema/API | Assessment |
|---|---|---|---|---|
| a | **Owner** as a Verification-level attribute | `verifByWhom` — free text, on the control record, conflated with "who performed it" | `owner_person_id` on `controls` (applies once, any classification); `performed_by_person_id` on `verification_activities` (per-instance, not standing) | No layer has a distinct standing "verification schedule owner" separate from control owner. The user's proposed model requires one; nothing currently provides it. |
| b | **Frequency** | `verifFrequency` / `FREQ_DAYS` | `verification_activities.frequency`, OpenAPI enum matches `FREQ_DAYS` keys exactly | **Fully reconciled — no gap.** Already exactly where the user's proposal wants it. |
| c | **Parameter** | Split across 4 free-text fields on the control record (`perfFunctionality/Availability/Reliability/Response`) — no single field, no separate Verification-level record at all | Lives on `performance_standards.measurable_criteria`, one level above `VerificationActivity` | Two-directional gap: V1 doesn't cleanly map to a single "Parameter" concept either, and the frozen model deliberately separates Parameter (Performance Standard) from Verification (the activity that checks it) — the opposite of embedding Parameter directly in Verification. |
| d | **Retired / decommissioned state** | No V1 equivalent (V1 has no control lifecycle at all beyond authoring) | `08 §6` requires it (`Critical --> Retired`); no column exists on `controls` or `critical_controls` in schema or API | Confirmed gap, both layers, no V1 precedent either way. |
| e | **V1's `effectivenessLevels`/`reduce{}` mechanism** | Real, wired-in, independent of EIA/FARSI (§2 above) | Not addressed in `07` (only R2/FARSI covers effectiveness→risk-reduction) or `08 §4` ("two tools, not one") | A real V1 mechanism the approved architecture doesn't currently account for. Needs an explicit scope decision, not a silent drop or silent port. |
| f | **Governance status of `06`/`08`** | N/A | Same "DRAFT" boilerplate as every knowledge-graph doc; unlike ACR-001/002/003, never explicitly in the v1.1 Board Approval Table ([14](14-architecture-change-requests.md)) | Procedural gap. Milestones 0–1 already implemented against docs carrying the identical boilerplate without treating it as a blocker — but 08 was never put before the Board the way the three ACR domains were. |
| g | Parameter is unstructured free text even in the target schema | Also free text (4 fields) | `measurable_criteria` — untyped text, no unit/threshold/comparator structure | Not a new gap relative to V1 (V1 was also free text) — noted for completeness, not a mismatch. |

---

## 7. Decision Points

| # | Decision | Current evidence | Options | Recommended action | ADR required |
|---|---|---|---|---|---|
| D1 | Object model: Option A vs Option B | V1, schema, OpenAPI, and `06` all converge on Option A (§5) | (a) Adopt Option A as-is; (b) Restructure to Option B | **(a).** Not a fresh choice — already the built, executed reality of the frozen baseline. | No, for (a) — matches frozen baseline unchanged. **ACR required** if (b) were ever pursued (changes frozen table structure). |
| D2 | Owner on Verification | No layer has a distinct standing verification owner (§6a) | (a) Use `controls.owner_person_id` as the de facto owner for all three roles [matches V1's own conflation]; (b) Use `verification_activities.performed_by_person_id` per-instance only, no standing owner concept; (c) Add a new column splitting "verification schedule owner" from control owner | **(a)** for Milestone 2 — no schema change, matches both V1 and frozen schema. | ADR to record the choice between (a)/(b) now. **ACR required** only if (c) is later pursued (adds a column). |
| D3 | Where "Parameter" lives | Schema/API: on `PerformanceStandard`. V1: split across 4 fields on the control record (§6c) | (a) Keep Parameter on `PerformanceStandard.measurable_criteria`/`requirement_text`, mapping V1's 4 fields into those 2 at migration time [matches frozen schema exactly]; (b) Add a parameter field directly to `VerificationActivity` | **(a).** | ADR to record the V1-field-mapping decision (still worth recording — a real data-shape choice). **ACR required** if (b) pursued. |
| D4 | Retired/decommissioned state | `08 §6` requires it; no column exists anywhere (§6d) | (a) Add a `status`/`is_retired` column now; (b) Represent retirement implicitly (no open `MITIGATED_BY` link, or a provenance entry only) — loses queryability; (c) Defer entirely, flag as known gap, don't implement decommissioning in Milestone 2 | **(c)** — matches the project's established norm of not adding columns ahead of the milestone that needs them (same reasoning as Milestone 0/1's YAGNI scoping). | ADR to record the deferral. **ACR required** only once (a) is actually pursued. |
| D5 | V1's qualitative `effectivenessLevels`/`reduce{}` mechanism | Real, wired-in V1 mechanism, unaddressed by `07`/`08` (§6e) | (a) Treat `controls.effectiveness_rating` as sufficient to capture only the V1 label string, and do **not** port the `reduce{}` risk-reduction lookup logic in Milestone 2 [matches R2's stated intent that only FARSI feeds risk-reduction]; (b) Port `reduce{}` as a new inference rule (new rule → `07 §3` governance gate); (c) Confirm with a domain expert whether this V1 mechanism is still in active use or is legacy | **(a)** now, with **(c)** flagged as a follow-up question before this decision point is fully closed. | ADR required — this is a deliberate scope-narrowing relative to what V1 actually computes, must be recorded, not silently dropped. |
| D6 | Governance/approval status of `06`/`08` for CCM | Same boilerplate as already-implemented-against docs; never in the v1.1 Board Approval Table (§6f) | (a) Treat as already-effectively-approved by precedent, no further process; (b) Require an explicit sign-off pass over `08` (and CCM rows of `06`) before implementation, mirroring ACR-001/002/003, closing the process gap after the fact | **(b)** — low-risk (the schema this content depends on is already executed; no schema changes flow from approving `08` itself), but keeps governance honest given the "same discipline that prevented us from inventing Hazard Category" standard the user has set. | This reconciliation document, once reviewed and explicitly signed off, **is** the required record — recommend treating it as ADR-equivalent for D2/D3/D4/D5, rather than requiring a separate heavyweight ACR, since none of the recommended options change the frozen schema. |

---

## 8. Implementation Boundary — buildable without changing the frozen baseline

Every column, table, and endpoint below already exists in the frozen schema/OpenAPI (§3, §4) — none require a schema change:

- Control CRUD tied to Risk: `POST/GET /risks/{riskId}/controls`, `GET /controls/{id}`
- Gate-test workflow endpoint — server computes `classification` from `gate_1/2/3` + follow-up, exactly matching `bowtie-ccm-generator.html:1505-1510`
- EIA-test endpoint (`eia_effective/independent/auditable`)
- Critical-control-test endpoint (409 if not `classification='Control'`; creates the 1:1 `critical_controls` row)
- `CriticalControl` GET/PATCH — FARSI scores, generated `farsi_score`
- `PerformanceStandard` CRUD under `CriticalControl`
- `VerificationActivity` CRUD under `PerformanceStandard`
- `Evidence` CRUD under `VerificationActivity`
- `TARP` CRUD + resolve, under `CriticalControl`
- Inference rules over existing columns only, no new columns needed: R2 (FARSI multiplier), R3 (overdue), R6 (superficial verification), R8 (missing failure mode), R17 (EIA/FARSI consistency cross-check), R18 (lagging-only indicator gap)
- Computed `health_state` (`Verified`/`Healthy`/`Degraded`/`Overdue`/`Unverified`) per `08 §6` + R3/R5/R6 — computed at read time, not stored
- Neo4j sync: `MITIGATED_BY`, `CLASSIFIED_AS_CRITICAL`, `HAS_FAILURE_MODE`, `GOVERNED_BY`, `VERIFIED_BY`, `PRODUCES`

**Not buildable without a further decision (per §7), and not part of Milestone 2 as scoped here:**
- A distinct Verification-level Owner field (only if D2 option (c) is later chosen)
- A distinct Parameter field embedded directly in Verification (only if D3 option (b) is later chosen)
- Retired/decommissioned state (deferred per D4)
- The V1 `reduce{}` effectiveness→risk-reduction lookup mechanism (deferred per D5, pending domain-expert confirmation)

---

## 9. ADR Requirement

**No ACR is required to begin Milestone 2 implementation as scoped in §8** — every column and table it relies on already exists, executed, in the frozen schema, and the OpenAPI contract already specifies the exact workflow endpoints needed.

**An ADR is recommended before implementation starts**, bundling Decision Points D2, D3, D4, D5, and D6 — the same pattern as ADR-001/ADR-002 in Milestone 0. None of the recommended options in those five points change the frozen schema; each is an implementation-time interpretation or a deliberate, documented scope deferral. This reconciliation document, once reviewed, is intended to serve as the evidentiary basis for that ADR.

---

## Acceptance Criteria

- [x] Every CCM field relied upon has an identified source — cited by file and line throughout §2–§4.
- [x] Control/Support/Verification semantics are evidenced, not assumed — §5, four independent converging sources.
- [x] Owner/Frequency/Parameter traced to V1/schema/OpenAPI/approved design — §2, §6a–c. Frequency fully reconciled; Owner and Parameter show genuine, explicitly documented gaps (D2, D3).
- [x] FARSI and EIA boundaries identified — §2 (V1 calculator verified independently), `08 §4a/4b`, R2, R17.
- [x] Any schema/architecture mismatch is explicitly documented — §6, §7 (D1–D6).
- [x] No code has been changed — this document is the only artifact produced by this pass.
- [x] No architectural decision has been silently made — every open point is routed to §7 as a Decision Point awaiting explicit authorization; none resolved unilaterally in this document.
