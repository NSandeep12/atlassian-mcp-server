#!/bin/bash

echo "🚀 Setting up Jira MCP Server..."

# Create virtual environment
echo "Creating virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "Creating .env file from template..."
    cp .env.example .env
    echo "⚠️  Please edit .env file with your Jira credentials before running the server"
else
    echo "✅ .env file already exists"
fi

# Make the server executable
chmod +x jira_server.py

echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Edit .env file with your Jira credentials:"
echo "   nano .env"
echo ""
echo "2. Test the server:"
echo "   source venv/bin/activate"
echo "   python jira_server.py"
echo ""
echo "3. Configure Q CLI to use this MCP server"
