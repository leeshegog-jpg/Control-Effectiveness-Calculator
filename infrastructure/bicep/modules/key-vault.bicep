// R0 scaffold placeholder -- Azure Key Vault module.
// One vault per environment, secrets injected into Container Apps at runtime
// -- never committed, never in CI logs (docs/implementation-blueprint/09-configuration-management.md §2).
// Not deployed yet -- this defines shape only; provisioning is an R0 exit item.

@description('Environment name, e.g. dev, test, uat, prod')
param environmentName string

@description('Azure region')
param location string = resourceGroup().location

var keyVaultName = 'kv-sms-${environmentName}'

resource keyVault 'Microsoft.KeyVault/vaults@2023-07-01' = {
  name: keyVaultName
  location: location
  properties: {
    sku: {
      family: 'A'
      name: 'standard'
    }
    tenantId: subscription().tenantId
    enableRbacAuthorization: true
    enableSoftDelete: true
    softDeleteRetentionInDays: 90
  }
}

output keyVaultName string = keyVault.name
output keyVaultUri string = keyVault.properties.vaultUri
