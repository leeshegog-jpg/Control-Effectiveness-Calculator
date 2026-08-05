// R0 scaffold -- composition root, parameterized per environment via
// infrastructure/environments/*.bicepparam.
// Only the Key Vault module is wired at R0 (secrets management is the one
// piece of infra this phase's engineering-foundation scope covers).
// Container Apps, Postgres Flexible Server, Storage, Networking, Identity,
// and Monitoring modules exist as placeholders only
// (docs/implementation-blueprint/13-application-foundation-scaffold.md §6)
// -- full provisioning is an R0 exit item, not implemented here.

@description('Environment name, e.g. dev, test, uat, prod')
param environmentName string

@description('Azure region')
param location string = resourceGroup().location

module keyVault 'modules/key-vault.bicep' = {
  name: 'keyVaultDeploy'
  params: {
    environmentName: environmentName
    location: location
  }
}

output keyVaultName string = keyVault.outputs.keyVaultName
