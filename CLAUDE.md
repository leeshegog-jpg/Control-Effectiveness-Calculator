# Claude Code Operating Rules — TP Risk Management SMS

## 1. Purpose

This repository is the Enterprise Safety Knowledge Graph & AI Risk Intelligence Platform for a Queensland major amusement park environment.

Claude Code is an implementation assistant. It must preserve the repository's approved business logic, architecture, contracts, governance boundaries, and migration strategy. The repository's authoritative documents take precedence over assumptions, generic patterns, or convenience.

## 2. Authoritative Sources

Use this precedence order when sources conflict:

1. Explicit user instruction in the current session.
2. Approved Architecture Change Requests (ACRs) and accepted Architecture Decision Records (ADRs), where applicable.
3. The current Design Baseline and authoritative `docs/knowledge-graph/` / implementation-blueprint documents.
4. The current OpenAPI contract and database/Neo4j definitions.
5. Existing implemented V1 business logic and existing platform behaviour.
6. Existing code and tests.
7. General framework conventions.

Do not invent missing business rules. If evidence is absent, state `TO BE CONFIRMED` and stop only where the missing decision genuinely blocks the authorised work.

## 3. Governance Boundary — GO Is Mandatory

Do not implement an unauthorised change merely because it appears logical, necessary, or already represented in a contract.

A literal user authorisation containing `GO` is required before modifying implementation files when the task is subject to an explicit implementation boundary.

Examples:

- `GO — implement Action API`
- `GO — fix safety.py:361–362 datetime type-shadow via import alias only`

If the user has not provided the required GO, perform discovery, reconciliation, impact analysis, or review only. Do not modify the governed implementation surface.

An ACR approval is governance approval, not automatically implementation authorisation, unless the user explicitly says otherwise.

## 4. Preserve the Frozen Baseline

The Design Baseline is frozen unless changed through the approved ACR process.

Never silently:

- add an ontology concept;
- add or change a relationship type;
- change a frozen database column;
- change an OpenAPI contract outside the authorised scope;
- add speculative Neo4j edges;
- change existing V1 business rules;
- resolve a `TO_BE_CONFIRMED` item by assumption;
- introduce a new taxonomy because it appears cleaner;
- alter graph property lists merely to make an implementation convenient.

If a proposed implementation conflicts with the frozen baseline, identify the conflict and require the appropriate governance decision.

## 5. Strangler-Fig Migration Rule

V1 remains the authoritative business-logic reference during migration.

Before implementing a domain change:

1. Discover the V1 behaviour.
2. Reconcile it against the frozen platform contract.
3. Identify deliberate differences.
4. Check existing implementation and tests.
5. Implement only the authorised delta.

Do not rewrite working V1 behaviour merely to make the new implementation aesthetically cleaner.

## 6. Traceability Chain

For every implementation task, maintain traceability through the relevant chain:

`Requirement / V1 rule → Design Baseline / ACR / ADR → OpenAPI / schema → ORM → DTO → repository → service → router → graph sync → tests → evidence`

Not every layer exists for every domain. Do not manufacture layers or relationships that are not required.

For graph work, verify the relationship and node-property requirements against the authoritative graph specification before changing `sync_service.py`.

## 7. Scope Discipline

Work in the smallest bounded slice that satisfies the authorised task.

Before editing:

- identify the exact files expected to change;
- identify dependencies;
- identify relevant contract/schema/graph implications;
- identify tests that must change or be added;
- identify unrelated defects and leave them untouched unless separately authorised.

Do not perform opportunistic refactoring.
Do not fix unrelated lint, typing, naming, formatting, or architecture issues during an authorised bounded change.

If the authorised scope expands, stop and obtain explicit direction/GO for the expansion.

## 8. Discovery Before Modification

For a domain implementation, inspect the relevant layers before editing:

1. frozen schema / OpenAPI;
2. ORM model;
3. DTOs;
4. repository;
5. service;
6. router;
7. graph synchronisation;
8. existing tests;
9. related domain routers/services/models;
10. V1 implementation where business-rule reconciliation is required.

Do not infer that a layer needs changing simply because another layer changed.

## 9. Tests and Validation

Use the repository's existing validation commands and test strategy.

Before declaring a slice complete:

- run the relevant unit tests;
- run relevant integration/contract/graph tests where applicable;
- run lint/type checking applicable to changed files;
- run contract/schema/ontology validation when those artefacts are touched;
- inspect the final diff;
- verify that only authorised files changed;
- confirm no unintended schema, OpenAPI, ontology, Neo4j, or graph-property changes occurred.

Do not claim a test passed unless it actually ran and passed.

## 10. OpenAPI and Shared Types

If `10-openapi.yaml` changes, verify whether `packages/shared-types` must be regenerated under the repository's development standards.

Do not add endpoints because a route would be convenient. The OpenAPI contract is authoritative for contracted API surface.

If a required implementation is absent from the contract, identify it as a contract gap rather than silently inventing an endpoint.

## 11. Graph Synchronisation

