# Bitbucket API Token Setup Guide

## Option 1: Repository Access Token (Recommended for specific repos)

1. **Go to your repository settings:**
   ```
   https://bitbucket.org/YOUR_WORKSPACE/YOUR_REPO/admin/access-tokens/
   ```

2. **Click "Create Repository Access Token"**

3. **Configure the token:**
   - **Name**: `MCP Server Token` or `Q CLI Integration`
   - **Expiration**: Choose appropriate duration (or no expiration)
   - **Permissions**:
     - ✅ **Repositories**: Read, Write
     - ✅ **Pull requests**: Read, Write
     - ✅ **Issues**: Read, Write

4. **Copy the generated token** (you won't see it again!)

## Option 2: Workspace Access Token (For all repos in workspace)

1. **Go to workspace settings:**
   ```
   https://bitbucket.org/YOUR_WORKSPACE/workspace/settings/api
   ```

2. **Create OAuth consumer** or use **App passwords** section

3. **For OAuth consumer:**
   - Set callback URL (can be localhost for CLI usage)
   - Select required permissions
   - Generate access token

## Option 3: Personal Access Token (If available)

Some Bitbucket setups may have personal access tokens available in account settings.

## Current Configuration

Your `.env` file is set up to use API token authentication:

```bash
# Method 1: API Token (Recommended)
BITBUCKET_USERNAME=nsandeep12
BITBUCKET_API_TOKEN=YOUR_API_TOKEN_HERE
BITBUCKET_WORKSPACE=nsandeep12
```

## Steps to Complete Setup:

1. **Get your API token** using one of the methods above

2. **Update your .env file:**
   ```bash
   nano /home/sandynal/jira-mcp-server/.env
   ```
   Replace `YOUR_API_TOKEN_HERE` with your actual token

3. **Test the connection:**
   ```bash
   cd /home/sandynal/jira-mcp-server
   source venv/bin/activate
   python test_bitbucket.py
   ```

4. **If API token doesn't work, fall back to app password:**
   - Uncomment the `BITBUCKET_APP_PASSWORD` line in `.env`
   - Get app password from: https://bitbucket.org/account/settings/app-passwords/
   - The server will automatically try app password if API token fails

## Testing Your Setup

Run the test script to verify everything works:

```bash
source venv/bin/activate
python test_bitbucket.py
```

You should see:
```
✅ API Token authentication successful!
✅ Found X repositories in workspace 'nsandeep12'
```

## Troubleshooting

- **401 Unauthorized**: Check your token and permissions
- **403 Forbidden**: Token may not have required permissions
- **404 Not Found**: Check workspace name is correct
- **Token expired**: Generate a new token

## Security Notes

- Store tokens securely in `.env` file
- Don't commit `.env` to version control
- Use repository-specific tokens when possible
- Set appropriate expiration dates
- Regularly rotate tokens
