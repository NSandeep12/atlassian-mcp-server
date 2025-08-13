#!/usr/bin/env python3
"""
Comprehensive Atlassian Suite MCP Server for AWS Lambda
Integrates Jira and Bitbucket with cross-referencing capabilities
"""

import json
import os
import requests
from requests.auth import HTTPBasicAuth
import re
from urllib.parse import quote

# Atlassian configuration from environment variables
JIRA_URL = os.environ.get("JIRA_URL")
JIRA_EMAIL = os.environ.get("JIRA_EMAIL")
JIRA_API_TOKEN = os.environ.get("JIRA_API_TOKEN")

BITBUCKET_WORKSPACE = os.environ.get("BITBUCKET_WORKSPACE")
BITBUCKET_USERNAME = os.environ.get("BITBUCKET_USERNAME")
BITBUCKET_APP_PASSWORD = os.environ.get("BITBUCKET_APP_PASSWORD")

def make_request(service, method, endpoint, data=None):
    """Make authenticated API request to Jira or Bitbucket"""
    if service == "jira":
        if not all([JIRA_URL, JIRA_EMAIL, JIRA_API_TOKEN]):
            raise ValueError("Missing Jira configuration")
        url = f"{JIRA_URL}/rest/api/2/{endpoint}"
        auth = HTTPBasicAuth(JIRA_EMAIL, JIRA_API_TOKEN)
    
    elif service == "bitbucket":
        if not all([BITBUCKET_WORKSPACE, BITBUCKET_USERNAME, BITBUCKET_APP_PASSWORD]):
            raise ValueError("Missing Bitbucket configuration")
        url = f"https://api.bitbucket.org/2.0/{endpoint}"
        auth = HTTPBasicAuth(BITBUCKET_USERNAME, BITBUCKET_APP_PASSWORD)
    
    else:
        raise ValueError(f"Unknown service: {service}")
    
    if method == "GET":
        response = requests.get(url, auth=auth)
    elif method == "POST":
        response = requests.post(url, auth=auth, json=data)
    elif method == "PUT":
        response = requests.put(url, auth=auth, json=data)
    else:
        raise ValueError(f"Unsupported HTTP method: {method}")
    
    response.raise_for_status()
    return response.json() if response.content else {}

# ============================================================================
# JIRA OPERATIONS
# ============================================================================

def search_jira_issues(jql, max_results=10):
    """Search Jira issues using JQL"""
    try:
        response = make_request("jira", "GET", f"search?jql={quote(jql)}&maxResults={max_results}")
        
        if not response.get("issues"):
            return "No issues found matching the query."
        
        results = []
        for issue in response["issues"]:
            key = issue["key"]
            summary = issue["fields"]["summary"]
            status = issue["fields"]["status"]["name"]
            assignee = issue["fields"].get("assignee")
            assignee_name = assignee["displayName"] if assignee else "Unassigned"
            
            # Look for Bitbucket references in description
            description = issue["fields"].get("description", "")
            bitbucket_refs = extract_bitbucket_references(description)
            bitbucket_info = f" [🔗 {', '.join(bitbucket_refs)}]" if bitbucket_refs else ""
            
            results.append(f"• {key}: {summary} [{status}] - {assignee_name}{bitbucket_info}")
        
        return f"Found {len(results)} issue(s):\n\n" + "\n".join(results)
    
    except Exception as e:
        return f"❌ Error searching issues: {str(e)}"

def create_jira_issue(project_key, summary, description="", issue_type="Task", bitbucket_repo=None, branch=None):
    """Create a new Jira issue with optional Bitbucket references"""
    try:
        # Add Bitbucket references to description if provided
        if bitbucket_repo or branch:
            bitbucket_section = "\n\n--- Bitbucket References ---\n"
            if bitbucket_repo:
                bitbucket_section += f"Repository: {bitbucket_repo}\n"
            if branch:
                bitbucket_section += f"Branch: {branch}\n"
            description += bitbucket_section
        
        issue_data = {
            "fields": {
                "project": {"key": project_key},
                "summary": summary,
                "description": description,
                "issuetype": {"name": issue_type}
            }
        }
        
        response = make_request("jira", "POST", "issue", issue_data)
        issue_key = response.get("key")
        
        result = f"✅ Created issue: {issue_key}\nTitle: {summary}\nType: {issue_type}"
        if bitbucket_repo:
            result += f"\n🔗 Linked to repository: {bitbucket_repo}"
        
        return result
    
    except Exception as e:
        return f"❌ Error creating issue: {str(e)}"

