# ADR-005: Incident Domain — Disposition of Six Orphan V1 Fields

**Status:** Accepted (2026-08-12)

## 1. Decision Statement

Of the six V1 `incident-report.html` fields with no direct frozen-schema column, **one (`fReporterRole`) is already representable through the existing model** — via `reporter_person_id → safety.persons.role_title`, already implemented in Milestone 0 — and requires no action. The remaining **five** (`fStaffPresent`, `fPersonStatus`, `fOtherNotes`, `fInvDate`/investigation completion date, `fLessons`/Lessons Learned) are **intentionally not ported** — deliberate, documented non-ports, not silent drops — matching the CCM Milestone 2A D4/D5 precedent of deferring rather than adding columns ahead of the milestone that needs them. **No PostgreSQL column is added by this decision.** This resolves [19-r1-milestone-3b-incident-decision-register.md](../docs/implementation-blueprint/19-r1-milestone-3b-incident-decision-register.md) **D5**.

**Correction to the record:** [18-r1-milestone-3a-incident-discovery-reconciliation.md](../docs/implementation-blueprint/18-r1-milestone-3a-incident-discovery-reconciliation.md) §1, §11, §12 (D5) and [19](../docs/implementation-blueprint/19-r1-milestone-3b-incident-decision-register.md) D5 all labeled this "**five** V1 fields" while every one of their own evidence rows lists **six** field names and 18's own §10 states "none of the six match any existing column." The heading undercounted; the body never did. This ADR reconciles all six individually — a field-by-field pass 3A/3B did not do — rather than perpetuating the five/six mismatch or treating the six as a single undifferentiated bucket.

## 2. Context

3A's discovery pass ([18](../docs/implementation-blueprint/18-r1-milestone-3a-incident-discovery-reconciliation.md) §10) found six V1 form fields with, as then assessed, no frozen-schema home at all, and grouped them as one gap (D5/D7 depending on section). This ADR was authorized specifically to reconcile each field individually against V1, schema, OpenAPI, Neo4j, prior decisions (D1–D4), and relevant business logic — a finer-grained pass than 3A performed — and to determine, per field, whether it: remains represented through the existing model; is intentionally retired/deferred; maps to an existing canonical entity/property; or genuinely requires a new column.

## 3. Evidence Reviewed, Per Field

### `fReporterRole` (line 99, "e.g. Duty Manager, Safety Officer")
- **V1:** free text, captured once per incident, describing the reporter's job role.
- **Schema:** `safety.incidents.reporter_person_id` (`03:524`) is a FK to `safety.persons`. `safety.persons.role_title` (`03:114`, `varchar(200)`) already exists — and is already implemented as a SQLAlchemy model column (`apps/api/app/models/safety.py:54`), not just a schema-only artefact.
- **OpenAPI:** `Person.role_title` (`10-openapi.yaml:960`) and `PersonInput.role_title` (`:967`) are already exposed.
- **D1–D4:** No conflict. Consistent with the free-text→Person-resolution pattern already established for CCM's Owner/Verified-By fields (Milestone 2A precedent, cited in [18](../docs/implementation-blueprint/18-r1-milestone-3a-incident-discovery-reconciliation.md) §9) and reused for `reporter_person_id` itself in [18](../docs/implementation-blueprint/18-r1-milestone-3a-incident-discovery-reconciliation.md) §10's own field-reconciliation table.
- **Disposition: Represented through the existing model.** Not a gap. The reporter's role is the linked `Person`'s `role_title` — resolving the free-text reporter name to a `Person` record (already a required step for `reporter_person_id`) already carries the role with it. No new field, no deferral needed, no ADR action beyond recording this finding.

### `fStaffPresent` (line 95, "e.g. 2 lifeguards, 1 duty manager")
- **V1:** free text, describes multiple staff members and their roles/counts at the time of the incident.
- **Schema:** No column on `safety.incidents` or elsewhere. No join table (unlike `incident_hazards`/`incident_actions`) links multiple `Person` records to an `Incident` in a "present at scene" capacity — only the single `reporter_person_id`.
- **OpenAPI/Neo4j:** No representation; `Incident` node properties (`02-neo4j-node-relationship-model.md:56`) list none.
- **D1–D4:** Unaffected by any of D2/D3/D4.
- **Disposition: Intentionally not ported.** No canonical single-entity mapping exists (it is inherently a list of people, not a scalar), and adding one would mean a new join table — a schema change, out of this ADR's boundary.

### `fPersonStatus` (line 96, "e.g. Transported to GCUH, ICU admission")
- **V1:** free text, distinct from and separately captured alongside `fInjuries` (line 86, "Nature and extent of any injuries or health effects") — V1 itself treats "what injury occurred" and "current status/whereabouts of the affected person" as two different concepts.
- **Schema:** `safety.incidents.injuries` (`03:526`) exists and is already mapped to `fInjuries`. No separate column exists for ongoing person-status/disposition.
- **Disposition: Intentionally not ported.** Mapping it onto `injuries` would conflate two concepts V1 itself keeps separate — exactly the kind of invented-semantics mapping this pass was told not to make.

