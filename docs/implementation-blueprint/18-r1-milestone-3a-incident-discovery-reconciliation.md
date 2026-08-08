# R1 Milestone 3A — Incident Management Discovery & Reconciliation Findings

**Status:** Research only. No application code, schema, migration, API, ontology, Neo4j, Azure, or Entra changes were made to produce this document. Authorized scope: discovery/reconciliation pass only (chat authorization, R1 Milestone 3A, 2026-08-08).

**Scope of this pass:** reconcile V1 (`incident-report.html`, `corrective-actions.html`, `sms-shared.js`), the frozen PostgreSQL schema (`03-postgresql-schema.sql`), the frozen OpenAPI contract (`10-openapi.yaml`), the frozen Neo4j relationship model (`02-neo4j-node-relationship-model.md`), the relationship/inference rule catalogues (`06`, `07`), the regulatory knowledge model (`09`), and ontology dependencies — against the Incident Management domain, with an explicit instruction **not** to assume Incident → Investigation → Corrective Action as the canonical structure.

Every finding below is labeled: **CONFIRMED** (single artefact, directly read), **RECONCILED** (multiple independent sources agree), **CONFLICT** (sources disagree), **GAP** (required information/capability absent), **TO_BE_CONFIRMED** (evidence insufficient), or **DECISION REQUIRED** (governance/architecture call needed).

---

## 1. Executive Finding

The Incident/Investigation/Action object model is **RECONCILED across V1, the frozen schema, and the frozen Neo4j model** — but it is **not** a linear chain. The frozen graph explicitly specifies three independent edges out of `Incident`: `REVEALS` (→ Hazard, N:N), `INVESTIGATED_AS` (→ Investigation, 1:1), and `TRIGGERS` (Incident *or* AuditFinding → Action, 1:N). Investigation and Action are **siblings hanging off Incident**, not a sequential Incident→Investigation→Action pipeline, and Action is a **shared polymorphic entity** (`safety.actions.source_type_concept_id` + `source_id`) also triggerable by Audit Findings, Risk Reviews, Hazard Reports, and Observations per V1's own `corrective-actions.html` source picker. This confirms the critical boundary flagged in the authorization prompt: the intuitive chain is **not** what the frozen baseline says (§5).

