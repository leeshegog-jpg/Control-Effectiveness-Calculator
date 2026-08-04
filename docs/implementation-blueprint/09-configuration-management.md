# 09 — Configuration Management
**Status: DRAFT — Phase 2.1 Implementation Blueprint. Baseline: Design Baseline v1.0 (frozen).**

---

## 1. Environment Variables

| Variable | Purpose | Environments |
|---|---|---|
| `DATABASE_URL` | Postgres connection string | All (value differs) |
| `NEO4J_URI`, `NEO4J_USER`, `NEO4J_PASSWORD` | Neo4j connection | All |
| `QDRANT_URL` | Vector search connection | All |
| `AZURE_BLOB_CONNECTION_STRING` | Document/evidence storage | All |
| `ANTHROPIC_API_KEY` | AI Extraction Service + Demonstration Engine LLM calls | All — **Key Vault-injected at runtime, never in a `.env` file, never client-side (architecture §1.4 finding 3)** |
| `ENTRA_TENANT_ID`, `ENTRA_CLIENT_ID`, `ENTRA_CLIENT_SECRET` | AuthN/AuthZ | All (per-environment app registrations, [06-environment-strategy.md](06-environment-strategy.md)) |
| `OPENAPI_SPEC_VERSION` | Contract version pin for client codegen | All |
| `EXTRACTION_CONFIDENCE_OVERRIDE_*` | Per-environment override of [04](../knowledge-graph/04-ai-extraction-specification.md) §6 default thresholds, for calibration during Dev/Test | Dev, Test only |

## 2. Secrets & Azure Key Vault

All secrets (API keys, connection strings with credentials, Entra client secrets) live in **Azure Key Vault**, one vault per environment, injected into Container Apps at runtime — never committed, never in CI logs, never in a plain environment file beyond `.env.example` (which contains variable *names* only, no values). PR validation's secrets-in-diff scan ([07-cicd-architecture.md](07-cicd-architecture.md) §6) is the backstop, not the primary control.

## 3. Configuration Hierarchy

```
Base config (checked into repo, non-secret defaults)
  → Environment-specific overrides (infrastructure/environments/*, non-secret)
    → Key Vault secrets (injected at container start, secret values only)
```

No layer duplicates another — a value lives in exactly one place in this hierarchy, avoiding the "same setting drifts across places" failure mode this entire document set has been correcting for at the data-model level (architecture §1.4 finding 1) applied here to configuration.

## 4. Feature Flags

| Flag | Purpose | Default |
|---|---|---|
| `DEMONSTRATION_AUTO_GENERATE` | Whether the Demonstration Engine runs on-demand only or also on a schedule | Off in Dev/Test, on in UAT/Prod once R7 ships |
| `EXTRACTION_AUTO_ACCEPT_ENABLED` | Master switch for [04](../knowledge-graph/04-ai-extraction-specification.md) §6 auto-accept routing — can be forced to "flag-for-review always" during calibration | Auto-accept off until golden-set accuracy is validated ([08-testing-strategy.md](08-testing-strategy.md) §6) |
| `ONTOLOGY_CURATOR_APPROVAL_REQUIRED` | Whether new concepts require curator approval before use, or can be provisionally used while pending (Dev convenience only) | Required in Test/UAT/Prod, relaxed in Dev |
| `MOC_RISK_REASSESSMENT_ENFORCED` | Whether `management_of_change.risk_reassessment_required = true` blocks closing a MOC record without a linked reassessment | On everywhere — this one should not be flagged off outside Dev, since it's a regulatory-adjacent control ([11](../knowledge-graph/11-safety-case-demonstration-model.md) §7.2a) |

Feature flags are a deployment-time convenience, not a substitute for the critical-item overrides already fixed in the design baseline (§4 above, [04](../knowledge-graph/04-ai-extraction-specification.md) §6, [11](../knowledge-graph/11-safety-case-demonstration-model.md) §7.3) — those overrides are not flaggable at all, by design.

## 5. Licensing Keys

Placeholder configuration only — no license currently held. Once VRTP obtains a license permitting redistribution of ISO 45001 / AS/NZS 3533 / AS/NZS 4024 / ISO 17842 clause text inside the platform ([09-regulatory-knowledge-model.md](../knowledge-graph/09-regulatory-knowledge-model.md) §2), a `STANDARDS_LICENSE_KEY` config value gates whether `regulatory.requirements.text` may store verbatim clause text vs. paraphrase-only. Until then, this flag stays unset and the platform behaves as if unlicensed (paraphrase + citation only) — the safe default, not an assumption to relax without confirmed license terms.
