# R1 Milestone 3B — Incident Decision Register (D1–D7)

**Status:** Governance-methodology output only. No application code, schema, migration, API, ontology, or Neo4j changes were made to produce this document. No ACR or ADR was raised — this document identifies which route each decision requires and recommends a position; it does not itself constitute an ACR, an ADR, or an approval. Authorized scope: decision-register pass only (chat authorization, R1 Milestone 3B, 2026-08-09).

## 1. Purpose and Authority

This document resolves the **governance pathway** — not the substance — of the seven decision points (D1–D7) surfaced by [18-r1-milestone-3a-incident-discovery-reconciliation.md](18-r1-milestone-3a-incident-discovery-reconciliation.md) (R1 Milestone 3A) and its subsequent review (3A §16). For each decision it records the evidence, the issue, the available options, the impact against Design Baseline v1.1, a clearly-marked recommendation, and — the deliverable this milestone actually exists to produce — the correct **governance route** (ACR / ADR / No Change / Defer) and **decision authority**.

Authorized by chat GO, R1 Milestone 3B, 2026-08-09: "discovery-to-governance only. No implementation authorisation is included in this GO." Every recommendation below is exactly that — a recommendation. None has been converted into a decision. None authorizes an ACR to be raised, an ADR to be written, or any schema/API/ontology/code change.

## 2. Source Baseline

- [18-r1-milestone-3a-incident-discovery-reconciliation.md](18-r1-milestone-3a-incident-discovery-reconciliation.md) — all evidence citations below trace back to this document's §1–§15, cross-referenced by section number.
- Design Baseline v1.1: `03-postgresql-schema.sql`, `10-openapi.yaml`, `02-neo4j-node-relationship-model.md`, `06-relationship-rules-catalogue.md`, `07-inference-rules-catalogue.md`, `09-regulatory-knowledge-model.md`, `ontology/schemes/`, `ontology/seed-concepts/`.
- Precedent for ACR/ADR routing discipline: [17-r1-milestone-2-ccm-discovery-reconciliation.md](17-r1-milestone-2-ccm-discovery-reconciliation.md) §7–§9 (D1–D6 for CCM), [14-architecture-change-requests.md](14-architecture-change-requests.md) (ACR-001/002/003 process and Board Approval Table), [.acr/README.md](../../.acr/README.md), [.adr/README.md](../../.adr/README.md).

## 3. Decision Methodology

Each decision below was tested against a single gate, per the routing rule this milestone was explicitly told to apply:

```text
Does the recommended option modify a Design Baseline v1.1 artefact
(03-postgresql-schema.sql, 10-openapi.yaml, 02-neo4j-node-relationship-model.md,
06/07/08/09/11-knowledge-graph docs, ontology schemes)?
                    │
            ┌───────┴────────┐
           YES                NO
            │                  │
            ▼                  ▼
        ACR path          Does it affect only implementation-time
      (Architecture         interpretation of an already-frozen
      Review Board)         artefact, with zero baseline edit?
                                       │
                              ┌────────┴────────┐
                             YES                NO (evidence alone
                              │                  resolves it — no
                              ▼                  fresh choice exists)
                          ADR path                    │
                       (Implementation                ▼
                        governance)              No Change / Defer
```

Additive-only and low-risk changes to a Design Baseline artefact still route to ACR — this was the explicit correction made at 3A Review (3A §16) and is applied consistently here, not just to D4.

Status values used: **Pending** (recommendation recorded, no governance authority has yet acted on it), **Resolved by evidence** (no fresh choice existed; already closed in 3A, carried here for completeness), **Approved**/**Rejected**/**Deferred** (not used in this document — none of D1–D7 have been acted on by a governance authority as of this pass).

---

## 4. D1–D7 Decision Register

### D1 — Canonical V1 source tree