Two structural artefacts exist for "V1 incident reporting" in the repository — the root-level SMS suite (`incident-report.html`, linked from `index.html`'s module nav, sharing `sms-shared.js`/`sms.css`) and a separate standalone tool (`OHS_Command_Centre/incident_report.html`, different visual system, different app). The frozen schema resolves this **CONFIRMED**, not ambiguous: its own comment at `03-postgresql-schema.sql:511-512` states the incident/action/audit chain "ports `incident-report.html`, `corrective-actions.html`, `audit-inspection.html` near-verbatim" — naming the root SMS suite files exactly, by filename, with no reference anywhere in any frozen doc to `OHS_Command_Centre`. §2 treats the root suite as sole V1 source and flags `OHS_Command_Centre/incident_report.html` explicitly as out of scope, not silently dropped.

Three **material gaps** were found that go beyond implementation-time interpretation (unlike Milestone 2A's CCM findings, which needed no schema/API changes to proceed):

1. `safety.investigations` — the table backing the `INVESTIGATED_AS` 1:1 relationship — **exists in the frozen schema and Neo4j model but has zero representation in the frozen OpenAPI contract**: no `Investigation` schema object, no `/incidents/{id}/investigation` (or equivalent) endpoint anywhere in `10-openapi.yaml`. Same finding for `safety.incident_hazards` (`REVEALS`) and for Incident-scoped `Evidence` (the polymorphic `Evidence` schema's own comment names `'incident'` as a valid `linked_entity_type`, but only `/verification-activities/{id}/evidence` and `/competencies/{id}/evidence` are wired up — no `/incidents/{id}/evidence`). See §4, §8, §12 D4.
2. `incidents.incident_type_concept_id` and `actions.root_cause_category_concept_id` are ontology-scheme-dependent foreign keys with **no seeded scheme anywhere in `ontology/schemes/` or `ontology/seed-concepts/`** — the exact same category of gap already deferred for `Hazard.category_concept_id` (per the standing deferred-items list). Not a fresh problem to solve; both are nullable in schema and optional in OpenAPI, so they don't block Incident CRUD, but a scheme must not be invented here either. See §6, §12 D3.
3. Five V1 form fields (`lessonsLearned`, `fInvDate`/investigation completion date, `staffPresent`, `personStatus`, `reporterRole`, `otherNotes`) have **no column anywhere** in `safety.incidents` or `safety.investigations`. See §10, §12 D7.

Two items surfaced here are **pre-existing, already-tracked** open items, not new discoveries, and are cited as such rather than re-raised: `investigations.method` is already marked `TO BE CONFIRMED` in `docs/knowledge-graph/README.md:34`, and the Schedule 18C sub-item number for "incident management, investigation, reporting, improvement" (§10.7 of the WHSQ Guide) is already tracked as risk **REG3** in `11-implementation-risk-register.md:55`. See §7.

---

## 2. V1 Behaviour (source-cited)

### 2.1 Root SMS suite — authoritative V1 source (confirmed by frozen schema citation, §1)

**`incident-report.html`** (509 lines) — list view + modal form, backed by `sms-shared.js`'s flat localStorage store (`SMS.get('incidents')` / `SMS.add`/`SMS.update`). No client-side concept of a separate Investigation object — investigation fields are flat properties on the same incident record:

| V1 field (id) | Line(s) | Notes |
|---|---|---|
| `fDateTime`, `fReportDate` | 79–80 | datetime-local + date |
| `fType` | 81 | fixed 6-option select: Injury / Near Miss / Property Damage / Environmental / Security / Other — **not** ontology-backed in V1 |
| `fSev` | 82 | 1–5 int, labels Insignificant→Catastrophic (`SEV_LABEL` array, line 172) |
| `fLocation`, `fReporter` | 83–84 | free text |
| `fDesc` | 85 | required (`if(!f.description.trim())`, line 315) |
| `fInjuries`, `fWitnesses`, `fImmediate` | 86–88 | free text |
| `fVrtpSeverity` | 93 | 6-option select, **values** (not labels) exactly: `First Aid`, `Medical Treatment Injury`, `Lost Time Injury`, `Serious Injury`, `Dangerous Incident`, `Near Miss` — labels show VRTP abbreviations (MTI/LTI) but stored value is the full name |
| `fRideAsset` | 94 | free text, e.g. "Tornado ride (Asset ID: WNW-042)" — human-composed, not a real FK |
| `fStaffPresent`, `fPersonStatus`, `fReporterRole`, `fOtherNotes` | 95–100 | free text, **no frozen-schema column anywhere** (§10) |
| `fWhsq` | 97 | 4-option select, values exactly: `Not yet assessed`, `Yes`, `No - assessed not required`, `No - under assessment` |
| `fOsr` | 98 | 4-option select, values exactly: `Not applicable / under assessment`, `Yes`, `No - assessed not required`, `No - under assessment` |
| `fImmCause`, `fRootCause` | 105–106 | free text — investigation section of the *same* modal, not a separate form |
| `fInvStatus` | 107 | 3-option select: `Not Started`, `In Progress`, `Complete` |
| `fInvDate` | 108 | investigation completion date — **no frozen-schema column** (§10) |
| `fLessons` | 109 | Lessons Learned — **no frozen-schema column** (§10) |
| `fCARs` | 110 | free-text comma-separated CAR IDs (`carRefs`), display-joined against a separate `cars` collection (`renderCarLinks()`, lines 189–199) — no referential integrity, just string matching |
| `fStatus` | 111 | 3-option select: `Open`, `Under Investigation`, `Closed` |

**Cross-navigation to Corrective Actions** — `openCAR()` (lines 322–330): saves the incident first, then navigates to `corrective-actions.html?source=Incident&sourceRef=<incidentId>&desc=<truncated description>`. This is the V1 precedent for the polymorphic Action-creation pattern (§5).

**AI/agent pipeline** (`runPipeline()`, lines 396–467; `linkPipelineJob()`/`checkPendingPipelines()`, lines 469–502) — posts to a local PowerShell-hosted pipeline (`start-incident-form.ps1`, default `http://localhost:8765`) running "Investigation Agent → Compliance Agent → Safety Case Trigger" steps, polled for status. This is the client-side precedent for the frozen OpenAPI's `/incidents/{id}/run-investigation-pipeline` (§4). **Confirmed out of scope for this domain pass** — falls under the standing deferred item "AI functionality" (item 6 of the deferred-items list); noted for completeness only, not to be built in 3B.

**`corrective-actions.html`** — confirms the Action/CAR object shape: `source` (free string: `Incident`/`Audit`/`Risk Review`, `srcHref()` lines 185–191), `sourceRef` (free string), `rootCauseCategory`, `priority`, `assignedTo`, `dueDate`, `status`, `completionDate`, `effectiveness`, `notes`. `qp.has('source')` auto-opens the create form pre-filled from the incident's cross-navigation params (line 271).

**`sms-shared.js`** — confirms V1's flat client-side ID scheme: `PREFIX = { risks:'R', incidents:'I', cars:'C', audits:'A' }` (line 4), localStorage keys `sms_incidents`/`sms_cars`/`sms_audits` (line 3). Not portable to the backend's UUID scheme as-is — same class of ID-mapping non-issue already resolved in Milestones 0–2 (backend already uses `uuid` PKs throughout).

### 2.2 `OHS_Command_Centre/incident_report.html` — excluded candidate

A second, structurally unrelated incident-reporting tool exists at `OHS_Command_Centre/incident_report.html` (423 lines, dark-theme standalone form, its own severity taxonomy via `sev-btn` classes `fa`/`mti`/`lti`/`si`/`di`/`nm`, its own pipeline UI). It is **not** referenced by any frozen knowledge-graph document, the schema comment, the OpenAPI contract, or `06`/`07`/`09`. Per the discipline established in prior milestones (don't silently drop artefacts, don't silently include them either), this is recorded as: **excluded from this reconciliation** on the strength of the schema's explicit citation of the root-suite filenames (§1), not because it was ignored. Its severity abbreviation set (`fa`/`mti`/`lti`/`si`/`di`/`nm`) is consistent with — not contradictory to — the root suite's `vrtp_severity` values, for what that's worth if it's ever revisited.

---

## 3. Frozen Schema — what currently exists ([03-postgresql-schema.sql](../knowledge-graph/03-postgresql-schema.sql))

| Table | Lines | Key columns | Notes |
|---|---|---|---|
| `safety.incidents` | 515–540 | `id`, `datetime` (NOT NULL), `report_date`, `incident_type_concept_id` (FK ontology, nullable), `severity` (smallint 1–5), `vrtp_severity` (varchar(30), unconstrained), `location`, `asset_id` (FK assets), `reporter_person_id` (FK persons), `description` (NOT NULL), `injuries`, `witnesses`, `immediate_actions`, `immediate_cause`, `root_cause`, `whsq_notified` (varchar, default `'Not yet assessed'`), `osr_notified` (varchar, default `'Not applicable / under assessment'`), `investigation_status` (varchar, default `'Not Started'`), `status` (varchar, default `'Open'`) | Richest single table in the whole schema per its own comment (line 512). **No `lessons_learned`, no investigation-completion-date, no `staff_present`/`person_status`/`reporter_role`/`other_notes` column.** |
| `safety.incident_hazards` | 542–546 | `incident_id` (FK), `hazard_id` (FK), composite PK | Backs `REVEALS`. **No OpenAPI representation (§4).** |
| `safety.investigations` | 548–558 | `id`, `incident_id` (FK, **UNIQUE** — enforces 1:1), `method` (varchar, comment: `-- TO BE CONFIRMED — ICAM or VRTP-mandated equivalent`), `findings`, `contributing_factors` | Backs `INVESTIGATED_AS`. **No `lessons_learned` column either** — V1's Lessons Learned field has no home in this table or `incidents`. **Zero OpenAPI representation (§4).** |
| `safety.actions` | 560–578 | `id`, `source_type_concept_id` (FK ontology, nullable — comment lists Incident/Audit/Risk Review/Hazard Report/Observation/Other), `source_id` (uuid, polymorphic, no FK constraint — can't be, spans tables), `description` (NOT NULL), `root_cause_category_concept_id` (FK ontology, nullable), `priority`, `assigned_to_person_id`, `due_date`, `status`, `completion_date`, `effectiveness_review` | Shared entity across every triggering source, matching V1's `source`/`sourceRef` pattern (§2.1) three ways. |
| `safety.action_controls` | 580–584 | `action_id`, `control_id`, composite PK | `REMEDIATES` — Action↔Control, not incident-specific; noted for completeness. |
| `safety.incident_actions` | 586–590 | `incident_id`, `action_id`, composite PK | Backs `TRIGGERS` for the Incident side specifically. |
| `safety.evidence` | 272–281 | `linked_entity_type` (varchar(50), comment: `-- polymorphic pointer, e.g. 'hazard' \| 'control' \| 'incident'`), `linked_entity_id` | `'incident'` **named explicitly** in the schema's own comment as a valid target. No FK constraint (can't be, polymorphic) — application-layer integrity only. |

**Confirms the sibling structure, not a chain (§1, §5):** `investigations.incident_id` is `UNIQUE` (1:1), and there is no `investigation_id` column anywhere on `safety.actions` — an Action cannot be modeled as a child of an Investigation in the frozen schema. `incident_actions` links `Action` directly to `Incident`, bypassing Investigation entirely.

---

## 4. Frozen OpenAPI — what currently exists ([10-openapi.yaml](../knowledge-graph/10-openapi.yaml))

| Path | Purpose | Lines |
|---|---|---|
| `GET/POST /incidents` | List/create | 530–538 |
| `GET/PATCH /incidents/{id}` | Get/update | 539–547 |
| `POST /incidents/{id}/run-investigation-pipeline` | Trigger AI extraction pipeline (202, returns `extraction_run_id`) — explicitly cites `04-ai-extraction-specification.md §7` | 548–561 |
| `GET/POST /actions` | List (filterable by `status`)/create | 562–570 |
| `PATCH /actions/{id}` | Update | 571–576 |
| `GET/POST /audits`, `GET/POST /audits/{id}/findings` | Adjacent domain, not this pass's scope | 577–594 |

**GAP, confirmed by exhaustive search (`grep -n "Investigation" 10-openapi.yaml` → one non-schema hit only):** no `Investigation`/`InvestigationInput` schema object, no `/incidents/{id}/investigation` or `/investigations/{id}` endpoint of any form. `safety.investigations` (§3) is entirely absent from the API surface.

**GAP:** no `incident_hazards`/`REVEALS` endpoint (no `/incidents/{id}/hazards` or similar).

**GAP:** no `/incidents/{id}/evidence` endpoint — the two existing nested-evidence endpoints are `/verification-activities/{id}/evidence` (line 502) and `/competencies/{id}/evidence` (line 822) only.

**Schema fields confirmed (lines 1080–1126):**
- `IncidentInput` — `required: [datetime, description]` only; every other field (including `incident_type`) is optional, so the ontology-scheme gap (§6) does **not** block Incident CRUD.
- `IncidentInput.vrtp_severity` enum: `["First Aid", "Medical Treatment Injury", "Lost Time Injury", "Serious Injury", "Dangerous Incident", "Near Miss"]` — **RECONCILED, exact match** to V1's `fVrtpSeverity` option *values* (§2.1). The schema comment's abbreviated form (`MTI`/`LTI`) is shorthand only; the column itself is unconstrained `varchar(30)`, compatible with either.
- `IncidentInput.whsq_notified` / `osr_notified` enums — **RECONCILED, exact three-way match** (V1 §2.1, schema defaults §3, OpenAPI enum here) including the `osr_notified` description's citation of `09-regulatory-knowledge-model.md §4`.
- `ActionInput` — `required: [description]` only; `source_type`/`root_cause_category` optional, same nullable pattern as Incident.

---

## 5. Neo4j Relationship Model — the critical-boundary question ([02-neo4j-node-relationship-model.md](../knowledge-graph/02-neo4j-node-relationship-model.md) §3.3, and [06-relationship-rules-catalogue.md](../knowledge-graph/06-relationship-rules-catalogue.md))

| Relationship | Direction/cardinality | Source |
|---|---|---|
| `REVEALS` | `Incident → Hazard`, N:N | `02` line 110, `06` line 35 |
| `INVESTIGATED_AS` | `Incident → Investigation`, 1:1 | `02` line 111, `06` line 36 — "`investigations.incident_id UNIQUE` enforces this structurally" |
| `TRIGGERS` | `Incident \| AuditFinding → Action`, 1:N | `02` line 112, `06` line 37 — explicit invariant: "`actions.source_type_concept_id` + `source_id` must agree with which edge was used — an `Action` triggered by an `AuditFinding` cannot also claim `source_type = 'Incident'`" |

**RECONCILED, three independent sources (V1's UX pattern in §2.1, the Postgres FK structure in §3, and this graph model): the frozen architecture is not Incident → Investigation → Action.** It is `Incident` as a hub with three independent, non-sequential edges. Investigation is a 1:1 satellite of Incident (never of Action). Action is a shared, polymorphic entity reachable from Incident *or* AuditFinding (and, per the schema comment on `source_type_concept_id`, conceptually from Risk Review/Hazard Report/Observation too, though those source types have no dedicated join table the way Incident and — implicitly — Audit do). Building an implementation where `Action` nests under `Investigation`, or where Investigation is a mandatory gate before an Action can exist, would contradict all three sources. **This directly answers the authorization prompt's critical boundary instruction.**

`REVEALS` (Incident→Hazard) additionally connects this domain to the Milestone 1 Hazard/Risk domain and is the graph-level anchor for the regulatory notification rule (§7).

---

## 6. Ontology Dependencies

| FK | Table.column | Seeded scheme? | Status |
|---|---|---|---|
| Incident type | `incidents.incident_type_concept_id` | **No** — `ontology/schemes/` is empty, `ontology/seed-concepts/` holds only `consequence-domains.yaml`, `control-hierarchy.yaml`, `energy-sources.yaml` | **GAP**, same class as the standing deferred `Hazard.category_concept_id` gap |
| Action root-cause category | `actions.root_cause_category_concept_id` | **No** | **GAP**, same class |
| Investigation method | `investigations.method` (varchar, not FK) | N/A — free text, not ontology-backed | Already `TO_BE_CONFIRMED` per `docs/knowledge-graph/README.md:34` (pre-existing, not new) |

Both concept-FK gaps are **nullable in schema and optional in the OpenAPI contract** (§3, §4) — neither blocks basic Incident/Action CRUD. Per the standing project discipline (no invented ontology schemes), V1's flat 6-value `incidentType` enum (Injury/Near Miss/Property Damage/Environmental/Security/Other, §2.1) must **not** be silently promoted into a new ontology scheme during implementation. This is recorded as Decision Point D3 (§12), explicitly analogous to the already-deferred Hazard Taxonomy item.

---

## 7. Regulatory / Reportable-Event Requirements

Source: [09-regulatory-knowledge-model.md](../knowledge-graph/09-regulatory-knowledge-model.md) §6, [07-inference-rules-catalogue.md](../knowledge-graph/07-inference-rules-catalogue.md) R10.

**RECONCILED, formalized, not inferred:** `09 §6` explicitly "formalizes V1's `whsqNotified`/`osrNotified` fields" against the confirmed ADI definition (WHS Regulation s.608B(1), transcribed at `09` line 60):
1. An `Incident` `REVEALS` a `Hazard` whose `Risk` has `is_serious_risk = true` (column added `03-postgresql-schema.sql:383`) or whose `Consequence` has `flag_608b = true` (`03:197`) → `osr_notified` is forced out of any "not yet assessed" default, requiring explicit human determination before closure.
2. "Serious risk" is not numerically defined by the Regulation — operator-defined threshold, per the Guide §7.5 — matches the platform's existing `SafetyAssessment.serious_risk_threshold_note` design, not a gap.
3. The automated flag is never a substitute for human judgement (matches `04-ai-extraction-specification.md §6`'s critical-item override).

This is inference rule **R10** (`07` lines 84–88): trigger is `consequences.flag_608b = true` or a new `Incident` `REVEALS`-linked to a flagged `Hazard`/`Risk`; logic propagates a "notification assessment required" state onto `Incident.osr_notified`. **This rule only touches already-implemented Milestone 1 entities (`safety.risks.is_serious_risk`, `safety.risks`' consequences) and already-existing Incident columns — no schema change required to implement it.** `services/incidents/rules.py` is currently an empty R0 placeholder (§9). Whether R10 is in-scope for Milestone 3B implementation, or deferred (analogous to the standing "FARSI → Risk rating feedback loop" deferral, item 5 of the deferred-items list), is Decision Point D8 (§12) — not resolved here.

**Two items are pre-existing tracked gaps, cited not re-discovered:**
- `investigations.method` — `TO BE CONFIRMED` per `docs/knowledge-graph/README.md:34` ("not specified by any source read so far").
- The Schedule 18C sub-item number for "Incident management, investigation, reporting, improvement" (Guide §10.7) is unread/unconfirmed — `09 §5` row, table note "sub-item `TO_BE_CONFIRMED`... Guide §10.7 *(not yet read in full)*" — already tracked as risk **REG3** in `11-implementation-risk-register.md:55`.

---

## 8. Evidence / Provenance

`safety.evidence.linked_entity_type` (`03:279`) is polymorphic free-varchar with the schema's own inline comment listing `'incident'` as a valid value alongside `'hazard'`/`'control'`. This confirms the **data model** already supports attaching Evidence to an Incident (or, by the same mechanism, to an Investigation) with zero schema change. The **API surface** does not: only `/verification-activities/{id}/evidence` and `/competencies/{id}/evidence` exist (§4). Building `/incidents/{id}/evidence` (or `/investigations/{id}/evidence`) would be additive-only against the existing generic `Evidence`/`EvidenceInput` schema — same class of decision as D4 (§12).

---

## 9. Existing Scaffold / Implementation State

All Incident-domain files are unmodified R0 placeholders — no SQLAlchemy models exist yet for `Incident`/`Investigation`/`Action`/`Audit` in `apps/api/app/models/safety.py` (confirmed by listing every `class`/`__tablename__` in that file — it stops at `Evidence`, the last CCM entity).

| File | State |
|---|---|
| `apps/api/app/dto/incidents.py` | 3-line placeholder, no DTOs |
| `apps/api/app/routers/incidents.py` | Empty `APIRouter(prefix="/incidents", tags=["incidents"])`, no routes |
| `apps/api/app/repositories/incidents_repository.py` | 3-line placeholder |
| `apps/api/app/services/incidents/service.py`, `rules.py` | Placeholders; `rules.py` explicitly points at `06`/`07` (confirms R10, §7, is the intended home) |
| `apps/web/src/modules/incidents/*` | `types.ts` placeholder, `api.ts`/`routes.tsx` present but unexamined in depth (out of scope for a backend-schema-focused reconciliation; no reason to expect they diverge from the established Milestone 0–2 module pattern) |

This is a **greenfield domain**, same state CCM was in before Milestone 2A. `safety.persons` and `safety.assets` (both already implemented, Milestone 0) are available for resolving `reporter_person_id` and `asset_id` — the free-text `fReporter`/`fRideAsset` V1 fields need the same "resolve or create a Person/Asset record" pattern already established for CCM's Owner/Verified-By fields (Milestone 2A D2 precedent), not a new decision.

---

## 10. Field-Level Reconciliation Summary

| V1 field | Frozen schema home | OpenAPI | Status |
|---|---|---|---|
| `fDateTime` → `datetime` | `incidents.datetime` NOT NULL | required | CONFIRMED |
| `fType` → `incidentType` | `incidents.incident_type_concept_id` | optional, `ConceptRef` | GAP — no scheme (§6, D3) |
| `fSev` → `severity` | `incidents.severity` (1–5) | optional int | CONFIRMED |
| `fVrtpSeverity` | `incidents.vrtp_severity` | enum, exact match | RECONCILED |
| `fLocation`, `fReporter`(name), `fDesc`, `fInjuries`, `fWitnesses`, `fImmediate` | `location`, (see below), `description` NOT NULL, `injuries`, `witnesses`, `immediate_actions` | matching fields | CONFIRMED |
| `fReporter` (name) → person resolution | `incidents.reporter_person_id` (FK) | `reporter_person_id` uuid | RECONCILED — needs free-text→Person resolution, precedent exists (§9) |
| `fRideAsset` → asset resolution | `incidents.asset_id` (FK) | `asset_id` uuid | RECONCILED — needs free-text→Asset resolution, precedent exists (§9) |
| `fWhsq`, `fOsr` | `whsq_notified`, `osr_notified` | enum, exact match | RECONCILED (§7 for the business rule) |
| `fImmCause`, `fRootCause` | `incidents.immediate_cause`, `root_cause` | matching fields | CONFIRMED — these stay on `Incident`, not `Investigation` |
| `fInvStatus` | `incidents.investigation_status` | enum, exact match | RECONCILED |
| `fStatus` | `incidents.status` | enum, exact match | RECONCILED |
| `fCARs` (carRefs string) | `incident_actions` join table | none (§4) | RECONCILED at schema level, GAP at API level (D4) |
| `fStaffPresent`, `fPersonStatus`, `fReporterRole`, `fOtherNotes` | **none** | **none** | GAP (D7) |
| `fInvDate` (investigation completion date) | **none** (not on `incidents` or `investigations`) | none | GAP (D7) |
| `fLessons` (Lessons Learned) | **none** (not on `incidents` or `investigations`) | none | GAP (D7) |
| Investigation section as a whole (`findings`, `contributing_factors`, `method`) | `safety.investigations` table exists | **none** (D4) | GAP |

---

## 11. Gaps / Conflicts Summary

| # | Item | Class | Severity |
|---|---|---|---|
| 1 | `safety.investigations` has zero OpenAPI representation | GAP | Material — blocks any Investigation-record implementation without an additive API decision |
| 2 | `safety.incident_hazards` (`REVEALS`) has zero OpenAPI representation | GAP | Material |
| 3 | Incident/Investigation-scoped `Evidence` has zero OpenAPI representation | GAP | Material |
| 4 | `incident_type_concept_id`, `root_cause_category_concept_id` — no seeded ontology scheme | GAP | Non-blocking (nullable, optional) but must not be silently invented |
| 5 | Five V1 fields with no schema home (`lessonsLearned`, investigation completion date, `staffPresent`, `personStatus`, `reporterRole`, `otherNotes`) | GAP | Data-loss risk if V1 records are ever migrated; not a blocker for net-new records |
| 6 | `investigations.method` value domain | TO_BE_CONFIRMED (pre-existing) | Tracked, not new |
| 7 | Schedule 18C §10.7 sub-item number | TO_BE_CONFIRMED (pre-existing, REG3) | Tracked, not new |
| 8 | Whether R10 (608B propagation rule) is in-scope for 3B | DECISION REQUIRED | No schema change needed either way |
| 9 | Two candidate V1 source trees | RESOLVED (§1, §2.2) | Root suite confirmed authoritative; `OHS_Command_Centre` excluded |
| 10 | Incident↔Investigation↔Action structural shape | RESOLVED (§5) | Sibling model confirmed, not a chain |

---

## 12. Decision Points

| # | Decision | Evidence | Options | Recommended action | ADR/ACR required |
|---|---|---|---|---|---|
| D1 | Which V1 tree is canonical | Schema comment names root-suite files exactly (§1, §2.2) | (a) Root SMS suite only; (b) include `OHS_Command_Centre` as a secondary reference | **(a)** — matches the only citation that exists anywhere in the frozen baseline | No — evidence-based, not a fresh choice |
| D2 | Incident/Investigation/Action structural shape | Three independent sources converge on the sibling model, not a chain (§5) | (a) Adopt the sibling model as-is (Investigation 1:1 off Incident; Action shared/polymorphic, reachable from Incident or Audit); (b) build the intuitive Incident→Investigation→Action chain | **(a)** — the built, frozen reality; (b) would require new FKs (`investigation_id` on `actions`) not present in the schema | ADR recommended before 3B implementation begins, purely to make this explicit given how easily (b) could be assumed by default — same reasoning as CCM's D1 |
| D3 | Incident type / root-cause category ontology scheme | No scheme seeded anywhere; both FKs nullable/optional (§6) | (a) Defer, leave `NULL`, matching the standing `Hazard.category_concept_id` precedent; (b) invent a scheme now from V1's 6-value enum | **(a)** | ADR recommended to record the deferral, explicitly linked to the existing Hazard Taxonomy deferred item (not a separate open question) |
| D4 | Additive OpenAPI extension for `Investigation`, `incident_hazards`/`REVEALS`, and Incident-scoped `Evidence` | All three exist at schema/graph level with zero API surface (§4, §5, §8) | (a) Extend `10-openapi.yaml` additively (new schema objects + endpoints, no changes to existing paths/schemas, no new tables/columns) before or during 3B; (b) implement Incident/Action CRUD only in 3B and explicitly exclude Investigation/hazard-link/evidence sub-resources until the OpenAPI extension is separately authorized | Recommend **(a)** treated as a documentation-completion of an already-fully-specified table/relationship (no new architecture), but this is the one point in this pass that **does** touch a frozen baseline artefact (`10-openapi.yaml` itself) rather than only interpreting it — flagged for explicit authorization, not assumed | **ADR required regardless of (a)/(b)** — this is the one decision point in this pass with a real, non-trivial chance of needing to be treated as ACR-adjacent, since "frozen OpenAPI" has so far meant *no changes*, not *additive-only changes*. Recommend the user explicitly confirm whether additive-only OpenAPI extensions require the same ACR process as schema changes, or a lighter ADR-only path, before 3B scoping is finalized |
| D5 | Five V1 fields with no schema home | §10, §11 item 5 | (a) Don't port (documented, deliberate non-port, matches CCM D4/D5 precedent of deferring rather than silently adding columns); (b) add columns now (schema change → ACR) | **(a)** | ADR recommended to record the deliberate non-port, mirroring CCM's D5 treatment of the `reduce{}` mechanism |
| D6 | R10 (608B/OSR notification propagation rule) — in scope for 3B? | §7 | (a) Implement in 3B (no schema change needed, touches only existing Milestone 1 + this domain's columns); (b) defer, analogous to the FARSI feedback-loop deferral | Not resolved here — genuinely open, recommend the user decide at 3B scoping, not implied by this document | ADR either way, to record the scope call |
| D7 | Governance status of `09 §6`/`07 R10` for this domain | Same "DRAFT" boilerplate pattern as every knowledge-graph doc (per CCM D6 precedent) | (a) Treat as already-effectively-approved by precedent (Milestones 0–2 implemented against docs with identical boilerplate); (b) require explicit sign-off pass | **(b)**, mirroring CCM's D6 treatment for consistency | This reconciliation document, once reviewed, is intended to serve as the evidentiary record, consistent with the CCM precedent |

---

## 13. Required Findings Table (per authorization scope)

| Area | Finding |
|---|---|
| V1 | Root SMS suite (`incident-report.html`, `corrective-actions.html`, `sms-shared.js`) confirmed as sole canonical source by frozen-schema citation; `OHS_Command_Centre/incident_report.html` excluded, not cited anywhere in the baseline. Flat, single-record model — no client-side Investigation concept; investigation fields live directly on the incident record. §2 |
| Schema | `safety.incidents`, `incident_hazards`, `investigations`, `actions`, `action_controls`, `incident_actions` fully read and cited by line. Investigation is a 1:1 satellite (`incident_id UNIQUE`); Action is polymorphic/shared. §3 |
| OpenAPI | `/incidents`, `/incidents/{id}`, `/incidents/{id}/run-investigation-pipeline`, `/actions`, `/actions/{id}` exist. **No** `Investigation` schema/endpoint, **no** `incident_hazards`/`REVEALS` endpoint, **no** `/incidents/{id}/evidence`. §4 |
| Ontology | `incident_type_concept_id` and `root_cause_category_concept_id` have no seeded scheme — same open-question class as the standing Hazard Taxonomy deferral, not resolved here. §6 |
| Graph | `REVEALS` (Incident→Hazard N:N), `INVESTIGATED_AS` (Incident→Investigation 1:1), `TRIGGERS` (Incident\|AuditFinding→Action 1:N) — sibling structure, confirmed not a chain. §5 |
| Workflow | V1 status/investigation-status enums reconciled exactly against schema defaults and OpenAPI enums. No V1 or frozen-doc evidence of any state-machine enforcement (e.g., can't-close-while-Open-actions-exist) — none found, none assumed. |
| Evidence | Polymorphic `Evidence.linked_entity_type` schema-level supports `'incident'` by its own comment; zero API surface for it. §8 |
| Gaps | Investigation/incident_hazards/incident-evidence OpenAPI absence (material); 5 V1 fields with no schema home (data-fidelity); two ontology FKs with no scheme (non-blocking). §11 |
| Decisions | D1–D7, §12 — none require a schema change; D4 is the one point touching the frozen OpenAPI file itself and needs explicit authorization on process (ADR vs ACR-adjacent) before 3B scoping. |
| ADRs | Recommended for D2, D3, D4, D5, D6, D7 before 3B implementation begins, bundled the same way CCM's D2–D6 were bundled into one ADR. §14 |
| Implementation boundary | Incident CRUD and Action CRUD (as currently specified) are buildable with zero baseline change. Investigation, hazard-linking, and incident-scoped Evidence are **not** buildable until D4 is resolved. §14 |

---

## 14. Implementation Boundary — buildable without changing the frozen baseline

Buildable today, no schema/API change required:
- `GET/POST /incidents`, `GET/PATCH /incidents/{id}` — full `IncidentInput` field set (§4), including free-text→Person/Asset resolution for `reporter_person_id`/`asset_id` using the CCM-established pattern (§9)
- `GET/POST /actions`, `PATCH /actions/{id}` — polymorphic, usable from the Incident side via `source_type`/`source_id`
- `incident_actions`/`incident_hazards` join-table writes are possible at the persistence layer even without dedicated endpoints, if reached indirectly (e.g., as a side effect of an Incident update) — but exposing them as first-class API operations requires D4

**Not buildable without D4 (§12) resolved:**
- Any `Investigation` create/read/update surface (no schema object, no endpoint)
- Any dedicated hazard-linking endpoint for `REVEALS`
- Any incident-scoped Evidence endpoint

**Not buildable / explicitly out of scope regardless of D4:**
- `/incidents/{id}/run-investigation-pipeline` — depends on the AI Extraction domain, standing deferred item
- Anything from the Audit/AuditFinding domain — adjacent, shares `TRIGGERS`→Action, but not the subject of this pass; would need its own discovery/reconciliation pass if taken up next
- Porting the five fields in D5 unless/until that decision is revisited
- Committing R10 (§7, D6) to any particular scope

---

## 15. ADR/ACR Requirement

**No ACR is clearly required to begin any part of Milestone 3B** — every table, column, and relationship the recommended options rely on already exists in the frozen schema and Neo4j model. The one open question is **D4**, which is not a schema change but does touch the frozen `10-openapi.yaml` file itself (additive endpoints only) — this pass recommends but does not decide whether that requires ACR-equivalent process or a lighter ADR; that determination is itself part of what needs explicit authorization before 3B scoping.

**An ADR is recommended before implementation starts**, bundling D2, D3, D4 (process question), D5, D6, and D7 — mirroring the CCM Milestone 2A precedent exactly.

---

## Acceptance Criteria

- [x] Every field relied upon has an identified source — cited by file and line throughout §2–§4.
- [x] Incident/Investigation/Action structure evidenced, not assumed — §5, three independent converging sources, explicitly answering the critical-boundary instruction.
- [x] Regulatory/reportable-event requirements traced to source — §7 (WHS Regulation s.608B(1), R10, pre-existing REG3/README tracked items cited, not re-raised as new).
- [x] Ontology dependencies identified, none invented — §6.
- [x] Any schema/API mismatch explicitly documented — §4, §8, §11, §12 D4.
- [x] No code, schema, API, ontology, or Neo4j change was made — this document is the only artefact produced by this pass.
- [x] No architectural decision was silently made — every open point routed to §12 as a Decision Point awaiting explicit authorization; none resolved unilaterally in this document.