Treat PostgreSQL persistence and Neo4j projection as distinct concerns.

Do not create graph edges merely because relational foreign keys exist.
Do not create node properties merely because an ORM field exists.
Do not change established graph node property lists without explicit authority.

Every graph change must be traceable to an approved relationship/property requirement.

## 12. Safety and Regulatory Logic

This is a safety-critical/high-risk operating context.

Do not invent regulatory obligations, risk criteria, notification rules, critical-control requirements, or safety-case claims.

Where relevant, preserve traceability to:

- WHS Act 2011 (Qld);
- WHS Regulation 2011 (Qld), including Chapter 9A where applicable;
- applicable Codes of Practice;
- ISO 45001;
- ISO 31000;
- applicable AS/AS-NZS standards;
- approved VRTP business rules and procedures.

Regulatory interpretation must remain evidence-based. A `TO_BE_CONFIRMED` marker is preferable to an unsupported conclusion.

## 13. Incident / Action / Investigation Boundary

Do not assume that a relational association automatically requires a graph relationship.

For Incident-domain work, preserve the established boundaries around:

- Incident;
- Investigation;
- Action;
- Evidence;
- Incident–Hazard links;
- `REVEALS`;
- `INVESTIGATED_AS`;
- `TRIGGERS`.

Check the current ACR/ADR and implementation state before modifying these areas.

## 14. Context Management — Do Not Stop Prematurely

Long Claude Code sessions can accumulate substantial context through file reads, tool calls, diffs, CI output, and prior discussion.

Do NOT terminate an authorised task merely because the conversation has become long.

When context is becoming a material constraint:

1. Finish the smallest safe checkpoint currently in progress.
2. Use `/compact` where appropriate to preserve the active task context.
3. If a clean context boundary is preferable, prepare a concise handoff containing:
   - current commit/branch;
   - authorised scope;
   - completed work;
   - outstanding work;
   - files changed;
   - tests run/results;
   - governance decisions;
   - exact next action;
   - whether further GO is required.
4. Recommend a fresh session when continuation in the current context creates a meaningful risk of lost or corrupted context.

Do not repeatedly re-read the entire repository when targeted inspection is sufficient.

## 15. Recovery From an Unexpected Stop

If a model/tool turn stops unexpectedly:

1. Do not assume the requested change was completed.
2. Inspect `git status` and the current diff.
3. Identify the last completed operation.
4. Check whether files were partially modified.
5. Run the smallest relevant validation needed to establish state.
6. Continue from the verified state rather than restarting blindly.

If the stop appears to be a Claude/API/context/tooling failure, report the failure mode separately from repository status.

## 16. Do Not Hide Uncertainty

Use explicit status labels:

- `CONFIRMED`
- `TO BE CONFIRMED`
- `BLOCKED`
- `DEFERRED`
- `AUTHORISED`
- `NOT AUTHORISED`

Never convert an unknown into a confident statement merely to keep implementation moving.

## 17. Commit and PR Discipline

Use Conventional Commits consistent with the repository standards.

Before committing:

- inspect `git diff`;
- inspect `git status`;
- confirm changed files are within scope;
- confirm tests/validation results;
- confirm no governance boundary was crossed.

Do not merge a PR unless the user has explicitly authorised the merge where a merge GO is required.

A green CI result is evidence of technical validation; it is not automatically governance approval.

## 18. Completion Report

When an authorised implementation slice is complete, report in this order:

### Status
`COMPLETE`, `BLOCKED`, or `PARTIAL`

### Scope
What was authorised and what was actually changed.

### Files Changed
Exact paths only.

### Validation
Exact tests/checks run and their results.

### Governance
ACR/ADR/GO references relevant to the change.

### Remaining Items
Only genuinely outstanding items. Mark each `TO BE CONFIRMED`, `BLOCKED`, or `DEFERRED` where applicable.

### Next Step
One bounded next action. Do not silently begin it.

## 19. Session Handoff Format

When a session needs to end because of context, tool, service, or user boundary, produce a compact handoff that another Claude Code session can consume directly:

```text
PROJECT: TP Risk Management SMS
BRANCH: <branch>
COMMIT: <sha>

AUTHORISED SCOPE:
- <scope>

COMPLETED:
- <item>

NOT COMPLETED:
- <item>

FILES CHANGED:
- <path>

VALIDATION:
- <command/result>

GOVERNANCE:
- <ACR/ADR/GO>

OPEN ITEMS:
- <item/status>

NEXT ACTION:
- <single bounded action>

GO REQUIRED:
- YES/NO — <exact reason>
```

## 20. Behavioural Rule

Be decisive within the authorised boundary.

Do not stop because a task is difficult. Stop because a real boundary, missing decision, failed validation, unavailable dependency, or service/tool failure requires it.

Do not ask for confirmation for every ordinary implementation step once the scope and GO are clear.

Do not expand the scope without authority.

The objective is: **bounded execution, traceable decisions, evidence-based validation, and no silent architecture or business-rule drift.**