# ============================================================================
# BITBUCKET OPERATIONS
# ============================================================================

def list_bitbucket_repositories(limit=10):
    """List Bitbucket repositories in workspace"""
    try:
        response = make_request("bitbucket", "GET", f"repositories/{BITBUCKET_WORKSPACE}?pagelen={limit}")
        
        if not response.get("values"):
            return "No repositories found in workspace."
        
        results = []
        for repo in response["values"]:
            name = repo["name"]
            full_name = repo["full_name"]
            language = repo.get("language", "Unknown")
            is_private = "🔒 Private" if repo.get("is_private") else "🌐 Public"
            
            # Look for Jira references in description
            description = repo.get("description", "")
            jira_refs = extract_jira_references(description)
            jira_info = f" [🎫 {', '.join(jira_refs)}]" if jira_refs else ""
            
            results.append(f"• {name} ({language}) - {is_private}{jira_info}")
        
        return f"Found {len(results)} repository(ies):\n\n" + "\n".join(results)
    
    except Exception as e:
        return f"❌ Error listing repositories: {str(e)}"

def list_pull_requests(repo_name, state="OPEN", limit=10):
    """List pull requests for a repository"""
    try:
        response = make_request("bitbucket", "GET", f"repositories/{BITBUCKET_WORKSPACE}/{repo_name}/pullrequests?state={state}&pagelen={limit}")
        
        if not response.get("values"):
            return f"No {state.lower()} pull requests found in {repo_name}."
        
        results = []
        for pr in response["values"]:
            id_num = pr["id"]
            title = pr["title"]
            author = pr["author"]["display_name"]
            source_branch = pr["source"]["branch"]["name"]
            dest_branch = pr["destination"]["branch"]["name"]
            
            # Look for Jira references in title and description
            jira_refs = extract_jira_references(f"{title} {pr.get('description', '')}")
            jira_info = f" [🎫 {', '.join(jira_refs)}]" if jira_refs else ""
            
            results.append(f"• PR #{id_num}: {title}\n  {source_branch} → {dest_branch} by {author}{jira_info}")
        
        return f"Found {len(results)} {state.lower()} pull request(s) in {repo_name}:\n\n" + "\n".join(results)
    
    except Exception as e:
        return f"❌ Error listing pull requests: {str(e)}"

def create_pull_request(repo_name, title, source_branch, dest_branch="main", description="", jira_issue=None):
    """Create a new pull request with optional Jira issue reference"""
    try:
        # Add Jira reference to description if provided
        if jira_issue:
            description += f"\n\nResolves: {jira_issue}"
        
        pr_data = {
            "title": title,
            "description": description,
            "source": {"branch": {"name": source_branch}},
            "destination": {"branch": {"name": dest_branch}}
        }
        
        response = make_request("bitbucket", "POST", f"repositories/{BITBUCKET_WORKSPACE}/{repo_name}/pullrequests", pr_data)
        pr_id = response.get("id")
        
        result = f"✅ Created pull request: #{pr_id}\nTitle: {title}\n{source_branch} → {dest_branch}"
        if jira_issue:
            result += f"\n🎫 Linked to Jira issue: {jira_issue}"
        
        return result
    
    except Exception as e:
        return f"❌ Error creating pull request: {str(e)}"

def list_branches(repo_name, limit=10):
    """List branches in a repository"""
    try:
        response = make_request("bitbucket", "GET", f"repositories/{BITBUCKET_WORKSPACE}/{repo_name}/refs/branches?pagelen={limit}")
        
        if not response.get("values"):
            return f"No branches found in {repo_name}."
        
        results = []
        for branch in response["values"]:
            name = branch["name"]
            # Check if it's the main branch
            is_main = "🌟 " if name in ["main", "master", "develop"] else ""
            results.append(f"• {is_main}{name}")
        
        return f"Found {len(results)} branch(es) in {repo_name}:\n\n" + "\n".join(results)
    
    except Exception as e:
        return f"❌ Error listing branches: {str(e)}"

