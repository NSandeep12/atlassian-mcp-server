# Q CLI Integration Guide

## Quick Start

1. **Configure Jira Credentials**
   ```bash
   cd /home/sandynal/jira-mcp-server
   nano .env
   ```
   
   Update with your details:
   ```
   JIRA_URL=https://your-domain.atlassian.net
   JIRA_EMAIL=your-email@company.com
   JIRA_API_TOKEN=your-api-token
   ```

2. **Start the MCP Server**
   ```bash
   ./start_server.sh
   ```

## Configuring Q CLI

The exact configuration method for Q CLI MCP servers may vary. Here are the common approaches:

### Method 1: Configuration File
If Q CLI uses a configuration file for MCP servers, add:

```json
{
  "mcpServers": {
    "jira-server": {
      "command": "/home/sandynal/jira-mcp-server/venv/bin/python",
      "args": ["/home/sandynal/jira-mcp-server/jira_server_simple.py"],
      "env": {
        "PYTHONPATH": "/home/sandynal/jira-mcp-server/venv/lib/python3.12/site-packages"
      }
    }
  }
}
```

### Method 2: Command Line Registration
```bash
q mcp add jira-server /home/sandynal/jira-mcp-server/jira_server_simple.py
```

### Method 3: Environment Variable
```bash
export Q_MCP_SERVERS="jira-server:/home/sandynal/jira-mcp-server/jira_server_simple.py"
```

## Usage Examples

Once configured, you can use these commands in Q CLI:

### Create Issues
```bash
q chat "Use jira-server___create_issue to create a bug in project DEV with summary 'Login API returns 500 error'"
```

### Get Issue Details
```bash
q chat "Use jira-server___get_issue to get details for DEV-123"
```

### Search Issues
```bash
q chat "Use jira-server___search_issues with JQL 'project = DEV AND status = Open'"
```

## Advanced Integration Examples

### AWS + Jira Workflows
```bash
# Monitor and create tickets
q chat "Check my EC2 instances and create a Jira issue if any are unexpectedly stopped"

# Deployment notifications
q chat "Deploy my Lambda function and update Jira issue DEV-456 with the status"

# Cost monitoring
q chat "If my AWS costs exceed $1000 this month, create a high-priority Jira issue"
```

### Automated Issue Management
```bash
# Create issues from logs
q chat "Parse my application logs and create Jira issues for any ERROR level entries"

# Status updates
q chat "Update all Jira issues in project DEV that mention 'deployment' to Done status"
```

## Available Tools

| Tool | Description | Required Parameters |
|------|-------------|-------------------|
| `create_issue` | Create new Jira issue | `project_key`, `summary` |
| `get_issue` | Get issue details | `issue_key` |
| `search_issues` | Search with JQL | `jql` |

## Troubleshooting

### Server Won't Start
- Check `.env` file configuration
- Verify Jira credentials
- Ensure virtual environment is activated

### Authentication Errors
- Verify API token is correct
- Check email address matches Jira account
- Ensure Jira URL is correct (include https://)

### Q CLI Integration Issues
- Check Q CLI documentation for MCP server configuration
- Verify server path is correct
- Ensure Python virtual environment is properly configured

## Getting Help

1. Check server logs for errors
2. Test Jira API access manually:
   ```bash
   curl -u "email@domain.com:api_token" \
        -H "Content-Type: application/json" \
        "https://your-domain.atlassian.net/rest/api/2/myself"
   ```
3. Verify MCP server is responding:
   ```bash
   echo '{"jsonrpc":"2.0","id":1,"method":"tools/list"}' | python jira_server_simple.py
   ```
