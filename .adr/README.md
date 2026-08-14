# Architecture Decision Records

Implementation-time decisions that don't change the frozen Design Baseline (v1.1) — tooling choices, library selections, internal code organisation. If a decision would change the ontology, schema, Neo4j model, OpenAPI contract, or module boundaries, it needs an [ACR](../.acr/README.md), not an ADR.

Use [TEMPLATE.md](TEMPLATE.md) for new entries.

## Decisions recorded

- **[ADR-001](ADR-001-baseline-tag-immutability.md)** — release tags (`vX.Y.Z-RN`) are immutable; defects are fixed forward, never by re-pointing a tag. Accepted 2026-08-05.
- **[ADR-002](ADR-002-branch-protection-model.md)** — branch protection model for `main`: PR + required CI checks, no minimum approval count while single-maintained ("Option A"), reserved for revisit once a second regular reviewer exists. Accepted 2026-08-07. Closes the merge deadlock discovered during the R0 merge (PR #11) — see [15-r0-exit-review.md](../docs/implementation-blueprint/15-r0-exit-review.md) §Release for the original investigation.
- **[ADR-003](ADR-003-incident-investigation-action-sibling-structure.md)** — Incident domain: `Investigation` and `Action` are independent siblings of `Incident` (`INVESTIGATED_AS` 1:1, `TRIGGERS` N:1), not a linear `Incident → Investigation → Action` chain. Accepted 2026-08-09. Resolves D2 of [19-r1-milestone-3b-incident-decision-register.md](../docs/implementation-blueprint/19-r1-milestone-3b-incident-decision-register.md); serves as the confirmed architectural basis for the D4 OpenAPI-extension ACR (ACR-004, implemented).
- **[ADR-004](ADR-004-incident-ontology-scheme-deferral.md)** — Incident domain: `incident_type_concept_id`/`root_cause_category_concept_id` left unseeded, no new ontology scheme created — same class of open question as the standing Hazard Taxonomy deferral. Accepted 2026-08-12. Resolves D3 of [19-r1-milestone-3b-incident-decision-register.md](../docs/implementation-blueprint/19-r1-milestone-3b-incident-decision-register.md).
- **[ADR-005](ADR-005-incident-orphan-v1-fields-disposition.md)** — Incident domain: of six orphan V1 fields, `fReporterRole` resolves via the existing `Person.role_title` model (no gap); the other five (`fStaffPresent`, `fPersonStatus`, `fOtherNotes`, investigation completion date, Lessons Learned) are deliberately not ported, no new columns added. Corrects a "five vs. six" undercount carried in the 3A/3B record. Accepted 2026-08-12. Resolves D5 of [19-r1-milestone-3b-incident-decision-register.md](../docs/implementation-blueprint/19-r1-milestone-3b-incident-decision-register.md).
- **[ADR-006](ADR-006-incident-notification-rule-formal-defer.md)** — Incident domain: D6 (R10 notification-rule scope). Formally deferred 2026-08-12, then **resolved same day**: `whsq_notified` = internal notification, R10 extended to general WHS Act incident categories, Safety Systems Manager as notifier, 48hr timeframe, 10yr evidence retention, V1 rule confirmed current. **"OSR" meaning remains unanswered** — `osr_notified` untouched, carried forward as a residual open item. **An ACR is required** (not yet raised) before R10's definition in `07-inference-rules-catalogue.md` can actually be extended. Resolves D6 of [19-r1-milestone-3b-incident-decision-register.md](../docs/implementation-blueprint/19-r1-milestone-3b-incident-decision-register.md).

## Open decisions flagged during R0/Phase 2.2 scaffolding

Per [docs/implementation-blueprint/13-application-foundation-scaffold.md](../docs/implementation-blueprint/13-application-foundation-scaffold.md) §2, these should become ADRs before R1 implementation begins:

- Frontend routing library (scaffold assumes React Router)
- Server-state library (scaffold assumes TanStack Query)
- Client-state library (scaffold assumes Zustand, UI-local state only)
- Form library (scaffold assumes React Hook Form + Zod)
- Build tool (scaffold uses Vite — this one is arguably already settled by having built the R0 scaffold with it; confirm and close out rather than re-litigate)

## Index

| ADR | Title | Status |
|---|---|---|
| [ADR-001](ADR-001-baseline-tag-immutability.md) | Release Tags Are Immutable | Accepted |
| [ADR-002](ADR-002-branch-protection-model.md) | Branch Protection Model — Option A (PR + CI, No Minimum Approval Count) | Accepted |
| [ADR-003](ADR-003-incident-investigation-action-sibling-structure.md) | Incident Domain — Investigation and Action as Siblings of Incident, Not a Chain | Accepted |
| [ADR-004](ADR-004-incident-ontology-scheme-deferral.md) | Incident Domain — Defer Ontology Scheme for Incident Type / Root Cause Category | Accepted |
| [ADR-005](ADR-005-incident-orphan-v1-fields-disposition.md) | Incident Domain — Disposition of Six Orphan V1 Fields | Accepted |
| [ADR-006](ADR-006-incident-notification-rule-formal-defer.md) | Incident Domain — D6 (Notification-Rule Scope) Formal Defer, then Resolved | Resolved — ACR pending, OSR meaning residual open |
