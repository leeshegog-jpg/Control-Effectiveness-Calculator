# Action — Incident↔Action Mechanism Reconciliation, Correction

**Status:** Reconciliation correction. Documentation only — no application code, schema, OpenAPI, ontology, or Neo4j model change is created or modified by this document.

## 1. Why This Record Exists

A read-only Action reconciliation pass (chat, 2026-08-21) flagged what it described as a genuine conflict between two frozen artifacts on the Incident↔Action relationship mechanism: `safety.actions.source_type_concept_id`/`source_id` (polymorphic FK, "Model A") versus `safety.incident_actions` (composite-key join table, "Model B"), on the basis that a strict 1:N `TRIGGERS` cardinality (`02-neo4j-node-relationship-model.md:112`) is already fully representable by a single FK, making the join table's N:N-capable structure appear redundant or contradictory.

That framing was **premature** — it was based on an incomplete evidence pass that missed `06-relationship-rules-catalogue.md`'s per-relationship business-rule text and [18-r1-milestone-3a-incident-discovery-reconciliation.md](18-r1-milestone-3a-incident-discovery-reconciliation.md)'s own prior reconciliation of the same question. A follow-up pass (chat, same session) found both, plus direct V1 confirmation, and resolves the apparent conflict by evidence. This record corrects the prior chat output (never committed to the repository) and establishes the corrected record.

## 2. Corrected Finding

`source_type_concept_id`/`source_id` and `incident_actions` are **not competing representations of the same fact** — they answer two different questions, both genuinely present in V1 and the frozen schema:

- **`actions.source_type_concept_id` + `source_id` = Action origin.** Single value per Action row — which domain object first spawned this corrective action (Incident, AuditFinding, Risk Review, Hazard Report, Observation, per the column's own comment, `03-postgresql-schema.sql:562`). Matches V1's `openCAR()` (`incident-report.html:322-330`): saves the incident, then navigates to `corrective-actions.html?source=Incident&sourceRef=<incidentId>&...` — a single-value, one-directional creation flow.
- **`safety.incident_actions` = Incident's linked-CAR roster.** Multi-value, composite-key join table. Matches V1's `fCARs` field (`incident-report.html:110`) — "Linked CAR IDs," free text, placeholder `"e.g. C0001, C0002"` — a **comma-separated list** an incident maintains, distinct in kind from the single `source`/`sourceRef` pair. Verified directly against the live V1 file, not assumed from citation.

**`06-relationship-rules-catalogue.md:37`**, on closer reading, does not contradict this: it states `source_type_concept_id`/`source_id` "must **agree with** which edge was used" — a consistency check between an Action's recorded origin and its `TRIGGERS` edge, not a claim that `source_type`/`source_id` is the edge's sole generating mechanism.

**[18 (3A), already a frozen governance record](18-r1-milestone-3a-incident-discovery-reconciliation.md)**, had already reconciled this at the time nobody had reason to revisit it: §3's table (line 76) states `safety.incident_actions` "backs `TRIGGERS` for the Incident side specifically"; §11's V1 field-mapping table (line 188) maps `fCARs` directly to `incident_actions`, disposition "RECONCILED at schema level, GAP at API level (D4)."

## 3. Correction to the Prior Reconciliation Pass

The prior chat-only reconciliation pass (2026-08-21, never committed) stated: *"This is a genuine conflict between two frozen artifacts... Nothing in the frozen baseline decides between them."* **That statement is withdrawn.** The evidence in §2 — `06-relationship-rules-catalogue.md:37`, doc 18 §3/§11, and direct V1 confirmation of `fCARs` — resolves the mechanism question without requiring a fresh governance decision. The error was an incomplete evidence pass, not a genuine baseline conflict; recorded here so the audit trail does not carry a false "unresolved" status forward.

## 4. What Remains Genuinely Open (Unchanged From the Prior Pass)

- **`incident_actions`/`TRIGGERS` has zero OpenAPI surface.** Checked whether ACR-004 already covered it — it did not; ACR-004's scope was Investigation + hazards (`REVEALS`) + Evidence only, per [19 D4](19-r1-milestone-3b-incident-decision-register.md#d4--openapi-extension-for-investigation-incident_hazardsreveals-and-incident-scoped-evidence). Exposing `incident_actions` as a first-class endpoint (e.g. `/incidents/{id}/actions`) requires its own **ACR**, same class as the original D4, not yet raised.
- **`completion_date`/`notes` exposure on `ActionInput`/`Action`** — genuinely omitted from the frozen OpenAPI contract (confirmed directly, `10-openapi.yaml:1203-1215`). Requires **ACR** if exposure is pursued.
- **`safety.action_controls`/`REMEDIATES`** — no OpenAPI surface, no polymorphic-FK alternative on `actions` (unlike the Incident/Action relationship, `REMEDIATES` has only one possible mechanism). Requires **ACR** if pursued.
- **No new ADR is required for the Incident↔Action relationship mechanism itself** — §2/§3 resolve it by evidence, not by fresh decision.

## 5. Updated Disposition

| Item | Status |
|---|---|
| Base Action CRUD (`/actions`, `/actions/{id}`, `source_type`/`source_id`) | Ready for implementation against the frozen contract — no ADR/ACR needed |
| `source_type`/`source_id` | Origin relationship — confirmed, not in question |
| `incident_actions`/`TRIGGERS` | Incident linked-CAR roster — mechanism confirmed, consistent with V1 `fCARs` |
| Incident Action endpoint (`/incidents/{id}/actions` or similar) | **ACR required** if exposed |
| `sync_action`'s Incident linkage | Technically scopeable once the endpoint's own ACR question is resolved |
| `completion_date`/`notes` | **ACR required** if exposed |
| `action_controls`/`REMEDIATES` | **ACR required** if exposed |
| Structural conflict (prior framing) | **Withdrawn — resolved by evidence, no governance decision required** |

## 6. Recommended Implementation Sequence (Not Authorized by This Record)

1. Base Action CRUD against the existing OpenAPI contract.
2. Separately decide/raise the ACR for Incident Action API exposure (`incident_actions`).
3. Then implement the Incident `TRIGGERS` API/graph linkage within that authorized boundary.
4. Treat `completion_date`/`notes` and `action_controls`/`REMEDIATES` as separate governance items, each needing its own ACR if pursued.

**No Action implementation GO has been issued by this record.**

## Acceptance Criteria

- [x] Corrects the prior chat-only "genuine conflict" framing explicitly, with the withdrawal stated plainly rather than silently superseded.
- [x] Traces the corrected finding to specific evidence (`06:37`, doc 18 §3/§11, direct V1 file confirmation of `fCARs`), not asserted without citation.
- [x] Distinguishes what's resolved by evidence (the mechanism question) from what remains genuinely open (OpenAPI surface gaps, each requiring its own ACR).
- [x] No implementation authorized by this record.
- [x] No code, schema, OpenAPI, ontology, Neo4j, ADR, or ACR change made in producing this document.
