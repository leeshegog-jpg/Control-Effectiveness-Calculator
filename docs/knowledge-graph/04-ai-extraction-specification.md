# AI Extraction Specification
**Status: DRAFT — controlled design document. Requires approval before implementation.**
**Parent:** [01-enterprise-knowledge-graph-specification.md](01-enterprise-knowledge-graph-specification.md)
**Depends on:** [03-postgresql-schema.sql](03-postgresql-schema.sql) `ontology.extraction_rules`, [05-knowledge-provenance-model.md](05-knowledge-provenance-model.md)

---

## 1. Purpose & Scope

Turns uploaded documents (procedures, manuals, checklists, risk assessments, investigation reports, audit reports) and submitted incident reports into structured, provenance-tagged draft records (Hazard, Risk, Control, Verification requirement, Evidence reference) for human review and commit. This formalizes two things that already exist informally in V1: `bowtie-ccm-generator.html`'s "Import AI Draft (JSON)" schema, and `local-automation`'s Investigation Agent → Compliance Agent pipeline. Neither runs server-side today, and one (`OHS_Command_Centre/hazard_register.html`) calls the LLM directly from the browser with an exposed API key — this spec replaces both with one governed, server-side pipeline.

## 2. Pipeline Stages

```
Document Upload → Parse → OCR (if needed) → Chunk → LLM Extraction → Ontology Validation
    → Confidence Routing → [Auto-accept | Human Review Queue | Reject] → Commit → Graph Sync
```

| Stage | Component | Detail |
|---|---|---|
| 1. Upload | FastAPI `Ingest` service | Writes file to Blob Storage, creates `safety.documents` row (`extraction_status = pending`) |
| 2. Parse | Apache Tika / Unstructured | Extracts raw text + structure (headings, tables) by file type (PDF, DOCX, XLSX) |
| 3. OCR | Tesseract | Only invoked when Parse yields no/low text (scanned PDFs, images) |
| 4. Chunk | Extraction service | Splits parsed text into semantically coherent chunks (by heading/section, not fixed token windows, where structure is available) |
| 5. Extract | LlamaIndex + Claude (Anthropic API, server-side key only) | Per chunk, produces one or more draft records against the schema in §4, using the prompt pattern in §5 |
| 6. Validate | Ontology Service | Every classification field in the draft is matched against `ontology.concepts` (+ aliases); unmatched terms are held as `proposed_concept` candidates, never silently coerced to the nearest existing concept |
| 7. Route | Extraction service, per `ontology.extraction_rules` | See §6 |
| 8. Review | Human reviewer, via Document AI Intelligence Engine UI | Approves / edits / rejects flagged drafts |
| 9. Commit | FastAPI REST layer | Writes to Postgres inside a transaction, creates a `provenance.records` row (`source_type = document_extraction`, `extraction_run_id`, `confidence`) |
| 10. Sync | Graph Sync Service | Propagates the committed record into Neo4j (EKG spec §4) |

Every run is tracked by an `extraction_run_id` (uuid) spanning stages 4–9, so a full run can be replayed/audited end-to-end.

## 3. Supported Input Types

