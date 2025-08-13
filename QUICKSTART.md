# 🚀 Quick Start Guide - 5 Minutes Setup

Get your Atlassian MCP Server running in 5 minutes!

## ⚡ Super Quick Setup

### 1. Prerequisites (2 minutes)
```bash
# Install AWS CLI
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip && sudo ./aws/install

# Install Amazon Q CLI
pip install amazon-q-cli

# Configure AWS
aws configure sso  # or aws configure
```

### 2. Get API Tokens (2 minutes)
- **Jira**: https://id.atlassian.com/manage-profile/security/api-tokens → Create token
- **Bitbucket**: https://bitbucket.org/account/settings/app-passwords/ → Create with Repos + PRs permissions

### 3. Deploy (1 minute)
```bash
git clone https://github.com/NSandeep12/atlassian-mcp-server.git
cd atlassian-mcp-server
chmod +x deploy.sh

./deploy.sh YOUR_JIRA_TOKEN YOUR_WORKSPACE YOUR_USERNAME YOUR_BITBUCKET_PASSWORD
```

### 4. Test
```bash
q chat "Show me my repositories"
q chat "List open issues"
```

## 🎯 That's it! 

Your serverless Atlassian integration is ready!

---

## 📝 Example Commands

```bash
# Jira
q chat "Show me all bugs in PROJECT-X"
q chat "Create a new issue about login problems"

# Bitbucket  
q chat "List branches in my-repo"
q chat "Show recent commits"

# Cross-platform
q chat "Create Jira issue for my-repo repository"
q chat "Find PRs related to JIRA-123"
```

## 🔧 Need Help?

- **Logs**: `aws logs tail /aws/lambda/atlassian-mcp-server --follow`
- **Test**: `aws lambda invoke --function-name atlassian-mcp-server --payload '{"action":"list_tools"}' response.json`
- **Full Guide**: See [README.md](README.md) for detailed instructions

## 💰 Cost
- **Free tier**: First 1M requests/month
- **After**: ~$0.002/month for normal usage
- **No always-on costs** - serverless!

---

**🎉 Enjoy your AI-powered Atlassian integration!**