def get_commits(repo_name, branch="main", limit=10):
    """Get recent commits from a branch"""
    try:
        response = make_request("bitbucket", "GET", f"repositories/{BITBUCKET_WORKSPACE}/{repo_name}/commits/{branch}?pagelen={limit}")
        
        if not response.get("values"):
            return f"No commits found in {repo_name}/{branch}."
        
        results = []
        for commit in response["values"]:
            hash_short = commit["hash"][:8]
            message = commit["message"].split('\n')[0]  # First line only
            author = commit["author"]["user"]["display_name"] if commit["author"].get("user") else "Unknown"
            
            # Look for Jira references in commit message
            jira_refs = extract_jira_references(commit["message"])
            jira_info = f" [🎫 {', '.join(jira_refs)}]" if jira_refs else ""
            
            results.append(f"• {hash_short}: {message} - {author}{jira_info}")
        
        return f"Recent commits in {repo_name}/{branch}:\n\n" + "\n".join(results)
    
    except Exception as e:
        return f"❌ Error getting commits: {str(e)}"

# ============================================================================
# CROSS-REFERENCE UTILITIES
# ============================================================================

def extract_jira_references(text):
    """Extract Jira issue keys from text"""
    if not text:
        return []
    # Match patterns like PROJ-123, ABC-456, etc.
    pattern = r'\b[A-Z]{2,10}-\d+\b'
    return list(set(re.findall(pattern, text)))

def extract_bitbucket_references(text):
    """Extract Bitbucket repository references from text"""
    if not text:
        return []
    # Match patterns like repo-name, workspace/repo-name
    pattern = r'\b(?:[\w-]+/)?[\w-]+(?:\.git)?\b'
    matches = re.findall(pattern, text)
    # Filter to likely repository names (contains hyphens or slashes)
    return [m for m in matches if '-' in m or '/' in m]

def search_cross_references(jira_issue_key):
    """Find Bitbucket references for a Jira issue"""
    try:
        # Get Jira issue details
        jira_response = make_request("jira", "GET", f"issue/{jira_issue_key}")
        issue_summary = jira_response["fields"]["summary"]
        issue_description = jira_response["fields"].get("description", "")
        
        # Search for pull requests mentioning this issue
        repos_response = make_request("bitbucket", "GET", f"repositories/{BITBUCKET_WORKSPACE}?pagelen=50")
        
        related_prs = []
        for repo in repos_response.get("values", []):
            repo_name = repo["name"]
            try:
                prs_response = make_request("bitbucket", "GET", f"repositories/{BITBUCKET_WORKSPACE}/{repo_name}/pullrequests?pagelen=50")
                for pr in prs_response.get("values", []):
                    pr_text = f"{pr['title']} {pr.get('description', '')}"
                    if jira_issue_key in pr_text:
                        related_prs.append(f"PR #{pr['id']} in {repo_name}: {pr['title']}")
            except:
                continue  # Skip repos we can't access
        
        result = f"Cross-references for {jira_issue_key}:\n"
        result += f"📋 Issue: {issue_summary}\n\n"
        
        if related_prs:
            result += "🔗 Related Pull Requests:\n"
            result += "\n".join(f"• {pr}" for pr in related_prs)
        else:
            result += "No related pull requests found."
        
        return result
    
    except Exception as e:
        return f"❌ Error finding cross-references: {str(e)}"

# ============================================================================
# LAMBDA HANDLER
# ============================================================================

