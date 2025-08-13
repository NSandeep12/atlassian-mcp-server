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

---

## 📋 Step-by-Step Setup Guide

### Step 1: Prerequisites Check ✅

Before starting, make sure you have:

**Required:**
- [ ] AWS Account with admin access
- [ ] Jira Cloud account (not Server/Data Center)
- [ ] Bitbucket Cloud account
- [ ] Computer with internet access

**We'll install these together:**
- [ ] AWS CLI
- [ ] Amazon Q CLI
- [ ] Python 3.8+ (usually pre-installed)

---

### Step 2: Install Required Tools 🛠️

#### 2.1 Install AWS CLI

**On macOS:**
```bash
# Using Homebrew (recommended)
brew install awscli

# Or download installer
curl "https://awscli.amazonaws.com/AWSCLIV2.pkg" -o "AWSCLIV2.pkg"
sudo installer -pkg AWSCLIV2.pkg -target /
```

**On Linux:**
```bash
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install
```

**On Windows:**
```bash
# Download and run: https://awscli.amazonaws.com/AWSCLIV2.msi
```

**Verify installation:**
```bash
aws --version
# Should show: aws-cli/2.x.x
```

#### 2.2 Install Amazon Q CLI

```bash
# Install Amazon Q CLI
pip install amazon-q-cli

# Or using pip3
pip3 install amazon-q-cli

# Verify installation
q --version
```

#### 2.3 Configure AWS CLI

**Option A: Using AWS SSO (Recommended for organizations)**
```bash
aws configure sso
# Follow prompts to set up SSO
```

**Option B: Using Access Keys**
```bash
aws configure
# Enter your AWS Access Key ID
# Enter your AWS Secret Access Key
# Enter your default region (e.g., us-west-2)
# Enter output format: json
```

**Test AWS connection:**
```bash
aws sts get-caller-identity
# Should show your AWS account info
```

---

### Step 3: Get API Credentials 🔑

#### 3.1 Get Jira API Token

1. **Go to Jira API Tokens page:**
   - Visit: https://id.atlassian.com/manage-profile/security/api-tokens
   - Click "Create API token"

2. **Create token:**
   - Label: `Amazon Q MCP Integration`
   - Click "Create"
   - **Copy the token** (starts with `ATATT3x...`)
   - ⚠️ **Save it now** - you won't see it again!

3. **Note your Jira details:**
   - Your Jira URL: `https://YOUR-DOMAIN.atlassian.net`
   - Your email: `your-email@domain.com`

#### 3.2 Get Bitbucket App Password

1. **Go to Bitbucket App Passwords:**
   - Visit: https://bitbucket.org/account/settings/app-passwords/
   - Click "Create app password"

2. **Configure permissions:**
   - Label: `Amazon Q MCP Integration`
   - Select permissions:
     - ✅ **Account: Read**
     - ✅ **Repositories: Read, Write**
     - ✅ **Pull requests: Read, Write**
   - Click "Create"

3. **Copy credentials:**
   - **App Password** (starts with `ATBB...`)
   - **Username** (your Bitbucket username)
   - **Workspace** (usually same as username, or your team name)

---

### Step 4: Download and Deploy 🚀

#### 4.1 Clone the Project

```bash
# Clone the repository
git clone https://github.com/NSandeep12/atlassian-mcp-server.git

# Navigate to project
cd atlassian-mcp-server

# Make scripts executable
chmod +x deploy.sh configure-bitbucket.sh
```

#### 4.2 Deploy to AWS Lambda

**Run the deployment command:**
```bash
./deploy.sh JIRA_API_TOKEN BITBUCKET_WORKSPACE BITBUCKET_USERNAME BITBUCKET_APP_PASSWORD
```

**Example with real values:**
```bash
./deploy.sh ATATT3xFfGF0... nsandeep12 nsandeep12-admin ATBBzpnPDsn4...
```

**What this does:**
- ✅ Creates AWS Lambda function
- ✅ Sets up IAM roles and permissions
- ✅ Configures environment variables securely
- ✅ Configures Amazon Q CLI integration
- ✅ Tests the deployment

