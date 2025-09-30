targetScope = 'subscription'

@minLength(1)
@maxLength(64)
@description('Name of the the environment which is used to generate a short unique hash used in all resources.')
param name string

@minLength(1)
@description('Primary location for all resources')
param location string

@secure()
@description('Oura API Personal Access Token')
param ouraApiToken string

@secure()
@description('GitHub OAuth Client ID')
param githubClientId string = ''

@secure()
@description('GitHub OAuth Client Secret')
param githubClientSecret string = ''

@description('Base URL for OAuth callbacks (e.g., https://your-app.azurewebsites.net)')
param baseUrl string = ''

var resourceToken = toLower(uniqueString(subscription().id, name, location))
var tags = { 'azd-env-name': name }

resource resourceGroup 'Microsoft.Resources/resourceGroups@2021-04-01' = {
  name: '${name}-rg'
  location: location
  tags: tags
}

module resources 'resources.bicep' = {
  name: 'resources'
  scope: resourceGroup
  params: {
    location: location
    resourceToken: resourceToken
    tags: tags
    ouraApiToken: ouraApiToken
    githubClientId: githubClientId
    githubClientSecret: githubClientSecret
    baseUrl: baseUrl
  }
}

output AZURE_LOCATION string = location
output WEB_URI string = resources.outputs.WEB_URI
