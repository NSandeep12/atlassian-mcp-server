# Jira MCP Server for Q CLI

This MCP server provides Jira integration capabilities for Amazon Q CLI, allowing you to interact with Jira directly from your command line.

## Features

- ✅ Create Jira issues
- 📋 Get issue details
- ✏️ Update issues
- 🔄 Transition issues between statuses
- 🔍 Search issues with JQL
- 💬 Add comments to issues

## Setup

### 1. Install Dependencies

```bash
chmod +x setup.sh
./setup.sh
```

### 2. Configure Jira Credentials

Edit the `.env` file with your Jira details:

```bash
nano .env
```

Add your credentials:
```
JIRA_URL=https://your-domain.atlassian.net
JIRA_EMAIL=your-email@company.com
JIRA_API_TOKEN=your-api-token
```

**Getting your Jira API Token:**
1. Go to https://id.atlassian.com/manage-profile/security/api-tokens
2. Click "Create API token"
3. Give it a name and copy the token

### 3. Test the Server

```bash
source venv/bin/activate
python jira_server.py
```

The server should start and wait for MCP protocol messages.

## Usage with Q CLI

Once configured with Q CLI, you can use these commands:

### Create an Issue
```bash
q chat "Use jira-server___create_issue to create a bug report in project DEV with summary 'API returning 500 errors' and description 'Users experiencing server errors on login endpoint'"
```

### Get Issue Details
```bash
q chat "Use jira-server___get_issue to get details for issue DEV-123"
```

### Update an Issue
```bash
q chat "Use jira-server___update_issue to update DEV-123 with new summary 'Fixed: API returning 500 errors'"
```

### Transition Issue Status
```bash
q chat "Use jira-server___transition_issue to move DEV-123 to 'In Progress'"
```

### Search Issues
```bash
q chat "Use jira-server___search_issues with JQL 'project = DEV AND status = Open'"
```

### Add Comment
```bash
q chat "Use jira-server___add_comment to add 'Deployed fix to staging environment' to issue DEV-123"
```

## Integration Examples

### AWS + Jira Workflows

```bash
# Monitor EC2 instances and create Jira tickets for issues
q chat "Check my EC2 instances and if any are in stopped state unexpectedly, create a Jira issue in project OPS"

# Update Jira after successful deployment
q chat "Deploy my Lambda function and then add a comment to Jira issue DEV-456 with the deployment status"

# Create infrastructure issues based on CloudWatch alarms
q chat "If my RDS CPU utilization is above 80%, create a high priority Jira issue in project INFRA"
```

## Troubleshooting

### Common Issues

1. **Authentication Error**: Verify your API token and email in `.env`
2. **Project Not Found**: Ensure the project key exists and you have access
3. **Transition Not Available**: Check available transitions for the issue status

### Debug Mode

Run with debug output:
```bash
PYTHONPATH=venv/lib/python3.*/site-packages python jira_server.py --debug
```

## Configuration

The server can be customized by modifying `jira_server.py`:

- Add custom fields to issue creation
- Implement additional Jira operations
- Add validation and error handling
- Customize response formatting

## Security Notes

- Store API tokens securely in `.env` file
- Don't commit `.env` to version control
- Use least-privilege Jira permissions
- Consider using Jira service accounts for automation
