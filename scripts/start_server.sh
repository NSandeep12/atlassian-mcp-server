#!/bin/bash

echo "🚀 Starting Jira MCP Server..."

# Check if .env file exists and has been configured
if [ ! -f .env ]; then
    echo "❌ .env file not found. Please run setup.sh first."
    exit 1
fi

# Check if credentials are still default values
if grep -q "your-domain.atlassian.net" .env; then
    echo "⚠️  Please configure your Jira credentials in .env file:"
    echo "   nano .env"
    echo ""
    echo "Required settings:"
    echo "   JIRA_URL=https://your-domain.atlassian.net"
    echo "   JIRA_EMAIL=your-email@company.com"
    echo "   JIRA_API_TOKEN=your-api-token"
    echo ""
    echo "Get your API token from: https://id.atlassian.com/manage-profile/security/api-tokens"
    exit 1
fi

# Activate virtual environment
source venv/bin/activate

# Start the server
echo "📡 Server ready for MCP connections..."
echo "💡 Use this server with Q CLI by configuring it as an MCP server"
echo ""

# Use the simple server version
python jira_server_simple.py
