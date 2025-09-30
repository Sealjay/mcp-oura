# mcp-oura

An Oura MCP (Model Context Protocol) server configured for the OpenAI spec. This server provides access to Oura Ring health data through a FastMCP API, deployable to Azure App Service.

## Features

- **FastMCP Server**: Built with FastMCP for easy MCP tool creation
- **Oura API Integration**: Access daily activity, sleep, readiness, heart rate, and personal info
- **API Key Security**: Secured with API key authentication
- **Azure Deployment**: Ready to deploy to Azure App Service using Azure Developer CLI (azd)
- **Free Tier Compatible**: Configured to use Azure's F1 (free) tier

## Available MCP Tools

The server provides the following tools for querying Oura data:

- `get_daily_activity`: Retrieve daily activity metrics (steps, calories, activity time)
- `get_daily_sleep`: Retrieve sleep data (duration, sleep stages, efficiency)
- `get_daily_readiness`: Retrieve readiness scores and contributing factors
- `get_heart_rate`: Retrieve heart rate measurements
- `get_personal_info`: Retrieve user profile information

## Prerequisites

- [Azure Developer CLI (azd)](https://learn.microsoft.com/azure/developer/azure-developer-cli/install-azd)
- [Python 3.11+](https://www.python.org/downloads/)
- [Oura API Personal Access Token](https://cloud.ouraring.com/personal-access-tokens)
- An Azure subscription

## Getting Your Oura API Token

1. Visit [Oura Cloud Personal Access Tokens](https://cloud.ouraring.com/personal-access-tokens)
2. Log in with your Oura account
3. Click "Create A New Personal Access Token"
4. Give it a name and click "Create"
5. Copy the token - you'll need it for deployment

## Deployment to Azure

### 1. Clone the repository

```bash
git clone https://github.com/Sealjay/mcp-oura.git
cd mcp-oura
```

### 2. Login to Azure

```bash
azd auth login
```

> **Note**: If using a government cloud, configure azd first:
> ```bash
> azd config set cloud.name AzureUSGovernment
> azd auth login
> ```

### 3. Set environment variables

Before deploying, you need to set your Oura API token and a custom API key for securing your MCP server:

```bash
azd env set OURA_API_TOKEN "your-oura-api-token-here"
azd env set MCP_API_KEY "your-custom-api-key-here"
```

Replace `"your-oura-api-token-here"` with your actual Oura API token, and `"your-custom-api-key-here"` with a strong API key you create (this will be used to authenticate requests to your MCP server).

### 4. Deploy to Azure

```bash
azd up
```

This command will:
- Prompt you for an environment name (used as prefix for resource group)
- Ask for Azure location and subscription
- Build your application
- Provision Azure resources (App Service, App Service Plan)
- Deploy the application code

> **Note**: The first deployment may take 5-10 minutes.

### 5. Get your deployment URL

After deployment completes, azd will output your web app URL. You can also retrieve it with:

```bash
azd env get-values | grep WEB_URI
```

## Using the MCP Server

### Health Check

Test that your server is running:

```bash
curl https://your-app-url.azurewebsites.net/health
```

### Calling MCP Tools

All tool requests require the `X-API-Key` header with the API key you configured:

```bash
curl -X POST https://your-app-url.azurewebsites.net/mcp/tools/call \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-custom-api-key-here" \
  -d '{
    "name": "get_daily_sleep",
    "arguments": {
      "start_date": "2024-01-01",
      "end_date": "2024-01-07"
    }
  }'
```

### Example Tool Calls

#### Get Daily Activity
```json
{
  "name": "get_daily_activity",
  "arguments": {
    "start_date": "2024-01-01",
    "end_date": "2024-01-07"
  }
}
```

#### Get Sleep Data
```json
{
  "name": "get_daily_sleep",
  "arguments": {
    "start_date": "2024-01-01",
    "end_date": "2024-01-07"
  }
}
```

#### Get Readiness Score
```json
{
  "name": "get_daily_readiness",
  "arguments": {
    "start_date": "2024-01-01",
    "end_date": "2024-01-07"
  }
}
```

## Local Development

### Setup

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r src/requirements.txt
```

3. Set environment variables:
```bash
export OURA_API_TOKEN="your-oura-api-token"
export MCP_API_KEY="your-api-key"
```

4. Run the server:
```bash
cd src
python app.py
```

The server will start on `http://localhost:8000`

### Testing Locally

```bash
curl http://localhost:8000/health

curl -X POST http://localhost:8000/mcp/tools/call \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-api-key" \
  -d '{"name": "get_personal_info", "arguments": {}}'
```

## Updating Your Deployment

After making changes, redeploy with:

```bash
azd deploy
```

## Cost Considerations

This template uses the F1 (free) tier for App Service by default. The free tier includes:
- 10 free apps
- 1 GB disk space
- 165 MB RAM
- No custom domains

For production use or higher performance, consider upgrading to a paid tier. See the [Azure App Service pricing page](https://azure.microsoft.com/en-us/pricing/details/app-service/windows/) for details.

To change the tier, edit `infra/resources.bicep` line 61:
- `F1`: Free tier
- `D1`: Shared tier (discounted developer rate)
- `B1`: Basic tier (recommended for production)

## Security Best Practices

1. **Never commit secrets**: Keep your `OURA_API_TOKEN` and `MCP_API_KEY` secure
2. **Rotate API keys regularly**: Update your keys periodically
3. **Use Azure Key Vault**: For production, consider using Azure Key Vault for secret management
4. **Enable monitoring**: Use Azure Monitor and Application Insights to track usage

## Troubleshooting

### Deployment Issues

View logs:
```bash
azd monitor --logs
```

Or through Azure Portal:
1. Navigate to your App Service
2. Go to "Log stream" or "Diagnose and solve problems"

### API Errors

- **401 Unauthorized**: Check your `MCP_API_KEY` is correct
- **Oura API errors**: Verify your `OURA_API_TOKEN` is valid
- **No data returned**: Ensure your Oura Ring has synced recently

## Resources

- [FastMCP Documentation](https://github.com/jlowin/fastmcp)
- [Oura API Documentation](https://cloud.ouraring.com/docs/)
- [OpenAI MCP Specification](https://platform.openai.com/docs/mcp)
- [Azure Developer CLI Documentation](https://learn.microsoft.com/azure/developer/azure-developer-cli/)

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