**Expected output:**
```
🚀 Deploying Atlassian Suite MCP Server (Jira + Bitbucket)...
✅ Lambda function created successfully
✅ Environment variables configured
✅ Q CLI configured
✅ Deployment complete!

💡 Test with: q chat "List my repositories"
```

---

### Step 5: Test Your Setup ✅

#### 5.1 Test Amazon Q Integration

```bash
# Test basic functionality
q chat "Hello, can you help me with Jira and Bitbucket?"

# Test Jira integration
q chat "Show me all open issues"
q chat "What projects do I have access to?"

# Test Bitbucket integration
q chat "List my repositories"
q chat "Show me recent commits"
```

#### 5.2 Test Advanced Features

```bash
# Cross-platform queries
q chat "Create a Jira issue for my main repository"
q chat "Find all pull requests related to bug fixes"
q chat "Show me commits that mention Jira issues"

# Specific project queries
q chat "Show me all open issues in PROJECT-NAME"
q chat "List branches in REPO-NAME repository"
```

#### 5.3 Verify AWS Lambda

```bash
# Check Lambda function status
aws lambda get-function --function-name atlassian-mcp-server

# View recent logs
aws logs tail /aws/lambda/atlassian-mcp-server --follow
```

---

## 🎯 Usage Examples

### Jira Operations
```bash
# Search and filter
q chat "Show me all open issues in SCRUM project"
q chat "Find issues assigned to me"
q chat "What are the latest 5 issues created?"
q chat "Show me high priority bugs"

# Create issues
q chat "Create a new bug about login issues in SCRUM project"
q chat "Create a story for user authentication feature"
```

### Bitbucket Operations
```bash
# Repository management
q chat "List all my repositories"
q chat "Show me branches in online-shop repository"
q chat "What are the recent commits in main branch?"

# Pull requests
q chat "List open pull requests in online-shop"
q chat "Show me pull requests I need to review"
q chat "Create a pull request from feature-branch to main"
```

### Cross-Platform Integration
```bash
# Link Jira and Bitbucket
q chat "Create a Jira issue for repository online-shop"
q chat "Find all pull requests related to SCRUM-123"
q chat "Show me commits that mention Jira issues"
q chat "Link this pull request to JIRA-456"
```

---

## 🔧 Available Tools

### Jira Tools
- **`search_jira_issues`** - Search with JQL queries
- **`create_jira_issue`** - Create new issues

### Bitbucket Tools
- **`list_bitbucket_repositories`** - List repositories
- **`list_pull_requests`** - List pull requests
- **`create_pull_request`** - Create new pull requests
- **`list_branches`** - List repository branches
- **`get_commits`** - Get recent commits

### Cross-Reference Tools
- **`search_cross_references`** - Find related activity across platforms

---

## 🛠️ Configuration & Customization

### Update AWS Settings

**Change AWS Profile/Region:**
```bash
# Edit deploy.sh
nano deploy.sh

# Update these lines:
PROFILE="your-aws-profile-name"
REGION="your-preferred-region"
```

### Update Credentials

**Update Jira credentials:**
```bash
aws lambda update-function-configuration \
    --function-name atlassian-mcp-server \
    --environment Variables='{
        "JIRA_EMAIL":"new-email@domain.com",
        "JIRA_API_TOKEN":"new-token",
        "JIRA_URL":"https://new-domain.atlassian.net"
    }'
```

**Update Bitbucket credentials:**
```bash
./configure-bitbucket.sh NEW_WORKSPACE NEW_USERNAME NEW_APP_PASSWORD
```

---

## 🧪 Testing & Troubleshooting

### Test Individual Components

**Test Lambda function directly:**
```bash
aws lambda invoke \
    --function-name atlassian-mcp-server \
    --region us-west-2 \
    --payload '{"action":"list_tools"}' \
    response.json && cat response.json
```

**Test MCP wrapper:**
```bash
echo '{"jsonrpc":"2.0","id":1,"method":"tools/list","params":{}}' | python3 q_mcp_wrapper.py
```

**Test API credentials:**
```bash
# Test Jira connection
curl -u "your-email@domain.com:YOUR_JIRA_TOKEN" \
    https://your-domain.atlassian.net/rest/api/3/myself

# Test Bitbucket connection
curl -u "username:YOUR_APP_PASSWORD" \
    https://api.bitbucket.org/2.0/user
```

