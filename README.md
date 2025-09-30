# mcp-oura

An Oura MCP (Model Context Protocol) server configured for the OpenAI spec. This server provides access to Oura Ring health data through a FastMCP API, deployable to Azure App Service.

## Features

- **FastMCP Server**: Built with FastMCP for easy MCP tool creation
- **GitHub OAuth Authentication**: Secure your server with GitHub OAuth authentication
- **Oura API Integration**: Access daily activity, sleep, readiness, heart rate, and personal info
- **Azure Deployment**: Ready to deploy to Azure App Service using Azure Developer CLI (azd)
- **Free Tier Compatible**: Configured to use Azure's F1 (free) tier

## Available MCP Tools

The server provides the following tools for querying Oura data:

### Basic Data Retrieval Tools

- `get_daily_activity`: Retrieve daily activity metrics (steps, calories, activity time)
- `get_daily_sleep`: Retrieve sleep data (duration, sleep stages, efficiency)
- `get_daily_readiness`: Retrieve readiness scores and contributing factors
- `get_heart_rate`: Retrieve heart rate measurements
- `get_personal_info`: Retrieve user profile information

### OpenAI MCP Spec Tools

- `fetch`: Fetch specific Oura data by type and date range (follows OpenAI MCP fetch spec)
  - Supports data types: `activity`, `sleep`, `readiness`, `heart_rate`, `personal_info`
  - Accepts optional `start_date` and `end_date` parameters in YYYY-MM-DD format
  - Example: `fetch("sleep", "2024-01-01", "2024-01-07")`

- `search`: Search through Oura data using natural language queries (follows OpenAI MCP search spec)
  - Intelligently determines which data sources to query based on your search query
  - Accepts optional `start_date` and `end_date` parameters in YYYY-MM-DD format
  - Examples:
    - `search("sleep quality last week")`
    - `search("activity and steps yesterday")`
    - `search("readiness score")`

## Prerequisites

- [Azure Developer CLI (azd)](https://learn.microsoft.com/azure/developer/azure-developer-cli/install-azd)
- [Python 3.11+](https://www.python.org/downloads/)
- [Oura API Personal Access Token](https://cloud.ouraring.com/personal-access-tokens)
- [GitHub OAuth App](https://github.com/settings/developers) (for authentication)
- An Azure subscription

## Getting Your Oura API Token

1. Visit [Oura Cloud Personal Access Tokens](https://cloud.ouraring.com/personal-access-tokens)
2. Log in with your Oura account
3. Click "Create A New Personal Access Token"
4. Give it a name and click "Create"
5. Copy the token - you'll need it for deployment

## Setting Up GitHub OAuth Authentication

This server uses GitHub OAuth to secure access to the FastMCP server. Follow these steps to create a GitHub OAuth App:

### 1. Create a GitHub OAuth App

1. Go to [GitHub Developer Settings](https://github.com/settings/developers)
2. Click "OAuth Apps" in the left sidebar
3. Click "New OAuth App"
4. Fill in the application details:
   - **Application name**: `mcp-oura` (or your preferred name)
   - **Homepage URL**: Your Azure App Service URL (e.g., `https://web-abc123.azurewebsites.net`)
   - **Authorization callback URL**: Your Azure App Service URL + `/auth/callback` (e.g., `https://web-abc123.azurewebsites.net/auth/callback`)
5. Click "Register application"
6. On the app details page:
   - Copy the **Client ID** - you'll need this for deployment
   - Click "Generate a new client secret"
   - Copy the **Client Secret** - you'll need this immediately (it won't be shown again)

> **Note**: If you don't know your Azure App Service URL yet, you can update the GitHub OAuth App settings after your first deployment. The URL will be shown after running `azd up`.

### 2. Understanding OAuth Configuration

The GitHub OAuth integration provides:
- **Secure authentication**: Only users who authenticate via GitHub can access the MCP server
- **User identification**: Access to GitHub user information (username, email, etc.)
- **Minimal configuration**: Just set three environment variables

The server will automatically configure the OAuth endpoints at:
- Authorization: `https://your-app.azurewebsites.net/auth/authorize`
- Token: `https://your-app.azurewebsites.net/auth/token`
- Callback: `https://your-app.azurewebsites.net/auth/callback`

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

Before deploying, set your Oura API token and GitHub OAuth credentials:

```bash
azd env set OURA_API_TOKEN "your-oura-api-token-here"
azd env set GITHUB_CLIENT_ID "your-github-client-id"
azd env set GITHUB_CLIENT_SECRET "your-github-client-secret"
```

Replace the placeholder values with:
- `your-oura-api-token-here`: Your actual Oura API token from the previous step
- `your-github-client-id`: The Client ID from your GitHub OAuth App
- `your-github-client-secret`: The Client Secret from your GitHub OAuth App

> **Note**: The `BASE_URL` will be automatically set to your Azure App Service URL. If you need to override it, you can set it manually:
> ```bash
> azd env set BASE_URL "https://your-custom-domain.com"
> ```

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
export GITHUB_CLIENT_ID="your-github-client-id"
export GITHUB_CLIENT_SECRET="your-github-client-secret"
export BASE_URL="http://localhost:8000"
```

> **Note**: For local development without authentication, you can omit the GitHub OAuth variables. The server will run without authentication if they are not set.

4. Run the server:
```bash
cd src
python app.py
```

The server will start on `http://localhost:8000/mcp`

### Testing Locally

Use an MCP-compatible client to connect to `http://localhost:8000/mcp` using the streamable-http transport.

## Securing Your Deployment

This deployment includes **GitHub OAuth authentication** by default when you configure the GitHub OAuth environment variables. This provides secure access control to your MCP server.

### Authentication Setup

When you deploy with GitHub OAuth credentials (as described in the setup section), the server will:
- Require GitHub authentication for all MCP tool access
- Validate OAuth tokens via GitHub's API
- Provide user information in the authentication context

### Additional Security Options

For additional security layers, you can also consider:

1. **Virtual Network**: Deploy to a virtual network and restrict access
2. **Managed Identity**: Use Azure Managed Identity for secure access to Azure resources
3. **API Management**: Use Azure API Management for additional rate limiting and monitoring

### Running Without Authentication (Development Only)

For local development or testing, you can run the server without authentication by not setting the GitHub OAuth environment variables. **This is not recommended for production use.**

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

### Authentication Errors

- **GitHub OAuth errors**: Verify your GitHub OAuth App credentials are correct
- **Callback URL mismatch**: Ensure the Authorization callback URL in your GitHub OAuth App matches your deployed URL + `/auth/callback`
- **Invalid token**: GitHub OAuth tokens are verified in real-time. Ensure you're using a valid token from the OAuth flow

## Resources

- [FastMCP Documentation](https://github.com/jlowin/fastmcp)
- [FastMCP GitHub OAuth Integration](https://gofastmcp.com/integrations/github)
- [Oura API Documentation](https://cloud.ouraring.com/docs/)
- [Model Context Protocol Specification](https://modelcontextprotocol.io/)
- [Azure Developer CLI Documentation](https://learn.microsoft.com/azure/developer/azure-developer-cli/)
- [GitHub OAuth Apps Documentation](https://docs.github.com/en/apps/oauth-apps/building-oauth-apps/creating-an-oauth-app)

## License

This project is licensed under the MIT License.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
