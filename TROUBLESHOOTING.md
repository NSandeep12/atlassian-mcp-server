# 🔧 Troubleshooting Guide

Common issues and their solutions for the Atlassian MCP Server.

## 🚨 Installation Issues

### AWS CLI Not Found
```bash
# Error: aws: command not found
# Solution:
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip && sudo ./aws/install
aws --version  # Verify
```

### Amazon Q CLI Not Found
```bash
# Error: q: command not found
# Solution:
pip3 install amazon-q-cli
# or
python -m pip install amazon-q-cli
q --version  # Verify
```

### Python/Pip Issues
```bash
# Error: pip not found
# Solution (Ubuntu/Debian):
sudo apt update && sudo apt install python3-pip

# Solution (macOS):
brew install python3

# Solution (Windows):
# Download Python from python.org
```

---

## 🔐 Authentication Issues

### AWS Credentials Not Found
```bash
# Error: Unable to locate credentials
# Solution 1 - Configure AWS CLI:
aws configure

# Solution 2 - Use AWS SSO:
aws configure sso

# Solution 3 - Check existing config:
aws sts get-caller-identity
```

### Jira Authentication Failed
```bash
# Error: 401 Unauthorized from Jira
# Solutions:

# 1. Check token hasn't expired
curl -u "your-email@domain.com:YOUR_TOKEN" \
  https://your-domain.atlassian.net/rest/api/3/myself

# 2. Verify Jira URL format
# Correct: https://your-domain.atlassian.net
# Wrong: https://your-domain.atlassian.net/

# 3. Check email matches Jira account
# Must be exact email used for Jira login
```

### Bitbucket Authentication Failed
```bash
# Error: 401 Unauthorized from Bitbucket
# Solutions:

# 1. Test app password
curl -u "username:YOUR_APP_PASSWORD" \
  https://api.bitbucket.org/2.0/user

# 2. Check app password permissions:
# Required: Account (Read), Repositories (Read/Write), Pull requests (Read/Write)

# 3. Verify workspace name
# Usually same as username, but check Bitbucket settings
```

---

## 🚀 Deployment Issues

### Lambda Function Creation Failed
```bash
# Error: AccessDenied or InvalidParameterValue
# Solutions:

# 1. Check AWS permissions
aws iam get-user  # Should show your user info

# 2. Verify region
aws configure get region  # Should show valid region like us-west-2

# 3. Check if function already exists
aws lambda list-functions | grep atlassian-mcp-server

# 4. Delete existing function if needed
aws lambda delete-function --function-name atlassian-mcp-server
```

### IAM Role Issues
```bash
# Error: Role does not exist or cannot be assumed
# Solution: Re-run deployment (it creates the role automatically)
./deploy.sh JIRA_TOKEN WORKSPACE USERNAME APP_PASSWORD

# Or manually check role:
aws iam get-role --role-name lambda-execution-role
```

### Environment Variables Not Set
```bash
# Error: Environment variables missing in Lambda
# Solution: Update Lambda environment
aws lambda update-function-configuration \
  --function-name atlassian-mcp-server \
  --environment Variables='{
    "JIRA_EMAIL":"your-email@domain.com",
    "JIRA_API_TOKEN":"your-token",
    "JIRA_URL":"https://your-domain.atlassian.net",
    "BITBUCKET_USERNAME":"your-username",
    "BITBUCKET_APP_PASSWORD":"your-app-password",
    "BITBUCKET_WORKSPACE":"your-workspace"
  }'
```

---

## 🤖 Q CLI Integration Issues

### Q CLI Not Responding
```bash
# Error: Q CLI doesn't recognize MCP server
# Solutions:

# 1. Check MCP configuration
cat ~/.config/q/mcp-servers.json

# 2. Verify file exists and has correct content
ls -la ~/.config/q/

# 3. Restart Q CLI
q --restart

# 4. Test MCP wrapper directly
echo '{"jsonrpc":"2.0","id":1,"method":"tools/list","params":{}}' | python3 q_mcp_wrapper.py
```

### MCP Configuration Issues
```bash
# Error: MCP server not found
# Solution: Manually configure Q CLI
mkdir -p ~/.config/q/
cp q-mcp-config.json ~/.config/q/mcp-servers.json

# Update path in config file to absolute path
nano ~/.config/q/mcp-servers.json
```

### Permission Denied on Scripts
```bash
# Error: Permission denied: ./deploy.sh
# Solution:
chmod +x deploy.sh configure-bitbucket.sh q_mcp_wrapper.py
```

---

## 🔍 Runtime Issues