PDF (native + scanned), DOCX, XLSX/CSV (register imports — e.g. migrating the `bowtie-ccm-generator.html` 108-row pilot register), plain text, and structured JSON matching §4 directly (the successor to V1's "Import AI Draft" box — a human or another AI assistant can still paste a pre-drafted hazard for validation, bypassing stages 2–5).

## 4. Extraction Target Schema

Extends V1's `bowtie-ccm-generator.html` AI-draft JSON shape (which already had `threats`/`consequences`/`controls`/`gates`/`effectiveness` fields validated by `validateDraft()`) into the full canonical model:

```json
{
  "extraction_run_id": "uuid",
  "source_document_id": "uuid",
  "source_span": { "page": 4, "section": "5.2 Isolation Procedure", "char_start": 1204, "char_end": 1687 },
  "hazard": {
    "name": "string",
    "description": "string",
    "category": { "matched_concept_id": "uuid | null", "proposed_label": "string", "confidence": 0.0 },
    "energy_source": { "matched_concept_id": "uuid | null", "proposed_label": "string", "confidence": 0.0 }
  },
  "risk": {
    "description": "string",
    "cause": "string",
    "inherent_likelihood": "1-5 | null",
    "inherent_consequence": "1-5 | null"
  },
  "controls": [{
    "description": "string",
    "type": "Prevention | Mitigation",
    "hierarchy": { "matched_concept_id": "uuid | null", "proposed_label": "string", "confidence": 0.0 },
    "gates": [null, null, null],
    "classification_suggestion": "Control | Support | Verification | null"
  }],
  "verification_requirements": [{ "description": "string", "suggested_frequency": "string | null" }],
  "evidence_refs": [{ "description": "string", "type_hint": "string" }],
  "standards_cited": ["string"],
  "extraction_confidence_overall": 0.0
}
```

**Worked example (from your spec's sample sentence):**

> Input: *"Operator must isolate hydraulic pressure before maintenance."*

```json
{
  "hazard": { "name": "Stored hydraulic energy", "energy_source": { "proposed_label": "Hydraulic" } },
  "risk": { "description": "Unexpected movement during maintenance" },
  "controls": [{ "description": "Hydraulic isolation procedure", "type": "Prevention",
                 "hierarchy": { "proposed_label": "Isolation" } }],
  "verification_requirements": [{ "description": "Isolation confirmation" }],
  "evidence_refs": [{ "description": "Maintenance record", "type_hint": "record" }]
}
```

This is the exact mapping given in your original brief — confirming the schema above is fit for purpose against it.

## 5. Prompt Construction

Prompts are **assembled at call time**, not hardcoded — this is the direct fix for V1's `OHS_Command_Centre/hazard_register.html`, which had fixed `CATEGORIES`/`HIERARCHY_OPTS` arrays baked into the client bundle:

1. Pull the live `Concept` + `Alias` list for every relevant `OntologyScheme` (Hazard, Energy Source, Control, Consequence, Evidence, Verification) from `ontology.concepts`/`ontology.concept_aliases`.
2. Pull few-shot examples from `ontology.extraction_rules.example_positive` / `example_negative` for the schemes in play.
3. Instruct the model to prefer an existing concept label; if none fits, populate `proposed_label` and leave `matched_concept_id` null rather than forcing a bad match (this is what feeds the ontology curator's new-concept review queue, not a extraction error).
4. Instruct the model to cite `source_span` for every extracted fact — extraction with no traceable source span is rejected outright regardless of confidence (provenance model §3).

## 6. Confidence Routing

Governed by `ontology.extraction_rules`, scoped per target concept/scheme. **Starting defaults below are exactly that — defaults to calibrate against real extraction runs, not fixed thresholds:**

| Overall confidence | Default action |
|---|---|
| ≥ 0.85 | `auto-accept` — commits directly, still fully provenance-tagged and reversible |
| 0.60 – 0.84 | `flag-for-review` — enters the human review queue |
| < 0.60 | `reject` — not committed; source span + reasoning logged for the curator, not silently discarded |

Overrides: any extraction touching a **critical control**, **SFARP justification**, or a **regulatory notification determination** (WHSQ/OSR/Chapter 9A) is **always** `flag-for-review` regardless of confidence score — mirrors V1's SFARP gate (which already refuses to accept "risk is acceptable" as a justification, `bowtie-ccm-generator.html`) and the local-automation Compliance Agent's Safety Case Trigger check, both of which treat these as human-decision points, not automatable ones.

## 7. Incident Pipeline (specialization of the above)

Ports `local-automation`'s Investigation Agent → Compliance Agent → Safety Case Trigger sequence into this same pipeline, as an `Incident`-specific extraction profile:

1. **Investigation Agent** — extracts immediate cause / root cause / contributing factors from the incident narrative into `safety.investigations`.
2. **Compliance Agent** — evaluates WHSQ/OSR (Chapter 9A) notification obligations against [09-regulatory-knowledge-model.md](09-regulatory-knowledge-model.md); **always** flag-for-review per §6 override.
3. **Safety Case Trigger check** — if the compliance output signals an ADI (Amusement Device Incident) on a Major Amusement Park asset, creates a draft `SafetyCaseClaim` for review rather than auto-publishing one.

Unlike V1, this runs as a FastAPI background task reachable from any client, not a Windows-only PowerShell listener on `localhost:8765` — removing the "only works on one machine with the vault open" constraint noted in `local-automation/README.md`.

## 8. Human Review Workflow

Reviewers see, per draft: the extracted fields, the source document span (rendered inline, not just cited), the matched/proposed concept for each classification field, and the confidence score. Actions: **Approve as-is**, **Edit then approve**, **Reject** (with reason — feeds back into calibrating §6 thresholds over time), **Propose new concept** (routes to the ontology curator, per EKG spec §6 governance — a reviewer can surface a gap in the vocabulary but cannot unilaterally publish a new concept).

## 9. Security

- The Anthropic API key is held server-side only (Azure Key Vault or Container Apps secret), never sent to or stored in the browser — the specific defect found in `OHS_Command_Centre/hazard_register.html` (`localStorage: gohs__apikey`) does not recur.
- Uploaded documents may contain personal information (witness names, injury details) — extraction prompts do not need to and must not forward document content to any third-party service other than the configured Anthropic endpoint; no other external calls in the pipeline.
- Rejected/low-confidence extractions retain their source span for audit but are not surfaced outside the review queue.

## 10. Failure Handling

Parse/OCR failure → `documents.extraction_status = 'failed'`, logged with reason, document remains available for manual re-attempt or manual entry (never silently dropped). LLM call failure/timeout → retried with backoff (bounded, e.g. 3 attempts); persistent failure marks the run failed and notifies the uploader, it does not silently produce a partial/empty draft.
