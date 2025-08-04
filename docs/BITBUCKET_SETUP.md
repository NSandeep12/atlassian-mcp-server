# Extended Jira-Bitbucket-Git MCP Server Setup

Your MCP server has been extended to include Bitbucket and Git functionality!

## New Configuration Required

### 1. Update your .env file with Bitbucket credentials:

```bash
# Bitbucket Configuration
BITBUCKET_USERNAME=your-bitbucket-username
BITBUCKET_APP_PASSWORD=your-bitbucket-app-password
BITBUCKET_WORKSPACE=your-workspace-name

# Git Configuration
GIT_DEFAULT_BRANCH=main
GIT_REPOS_PATH=/home/sandynal/repos
```

### 2. Get Bitbucket App Password:

1. Go to https://bitbucket.org/account/settings/app-passwords/
2. Click "Create app password"
3. Give it a name like "MCP Server"
4. Select permissions:
   - Repositories: Read, Write
   - Pull requests: Read, Write
   - Issues: Read, Write
5. Copy the generated password

### 3. Find your workspace name:
- Go to your Bitbucket dashboard
- The workspace name is in the URL: `https://bitbucket.org/workspace-name/`

## New Capabilities

### Jira + Git Workflow Tools:
- `create_feature_branch_for_issue` - Clone repo and create branch for Jira issue
- `search_issues` - Find your assigned issues
- `get_issue` - Get issue details

### Bitbucket Tools:
- `list_repositories` - List all repos in workspace
- `get_repository_info` - Get repo details
- `clone_repository` - Clone a repository

### Git Tools:
- `create_branch` - Create feature branches
- `git_status` - Check repository status
- `commit_changes` - Commit with Jira issue references

## Usage Examples

### Complete Workflow:
```bash
# Find your assigned issues
q chat "Use jira-bitbucket-git-server___search_issues with JQL 'assignee = currentUser() AND status != Done'"

# Set up development environment for an issue
q chat "Use jira-bitbucket-git-server___create_feature_branch_for_issue with issue_key 'DEV-123' and repo_slug 'my-project'"

# Check status while working
q chat "Use jira-bitbucket-git-server___git_status with repo_path '/home/sandynal/repos/my-project'"

# Commit your changes
q chat "Use jira-bitbucket-git-server___commit_changes with repo_path '/home/sandynal/repos/my-project', message 'Fix login bug' and issue_key 'DEV-123'"
```

### List your repositories:
```bash
q chat "Use jira-bitbucket-git-server___list_repositories"
```

### Clone a specific repository:
```bash
q chat "Use jira-bitbucket-git-server___clone_repository with repo_slug 'my-project'"
```

## Testing the Extended Server

1. Update your .env file with Bitbucket credentials
2. Test the server:
```bash
source venv/bin/activate
python jira_bitbucket_server.py
```

3. Update your Q CLI MCP configuration to use the new server file.

## Directory Structure

The server will create a `/home/sandynal/repos` directory to store cloned repositories. You can change this by updating `GIT_REPOS_PATH` in your .env file.
