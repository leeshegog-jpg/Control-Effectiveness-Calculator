# Regulatory Knowledge Model
**Status: DRAFT — controlled design document. Requires approval before implementation.**
**Parent:** [01-enterprise-knowledge-graph-specification.md](01-enterprise-knowledge-graph-specification.md)
**Schema:** [03-postgresql-schema.sql](03-postgresql-schema.sql) `regulatory.requirements`
**Revision note (2026-08-03):** Substantially rewritten after direct reading of the *Guide for major amusement parks: Preparing a safety case* (WHSQ, 2021, 53pp) — previously this document only had WHS Act/Reg full text to work from and left Chapter 9A structure largely `TO_BE_CONFIRMED`. Citations below are transcribed from the Guide's own footnotes, which cite the WHS Regulation section numbers directly — this is now a confirmed regulatory structure, not an inferred one. See [11-safety-case-demonstration-model.md](11-safety-case-demonstration-model.md) §0 for what was and wasn't independently verified.
**Revision note 2 (same day):** You provided **Schedule 18B** (Amusement Device Emergency Plan) directly — full text read (§2, §5a below) — and corrected an error the Phase 2.1 Implementation Blueprint had propagated: **Schedule 19 is the Dictionary, not a device-specific schedule, and there is no "Schedule 19C."** Corrected throughout this document and cascaded to the implementation-blueprint set. I attempted to independently fetch the Schedule 19 text from the `legislation.qld.gov.au` URL you provided — WebFetch failed this session (tool infrastructure issue, same failure mode as the earlier WebSearch outage, not a refusal) — so the exact "amusement device" definition text in Schedule 19 (Dictionary) is still `TO_BE_CONFIRMED` verbatim, even though its *location* (Dictionary, not a standalone device schedule) is now confirmed from you directly.

---

## 1. Purpose

Structures the "Regulatory ontology" scheme referenced throughout ([03-postgresql-schema.sql](03-postgresql-schema.sql), [06-relationship-rules-catalogue.md](06-relationship-rules-catalogue.md)) so that every SMS section, control, and Safety Case claim can cite a specific obligation — the requirement stated in your original brief ("each SMS section must link to an ISO 45001 clause, WHS requirement, and evidence source") and the platform's core traceability chain (`SafetyCaseClaim -[TRACES_TO]-> Requirement`).

## 2. Source Availability — what's actually confirmable today

