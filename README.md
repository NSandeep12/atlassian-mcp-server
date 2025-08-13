# Atlassian MCP Server - Serverless

A serverless AWS Lambda integration for **Jira** and **Bitbucket** with Amazon Q CLI using the Model Context Protocol (MCP).

## ✨ Features

- 🎫 **Jira Integration**: Search issues, create issues, manage projects
- 🔧 **Bitbucket Integration**: Repositories, pull requests, branches, commits
- 🔗 **Cross-References**: Automatic linking between Jira issues and Bitbucket PRs/commits
- 🤖 **Natural Language**: Use Q CLI to interact with both platforms seamlessly
- ☁️ **Serverless**: AWS Lambda deployment - only runs when needed
- 💰 **Cost Effective**: ~$0.002/month for moderate usage

## 🏗️ Architecture

```
┌─────────────┐    ┌──────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   USER      │    │   AMAZON Q   │    │   MCP WRAPPER   │    │   AWS LAMBDA    │
│             │    │     CLI      │    │                 │    │                 │
│ "Show me    │───▶│              │───▶│ q_mcp_wrapper   │───▶│ atlassian-mcp   │
│  issues"    │    │ Natural Lang │    │     .py         │    │    -server      │
│             │    │ Processing   │    │                 │    │                 │
└─────────────┘    └──────────────┘    └─────────────────┘    └─────────────────┘
                                                │                        │
                                                │                        ▼
                                                ▼                ┌─────────────────┐
                                    ┌─────────────────┐          │ ATLASSIAN APIS  │
                                    │ MCP PROTOCOL    │          │                 │
                                    │                 │          │ • Jira Cloud    │
                                    │ • tools/list    │          │ • Bitbucket     │
                                    │ • tools/call    │          │                 │
                                    │ • initialize    │          │ Only connects   │
                                    │                 │          │ when needed     │
                                    └─────────────────┘          └─────────────────┘
```

## 📋 Prerequisites

1. **AWS Account** with Lambda and IAM permissions
2. **AWS CLI** installed and configured with SSO
3. **Jira Cloud** account and API token
4. **Bitbucket Cloud** account and app password
5. **Amazon Q CLI** installed

## 🚀 Quick Setup

### 1. Get API Credentials

**Jira API Token:**
- Go to: https://id.atlassian.com/manage-profile/security/api-tokens
- Create token (starts with `ATATT3x...`)

**Bitbucket App Password:**
- Go to: https://bitbucket.org/account/settings/app-passwords/
- Create with permissions: Account (Read), Repositories (Read/Write), Pull requests (Read/Write)
- Copy password (starts with `ATBB...`)

### 2. Deploy to AWS Lambda

**For Jira + Bitbucket (Recommended):**
```bash
./deploy.sh JIRA_API_TOKEN BITBUCKET_WORKSPACE BITBUCKET_USERNAME BITBUCKET_APP_PASSWORD
```

**Example:**
```bash
./deploy.sh ATATT3x... nsandeep12 nsandeep12-admin ATBBApp...
```

### 3. Configure Q CLI

The deployment script automatically configures Q CLI. You can also manually add to `~/.config/q/mcp-servers.json`:

```json
{
  "mcpServers": {
    "atlassian-mcp-server": {
      "command": "python3",
      "args": ["/path/to/q_mcp_wrapper.py"]
    }
  }
}
```

## 🎯 Usage Examples

### Jira Operations
```bash
q chat "Show me all open issues in SCRUM project"
q chat "Create a new bug about login issues in SCRUM project"
q chat "Find issues assigned to me"
q chat "What are the latest 5 issues created?"
```

### Bitbucket Operations
```bash
q chat "List all my repositories"
q chat "Show me branches in online-shop repository"
q chat "What are the recent commits in main branch?"
q chat "List open pull requests in online-shop"
```

### Cross-Platform Integration
```bash
q chat "Create a Jira issue for repository online-shop"
q chat "Find all pull requests related to SCRUM-123"
q chat "Show me commits that mention Jira issues"
```

