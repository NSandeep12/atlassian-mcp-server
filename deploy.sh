#!/bin/bash
# Comprehensive Atlassian Suite deployment (Jira + Bitbucket)

set -e

FUNCTION_NAME="atlassian-mcp-server"
REGION="us-west-2"
PROFILE="AdministratorAccess-542754948868"

echo "🚀 Deploying Atlassian Suite MCP Server (Jira + Bitbucket)..."

# Create IAM role if needed
if ! aws iam get-role --role-name lambda-execution-role --profile $PROFILE &>/dev/null; then
    echo "📝 Creating IAM role..."
    cat > trust-policy.json << EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {"Service": "lambda.amazonaws.com"},
      "Action": "sts:AssumeRole"
    }
  ]
}
EOF
    aws iam create-role --role-name lambda-execution-role --assume-role-policy-document file://trust-policy.json --profile $PROFILE
    aws iam attach-role-policy --role-name lambda-execution-role --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole --profile $PROFILE
    rm trust-policy.json
    sleep 10
fi

# Create deployment package
rm -rf package
mkdir package
cp lambda_handler.py package/
pip install -r requirements.txt -t package/
cd package && zip -r ../function.zip . && cd ..

# Deploy function
if aws lambda get-function --function-name $FUNCTION_NAME --region $REGION --profile $PROFILE &>/dev/null; then
    echo "🔄 Updating function..."
    aws lambda update-function-code --function-name $FUNCTION_NAME --zip-file fileb://function.zip --region $REGION --profile $PROFILE
else
    echo "🆕 Creating function..."
    aws lambda create-function \
        --function-name $FUNCTION_NAME \
        --runtime python3.11 \
        --role arn:aws:iam::$(aws sts get-caller-identity --profile $PROFILE --query Account --output text):role/lambda-execution-role \
        --handler lambda_handler.lambda_handler \
        --zip-file fileb://function.zip \
        --timeout 60 \
        --memory-size 256 \
        --region $REGION \
        --profile $PROFILE
fi

# Configure credentials
if [ ! -z "$1" ] && [ ! -z "$2" ] && [ ! -z "$3" ] && [ ! -z "$4" ]; then
    echo "🔧 Configuring Atlassian credentials..."
    cat > env-config.json << EOF
{
  "Variables": {
    "JIRA_URL": "https://nsandeep12.atlassian.net",
    "JIRA_EMAIL": "nsandeep12@gmail.com",
    "JIRA_API_TOKEN": "$1",
    "BITBUCKET_WORKSPACE": "$2",
    "BITBUCKET_USERNAME": "$3",
    "BITBUCKET_APP_PASSWORD": "$4"
  }
}
EOF
    aws lambda update-function-configuration --function-name $FUNCTION_NAME --region $REGION --profile $PROFILE --environment file://env-config.json
    rm env-config.json
elif [ ! -z "$1" ]; then
    echo "🔧 Configuring Jira credentials only..."
    cat > env-config.json << EOF
{
  "Variables": {
    "JIRA_URL": "https://nsandeep12.atlassian.net",
    "JIRA_EMAIL": "nsandeep12@gmail.com",
    "JIRA_API_TOKEN": "$1"
  }
}
EOF
    aws lambda update-function-configuration --function-name $FUNCTION_NAME --region $REGION --profile $PROFILE --environment file://env-config.json
    rm env-config.json
fi

# Setup Q CLI
mkdir -p ~/.config/q
cp q-mcp-config.json ~/.config/q/mcp-servers.json

# Clean up
rm -rf package function.zip

echo "✅ Deployment complete!"
echo ""
echo "📋 Available integrations:"
echo "  🎫 Jira: Search issues, create issues, cross-reference with Bitbucket"
echo "  🔧 Bitbucket: Repositories, pull requests, branches, commits"
echo "  🔗 Cross-references: Link Jira issues with Bitbucket PRs and commits"
echo ""

if [ -z "$1" ]; then
    echo "💡 Configure credentials:"
    echo "  Jira only: ./deploy.sh JIRA_API_TOKEN"
    echo "  Full suite: ./deploy.sh JIRA_API_TOKEN BITBUCKET_WORKSPACE BITBUCKET_USERNAME BITBUCKET_APP_PASSWORD"
    echo ""
    echo "🔑 Get Bitbucket app password: https://bitbucket.org/account/settings/app-passwords/"
elif [ -z "$2" ]; then
    echo "💡 Add Bitbucket: ./deploy.sh $1 BITBUCKET_WORKSPACE BITBUCKET_USERNAME BITBUCKET_APP_PASSWORD"
    echo "🔑 Get Bitbucket app password: https://bitbucket.org/account/settings/app-passwords/"
else
    echo "🧪 Test Jira: aws lambda invoke --function-name $FUNCTION_NAME --region $REGION --profile $PROFILE --cli-binary-format raw-in-base64-out --payload '{\"action\":\"call_tool\",\"tool_name\":\"search_jira_issues\",\"arguments\":{\"jql\":\"project = SCRUM\",\"max_results\":3}}' response.json"
    echo "🧪 Test Bitbucket: aws lambda invoke --function-name $FUNCTION_NAME --region $REGION --profile $PROFILE --cli-binary-format raw-in-base64-out --payload '{\"action\":\"call_tool\",\"tool_name\":\"list_bitbucket_repositories\",\"arguments\":{\"limit\":5}}' response.json"
fi