### Common Issues & Solutions

**Issue: "Command not found: q"**
```bash
# Solution: Install Amazon Q CLI
pip3 install amazon-q-cli
```

**Issue: "AWS credentials not found"**
```bash
# Solution: Configure AWS CLI
aws configure
# Or set up AWS SSO
aws configure sso
```

**Issue: "Lambda function not found"**
```bash
# Solution: Check if deployment completed
aws lambda list-functions | grep atlassian-mcp-server

# Re-deploy if needed
./deploy.sh JIRA_TOKEN WORKSPACE USERNAME APP_PASSWORD
```

**Issue: "Jira/Bitbucket authentication failed"**
```bash
# Solution: Verify credentials
# For Jira: Check token hasn't expired
# For Bitbucket: Verify app password permissions
```

**Issue: "Q CLI not responding"**
```bash
# Solution: Check MCP configuration
cat ~/.config/q/mcp-servers.json

# Restart Q CLI
q --restart
```

---

## 🔐 Security Features

- **🔒 No Hardcoded Credentials**: All secrets stored as encrypted Lambda environment variables
- **🛡️ Encrypted at Rest**: Lambda environment variables are encrypted with AWS KMS
- **🔐 HTTPS Only**: All API communications use TLS encryption
- **⚡ Minimal Permissions**: Lambda runs with minimal required IAM permissions
- **🎯 On-Demand**: Only connects to APIs when requests are made
- **🚫 No Data Storage**: No persistent data storage, stateless execution

---

## 💰 Cost Breakdown

### AWS Lambda Costs
- **Free Tier**: 1M requests/month + 400,000 GB-seconds/month
- **After Free Tier**: $0.0000002 per request + $0.0000166667 per GB-second
- **Typical Usage**: ~$0.002/month for moderate usage (100 requests/day)

### Atlassian API Costs
- **Jira Cloud**: Free tier includes API access
- **Bitbucket Cloud**: Free tier includes API access

### Total Monthly Cost
- **Light Usage** (10 requests/day): **FREE** (within AWS free tier)
- **Moderate Usage** (100 requests/day): **~$0.002/month**
- **Heavy Usage** (1000 requests/day): **~$0.02/month**

---

## 📁 Project Structure

```
atlassian-mcp-server/
├── lambda_handler.py          # Main AWS Lambda function
├── q_mcp_wrapper.py           # Amazon Q CLI MCP bridge
├── deploy.sh                  # One-command deployment script
├── configure-bitbucket.sh     # Bitbucket configuration helper
├── test-bitbucket-endpoints.py # Testing utilities
├── requirements.txt           # Python dependencies
├── q-mcp-config.json         # Q CLI configuration
├── README.md                 # This documentation
└── LICENSE                   # MIT license
```

---

## 🆘 Support & Help

### Getting Help

1. **Check the logs:**
   ```bash
   aws logs tail /aws/lambda/atlassian-mcp-server --follow
   ```

2. **Test individual components** using the testing section above

3. **Check AWS Lambda console:**
   - Go to AWS Console → Lambda → atlassian-mcp-server
   - Check function configuration and recent invocations

4. **Verify Q CLI configuration:**
   ```bash
   cat ~/.config/q/mcp-servers.json
   ```

### Common Commands Reference

```bash
# Deploy/Update
./deploy.sh JIRA_TOKEN WORKSPACE USERNAME APP_PASSWORD

# Test Q CLI
q chat "test message"

# Check AWS function
aws lambda get-function --function-name atlassian-mcp-server

# View logs
aws logs tail /aws/lambda/atlassian-mcp-server

# Update Bitbucket config
./configure-bitbucket.sh WORKSPACE USERNAME APP_PASSWORD
```

---

## 📄 License

MIT License - see [LICENSE](LICENSE) file.

---

## 🚀 Quick Start Summary

1. **Install tools**: AWS CLI + Amazon Q CLI
2. **Get credentials**: Jira API token + Bitbucket app password  
3. **Deploy**: `./deploy.sh JIRA_TOKEN WORKSPACE USERNAME APP_PASSWORD`
4. **Use**: `q chat "List my repositories and open issues"`

**Your serverless Atlassian integration is ready in under 10 minutes!** 🎉