### `fOtherNotes` (line 100, "Witness names not captured above, CCTV coverage, equipment status, weather, patron count, etc.")
- **V1:** explicitly a catch-all field, and its own placeholder text says "not captured above" — a deliberate V1 design signal that it is *not* a duplicate of `witnesses` (line 87).
- **Schema:** `safety.incidents.witnesses` (`03:527`) exists and is mapped to `fWitnesses`; no separate free-text catch-all column exists.
- **Disposition: Intentionally not ported.** No canonical mapping; conflating it with `witnesses` would misrepresent both V1's own field boundary and the frozen schema's field boundary.

### `fInvDate` (line 108, "Investigation Completion Date")
- **Schema:** `safety.incidents.investigation_status` (`03:533`) tracks *state* (Not Started/In Progress/Complete) but no completion *date* column exists on `incidents`. `safety.investigations` (`03:548-558`) — the table now exposed via [ACR-004](../.acr/ACR-004-incident-openapi-extension.md)'s `Investigation`/`InvestigationInput` schema — has `id`, `incident_id`, `method`, `findings`, `contributing_factors`, `created_at`, `updated_at`. **No `completion_date` column exists there either.**
- **D4 interaction (checked specifically, per this ADR's required evidence scope):** ACR-004 exposed `Investigation` additively, mirroring the table's existing columns exactly — it did not, and could not without a schema change, add a completion-date field that the table itself lacks. D4's implementation does not retroactively resolve D5 for this field.
- **Disposition: Intentionally not ported.** `updated_at` (auto-maintained, not user-set) is not evidence-equivalent to a deliberately-recorded completion date and using it as a substitute would misrepresent what V1 actually captured (a specific, operator-entered date).

### `fLessons` (line 109, "Lessons Learned")
- **V1:** free text, forward-looking ("What was learned? How can this be prevented?") — distinct in kind from `safety.investigations.findings` (what was found) and `.contributing_factors` (why it happened), which are backward/causal, not forward/preventive.
- **Schema:** No column on `incidents` or `investigations` matches this concept.
- **D4 interaction:** Same as `fInvDate` — ACR-004's `Investigation` schema mirrors the existing table exactly; no `lessons_learned` column exists to expose.
- **Disposition: Intentionally not ported.** Mapping it onto `findings` or `contributing_factors` would conflate three V1-distinct concepts into two frozen-schema fields — not supported by the evidence.

## 4. Options Considered (per the five genuinely-orphan fields)

- **(a) Don't port** — documented, deliberate non-port. Matches the CCM Milestone 2A D4/D5 precedent (deferring the "Retired" control state and the `reduce{}` effectiveness mechanism rather than adding columns ahead of the milestone that needs them).
- **(b) Add new PostgreSQL columns now** — `staff_present` (text) on `incidents`; a person-presence join table for the same; `person_status` (text) on `incidents`; `other_notes` (text) on `incidents`; `completion_date` (date) on `investigations`; `lessons_learned` (text) on `investigations`. Would require a schema change → ACR, out of this ADR's authorized boundary.

## 5. Decision and Rationale

**(a) for all five.** None of the five has a canonical existing-model mapping (unlike `fReporterRole`), and none can be safely folded into an adjacent existing field without inventing semantics the evidence doesn't support (§3, per field). Adding columns now would be schema expansion ahead of any milestone that has demonstrated it needs them — the same reasoning already applied twice in this domain's governance (CCM's Retired-state deferral, and D3's ontology-scheme deferral, [ADR-004](ADR-004-incident-ontology-scheme-deferral.md)). **No new PostgreSQL column is added. No ACR is raised.**

## 6. Consequences

- Any future Incident/Investigation record created without these five fields is not a data-loss defect relative to the frozen baseline — it is the frozen baseline's own current shape.
- If V1 historical incident records are ever migrated, these five fields' content has nowhere to land without a subsequent, separately-authorized schema change (ACR) — this is a documented migration-completeness gap, not a silent one.
- `fReporterRole`'s resolution requires no schema/API change, but implementation (when authorized) must resolve the V1 free-text reporter-role value against the linked `Person.role_title`, not drop it — mirroring the existing `reporter_person_id`/`asset_id` free-text-to-FK resolution pattern already established for CCM.
- If any of the five is later demonstrated to be operationally necessary, the correct next step is a new ACR (schema change) — not a silent implementation-time addition.

## 7. Relationship to Other Decisions

Independent of D2/ADR-003, D3/ADR-004, and D6. Directly informed by D4/ACR-004's implemented `Investigation` schema (§3, `fInvDate`/`fLessons` checked against it specifically and found still unhomed). Does not resolve, and takes no position on, D6.

## 8. Explicit Scope Boundary

This ADR resolves **D5 only**, for all six named fields individually. It does not resolve, and takes no position on:
- **D6** (R10 notification-rule scope) — remains PENDING, awaiting Compliance/Legal input, not touched by this ADR.
- No PostgreSQL, OpenAPI, Neo4j, ontology, or application-code change is made or authorized by this ADR.
- No ACR is raised — the evidence in §3 did not establish that a new column is actually required for any of the five deferred fields.
- No implementation of the Incident domain is authorized by this ADR.

## 9. Status

**Accepted (2026-08-12).** D5 closed — `fReporterRole` resolved as already-represented; the other five deliberately deferred. D6 remains open per [19-r1-milestone-3b-incident-decision-register.md](../docs/implementation-blueprint/19-r1-milestone-3b-incident-decision-register.md).
