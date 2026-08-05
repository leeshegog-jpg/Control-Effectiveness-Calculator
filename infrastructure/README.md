# Infrastructure as Code

Azure resources — see [docs/implementation-blueprint/13-application-foundation-scaffold.md](../docs/implementation-blueprint/13-application-foundation-scaffold.md) §6 and [docs/implementation-blueprint/06-environment-strategy.md](../docs/implementation-blueprint/06-environment-strategy.md).

- `bicep/modules/` — one Bicep module per Azure resource type (Container Apps, PostgreSQL Flexible Server, Neo4j, Qdrant, Storage, Key Vault, Networking, Identity, Monitoring). Empty at R0 — provisioning is an R0 exit item, not scaffolded as live infrastructure here.
- `bicep/main.bicep` — composition root, parameterized per environment. Not created yet.
- `environments/` — per-environment `.bicepparam` files (dev/test/uat/prod). Empty at R0.

**IaC tool:** Bicep, per the folder naming already established in the approved scaffold — final confirmation is an R0 exit item ([docs/implementation-blueprint/04-implementation-roadmap.md](../docs/implementation-blueprint/04-implementation-roadmap.md)), not re-litigated by this placeholder.
