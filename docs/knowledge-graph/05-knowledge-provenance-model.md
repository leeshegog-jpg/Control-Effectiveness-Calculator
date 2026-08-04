# Knowledge Provenance Model
**Status: DRAFT — controlled design document. Requires approval before implementation.**
**Parent:** [01-enterprise-knowledge-graph-specification.md](01-enterprise-knowledge-graph-specification.md)
**Schema:** [03-postgresql-schema.sql](03-postgresql-schema.sql) `provenance.records`

---

## 1. Purpose

Every fact in the platform — a hazard's existence, a control's classification, a risk rating, a safety case claim — must be traceable to **why it's there**: which document it came from, which extraction run produced it, which person entered or approved it, or which rule derived it, and with what confidence. This is not optional polish; a Safety Case argument that cannot show its evidence chain is not a Safety Case (briefing doc §3.12, assurance = three lines of defence, all of which depend on knowing where a claim's support actually came from). V1 has none of this — a `localStorage` record has a `created`/`updated` timestamp and nothing else; there is no way to know today whether a given risk-register row was typed by a human, copied from another tool, or drafted by an AI and never reviewed.

## 2. Model

One append-only `provenance.records` row per **write event** on a tracked entity (all entities in [02-neo4j-node-relationship-model.md](02-neo4j-node-relationship-model.md) §3 are tracked). The entity table itself (e.g. `safety.hazards`) always holds **current state**, mutable, with its own `updated_at` — the provenance schema is the append-only history layered underneath it, not a replacement for normal row updates. This is a deliberate simplification over full event-sourcing: current-state tables stay simple and queryable, history/audit is a separate concern that doesn't leak into every join.

| Field | Meaning |
|---|---|
| `entity_type` / `entity_id` | What this provenance record is about |
| `source_type` | `document_extraction` \| `human_entry` \| `v1_migration` \| `system_derived` |
| `document_id` | Set only for `document_extraction` — the source document |
| `extraction_run_id` | Set only for `document_extraction` — ties every fact from one AI run together (AI Extraction Spec §2) |
| `created_by_person_id` | Set for `human_entry` and human-approved `document_extraction`; null for unattended `system_derived` |
| `confidence` | 0–1. `human_entry` = 1.0. `document_extraction` = the extraction confidence (AI Extraction Spec §6). `v1_migration` = 1.0 (verbatim carry-over) unless the migration itself involved a lossy schema reconciliation, in which case < 1.0 and the reconciliation logic is cited in a note field. `system_derived` = 1.0 for deterministic derivations (e.g. risk rating from likelihood×consequence), < 1.0 for probabilistic ones (e.g. a duplicate-hazard suggestion) |
| `previous_version_id` | Self-reference — chains this write to the provenance record of the write it supersedes, enabling full history reconstruction for one entity |

## 3. Source Types in Detail

- **`document_extraction`** — produced by the AI Extraction Service. Always carries `document_id` + `extraction_run_id`. Auto-accepted facts (AI Extraction Spec §6, ≥0.85) still get a full provenance record — "auto-accepted" is a routing decision, not an exemption from traceability.
- **`human_entry`** — a person typed or edited a value directly through the platform UI. `confidence = 1.0` by convention (a human asserting a fact is treated as ground truth at the point of entry; it can still be wrong, but that's a data-quality problem, not a confidence problem).
- **`v1_migration`** — set on every record carried over from the legacy `localStorage`/flat-file system during Phase 5 (architecture doc). Preserves V1's original `created`/`updated` timestamps as data fields on the migrated record itself, distinct from the provenance record's own `created_at` (which is the migration event's timestamp, not the original entry's). This distinction matters for audit: "when was this hazard first identified" (V1 timestamp) is a different question from "when did it enter the new system" (migration provenance timestamp).
- **`system_derived`** — a value computed by a rule, not entered or extracted (e.g. `risks.current_rating`, [07-inference-rules-catalogue.md](07-inference-rules-catalogue.md)). Cites the specific inference rule ID that produced it, not a document or person.

## 4. Confidence Propagation

Confidence does not stay isolated to the record it was assigned to — it needs to be visible wherever that record is used as support for something else, particularly Safety Case claims:

- A `SafetyCaseClaim`'s **effective confidence** is the minimum confidence across its full evidence chain (Evidence → VerificationActivity → PerformanceStandard → CriticalControl), not an average — a claim is only as strong as its weakest supporting fact. This is a deliberate conservative choice: averaging would let one solid piece of evidence mask one weak one.
- Any chain containing a `flag-for-review` item that has not yet been reviewed is surfaced as **unresolved**, not silently treated as confidence 0 or excluded — the Gap Analysis Service ([07-inference-rules-catalogue.md](07-inference-rules-catalogue.md) R7) reports these explicitly rather than letting them disappear from view.

## 5. Corrections & Immutability

Provenance records are **never edited or deleted**. A correction to an entity is: (1) update the entity's current-state row as normal, (2) insert a new `provenance.records` row for that write, `previous_version_id` pointing at the record it supersedes. The full history of any entity is `SELECT * FROM provenance.records WHERE entity_type = ? AND entity_id = ? ORDER BY created_at` — walkable forward or backward, and this is what a Safety Case audit or a regulator's "show me how this record has changed" request is served from.

## 6. What This Enables (concretely, not aspirationally)

- **"Is this safe to rely on?"** — every fact in the Knowledge Graph Explorer and every Safety Case claim can show its confidence and source inline, not as a separate lookup.
- **"Who approved this critical control's classification?"** — walk `provenance.records` for that `Control` row; find the `human_entry` or reviewer-approved `document_extraction` record and its `created_by_person_id`.
- **Migration integrity check** — after Phase 5, every migrated record must have exactly one `v1_migration` provenance record; a record with none is a migration bug, not a data-entry gap, and this is mechanically checkable.
- **Extraction quality monitoring** — aggregate `document_extraction` provenance records by `extraction_run_id` and confidence band to calibrate the thresholds in AI Extraction Spec §6 against real outcomes over time, rather than leaving them as permanent guesses.