def get_available_tools():
    """Return list of available MCP tools"""
    return [
        # Jira Tools
        {
            "name": "search_jira_issues",
            "description": "Search Jira issues using JQL with Bitbucket cross-references",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "jql": {"type": "string", "description": "JQL query"},
                    "max_results": {"type": "integer", "default": 10}
                },
                "required": ["jql"]
            }
        },
        {
            "name": "create_jira_issue",
            "description": "Create a new Jira issue with optional Bitbucket references",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "project_key": {"type": "string", "description": "Jira project key"},
                    "summary": {"type": "string", "description": "Issue title"},
                    "description": {"type": "string", "default": ""},
                    "issue_type": {"type": "string", "default": "Task"},
                    "bitbucket_repo": {"type": "string", "description": "Related Bitbucket repository"},
                    "branch": {"type": "string", "description": "Related branch name"}
                },
                "required": ["project_key", "summary"]
            }
        },
        
        # Bitbucket Tools
        {
            "name": "list_bitbucket_repositories",
            "description": "List Bitbucket repositories with Jira cross-references",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "limit": {"type": "integer", "default": 10}
                }
            }
        },
        {
            "name": "list_pull_requests",
            "description": "List pull requests for a repository with Jira cross-references",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "repo_name": {"type": "string", "description": "Repository name"},
                    "state": {"type": "string", "default": "OPEN", "description": "PR state (OPEN, MERGED, DECLINED)"},
                    "limit": {"type": "integer", "default": 10}
                },
                "required": ["repo_name"]
            }
        },
        {
            "name": "create_pull_request",
            "description": "Create a new pull request with optional Jira issue reference",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "repo_name": {"type": "string", "description": "Repository name"},
                    "title": {"type": "string", "description": "Pull request title"},
                    "source_branch": {"type": "string", "description": "Source branch name"},
                    "dest_branch": {"type": "string", "default": "main", "description": "Destination branch"},
                    "description": {"type": "string", "default": ""},
                    "jira_issue": {"type": "string", "description": "Related Jira issue key (e.g., PROJ-123)"}
                },
                "required": ["repo_name", "title", "source_branch"]
            }
        },
        {
            "name": "list_branches",
            "description": "List branches in a repository",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "repo_name": {"type": "string", "description": "Repository name"},
                    "limit": {"type": "integer", "default": 10}
                },
                "required": ["repo_name"]
            }
        },
        {
            "name": "get_commits",
            "description": "Get recent commits from a branch with Jira cross-references",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "repo_name": {"type": "string", "description": "Repository name"},
                    "branch": {"type": "string", "default": "main", "description": "Branch name"},
                    "limit": {"type": "integer", "default": 10}
                },
                "required": ["repo_name"]
            }
        },
        
        # Cross-Reference Tools
        {
            "name": "search_cross_references",
            "description": "Find Bitbucket references for a Jira issue",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "jira_issue_key": {"type": "string", "description": "Jira issue key (e.g., PROJ-123)"}
                },
                "required": ["jira_issue_key"]
            }
        }
    ]

def lambda_handler(event, context):
    """AWS Lambda handler for Atlassian Suite MCP requests"""
    
    try:
        action = event.get("action")
        
        if action == "list_tools":
            return {
                "statusCode": 200,
                "body": json.dumps({"tools": get_available_tools()})
            }
        
        elif action == "call_tool":
            tool_name = event.get("tool_name")
            args = event.get("arguments", {})
            
            # Jira Tools
            if tool_name == "search_jira_issues":
                result = search_jira_issues(args.get("jql"), args.get("max_results", 10))
            
            elif tool_name == "create_jira_issue":
                result = create_jira_issue(
                    args.get("project_key"),
                    args.get("summary"),
                    args.get("description", ""),
                    args.get("issue_type", "Task"),
                    args.get("bitbucket_repo"),
                    args.get("branch")
                )
            
            # Bitbucket Tools
            elif tool_name == "list_bitbucket_repositories":
                result = list_bitbucket_repositories(args.get("limit", 10))
            
            elif tool_name == "list_pull_requests":
                result = list_pull_requests(
                    args.get("repo_name"),
                    args.get("state", "OPEN"),
                    args.get("limit", 10)
                )
            
            elif tool_name == "create_pull_request":
                result = create_pull_request(
                    args.get("repo_name"),
                    args.get("title"),
                    args.get("source_branch"),
                    args.get("dest_branch", "main"),
                    args.get("description", ""),
                    args.get("jira_issue")
                )
            
            elif tool_name == "list_branches":
                result = list_branches(args.get("repo_name"), args.get("limit", 10))
            
            elif tool_name == "get_commits":
                result = get_commits(
                    args.get("repo_name"),
                    args.get("branch", "main"),
                    args.get("limit", 10)
                )
            
            # Cross-Reference Tools
            elif tool_name == "search_cross_references":
                result = search_cross_references(args.get("jira_issue_key"))
            
            else:
                return {
                    "statusCode": 400,
                    "body": json.dumps({"error": f"Unknown tool: {tool_name}"})
                }
            
            return {
                "statusCode": 200,
                "body": json.dumps({"result": result})
            }
        
        else:
            return {
                "statusCode": 400,
                "body": json.dumps({"error": f"Unknown action: {action}"})
            }
    
    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        }

# AWS Lambda entry point
if __name__ == "__main__":
    # This will only run in AWS Lambda environment
    pass
