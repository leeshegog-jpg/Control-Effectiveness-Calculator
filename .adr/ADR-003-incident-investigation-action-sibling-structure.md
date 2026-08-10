# ADR-003: Incident Domain — Investigation and Action as Siblings of Incident, Not a Chain

**Status:** Accepted (2026-08-09)

## 1. Decision Statement

The Incident Management domain implements `Investigation` and `Action` as **independent satellites of `Incident`**, per the frozen baseline's own relationship model — `Incident --INVESTIGATED_AS(1:1)--> Investigation` and `(Incident | AuditFinding) --TRIGGERS(1:N)--> Action` — and **not** as a sequential `Incident → Investigation → Action` pipeline. This decision governs the shape of any future implementation and, specifically, the endpoint/schema shapes proposed by the D4 OpenAPI-extension ACR.

## 2. Context

R1 Milestone 3A's authorization explicitly instructed: *"Do not assume that Incident → Investigation → Corrective Action is the final domain structure simply because that is operationally intuitive... establish what the frozen architecture and V1 actually say."* The discovery pass ([18-r1-milestone-3a-incident-discovery-reconciliation.md](../docs/implementation-blueprint/18-r1-milestone-3a-incident-discovery-reconciliation.md) §5) found the frozen baseline does not support the intuitive chain. This decision (D2) closes that question, recorded per [19-r1-milestone-3b-incident-decision-register.md](../docs/implementation-blueprint/19-r1-milestone-3b-incident-decision-register.md) D2, which routed it to ADR (no baseline artefact change under the recommended option) and flagged it as a prerequisite for D4 (§5 dependency matrix: "D2 should be resolved before D4's ACR is drafted").

## 3. Evidence Reviewed

- **Neo4j relationship model** ([02-neo4j-node-relationship-model.md](../docs/knowledge-graph/02-neo4j-node-relationship-model.md):110–112) — three edges out of `Incident`, none of them transiting through another: `REVEALS` (`Incident → Hazard`, N:N), `INVESTIGATED_AS` (`Incident → Investigation`, 1:1), `TRIGGERS` (`Incident | AuditFinding → Action`, 1:N).
- **Relationship rules catalogue** ([06-relationship-rules-catalogue.md](../docs/knowledge-graph/06-relationship-rules-catalogue.md):35–37) — `INVESTIGATED_AS` line 36: *"`investigations.incident_id UNIQUE` enforces this structurally."* `TRIGGERS` line 37: explicit invariant that an `Action` triggered by an `AuditFinding` cannot also claim `source_type = 'Incident'` — confirming `Action` is a shared, polymorphic entity addressable from more than one source type, not a child of `Investigation`.
- **Frozen PostgreSQL schema** ([03-postgresql-schema.sql](../docs/knowledge-graph/03-postgresql-schema.sql)):
  - `safety.investigations.incident_id` (line 550) is `NOT NULL UNIQUE` — a 1:1 satellite of `Incident`, never of anything else.
  - `safety.actions` (lines 560–578) has no `investigation_id` column anywhere. `safety.incident_actions` (lines 586–590) is a direct `incident_id`/`action_id` join table — `Action` reaches back to `Incident` directly, bypassing `Investigation` entirely.
  - Building the alternative (Action nested under Investigation) would require a new FK not present anywhere in the frozen schema.
- **V1 source** ([incident-report.html](../incident-report.html), root SMS suite, confirmed canonical per [18](../docs/implementation-blueprint/18-r1-milestone-3a-incident-discovery-reconciliation.md) §1/§2.2) — investigation fields (`fImmCause`, `fRootCause`, `fInvStatus`, `fInvDate`, `fLessons`) are flat properties on the same incident record, lines 105–110; there is no client-side concept of Investigation as a separate object at all. `openCAR()` (lines 322–330) creates an `Action`/CAR directly from the incident, with no Investigation step in between.
- **Milestone 2 (CCM) precedent** ([17-r1-milestone-2-ccm-discovery-reconciliation.md](../docs/implementation-blueprint/17-r1-milestone-2-ccm-discovery-reconciliation.md) §5) — the same class of "is this a parent/child nesting or independent sibling rows" question was resolved the same way for Control/Support/Verification: the frozen schema's actual foreign-key structure governs, not the intuitively-nameable hierarchy.

