# mcp-oura

An Oura MCP (Model Context Protocol) server configured for the OpenAI spec. This server provides access to Oura Ring health data through a FastMCP API, deployable to Azure App Service.

## Features

- **FastMCP Server**: Built with FastMCP for easy MCP tool creation
- **Oura API Integration**: Access daily activity, sleep, readiness, heart rate, and personal info
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

Before deploying, set your Oura API token:

```bash
azd env set OURA_API_TOKEN "your-oura-api-token-here"
```

Replace `"your-oura-api-token-here"` with your actual Oura API token from the previous step.

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

The server runs as an MCP streamable-http server at `/mcp` endpoint. You can connect to it using any MCP-compatible client.

### Example with MCP Client

```python
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

# Connect to your deployed server
async with stdio_client(StdioServerParameters(
    command="python",
    args=["-m", "httpx", "https://your-app.azurewebsites.net/mcp"],
)) as (read, write):
    async with ClientSession(read, write) as session:
        # Initialize the connection
        await session.initialize()
        
        # List available tools
        tools = await session.list_tools()
        print(f"Available tools: {tools}")
        
        # Call a tool
        result = await session.call_tool("get_daily_activity", {
            "start_date": "2024-01-01",
            "end_date": "2024-01-07"
        })
        print(result)
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
```

4. Run the server:
```bash
cd src
python app.py
```

The server will start on `http://localhost:8000/mcp`

### Testing Locally

Use an MCP-compatible client to connect to `http://localhost:8000/mcp` using the streamable-http transport.

## Securing Your Deployment

The basic deployment does not include authentication. For production use, consider:

1. **Azure App Service Authentication**: Enable built-in authentication with Azure AD, Microsoft accounts, or other identity providers
2. **API Management**: Use Azure API Management to add API key authentication, rate limiting, and monitoring
3. **Virtual Network**: Deploy to a virtual network and restrict access
4. **Managed Identity**: Use Azure Managed Identity for secure access to Azure resources

To enable Azure App Service Easy Auth:
```bash
az webapp auth update --resource-group <your-rg> --name <your-app-name> \
  --enabled true --action LoginWithAzureActiveDirectory
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

- **Oura API errors**: Verify your `OURA_API_TOKEN` is valid and not expired
- **No data returned**: Ensure your Oura Ring has synced recently
- **Connection issues**: Check that your App Service is running and accessible

## Resources

- [FastMCP Documentation](https://github.com/jlowin/fastmcp)
- [Oura API Documentation](https://cloud.ouraring.com/docs/)
- [Model Context Protocol Specification](https://modelcontextprotocol.io/)
- [Azure Developer CLI Documentation](https://learn.microsoft.com/azure/developer/azure-developer-cli/)

## License

This project is licensed under the MIT License.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