### Lambda Function Timeout
```bash
# Error: Task timed out after X seconds
# Solutions:

# 1. Check Lambda logs
aws logs tail /aws/lambda/atlassian-mcp-server --follow

# 2. Increase timeout (if needed)
aws lambda update-function-configuration \
  --function-name atlassian-mcp-server \
  --timeout 30

# 3. Check API response times
curl -w "@curl-format.txt" -u "user:pass" https://api.bitbucket.org/2.0/user
```

### API Rate Limiting
```bash
# Error: 429 Too Many Requests
# Solutions:

# 1. Check rate limits in logs
aws logs tail /aws/lambda/atlassian-mcp-server

# 2. Reduce request frequency
# 3. Check if multiple instances are running

# 4. Verify API quotas:
# Jira: 10,000 requests/hour
# Bitbucket: 1,000 requests/hour
```

### Memory Issues
```bash
# Error: Runtime.ExceededMemoryLimit
# Solution: Increase Lambda memory
aws lambda update-function-configuration \
  --function-name atlassian-mcp-server \
  --memory-size 256
```

---

## 🧪 Testing & Debugging

### Test Lambda Function Directly
```bash
# Test basic functionality
aws lambda invoke \
  --function-name atlassian-mcp-server \
  --payload '{"action":"list_tools"}' \
  response.json

cat response.json
```

### Test Individual APIs
```bash
# Test Jira API
curl -u "email:token" \
  "https://your-domain.atlassian.net/rest/api/3/search?jql=project=TEST&maxResults=1"

# Test Bitbucket API
curl -u "username:app_password" \
  "https://api.bitbucket.org/2.0/repositories/username"
```

### Debug MCP Communication
```bash
# Test MCP wrapper with verbose output
echo '{"jsonrpc":"2.0","id":1,"method":"tools/list","params":{}}' | \
  python3 -u q_mcp_wrapper.py 2>&1

# Check Q CLI logs (if available)
q chat --debug "test message"
```

---

## 📊 Monitoring & Logs

### View Lambda Logs
```bash
# Real-time logs
aws logs tail /aws/lambda/atlassian-mcp-server --follow

# Recent logs
aws logs tail /aws/lambda/atlassian-mcp-server --since 1h

# Specific time range
aws logs tail /aws/lambda/atlassian-mcp-server \
  --start-time 2024-01-01T00:00:00 \
  --end-time 2024-01-01T23:59:59
```

### Check Lambda Metrics
```bash
# Function status
aws lambda get-function --function-name atlassian-mcp-server

# Recent invocations
aws lambda get-function-configuration --function-name atlassian-mcp-server

# CloudWatch metrics (if needed)
aws cloudwatch get-metric-statistics \
  --namespace AWS/Lambda \
  --metric-name Invocations \
  --dimensions Name=FunctionName,Value=atlassian-mcp-server \
  --start-time 2024-01-01T00:00:00Z \
  --end-time 2024-01-01T23:59:59Z \
  --period 3600 \
  --statistics Sum
```

---

## 🔄 Reset & Cleanup

### Complete Reset
```bash
# Delete Lambda function
aws lambda delete-function --function-name atlassian-mcp-server

# Delete IAM role (optional)
aws iam delete-role --role-name lambda-execution-role

# Remove Q CLI configuration
rm ~/.config/q/mcp-servers.json

# Re-deploy from scratch
./deploy.sh JIRA_TOKEN WORKSPACE USERNAME APP_PASSWORD
```

### Update Credentials
```bash
# Update Jira credentials
aws lambda update-function-configuration \
  --function-name atlassian-mcp-server \
  --environment Variables='{
    "JIRA_EMAIL":"new-email@domain.com",
    "JIRA_API_TOKEN":"new-token",
    "JIRA_URL":"https://new-domain.atlassian.net"
  }'

# Update Bitbucket credentials
./configure-bitbucket.sh NEW_WORKSPACE NEW_USERNAME NEW_APP_PASSWORD
```

---

## 🆘 Still Need Help?

### Diagnostic Commands
```bash
# System info
python3 --version
aws --version
q --version

# AWS configuration
aws configure list
aws sts get-caller-identity

# Project files
ls -la
cat requirements.txt

# Lambda function info
aws lambda get-function --function-name atlassian-mcp-server
```

### Get Support
1. **Check logs first**: `aws logs tail /aws/lambda/atlassian-mcp-server --follow`
2. **Test components individually** using commands above
3. **Create GitHub issue** with:
   - Error message
   - Steps to reproduce
   - System info (OS, Python version, etc.)
   - Relevant log snippets (remove sensitive data)

---

**💡 Most issues are solved by checking logs and verifying credentials!**