| Source | Status | Where |
|---|---|---|
| **WHS Act 2011 (Qld)** | Full text available | `WHS Act 2011.md` — already in your local clone (uncommitted) |
| **WHS Regulation 2011 (Qld)**, incl. Chapter 9A Major Amusement Parks, Schedule 18C, Schedule 19 (Dictionary) | Full text available | `WHS Reg 2011.md` — already in your local clone |
| **Schedule 18B — Matters to be included in amusement device emergency plan for major amusement parks (s.608N)** | **Confirmed — read in full this session.** 2 pages, 5 numbered parts (Workplace hazard and detail; Command structure and workplace personnel; Notifications; Resources and equipment; Procedures) | `D:\OneDrive - Village Roadshow Limited\06_IOS_ASNZS_Standards\WHS Reg 2011\WHS Reg 2011 18B Emergencey Plan.pdf` — full breakdown in §5a below |
| **Schedule 19 — Dictionary** | Confirmed **by you directly** to be the Dictionary schedule (defined terms), not a device-specific schedule — corrects an earlier assumption in this document that implied otherwise. The "amusement device" defined term is understood to live here (per the Guide's own footnote 18, "See Schedule 19... for the full definition including exclusions"), consistent with a dictionary schedule housing defined terms — **but the exact definition text has not been independently fetched** (WebFetch to `legislation.qld.gov.au` failed this session — tool infrastructure issue) | `https://www.legislation.qld.gov.au/view/html/inforce/current/sl-2011-0240` (provided by you) — verbatim text still `TO_BE_CONFIRMED` |
| **Guide for major amusement parks: Preparing a safety case (WHSQ, 2021)** | **Read directly, in full, this session** — 53 pages, sections 7–11 read in full text, section 8/12/appendices read in part | `D:\OneDrive - Village Roadshow Limited\06_IOS_ASNZS_Standards\WHS Reg 2011\Guide for major amusement parks Safety Case 2021.pdf` (Creative Commons Attribution 4.0 — State of Queensland, so reproducible, unlike the standards below) |
| **Guide for Developing Major Amusement Parks Safety Case Outline** | **Not yet read** — you provided this file this session; only the main 2021 Guide was reviewed. Recommend reading before this document is finalized, since §7.2 of the main Guide says the safety case must follow this outline | `D:\OneDrive - Village Roadshow Limited\06_IOS_ASNZS_Standards\WHS Reg 2011\Guide for Developing Major Amusement Parks Safety Case Outline.pdf` |
| **ICMM Critical Control Management — Practical Guide** | **Not yet read** — provided this session, not yet reviewed against `CRITICAL_RISK_MANAGEMENT_BRIEFING.md`'s existing ICMM citations | `D:\OneDrive - Village Roadshow Limited\01_Corporate OHS SMS\04_Standards\Managing Risks to Health and Safety Standard\ICMM Critical Control Management - Practical Gudie.pdf` |
| **ISO 31000:2018 Risk Management — Guidelines** | Full text available locally; Guide itself cross-references it directly (§9, Part 6: 6.3 Setting the scope, 6.4 Risk assessment, 6.5 Risk treatment — "similar" to the Chapter 9A safety assessment process) | `ISO 31000 -2018 Risk management - Guidelines.md` |
| **ISO 45001:2018 OHS Management Systems** | **Not present locally.** Not cited by the Guide either (the Guide's own governance/audit structure is Schedule 18C-driven, not ISO-45001-clause-driven — see §5). | `TO BE CONFIRMED` if a clause-level mapping is still wanted for internal ISO 45001 conformance purposes, separate from the Chapter 9A safety case itself |
| **AS/NZS 3533.1-2009 Amusement Rides and Devices — Design and Construction** | **Not present locally**, but the Guide cites a specific clause directly: **§2.1** defines the amusement device "class" required in the safety case (§8.3 of the Guide) | `TO BE CONFIRMED` for full text; the citation itself (cl. 2.1, device classification) is confirmed from the Guide |
| **ISO 17842 (Amusement ride/device safety)** | **Not present locally**, cited only inside V1's `bowtie-ccm-generator.html` (not independently verified), and not cited anywhere in the Guide itself | `TO BE CONFIRMED` |
| **GOHS internal standards** (`GOHS2.1.2`, `GOHS2.1.38`, `OHS-PRO-003`, `GOHS-REF-SMS-001`, `GOHS-GN-HAZID-001`, `GOHS4.1.8`) | Referenced throughout V1 code/UI text; documents themselves not located | `TO BE CONFIRMED` — VRTP-internal, source from VRTP's document management system |

**Copyright note, unchanged:** AS/NZS and ISO standards remain copyrighted commercial publications — paraphrase + clause reference only, unless VRTP's license terms permit redistribution. The WHSQ Guide itself is CC BY 4.0 (State of Queensland) — safe to quote/reproduce with attribution, which is why this document now cites it directly rather than paraphrasing at a distance.

## 3. Confirmed Terminology (supersedes earlier drafts)

| Term | Confirmed meaning | Source |
|---|---|---|
| **MAP** | Major amusement park | Guide §5 Acronyms |
| **ADH** | Amusement device hazard | Guide §5 |
| **ADI** | Amusement device incident | Guide §5 |
| **SFAIRP** | So far as is reasonably practicable | Guide §5 — **this is the term used throughout Chapter 9A / the Guide, not "SFARP."** V1's `sfarp_justification` field (general Risk entity, WHS Act s.17/19 duty) and this platform's general risk model may legitimately keep "SFARP" as it's the same underlying test worded differently by convention elsewhere — but every Chapter 9A/ADI/MAP-specific field, label, and generated demonstration text in this platform must say **SFAIRP**, not SFARP. This resolves the flag raised in [11-safety-case-demonstration-model.md](11-safety-case-demonstration-model.md) §9 |
| **FARSI** | Functionality, Availability, Reliability, Survivability, **Interdependency** | Guide §5, §9.2.2.1, Table 3 — confirmed; V1's calculator has this wrong ("Interaction") — see [08-critical-control-assurance-model.md](08-critical-control-assurance-model.md) §4b |
| **Safety case** | Amusement device safety case specifically — "not necessarily a complete picture of all hazards and risks at the MAP," scoped to ADH→ADI | Guide §5, §7.1 |
| **SMS ≠ Safety case** | "It is also important to distinguish between the safety case and the SMS. The safety case is descriptive of how 'you', the operator, manages the risks of ADIs. The SMS is the documentation of policy, procedures, operational management tools and governance... The SMS reduces risk SFAIRP." | Guide §7.1, quoted directly (CC BY 4.0) |
| **Demonstration** | "a practical explanation of how something works" — more than evidence of existence. Guide's own explicit anti-pattern: *"we manage all changes... by a change management system as described in the MOC procedure document number 124.02"* is called out as **insufficient** — "no verifiable evidence... no understanding for the reader as to how the MOC system works" | Guide §7.3, quoted directly |
| **Unmitigated / mitigated / (proposed) risk** | Three-stage assessment: (1) unmitigated = worst-case consequence disregarding controls, considered first; (2) mitigated = risk with current controls; (3) risk with proposed additional controls | Guide §9, confirms this platform's existing `Risk.inherent_*` / `current_*` / `target_*` fields map directly — **terminology should display as "unmitigated/mitigated/proposed" in any Chapter-9A-facing UI or Demonstration text**, even though the underlying columns keep their existing names for consistency with the rest of the platform |
| **Amusement device definition** | "plant that is operated for hire or reward that provides entertainment, sightseeing or amusement through movement of the equipment... or when passengers or other users travel or move on, around or along the equipment" | Guide §7.4, quoting **Schedule 19 (Dictionary)** of the WHS Regulation — corrected: Schedule 19 is the general Dictionary schedule (confirmed by you), not a standalone device-definition schedule; full definition + exclusions text still `TO_BE_CONFIRMED` verbatim (see §2) |
| **Schedule 18B vs Schedule 18C** | Two distinct schedules, not tiers of one — **18B** is the Amusement Device Emergency Plan content requirement (s.608N); **18C** is the amusement device SMS statutory content requirement (§5). Do not conflate: an Emergency Plan is not part of the SMS description module, it is its own regulatory artefact with its own schedule | Confirmed directly — Schedule 18B read in full this session (§5a) |

## 4. Confirmed WHS Regulation Citation Map

Every citation below is transcribed from the Guide's own footnotes (not inferred), organized by what it governs. `clause_ref` in `regulatory.requirements` should use these exact section numbers.

| Topic | Citation |
|---|---|
| Primary duty (SFAIRP) for MAP operators | WHS Act s.17, s.19 |
| Officer due diligence | WHS Act s.27 (Division 4) |
| Object of the Act | WHS Act s.3 |
| Nature of consultation | WHS Act s.48 |
| MAP definition criteria | WHS Regulation s.608A |
| **ADI definition** | WHS Regulation **s.608B(1)**: *"(a) involves an amusement device at the park and (b) exposes or potentially exposes, a person to a serious risk to health or safety emanating from an exposure, or potential exposure, to the occurrence."* — quoted directly, CC BY 4.0 |
| Control of risk (SFAIRP) | WHS Regulation s.608M(1) |
| Identification of ADIs and ADHs | WHS Regulation s.608K(3)(b); external conditions s.608K(3)(c) |
| Safety assessment | WHS Regulation s.608L (general), s.608L(2)(c) unmitigated risk, s.608V |
| Safety case content / demonstration requirements | WHS Regulation s.608R generally; s.608R(2) required summaries; s.608R(4) demonstration; s.608R(5)(c)(iii) minimising ADI effects; s.608R(2)(l) security of the park |
| Material particulars (safety case content, all of it) | WHS Regulation s.608ZP |
| Worker safety role | WHS Regulation s.608ZA |
| Worker consultation | WHS Regulation s.608ZB |
| Licence application requirements | WHS Regulation s.608ZE |
| Request for additional information | WHS Regulation s.608ZF |
| Licence decision | WHS Regulation s.608ZG (s.608ZG(2) decision basis, s.608ZG(7) new-application timing effect) |
| Assessment stage timing (6 months) | WHS Regulation s.608ZI |
| Consultation before licence refusal | WHS Regulation s.608ZJ |
| Licence continuation pending renewal decision | WHS Regulation s.608ZY |
| Review of regulator decisions | WHS Regulation s.676 (Table 676) |
| Hierarchy of controls | WHS Regulation s.36 |
| Management of risk (safety assessment process) | WHS Regulation Part 9A.3, Division 3 |
| Compliance cross-referencing requirement (SMS → regulation clause annotation) | WHS Regulation Part 9A.7 |
| Amusement device definition | WHS Regulation Schedule 19 (Dictionary) — verbatim text `TO_BE_CONFIRMED` |
| **Amusement device emergency plan content — Schedule 18B** | WHS Regulation s.608N; see §5a below — full breakdown, confirmed |
| **Amusement device SMS statutory content — Schedule 18C** | See §5 below — full subsection breakdown |
| Plant operation requirements (competency, storage, maintenance, inspection, log books) applying alongside Chapter 9A | WHS Regulation Chapter 5 |

## 5. Schedule 18C — Confirmed Structure (drives the SMS Section → Requirement mapping)

The Guide's own §10 ("Safety management system description") walks through Schedule 18C element by element. Confirmed subsection numbers, cross-referenced to the Guide's own section that describes each:

| Schedule 18C item | Content | Guide §, footnote |
|---|---|---|
| 18C(1) — Safety policy and safety objectives (1.1, 1.2) | Safety policy, communication, commitment, duties of operators | Guide §10.2, fn.67–71 |
| 18C(2) — Organisation and personnel (2.1, 2.2) | Command structure, roles, competency/training assurance | Guide §10.3, fn.72–73 |
| 18C(3) — Operational controls | Start-up/shutdown, patron access/egress, isolation, permits, interfaces, alarms | Guide §10.4, fn.74–75 |
| 18C(4) — Duties of operators (4.1, 4.2) | Compliance cross-referencing to Chapter 9A Part 9A.7 | Guide §10.2 "Duties of operators", fn.71 |
| — Change management | *(exact 18C sub-item number not captured in the pages read — `TO_BE_CONFIRMED` against `WHS Reg 2011.md` directly)* — content confirmed extensively: minor/major change examples, MOC integrated with Chapter 9A Part 9A.3 triggers | Guide §10.5, §10.12 |
| — Contractor management | *(sub-item TO_BE_CONFIRMED)* | Guide §10.6 *(not yet read in full — page range not covered this session)* |
| — Incident management, investigation, reporting, improvement | *(sub-item TO_BE_CONFIRMED)* | Guide §10.7 *(not yet read in full)* |
| — Training and competency | **Confirmed: Schedule 18C s.2.1** — "the SMS to provide a means of ensuring persons have the knowledge and skills necessary to enable them to undertake their allocated tasks and discharge their allocated responsibilities," plus retention of that knowledge/skill over time. Same sub-item as 18C(2) row above, not a separate one. Also grounded in s.39 (provision of info/training/instruction) and s.238(3) (operation of amusement devices, instruction and training) of the WHS Regulation, and s.27 (duty of officers) of the WHS Act. | Guide §10.8, fn.80–83 — **read in full, 2026-08-04**; see [11-safety-case-demonstration-model.md](11-safety-case-demonstration-model.md) §0 and [implementation-blueprint/14-architecture-change-requests.md](../implementation-blueprint/14-architecture-change-requests.md) §4a |
| — Asset integrity (maintenance, reliability, inspection, testing incl. major/annual inspections, logbooks) | Content confirmed — no explicit Schedule 18C sub-item number cited in this section's text itself; sub-item number remains `TO_BE_CONFIRMED` against `WHS Reg 2011.md` directly. | Guide §10.9 — **read in full, 2026-08-04** |
| — MAP security | Physical + cyber security of MAP boundary, ride envelopes, back-of-house | Guide §10.10, s.608R(2)(l) |
| — Worker safety role and consultation | See WHS Act s.48, WHS Reg s.608ZA/608ZB above | Guide §10.11, fn.86–89 |
| 18C(7) — Performance monitoring | Standards + leading/lagging performance indicators | Guide §11.1, fn.95–96 |
| 18C(8) — Audit | Methods, frequency, results of auditing | Guide §11.2, fn.97 |

**Honest gap — updated 2026-08-04:** §10.8 (Training and competency) and §10.9 (Asset integrity) are now read in full and confirmed above. **Two** sub-items remain open, not three: contractor management (§10.6) and incident management/investigation/reporting/improvement (§10.7) — both still unread this session — plus asset integrity's specific 18C sub-item *number* (content is confirmed, only the citation number is open). Recommend a follow-up pass reading pages ~34–36 of the Guide (§10.6–10.7) directly against `WHS Reg 2011.md`'s Schedule 18C before this table is treated as complete.

## 5a. Schedule 18B — Confirmed Structure (Emergency Plan)

Full text read directly this session — **all 5 parts confirmed, not partial**, unlike the three still-open Schedule 18C sub-items in §5:

| Schedule 18B item | Content |
|---|---|
| 1 — Workplace hazard and detail | Park location/address/entry-exit points; detailed map (workplace, surrounding land use, amusement device locations, emergency-service staging points); maximum persons likely present; emergency planning assumptions (measures for identified ADIs, likely affected areas); protective resources available; emergency response procedures |
| 2 — Command structure and workplace personnel | Command philosophy/structure activated in an emergency (who does what, when, where); person who can clarify the plan's content; contact details for liaising with emergency service organisations; 24-hour emergency contact list |
| 3 — Notifications | Procedures for notifying emergency services when an ADI has seriously injured a person and could reasonably require an emergency service response (s.608N); workplace warning systems; contact details for emergency services/support services assisting with evacuation; workplace communication systems |
| 4 — Resources and equipment | Workplace emergency resources, including emergency equipment and personnel |
| 5 — Procedures | Safe evacuation and accounting-for-all-people procedures; procedures and control points for utilities (gas, water, electricity) |

**Platform implication — ACR approved, Design Baseline v1.1:** no entity in Design Baseline v1.0 modeled an Emergency Plan — the architecture's original 10-module spec named "Emergency Management" as an SMS module (architecture doc), and V1's `incident-report.html` references isolation points belonging to "your emergency plan procedures," but no `EmergencyPlan` entity, `EmergencyContact`, or evacuation-procedure structure existed in [02-neo4j-node-relationship-model.md](02-neo4j-node-relationship-model.md) or [03-postgresql-schema.sql](03-postgresql-schema.sql). [ACR-002](../../.acr/ACR-002-emergency-planning-domain.md) was raised, reviewed against the Guide's §12 (Emergency plans, read in full 2026-08-04) in [implementation-blueprint/14-architecture-change-requests.md](../implementation-blueprint/14-architecture-change-requests.md) §3/§3a, and **approved by the Architecture Review Board on 2026-08-04**. `safety.emergency_plans` (one per park, mirroring the Guide's own "one MAP, one plan" structure — §12.4), `safety.emergency_exercises`, `safety.emergency_plan_credible_events`, and `safety.emergency_service_consultations` are now part of Design Baseline v1.1 ([03-postgresql-schema.sql](03-postgresql-schema.sql)) — reusing `DeviceBoundary`/`Asset` and `CriticalControl` isolation points via foreign key rather than new entities. Risk D4 ([implementation-blueprint/11-implementation-risk-register.md](../implementation-blueprint/11-implementation-risk-register.md)) is closed.

## 6. Notifiable Incident / Serious Risk Determination (formalizes V1's `whsqNotified`/`osrNotified` fields)

Now grounded in the confirmed ADI definition (§4):

1. An `Incident` REVEALS a `Hazard` whose `Risk` has `is_serious_risk = true` (or a `Consequence` with `flag_608b = true`) → `osr_notified` is forced out of any "not yet assessed" default, requiring explicit human determination before closure.
2. **The test is now confirmed, not inferred:** per s.608B(1), an occurrence is an ADI if it (a) involves an amusement device at the park **and** (b) exposes or potentially exposes a person to a serious risk to health or safety. "Serious risk" itself is **not** numerically defined by the Regulation — the Guide is explicit that the *operator* must define and document their own threshold interpretation (§7.5, Table 1 examples of serious vs. minor consequence), which is exactly what `SafetyAssessment.serious_risk_threshold_note` ([11-safety-case-demonstration-model.md](11-safety-case-demonstration-model.md) §4) captures — this is not a gap in the platform design, it's a correct reflection of how the Regulation itself is structured (operator-defined threshold, transparently documented, assessed by the regulator on its reasonableness).
3. This automated flag is still never a substitute for human judgement on notifiability — matches [04-ai-extraction-specification.md](04-ai-extraction-specification.md) §6's critical-item override.
4. V1's `local-automation` Compliance Agent already reasons about this decision point informally; that logic is a starting point for rule text, not a substitute for the confirmed citation above.

## 7. SMS Section → Requirement Mapping

Revised: the Guide's own governance structure (§5 Schedule 18C(7)/(8)) does not reference ISO 45001 clauses at all — the original brief's request for an ISO 45001 mapping remains valid for internal conformance purposes (VRTP may hold ISO 45001 certification independent of the Chapter 9A safety case), but **the Chapter 9A safety case itself is assessed against Schedule 18C, not ISO 45001** — these are two different, both-legitimate mappings and should not be conflated in the UI or in generated Demonstrations.

```sql
-- addendum to 03-postgresql-schema.sql
CREATE TABLE safety.sms_sections (
  id                uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  name              varchar(100) NOT NULL,
  schedule_18c_ref  varchar(20),     -- e.g. '18C(1)' — populate from §5 above; NULL where TO_BE_CONFIRMED
  description       text
);
CREATE TABLE safety.sms_section_requirements (
  sms_section_id  uuid NOT NULL REFERENCES safety.sms_sections(id),
  requirement_id  uuid NOT NULL REFERENCES regulatory.requirements(id),
  PRIMARY KEY (sms_section_id, requirement_id)
);
```

Seed the section rows directly from Guide §10.1–10.12/§11 (now real, confirmed content — §5 above), not from `index.html`'s nav as originally planned (V1's nav doesn't currently distinguish Schedule 18C boundaries at all). The ISO 45001 clause linkage remains a **separate, optional** table for internal conformance tracking, populated only once that source is obtained (§2).

## 8. Consumers

`regulatory.requirements` and this mapping are read by: the SMS module views (display linked Schedule 18C clauses), [07-inference-rules-catalogue.md](07-inference-rules-catalogue.md) R11 (coverage gap detection), the Safety Case Workspace (`TRACES_TO`), and the Safety Case Demonstration Engine ([11](11-safety-case-demonstration-model.md) §7 — every generated Demonstration cites the Schedule 18C item it addresses).
