// R0 scaffold placeholder. Non-secret environment overrides only -- secret
// values are Key Vault-injected at runtime, never here
// (docs/implementation-blueprint/09-configuration-management.md §3).
// main.bicep does not exist yet -- provisioning is an R0 exit item
// (docs/implementation-blueprint/04-implementation-roadmap.md, R0).
using '../bicep/main.bicep'

param environmentName = 'dev'
param location = 'australiaeast'