| Field | Value |
|---|---|
| Finding | 3A §1, §2.2 |
| Evidence | `03-postgresql-schema.sql:511-512` comment names `incident-report.html`, `corrective-actions.html`, `audit-inspection.html` by filename as the V1 ported source. No frozen document anywhere references `OHS_Command_Centre/incident_report.html`. |
| Issue | Two structurally unrelated V1 candidate trees exist in the repository; which is authoritative for this domain. |
| Options | (a) Root SMS suite only; (b) treat `OHS_Command_Centre/incident_report.html` as a secondary/supplementary source. |
| Impact | None on Baseline, schema, API, ontology, graph, or workflow — this is a research-methodology question, not an architectural one. |
| Recommendation | **RECOMMENDATION — NOT DECISION:** (a), root SMS suite as sole V1 source; `OHS_Command_Centre` excluded from this domain's reconciliation. |
| Governance route | **No Change** — evidence resolves this without a formal governance instrument; not a fresh choice (matches 3A §12's own framing: "No — evidence-based, not a fresh choice"). |
| Decision authority | N/A |
| Status | **Resolved by evidence** (3A) — carried here for completeness, no further governance action required. |
| Traceability | 3A §1, §2.2. |

### D2 — Incident/Investigation/Action structural shape (sibling model, not a chain)

| Field | Value |
|---|---|
| Finding | 3A §5, §12 D2 |
| Evidence | Neo4j model `02-neo4j-node-relationship-model.md:110-112` (`REVEALS`/`INVESTIGATED_AS`/`TRIGGERS`); schema `03-postgresql-schema.sql:550` (`investigations.incident_id UNIQUE`, enforcing 1:1) and `:586-590` (`incident_actions` links Action directly to Incident — no `investigation_id` column exists anywhere on `safety.actions`); relationship rules `06-relationship-rules-catalogue.md:35-37`; V1 `incident-report.html` keeps investigation fields flat on the incident record with no separate object (3A §2.1). |
| Issue | Whether to formally record — and thus bind future implementation to — the sibling model, given how easily an implementer could default to the intuitive Incident→Investigation→Action chain instead (the exact risk the 3A authorization warned against). |
| Options | (a) Adopt/record the sibling model as-is; (b) build the linear chain (would require a new `investigation_id` FK on `safety.actions` — not present in the frozen schema). |
| Impact | **Baseline:** none — (a) matches the frozen schema/graph exactly, zero change; (b) would require a schema change. **Schema/API/Ontology/Graph:** no change under (a). **Workflow:** governs how the eventual implementation structures its service/router layer (Investigation as an Incident satellite; Action as a shared, polymorphic entity reachable from Incident or AuditFinding). |
| Recommendation | **RECOMMENDATION — NOT DECISION:** (a). |
| Governance route | **ADR** — implementation-time interpretation of an already-frozen structure; option (a) alters no baseline artefact. |
| Decision authority | Implementation governance (does not require Architecture Review Board, since no baseline artefact changes under the recommended option). |
| Status | **Accepted (2026-08-09)** — [ADR-003](../../.adr/ADR-003-incident-investigation-action-sibling-structure.md). |
| Traceability | 3A §5, §12 D2. **Feeds D4** — see §5 dependency matrix. Resolved by [ADR-003](../../.adr/ADR-003-incident-investigation-action-sibling-structure.md), which is now the confirmed architectural basis for D4's not-yet-raised ACR. |

### D3 — Ontology scheme deferral (`incident_type_concept_id`, `root_cause_category_concept_id`)

| Field | Value |
|---|---|
| Finding | 3A §6, §12 D3 |
| Evidence | `ontology/schemes/` is empty; `ontology/seed-concepts/` holds only `consequence-domains.yaml`, `control-hierarchy.yaml`, `energy-sources.yaml`. Both FKs are nullable in schema (`03:519`, `03:565`) and optional in OpenAPI (`IncidentInput`/`ActionInput` `required` lists, `10-openapi.yaml:1089`, `:1116`). Precedent: `Hazard.category_concept_id` (`03:155`) left `NULL`, same deferred-item class (standing deferred item, pre-dates this milestone). |
| Issue | Whether to seed a new ontology scheme now from V1's flat 6-value `incidentType` enum (Injury/Near Miss/Property Damage/Environmental/Security/Other) — noting V1 has no root-cause-category concept at all, only free-text Immediate Cause/Root Cause fields — or defer, matching the Hazard Taxonomy precedent. |
| Options | (a) Defer, leave `NULL`, matching Hazard Taxonomy precedent; (b) seed a scheme now, mapped from V1's flat enum. |
| Impact | **Baseline:** none either way — both columns already exist, already nullable. **Ontology:** (b) would add new `ontology.schemes`/`ontology.concepts` rows — data seeding, not a structural schema change, but exactly the "invent a scheme" move the project's standing discipline prohibits absent an explicit, separately-authorized V1-grounded mapping decision. **API/Graph/Workflow:** unaffected either way — fields stay optional under (a). |
| Recommendation | **RECOMMENDATION — NOT DECISION:** (a) — defer, explicitly treated as the same open question as the standing Hazard Taxonomy deferral, not a second independent one. |
| Governance route | **ADR** to record the deferral (no baseline artefact changes under (a) — the columns already exist and are already nullable). If a scheme is ever proposed, that seeding activity gets its own governance assessment at that time — not pre-decided here. |
| Decision authority | Implementation governance, consistent with how the Hazard Taxonomy deferral has been handled to date. |
| Status | **Accepted (2026-08-12)** — [ADR-004](../../.adr/ADR-004-incident-ontology-scheme-deferral.md). |
| Traceability | 3A §6, §12 D3; linked to the standing deferred item "Hazard Taxonomy ontology scheme (needs ADR)." Resolved by [ADR-004](../../.adr/ADR-004-incident-ontology-scheme-deferral.md). |

### D4 — OpenAPI extension for `Investigation`, `incident_hazards`/`REVEALS`, and incident-scoped `Evidence`

| Field | Value |
|---|---|
| Finding | 3A §4, §8, §12 D4; corrected at 3A Review, 2026-08-08 (3A §16). |
| Evidence | Exhaustive search of `10-openapi.yaml` shows zero `Investigation` schema object or endpoint; no `incident_hazards`/`REVEALS` endpoint; no `/incidents/{id}/evidence` (only `/verification-activities/{id}/evidence:502` and `/competencies/{id}/evidence:822` exist). `safety.investigations` (`03:548-558`) and `safety.incident_hazards` (`03:542-546`) are fully specified in the frozen schema; `REVEALS`/`INVESTIGATED_AS` are fully specified in the Neo4j model (`02:110-111`). |
| Issue | Three artefacts (`safety.investigations`, `safety.incident_hazards`, incident-scoped `Evidence`) exist in the frozen schema/graph but have no REST surface — they cannot be exposed by implementation without adding to `10-openapi.yaml`, a named Design Baseline v1.1 artefact. |
| Options | (a) Extend `10-openapi.yaml` additively — new schema objects and endpoints only, no changes to any existing path, schema, table, or column; (b) implement Incident/Action CRUD only, explicitly excluding Investigation/hazard-link/evidence sub-resources until the extension is separately authorized. |
| Impact | **Baseline: YES** — modifies a named Design Baseline v1.1 artefact (`10-openapi.yaml`) under option (a). **Schema/Ontology:** none. **Graph:** none (already fully specified there — the extension only exposes what the graph model already describes). **Workflow:** determines whether the next implementation phase can expose Investigation records, hazard-linking, or incident-scoped Evidence at all. |
| Recommendation | **RECOMMENDATION — NOT DECISION:** (a), pursued via ACR. |
| Governance route | **ACR** — resolved at 3A Review: OpenAPI is a controlled Design Baseline artefact ([02-development-standards.md](02-development-standards.md) §7); additive-only and low-risk does not exempt a change to it from the ACR process. |
| Decision authority | Architecture Review Board (ACR-001/002/003 precedent). |
| Status | **Approved (2026-08-11) and implemented, contract only** — [ACR-004](../../.acr/ACR-004-incident-openapi-extension.md), raised 2026-08-09, approved 2026-08-11, `10-openapi.yaml` additively extended and validated the same day (Option A for the hazard-link shape). Contract change only — no application code written; a separate GO is still required before any implementation against these endpoints (ACR-004 §17–§18). |
| Traceability | 3A §4, §8, §12 D4; 3A Review disposition (3A §16). **Depends on D2** being recorded first — see §5 dependency matrix. |

### D5 — Six orphan V1 fields (corrected from "five" — see below), per-field disposition

**Correction:** [18](18-r1-milestone-3a-incident-discovery-reconciliation.md) §1/§11/§12 and this document originally labeled this "Five V1 fields," though every cited evidence row and 18's own §10 text ("none of the six match any existing column") always listed six. [ADR-005](../../.adr/ADR-005-incident-orphan-v1-fields-disposition.md) reconciles all six individually rather than perpetuating the mismatched count.

| Field | Value |
|---|---|
| Finding | 3A §10, §11 item 5, §12 D5 |
| Evidence | V1 `incident-report.html` fields: `fLessons` (line 109, Lessons Learned), `fInvDate` (line 108, investigation completion date), `fStaffPresent` (line 95), `fPersonStatus` (line 96), `fReporterRole` (line 99), `fOtherNotes` (line 100). Exhaustive column listing of `safety.incidents` (`03:515-537`) and `safety.investigations` (`03:548-558`) — none of the six match any existing column *by that exact name*, but see per-field disposition below — one resolves through a linked entity. |
| Issue | Whether each V1 field should be silently dropped, mapped to an existing canonical entity/property, or given a new column. |
| Per-field disposition | **`fReporterRole`** — **represented through the existing model**, not a gap: `incidents.reporter_person_id` (`03:524`) → `safety.persons.role_title` (`03:114`, already an implemented SQLAlchemy column, `apps/api/app/models/safety.py:54`; already in `10-openapi.yaml` as `Person.role_title`). **`fStaffPresent`** — no canonical mapping (inherently a list of people, no join table exists); deferred. **`fPersonStatus`** — distinct V1 concept from `injuries` (V1 captures both separately); no canonical mapping; deferred. **`fOtherNotes`** — V1's own placeholder text marks it as non-duplicative of `witnesses`; no canonical mapping; deferred. **`fInvDate`** (investigation completion date) — checked specifically against ACR-004's now-implemented `Investigation` schema; that schema mirrors `safety.investigations`' existing columns exactly and has no completion-date column to expose; deferred. **`fLessons`** (Lessons Learned) — distinct in kind (forward/preventive) from `investigations.findings`/`.contributing_factors` (backward/causal); no canonical mapping; deferred. |
| Options (for the five genuinely-deferred fields) | (a) Don't port — documented, deliberate non-port; (b) add new columns. |
| Impact | **Baseline:** (b) would modify `03-postgresql-schema.sql`, a Design Baseline artefact. **(a):** no baseline impact for the five deferred fields; `fReporterRole` requires no schema change either — it already has a home. Deferring the five leaves a documented data-fidelity gap relative to full V1 field parity — stays documented, not silently accepted as complete parity. |
| Recommendation | **RECOMMENDATION — NOT DECISION, now Accepted:** (a) for the five genuinely-orphan fields, mirroring the CCM Milestone 2A D4/D5 precedent; `fReporterRole` requires no non-port decision at all. |
| Governance route | **ADR** — [ADR-005](../../.adr/ADR-005-incident-orphan-v1-fields-disposition.md), Accepted 2026-08-12. No baseline change. **ACR required only if a new column is later pursued for one of the five deferred fields** — none is proposed by ADR-005. |
| Decision authority | Implementation governance. |
| Status | **Accepted (2026-08-12)** — [ADR-005](../../.adr/ADR-005-incident-orphan-v1-fields-disposition.md). |
| Traceability | 3A §10, §11, §12 D5. Resolved by [ADR-005](../../.adr/ADR-005-incident-orphan-v1-fields-disposition.md), which also checked D4/ACR-004's implemented `Investigation` schema specifically for `fInvDate`/`fLessons` and found it did not change their disposition. |

### D6 — R10 (608B/OSR notification propagation rule) — in scope for the next implementation phase?

| Field | Value |
|---|---|
| Finding | 3A §7, §12 D6 |
| Evidence | `09-regulatory-knowledge-model.md §6` formalizes `whsq_notified`/`osr_notified` against WHS Regulation s.608B(1); `07-inference-rules-catalogue.md` R10 (lines 84–88). Touches only already-implemented Milestone 1 columns (`safety.risks.is_serious_risk`, `03:383`; `Consequence.flag_608b`, `03:197`) plus already-existing Incident columns. `apps/api/app/services/incidents/rules.py` is currently an empty R0 placeholder pointing at `06`/`07`. |
| Issue | Whether implementing R10 belongs in the next Incident implementation scope, or is deferred — analogous to the standing "FARSI → Risk rating feedback loop" deferred item. |
| Options | (a) Implement in the next Incident implementation scope (no schema/API/ontology change needed — service-layer logic only, over already-existing columns); (b) defer. |
| Impact | **Baseline:** none either way. **Workflow:** determines whether automated `osr_notified` propagation exists in the first Incident release or remains a manually-set field until a later one. This concerns a **statutory notification trigger** (WHS Regulation s.608B(1)), not a pure engineering tradeoff. |
| Recommendation | Formally deferred, then substantively resolved — [ADR-006](../../.adr/ADR-006-incident-notification-rule-formal-defer.md) §9: `whsq_notified` = internal notification; R10 extended to cover general WHS Act incident categories (not Chapter-9A-only); Safety Systems Manager as responsible notifier; 48hr timeframe; 10yr evidence retention; V1 rule confirmed still current. **"OSR" meaning left unanswered** — `osr_notified`/R10's existing Chapter-9A behaviour explicitly untouched, carried forward as a residual open item (ADR-006 §11). |
| Governance route | **ADR** — [ADR-006](../../.adr/ADR-006-incident-notification-rule-formal-defer.md), **Resolved 2026-08-12** (deferred, then resolved same day). **ADR-006 §10 concludes an ACR is required** before R10's definition in `07-inference-rules-catalogue.md` (a Design Baseline v1.1 artefact) can actually be extended, and before any new trigger-flag column the extension likely needs (mirroring `is_serious_risk`/`flag_608b` for the general WHS Act test) is added. **That ACR has not been raised.** |
| Decision authority | Determination recorded from the project sponsor/governance authority in chat (2026-08-12) — same authority pattern as ACR-002/003/004 and D2/D7's acceptance, not independently sourced from a separately-documented Compliance/Legal function. Recorded as such, not relabeled — see ADR-006's provenance note. |
| Status | **Resolved (2026-08-12), scope decided; ACR approved.** [ACR-005](../../.acr/ACR-005-incident-general-notifiable-incident-rule.md), raised and **Approved 2026-08-12** — approval is a governance act only, not itself implementation authorization; the four artefacts in ACR-005 §5 remain unedited pending a separate GO. `osr_notified`/"OSR" meaning: **`TO_BE_CONFIRMED`** (ADR-006 §11 — one candidate, "Office of State Revenue," checked and ruled out 2026-08-12; not to be renamed or reinterpreted by inference), out of ACR-005's scope. |
| Traceability | 3A §7, §12 D6; [20-r1-milestone-3c-d6-notification-evidence-matrix.md](20-r1-milestone-3c-d6-notification-evidence-matrix.md) (evidence); [ADR-006](../../.adr/ADR-006-incident-notification-rule-formal-defer.md) (formal defer, then resolution + ACR assessment); [ACR-005](../../.acr/ACR-005-incident-general-notifiable-incident-rule.md) (raised ACR). |

### D7 — Governance status of `09 §6` / `07 R10` for the Incident domain

| Field | Value |
|---|---|
| Finding | 3A §12 D7 (CCM D6 precedent, `17-r1-milestone-2-ccm-discovery-reconciliation.md` §6f, §7 D6) |
| Evidence | `09-regulatory-knowledge-model.md` and `07-inference-rules-catalogue.md` both carry the same "DRAFT — controlled design document. Requires approval before implementation" boilerplate as every knowledge-graph document (`09:2`). Milestones 0–2 already implemented against docs carrying identical boilerplate without treating it as a blocker (CCM D6 precedent). `09 §6`/`07 R10`'s Incident-specific content was never explicitly listed in the v1.1 Board Approval Table (`14-architecture-change-requests.md`). |
| Issue | Whether `09 §6`/`07 R10`'s Incident-specific content is already effectively approved by precedent, or needs an explicit sign-off pass — mirroring ACR-001/002/003 — before it can be relied on to resolve D6. |
| Options | (a) Treat as already-effectively-approved by precedent; (b) require an explicit sign-off pass, closing the process gap after the fact — same treatment as CCM D6. |
| Impact | **Baseline:** none — no content changes are proposed to `09`/`07` themselves. Procedural only. |
| Recommendation | **RECOMMENDATION — NOT DECISION:** (b), consistent with the CCM D6 treatment. |
| Governance route | **No formal ACR/ADR instrument required** — recommend that this decision register, once reviewed and explicitly signed off, itself serves as the evidentiary sign-off record for `09 §6`/`07 R10`'s Incident-domain content, the same treatment CCM D6 proposed for `08`. |
| Decision authority | Whoever holds sign-off authority over knowledge-graph document content generally (the same authority that reviewed 3A). |
| Status | **Accepted (2026-08-09)** — governance authority confirmed this register serves as the evidentiary sign-off record for `09 §6`/`07 R10`'s Incident-domain content; option (b) treated as satisfied by that acceptance. |
| Traceability | 3A §12 D7; CCM precedent `17-r1-milestone-2-ccm-discovery-reconciliation.md` §6f, §7 D6. **Blocks D6** — dependency satisfied; D6 itself formally deferred via [ADR-006](../../.adr/ADR-006-incident-notification-rule-formal-defer.md), substance still open — see §5. |

---

## 5. Cross-Decision Dependency Matrix

| Decision | Depends on | Reason | Effect on resolution order |
|---|---|---|---|
| D1 | — | Already resolved by evidence | No ordering constraint |
| D2 | — | Self-contained; evidenced directly from schema/graph/V1, no dependency on any other decision. **Resolved — [ADR-003](../../.adr/ADR-003-incident-investigation-action-sibling-structure.md), Accepted 2026-08-09.** | Resolved first among the still-open items, as recommended |
| D3 | — | Independent of every other decision — a separate ontology axis untouched by the OpenAPI/structural questions. **Resolved — [ADR-004](../../.adr/ADR-004-incident-ontology-scheme-deferral.md), Accepted 2026-08-12.** | Resolved, no ordering constraint applied |
| D4 | **D2** | The ACR for D4 should propose endpoint shapes consistent with the confirmed sibling structure (D2), not re-litigate Incident/Investigation/Action's shape mid-ACR. **D2 now recorded ([ADR-003](../../.adr/ADR-003-incident-investigation-action-sibling-structure.md)) — dependency satisfied.** | D4's ACR may now be drafted on D2's basis, once separately authorized — not authorized by this document |
| D5 | — | Independent — concerns different columns/tables (`incidents`/`investigations` field-level parity) untouched by D2/D3/D4. **Resolved — [ADR-005](../../.adr/ADR-005-incident-orphan-v1-fields-disposition.md), Accepted 2026-08-12** (its own field-level check against D4/ACR-004's `Investigation` schema found no interaction requiring reordering) | Resolved, no ordering constraint applied |
| D6 | **D7** | D6's recommended-in-scope option (a) relies on `09 §6`/R10 as its evidentiary basis; implementing a statutory-notification-trigger rule against a document still nominally "DRAFT" carries more compliance risk than implementing against one whose Incident-domain content has been explicitly signed off. **D7 accepted — dependency satisfied. D6 resolved via [ADR-006](../../.adr/ADR-006-incident-notification-rule-formal-defer.md); [ACR-005](../../.acr/ACR-005-incident-general-notifiable-incident-rule.md) raised and Approved 2026-08-12, not yet incorporated. OSR/`osr_notified` residual open.** | Closed (resolved, ACR approved, not incorporated) |
| D7 | — | Self-contained procedural question about existing document status. **Resolved — accepted by governance authority, 2026-08-09.** | Resolved, unblocking D6 |

**Resolution order as executed:** D1 (closed) → D7 (accepted) → D2 (**Accepted, ADR-003**) → D4 (**Approved + contract-implemented, ACR-004**) → D3 (**Accepted, ADR-004**) → D5 (**Accepted, ADR-005**) → **D6** (**Deferred then Resolved, ADR-006**; **[ACR-005](../../.acr/ACR-005-incident-general-notifiable-incident-rule.md) raised and Approved 2026-08-12, not yet incorporated**; OSR/`osr_notified` residual open). **All seven decision points now have a recorded disposition; D6's follow-on ACR is approved but its four artefacts remain unedited pending a separate implementation GO.**

---

## 6. ACR/ADR Routing Summary

| Decision | Route | Rationale (one line) |
|---|---|---|
| D1 | No Change | Evidence-resolved, no baseline artefact touched |
| D2 | ADR | Interpretation of an already-frozen structure; zero baseline edit — **[ADR-003](../../.adr/ADR-003-incident-investigation-action-sibling-structure.md), Accepted 2026-08-09** |
| D3 | ADR | Records a deferral; no baseline edit (columns already nullable/exist) — **[ADR-004](../../.adr/ADR-004-incident-ontology-scheme-deferral.md), Accepted 2026-08-12** |
| D4 | **ACR** | Modifies `10-openapi.yaml`, a named Design Baseline v1.1 artefact — additive-only does not exempt it |
| D5 | ADR (for the recommended non-port option); ACR only if new columns are later pursued | Recommended option (a) touches no baseline artefact — **[ADR-005](../../.adr/ADR-005-incident-orphan-v1-fields-disposition.md), Accepted 2026-08-12; no ACR raised** |
| D6 | ADR (scope decision) — **[ADR-006](../../.adr/ADR-006-incident-notification-rule-formal-defer.md), Resolved 2026-08-12** — plus **[ACR-005](../../.acr/ACR-005-incident-general-notifiable-incident-rule.md), raised 2026-08-12, Approved 2026-08-12, incorporated 2026-08-15** | Scope resolved; extending `07-inference-rules-catalogue.md` (new rule R23, not an edit to R10) plus a new `incidents.is_notifiable_incident` column is a Design Baseline artefact change requiring ACR, same class as D4/`10-openapi.yaml` |
| D7 | No formal ACR/ADR — this register serves as the evidentiary sign-off record | Procedural governance-status question, not a content change — **Accepted 2026-08-09** |

**Two ACRs are now implicated:** D4 — [ACR-004](../../.acr/ACR-004-incident-openapi-extension.md), **Approved and contract-implemented 2026-08-11**. D6 — [ACR-005](../../.acr/ACR-005-incident-general-notifiable-incident-rule.md), raised and **Approved 2026-08-12**, **incorporated 2026-08-15** (its four artefacts additively extended per a separate GO — same gap ACR-004 had between approval and implementation, now closed the same way). **No ACR was required or raised for D2, D3, or D5 — all resolved via ADR only.**

*(Addendum, 2026-08-15: ACR-005 incorporation record above supersedes the "not yet incorporated" framing this register originally carried as of its 2026-08-12 authoring — see [.acr/README.md](../../.acr/README.md) and [12-deliverables-index.md](12-deliverables-index.md) for the current disposition.)*

---

## 7. Implementation Implications

None of D1–D7's *pending* status blocks basic Incident/Action CRUD as already specified in the frozen OpenAPI contract (3A §14) — this was true before this register and remains true after it; nothing in this pass changes that boundary. Specifically:

- D3's ontology gap (now resolved, deferred per ADR-004) does not block Incident/Action CRUD (`incident_type`/`root_cause_category` are optional fields) — unchanged conclusion, now formally recorded rather than merely observed.
- D5's field gaps (now resolved, five deferred per ADR-005; `fReporterRole` was never a gap) do not block CRUD — unchanged conclusion, now formally recorded.
- D6's rule (scope resolved per ADR-006, ACR-005 approved 2026-08-12) is service-layer logic layered on top of CRUD, not a precondition for it — Investigation, hazard-linking, and incident-Evidence (all ACR-004) proceed unaffected; only automated notification-propagation logic (both the resolved `whsq_notified` scope and the still-open `osr_notified`/OSR question) is blocked, pending a separate implementation GO for ACR-005's four artefacts.
- D2 (now recorded, ADR-003) and D7 (now accepted) governed internal structure and document status respectively, not API availability — their resolution changes nothing about the CRUD boundary either.
- **D4 blocks only the Investigation / hazard-linking / incident-Evidence sub-resources specifically** — it does not block Incident or Action CRUD.

This is stated for completeness, carried forward from 3A §14 — **it is not a re-authorization to build anything.** No implementation GO has been issued for any part of this domain; this milestone's authorization is explicitly "discovery-to-governance only."

---

## 8. Outstanding Governance Decisions

- **D4** — [ACR-004](../../.acr/ACR-004-incident-openapi-extension.md), drafted against ADR-003, raised 2026-08-09, **Approved and contract-implemented 2026-08-11**. Investigation/hazard-linking/incident-Evidence are now exposed in `10-openapi.yaml` (v0.3.0-draft, validated: 0 dangling `$ref`s, strictly additive diff). §14(b) resolved same day: **Option A** (bare reference list) chosen for the hazard-link shape — `incident_hazards` has no columns beyond its composite key, and no join table anywhere in the frozen contract is exposed as a first-class resource. Application-code implementation against these endpoints remains a separate, not-yet-authorized gate.
- ~~D3~~ — **Resolved.** [ADR-004](../../.adr/ADR-004-incident-ontology-scheme-deferral.md), Accepted 2026-08-12.
- ~~D5~~ — **Resolved.** [ADR-005](../../.adr/ADR-005-incident-orphan-v1-fields-disposition.md), Accepted 2026-08-12.
- ~~D6~~ — **Resolved (scope), ACR approved, not yet incorporated.** [ADR-006](../../.adr/ADR-006-incident-notification-rule-formal-defer.md) — deferred 2026-08-12, resolved same day: `whsq_notified` = internal, R10's scope-equivalent extended to general WHS Act categories via a new rule, Safety Systems Manager/48hr/10yr. **[ACR-005](../../.acr/ACR-005-incident-general-notifiable-incident-rule.md) raised and Approved 2026-08-12** — its four artefacts (`03-postgresql-schema.sql`, `10-openapi.yaml`, `02-neo4j-node-relationship-model.md`, `07-inference-rules-catalogue.md`) remain unedited pending a separate implementation GO. `osr_notified`/"OSR" meaning: **`TO_BE_CONFIRMED`** — "Office of State Revenue" checked and ruled out (2026-08-12) as not fitting this WHS/amusement-park context; the field is explicitly untouched, not renamed, not reinterpreted; residual open item (ADR-006 §11), out of ACR-005's scope.
- ~~D7~~ — **Resolved.** Governance authority accepted this register as the evidentiary sign-off record, 2026-08-09.
- ~~D2~~ — **Resolved.** [ADR-003](../../.adr/ADR-003-incident-investigation-action-sibling-structure.md), Accepted 2026-08-09.
- **All seven decision points now have a recorded governance disposition.** D1 (evidence-resolved), D2 ([ADR-003](../../.adr/ADR-003-incident-investigation-action-sibling-structure.md)), D3 ([ADR-004](../../.adr/ADR-004-incident-ontology-scheme-deferral.md)), D4 ([ACR-004](../../.acr/ACR-004-incident-openapi-extension.md), Approved + contract-implemented), D5 ([ADR-005](../../.adr/ADR-005-incident-orphan-v1-fields-disposition.md)), D6 ([ADR-006](../../.adr/ADR-006-incident-notification-rule-formal-defer.md), resolved, with [ACR-005](../../.acr/ACR-005-incident-general-notifiable-incident-rule.md) Approved), D7 (accepted). **D6 has the only item with unfinished follow-through** — ACR-005 approved but not incorporated, plus a residual "OSR" question outside its scope. None of D2–D5's resolutions authorize any application-code implementation — that remains a separate gate.

---

## 9. R1 Milestone 3B Exit Criteria

- [x] All seven 3A decision points (D1–D7) have a recorded evidence trail, issue statement, options set, impact assessment, and a recommendation explicitly marked as a recommendation, not a decision.
- [x] Governance route (ACR / ADR / No Change / Defer) assigned to each decision, per the gate in §3.
- [x] Cross-decision dependencies identified and a resolution order documented (§5) rather than resolving decisions independently of each other.
- [x] D4 confirmed routed to ACR, consistent with the 3A Review correction — not weakened because the change is additive.
- [x] No ACR, ADR, schema change, API change, ontology change, or implementation change was made in producing this document.
- [ ] Document reviewed and an explicit disposition recorded by the governance authority — **not yet done; pending, same pattern as 3A.**
- [ ] CI green on the registering PR — to be confirmed after push (§10 of this report cycle).

3B is **not** closed until the unchecked items above are satisfied by the governance authority's review, separate from this document's production.

---

## 10. Traceability to Milestone 3A

| This document | Milestone 3A source |
|---|---|
| §4 D1 | 3A §1, §2.2 |
| §4 D2 | 3A §5, §12 D2 |
| §4 D3 | 3A §6, §12 D3 |
| §4 D4 | 3A §4, §8, §12 D4; 3A §16 (Review correction) |
| §4 D5 | 3A §10, §11 item 5, §12 D5 |
| §4 D6 | 3A §7, §12 D6; [20-r1-milestone-3c-d6-notification-evidence-matrix.md](20-r1-milestone-3c-d6-notification-evidence-matrix.md); [ADR-006](../../.adr/ADR-006-incident-notification-rule-formal-defer.md); [ACR-005](../../.acr/ACR-005-incident-general-notifiable-incident-rule.md) |
| §4 D7 | 3A §12 D7 |
| §5 | Not present in 3A — new analysis performed at 3B per the GO's explicit "check for dependencies" requirement |
| §6 | Consolidates 3A §15 and the 3A §16 correction into a single routing table |

---

## Acceptance Criteria

- [x] Every decision traces to a specific 3A finding with file/line evidence — no new evidence gathered or fabricated in this pass.
- [x] Every recommendation is explicitly labeled "RECOMMENDATION — NOT DECISION."
- [x] Governance route assigned using the single stated gate (§3), applied consistently — including to D4, where additive/low-risk did not change the outcome.
- [x] Cross-decision dependencies (D2→D4, D7→D6) identified and a resolution order proposed, not left implicit.
- [x] No decision was silently resolved; no ACR or ADR was raised; no baseline/code/schema/API/ontology change was made.
- [x] V1 behaviour, frozen architecture, and proposed future implementation kept distinct throughout (see each decision's Evidence vs. Options vs. Impact rows).
