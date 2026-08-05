# TP Risk Management SMS — Safety Knowledge Graph Platform

**Status: R0 — Repository Initialisation. Design Baseline v1.1 (Approved and Frozen, 2026-08-04). No business functionality implemented — engineering foundation only.**

Enterprise Safety Knowledge Graph and AI Risk Intelligence Platform for Village Roadshow Theme Parks (VRTP) — replacing the V1 static-HTML Safety Management System suite (still present at this repository's root during the strangler-fig migration, see [Legacy Tools](#legacy-tools-root-level-static-files) below) with a governed, multi-user platform: PostgreSQL system of record, Neo4j knowledge graph projection, AI-assisted document extraction, and a generated Safety Case Demonstration Engine for Chapter 9A (major amusement parks) compliance.

## Start here

| If you want to... | Read |
|---|---|
| Understand the architecture decisions | [docs/PLATFORM_ARCHITECTURE_V2.md](docs/PLATFORM_ARCHITECTURE_V2.md) |
| See the full Design Baseline (ontology, schema, OpenAPI, Safety Case model) | [docs/knowledge-graph/README.md](docs/knowledge-graph/README.md) |
| Understand how the codebase is organised and why | [docs/implementation-blueprint/README.md](docs/implementation-blueprint/README.md) |
| Set up a local dev environment | [DEVELOPMENT.md](DEVELOPMENT.md) |
| Contribute a change | [CONTRIBUTING.md](CONTRIBUTING.md) |
| Raise or review an Architecture Change Request | [.acr/README.md](.acr/README.md) |
| See implementation decisions made outside the frozen baseline | [.adr/README.md](.adr/README.md) |

## Repository layout

```
apps/web/           React + TypeScript + Vite + Tailwind + shadcn/ui frontend
apps/api/            FastAPI backend
packages/            Shared code: shared-types, api-client, ontology-client, ui-components
ontology/            Ontology content (governed data, not code)
database/            PostgreSQL migrations/seeds, Neo4j constraints/migrations
infrastructure/      Azure Bicep + per-environment parameters
docs/                Design Baseline v1.1 + Implementation Blueprint (authoritative)
tests/               unit / integration / contract / e2e / graph / ontology / ai-extraction / performance / security / uat
scripts/             Dev tooling
.adr/                Architecture Decision Records (implementation-time decisions)
.acr/                Architecture Change Requests (changes to the frozen baseline)
```

Full per-folder rationale: [docs/implementation-blueprint/01-repository-structure.md](docs/implementation-blueprint/01-repository-structure.md) and [docs/implementation-blueprint/13-application-foundation-scaffold.md](docs/implementation-blueprint/13-application-foundation-scaffold.md).

## Governance

The Design Baseline (architecture, ontology, PostgreSQL schema, Neo4j model, OpenAPI contract, Safety Case model) is **frozen at v1.1**. Any change to it requires an Architecture Change Request — see [docs/implementation-blueprint/02-development-standards.md](docs/implementation-blueprint/02-development-standards.md) §7. Do not edit `docs/knowledge-graph/` directly.

## License

Proprietary — see [LICENSE](LICENSE). Licensing terms are `TO_BE_CONFIRMED` pending VRTP legal review; this is not an open-source project by default.

---

## Legacy tools (root-level static files)

This repository also hosts pre-existing standalone tools at the root, unrelated to the platform above and predating it. They are left in place, unmodified, during the migration and are out of scope for the platform's build/lint/CI tooling.

# URL Parser — Excel Edition

A zero-dependency, browser-based tool that reads URLs from an Excel or CSV file
and instantly parses each one into its individual components.

## Features

- **Drag-and-drop** Excel (`.xlsx`, `.xls`) or CSV upload
- **Auto-detects** which column contains URLs — or let you specify it
- Parses every URL into: scheme, username, password, hostname, port, path, query string, individual query parameters, fragment
- **Sortable, filterable table** with pagination (50 rows/page)
- **Stats bar**: total, valid, invalid counts; unique schemes and hosts
- **Detail panel**: click any row for a full breakdown including a query-parameter table
- **Export**: copy to clipboard, download as CSV, or download as Excel
- Runs entirely in the browser — no data is uploaded anywhere

### Usage

1. Open `index.html` in any modern browser (Chrome, Firefox, Edge, Safari).
2. Drop your Excel file onto the upload area, or click **Browse file**.
3. Select the sheet and, optionally, specify the URL column header.
4. Click **Parse URLs**.

A sample file `sample_urls.xlsx` is included to try immediately.

### File format

Your Excel file needs at least one column of URLs. The column can have any header
name — the tool looks for a header containing "url" first, then scores each column
by how many cells look like URLs and picks the best match.

| ID | URL | Category | Notes |
|----|-----|----------|-------|
| 1  | https://example.com/path?q=1 | Web | … |

### VRTP Agent Investigation Pipeline

`incident-report.html` now includes a **🔬 Run Agent Investigation** action alongside the standard incident register. It submits the report to a local agent pipeline (Investigation Agent → Compliance Agent → Safety Case Trigger check) running on the reporting machine, then links the resulting investigation, compliance and safety-case outputs — plus a printable report — back onto the incident record.

The pipeline itself (PowerShell HTTP server + the two Claude-driven agents) lives in [`local-automation/`](local-automation/README.md) and only runs locally; it cannot run on a static host like GitHub Pages. Without it running, the page still works as a standard incident register (`Save Incident`).

## AI Hazard, Bow-Tie & Critical Control Generator

[`bowtie-ccm-generator.html`](bowtie-ccm-generator.html) is a self-contained hazard/bow-tie/critical-control-management tool, seeded with the live 14-hazard / 108-row pilot register. It is grounded directly in VRTP's own documents — GOHS2.1.2 Managing Risks to H&S Standard, the VRTP Risk Matrix, OHS-PRO-003 Bow-Tie Analysis Procedure, GOHS-REF-SMS-001 Control/Support/Verification Register Guide, and GOHS-GN-HAZID-001 Hazard Identification Guidance — not generic risk boilerplate. Four tabs:

- **Register** — searchable, filterable hazard → risk → control table
- **Bow-Tie Diagram** — threats/preventive controls, top event, consequences/mitigative controls, critical-control flags
- **Critical Control Management** — critical-control register with verification due-status, plus the 3-gate Control/Support/Verification classification reference
- **AI Hazard Generator** — 8-step wizard: hazard statement builder, VRTP Risk Matrix scoring, the 3-gate control test, critical-control test, effectiveness-based current-risk suggestion, SFARP gate (blocks "risk is acceptable"), target risk & actions. Includes an **Import AI Draft (JSON)** box so a hazard drafted in conversation with an AI assistant can be pasted in for validation before saving to the register.

Runs entirely client-side (no server, no data leaves the browser) — open the file directly or reach it from the Hub nav / Supporting Tools grid.

Last updated: 28 July 2026.