Three independent sources — V1 behaviour, the Postgres foreign-key structure, and the Neo4j relationship model — converge on the same shape. No source reviewed supports the chain.

## 4. Options Considered

- **(a) Sibling model** — `Investigation` is a 1:1 satellite of `Incident`; `Action` is a shared, polymorphic entity reachable from `Incident` (via `incident_actions`) or `AuditFinding`, with no dependency on `Investigation`. Matches the frozen schema and graph model exactly, as built.
- **(b) Linear chain** — `Incident → Investigation → Action`, with `Action` nested under `Investigation`. Would require adding an `investigation_id` FK to `safety.actions` — a change to a Design Baseline v1.1 artefact not evidenced anywhere in the frozen schema, and contradicted by the `TRIGGERS`/`INVESTIGATED_AS` edges as specified.

## 5. Decision and Rationale

**(a) is adopted.** This is not a fresh architectural choice — it is the already-built, already-frozen reality of Design Baseline v1.1, confirmed independently by three sources (§3). Option (b) is rejected: it is not merely unevidenced, it actively contradicts the frozen schema's constraint structure (`investigations.incident_id UNIQUE`, no `investigation_id` on `actions`) and would require a schema change, which is out of scope for an ADR and would need its own ACR if ever pursued — nothing in the evidence reviewed motivates reopening that question.

## 6. Consequences

- Implementation of the Incident domain must model `Investigation` as an optional 1:1 extension of `Incident`, never as a prerequisite for creating an `Action`.
- `Action` creation/service logic must treat `source_type`/`source_id` as the sole linkage mechanism back to `Incident` (or `AuditFinding`), with no assumption that an `Investigation` record exists or is referenced.
- Service/router layering (when implementation is eventually authorized) should expose Investigation and Action as siblings under Incident's resource tree, not as nested resources of one another (e.g. `/incidents/{id}/investigation` and `/incidents/{id}/actions` as parallel sub-resources, not `/incidents/{id}/investigation/actions`).
- This decision constrains but does not perform the D4 OpenAPI extension — see §7.

## 7. Relationship to D4

This decision is the **confirmed architectural basis** the D4 ACR (OpenAPI extension for `Investigation`, `incident_hazards`/`REVEALS`, and incident-scoped `Evidence`) must draft against. Per [19-r1-milestone-3b-incident-decision-register.md](../docs/implementation-blueprint/19-r1-milestone-3b-incident-decision-register.md) §5, D4's ACR should propose endpoint shapes consistent with the sibling model recorded here (e.g. `Investigation` as a 1:1 resource keyed off `Incident`, not nested under any other new resource) — not re-litigate Incident/Investigation/Action's shape mid-ACR. **This ADR does not draft, propose, or authorize that ACR.** Raising the D4 ACR remains a separate, not-yet-authorized action.

## 8. Explicit Scope Boundary

This ADR resolves **D2 only**. It does not resolve, and takes no position on:
- **D3** (ontology scheme for `incident_type_concept_id`/`root_cause_category_concept_id`) — remains PENDING.
- **D5** (five V1 fields with no schema home) — remains PENDING.
- **D6** (R10 notification-rule scope) — remains PENDING, genuinely open, awaiting Compliance/Legal input.
- **D4** (OpenAPI extension ACR) — remains PENDING; this ADR is an input to that ACR, not a substitute for it. No ACR has been raised by this document.
- No schema, OpenAPI, ontology, Neo4j, or application-code change is made or authorized by this ADR.
- No implementation of the Incident domain is authorized by this ADR.

## 9. Status

**Accepted (2026-08-09).** Recorded as the controlled input to D4. D3, D5, D6, and D4 itself remain open per [19-r1-milestone-3b-incident-decision-register.md](../docs/implementation-blueprint/19-r1-milestone-3b-incident-decision-register.md).
