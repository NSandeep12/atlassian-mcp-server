#!/bin/bash
# Configure Bitbucket integration for Atlassian MCP Server

set -e

FUNCTION_NAME="atlassian-mcp-server"
REGION="us-west-2"
PROFILE="AdministratorAccess-542754948868"

echo "🔧 Configuring Bitbucket integration..."

# Check if all parameters are provided
if [ -z "$1" ] || [ -z "$2" ] || [ -z "$3" ]; then
    echo "❌ Missing parameters!"
    echo "Usage: ./configure-bitbucket.sh BITBUCKET_WORKSPACE BITBUCKET_USERNAME BITBUCKET_APP_PASSWORD"
    echo ""
    echo "Example: ./configure-bitbucket.sh nsandeep12 nsandeep12 ATBBApp..."
    echo ""
    echo "🔑 Get your app password from: https://bitbucket.org/account/settings/app-passwords/"
    exit 1
fi

BITBUCKET_WORKSPACE="$1"
BITBUCKET_USERNAME="$2"
BITBUCKET_APP_PASSWORD="$3"

echo "📝 Adding Bitbucket credentials to existing Jira configuration..."

# Get current environment variables
CURRENT_ENV=$(aws lambda get-function-configuration --function-name $FUNCTION_NAME --region $REGION --profile $PROFILE --query 'Environment.Variables' --output json)

# Create new environment configuration with both Jira and Bitbucket
cat > env-config.json << EOF
{
  "Variables": {
    "JIRA_URL": "$(echo $CURRENT_ENV | jq -r '.JIRA_URL')",
    "JIRA_EMAIL": "$(echo $CURRENT_ENV | jq -r '.JIRA_EMAIL')",
    "JIRA_API_TOKEN": "$(echo $CURRENT_ENV | jq -r '.JIRA_API_TOKEN')",
    "BITBUCKET_WORKSPACE": "$BITBUCKET_WORKSPACE",
    "BITBUCKET_USERNAME": "$BITBUCKET_USERNAME",
    "BITBUCKET_APP_PASSWORD": "$BITBUCKET_APP_PASSWORD"
  }
}
EOF

# Update Lambda configuration
aws lambda update-function-configuration \
    --function-name $FUNCTION_NAME \
    --region $REGION \
    --profile $PROFILE \
    --environment file://env-config.json

echo "✅ Bitbucket credentials configured!"
echo ""
echo "🧪 Testing Bitbucket connection..."

# Wait for configuration to propagate
sleep 5

# Test Bitbucket repositories
echo "📂 Testing repository listing..."
aws lambda invoke \
    --function-name $FUNCTION_NAME \
    --region $REGION \
    --profile $PROFILE \
    --cli-binary-format raw-in-base64-out \
    --payload '{"action":"call_tool","tool_name":"list_bitbucket_repositories","arguments":{"limit":5}}' \
    test-response.json

echo "Response:"
cat test-response.json | jq -r '.body' | jq .

# Clean up
rm -f env-config.json test-response.json

echo ""
echo "✅ Bitbucket integration complete!"
echo ""
echo "🎯 You can now use these Q CLI commands:"
echo "  • 'List all my Bitbucket repositories'"
echo "  • 'Show me open pull requests in my-repo'"
echo "  • 'Create a pull request for SCRUM-123'"
echo "  • 'Find all Bitbucket activity related to SCRUM-123'"