## 🔧 Available Tools

### Jira Tools
- `search_jira_issues` - Search with JQL queries
- `create_jira_issue` - Create new issues

### Bitbucket Tools
- `list_bitbucket_repositories` - List repositories
- `list_pull_requests` - List pull requests
- `create_pull_request` - Create new pull requests
- `list_branches` - List repository branches
- `get_commits` - Get recent commits

### Cross-Reference Tools
- `search_cross_references` - Find related activity across platforms

## 🧪 Testing

### Test Lambda Function
```bash
aws lambda invoke \
    --function-name atlassian-mcp-server \
    --region us-west-2 \
    --payload '{"action":"call_tool","tool_name":"search_jira_issues","arguments":{"jql":"project = SCRUM","max_results":3}}' \
    response.json
```

### Test MCP Wrapper
```bash
echo '{"jsonrpc":"2.0","id":1,"method":"tools/list","params":{}}' | python3 q_mcp_wrapper.py
```

## 🛠️ Configuration

### Update AWS Profile/Region
Edit `deploy.sh` and `q_mcp_wrapper.py`:
```bash
PROFILE="YOUR_AWS_SSO_PROFILE_NAME"
REGION="your-preferred-region"
```

### Environment Variables (Lambda)
The Lambda function uses these environment variables:
- `JIRA_EMAIL` - Your Jira email
- `JIRA_API_TOKEN` - Jira API token
- `JIRA_URL` - Your Jira instance URL
- `BITBUCKET_USERNAME` - Bitbucket username
- `BITBUCKET_APP_PASSWORD` - Bitbucket app password
- `BITBUCKET_WORKSPACE` - Bitbucket workspace name

## 🔐 Security Features

- **No Hardcoded Credentials**: All secrets stored as Lambda environment variables
- **Encrypted at Rest**: Lambda environment variables are encrypted
- **HTTPS Only**: All API communications use TLS
- **Minimal Permissions**: Lambda runs with minimal required IAM permissions
- **On-Demand**: Only connects to APIs when requests are made

## 💰 Cost

- **AWS Lambda**: ~$0.002/month for moderate usage
- **No Always-On Costs**: Serverless - only pay when used
- **Free Tier**: First 1M requests/month are free

## 📁 Project Structure

```
atlassian-mcp-server/
├── lambda_handler.py          # Main Lambda function
├── q_mcp_wrapper.py           # Q CLI MCP bridge
├── deploy.sh                  # One-command deployment
├── configure-bitbucket.sh     # Bitbucket configuration helper
├── test-bitbucket-endpoints.py # Testing utilities
├── q-mcp-config.json         # Q CLI configuration
├── requirements.txt          # Python dependencies
├── README.md                 # This documentation
└── LICENSE                   # MIT license
```

## 🛠️ Troubleshooting

### Common Issues

**Lambda Deployment:**
```bash
# Check function status
aws lambda get-function --function-name atlassian-mcp-server

# View logs
aws logs tail /aws/lambda/atlassian-mcp-server --follow
```

**API Authentication:**
```bash
# Test Jira
curl -u "email@domain.com:JIRA_TOKEN" https://your-domain.atlassian.net/rest/api/3/myself

# Test Bitbucket
curl -u "username:APP_PASSWORD" https://api.bitbucket.org/2.0/user
```

**Q CLI Integration:**
```bash
# Test MCP connection
echo '{"jsonrpc":"2.0","id":1,"method":"tools/list","params":{}}' | python3 q_mcp_wrapper.py
```

## 📄 License

MIT License - see [LICENSE](LICENSE) file.

---

## 🚀 Quick Start Summary

1. **Get Credentials**: Jira API token + Bitbucket app password
2. **Deploy**: `./deploy.sh JIRA_TOKEN WORKSPACE USERNAME APP_PASSWORD`
3. **Use**: `q chat "List my repositories and open issues"`

**Your serverless Atlassian integration is ready!** 🎉
