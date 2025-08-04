#!/usr/bin/env python3
"""
Jira-Bitbucket-Git MCP Server - Provides integrated Jira, Bitbucket, and Git tools for Q CLI
"""

import asyncio
import os
import json
import subprocess
from typing import Any, Sequence
from pathlib import Path
from dotenv import load_dotenv
import requests
from requests.auth import HTTPBasicAuth
from git import Repo, GitCommandError
from atlassian import Bitbucket

from mcp.server import Server
from mcp.types import Tool, TextContent, ImageContent, EmbeddedResource
from mcp.server.models import InitializationOptions
import mcp.server.stdio
import mcp.types as types

# Load environment variables
load_dotenv()

# Jira configuration
JIRA_URL = os.getenv("JIRA_URL")
JIRA_EMAIL = os.getenv("JIRA_EMAIL")
JIRA_API_TOKEN = os.getenv("JIRA_API_TOKEN")

# Bitbucket configuration
BITBUCKET_USERNAME = os.getenv("BITBUCKET_USERNAME")
BITBUCKET_APP_PASSWORD = os.getenv("BITBUCKET_APP_PASSWORD")  # For app password method
BITBUCKET_API_TOKEN = os.getenv("BITBUCKET_API_TOKEN")  # For API token method
BITBUCKET_OAUTH_KEY = os.getenv("BITBUCKET_OAUTH_KEY")  # For OAuth method
BITBUCKET_OAUTH_SECRET = os.getenv("BITBUCKET_OAUTH_SECRET")  # For OAuth method
BITBUCKET_WORKSPACE = os.getenv("BITBUCKET_WORKSPACE")

# Git configuration
GIT_DEFAULT_BRANCH = os.getenv("GIT_DEFAULT_BRANCH", "main")
GIT_REPOS_PATH = os.getenv("GIT_REPOS_PATH", "/home/sandynal/repos")

# Validate required environment variables
if not all([JIRA_URL, JIRA_EMAIL, JIRA_API_TOKEN]):
    raise ValueError("Missing required Jira environment variables. Please check your .env file.")

# Initialize the server
server = Server("jira-bitbucket-git-server")

def get_jira_auth():
    """Get Jira authentication"""
    return HTTPBasicAuth(JIRA_EMAIL, JIRA_API_TOKEN)

def get_bitbucket_client():
    """Get Bitbucket client with OAuth, API token, or app password"""
    if BITBUCKET_OAUTH_KEY and BITBUCKET_OAUTH_SECRET:
        # Use OAuth authentication
        return Bitbucket(
            username=BITBUCKET_USERNAME,
            password=BITBUCKET_OAUTH_SECRET,  # Use secret as password for basic auth
            cloud=True
        )
    elif BITBUCKET_API_TOKEN:
        # Use API token authentication
        return Bitbucket(
            username=BITBUCKET_USERNAME,
            password=BITBUCKET_API_TOKEN,
            cloud=True
        )
    elif BITBUCKET_USERNAME and BITBUCKET_APP_PASSWORD:
        # Fall back to app password authentication
        return Bitbucket(
            username=BITBUCKET_USERNAME,
            password=BITBUCKET_APP_PASSWORD,
            cloud=True
        )
    else:
        raise ValueError("Missing Bitbucket credentials. Please provide OAuth key/secret, API token, or app password")

def make_bitbucket_api_request(method: str, endpoint: str, data: dict = None) -> dict:
    """Make a direct request to Bitbucket API using available authentication"""
    url = f"https://api.bitbucket.org/2.0/{endpoint}"
    headers = {"Content-Type": "application/json"}
    
    # Choose authentication method
    if BITBUCKET_OAUTH_KEY and BITBUCKET_OAUTH_SECRET:
        # Use OAuth key as username and secret as password for basic auth
        auth = HTTPBasicAuth(BITBUCKET_OAUTH_KEY, BITBUCKET_OAUTH_SECRET)
    elif BITBUCKET_API_TOKEN:
        headers["Authorization"] = f"Bearer {BITBUCKET_API_TOKEN}"
        auth = None
    elif BITBUCKET_USERNAME and BITBUCKET_APP_PASSWORD:
        auth = HTTPBasicAuth(BITBUCKET_USERNAME, BITBUCKET_APP_PASSWORD)
    else:
        raise ValueError("No valid Bitbucket authentication method configured")
    
    try:
        if method.upper() == "GET":
            response = requests.get(url, headers=headers, auth=auth)
        elif method.upper() == "POST":
            response = requests.post(url, headers=headers, json=data, auth=auth)
        elif method.upper() == "PUT":
            response = requests.put(url, headers=headers, json=data, auth=auth)
        else:
            raise ValueError(f"Unsupported HTTP method: {method}")
        
        response.raise_for_status()
        return response.json() if response.content else {}
    except requests.exceptions.RequestException as e:
        raise Exception(f"Bitbucket API request failed: {str(e)}")

def make_jira_request(method: str, endpoint: str, data: dict = None) -> dict:
    """Make a request to Jira API"""
    url = f"{JIRA_URL}/rest/api/2/{endpoint}"
    headers = {"Content-Type": "application/json"}
    
    try:
        if method.upper() == "GET":
            response = requests.get(url, auth=get_jira_auth(), headers=headers)
        elif method.upper() == "POST":
            response = requests.post(url, auth=get_jira_auth(), headers=headers, json=data)
        elif method.upper() == "PUT":
            response = requests.put(url, auth=get_jira_auth(), headers=headers, json=data)
        else:
            raise ValueError(f"Unsupported HTTP method: {method}")
        
        response.raise_for_status()
        return response.json() if response.content else {}
    except requests.exceptions.RequestException as e:
        raise Exception(f"Jira API request failed: {str(e)}")

def ensure_repos_directory():
    """Ensure the repos directory exists"""
    Path(GIT_REPOS_PATH).mkdir(parents=True, exist_ok=True)

@server.list_tools()
async def handle_list_tools() -> list[Tool]:
    """List available tools"""
    return [
        # Jira tools
        Tool(
            name="search_issues",
            description="Search for Jira issues using JQL",
            inputSchema={
                "type": "object",
                "properties": {
                    "jql": {
                        "type": "string",
                        "description": "JQL query string (e.g., 'project = PROJ AND status = Open')"
                    },
                    "max_results": {
                        "type": "integer",
                        "description": "Maximum number of results to return",
                        "default": 10
                    }
                },
                "required": ["jql"]
            }
        ),
        Tool(
            name="get_issue",
            description="Get details of a Jira issue",
            inputSchema={
                "type": "object",
                "properties": {
                    "issue_key": {
                        "type": "string",
                        "description": "The issue key (e.g., 'PROJ-123')"
                    }
                },
                "required": ["issue_key"]
            }
        ),
        Tool(
            name="create_issue",
            description="Create a new Jira issue",
            inputSchema={
                "type": "object",
                "properties": {
                    "project_key": {
                        "type": "string",
                        "description": "The project key (e.g., 'PROJ', 'DEV')"
                    },
                    "summary": {
                        "type": "string",
                        "description": "Issue summary/title"
                    },
                    "description": {
                        "type": "string",
                        "description": "Detailed description of the issue"
                    },
                    "issue_type": {
                        "type": "string",
                        "description": "Type of issue (Task, Bug, Story, etc.)",
                        "default": "Task"
                    }
                },
                "required": ["project_key", "summary"]
            }
        ),
        # Bitbucket tools
        Tool(
            name="list_repositories",
            description="List Bitbucket repositories in workspace",
            inputSchema={
                "type": "object",
                "properties": {
                    "workspace": {
                        "type": "string",
                        "description": "Workspace name (optional, uses default from config)"
                    }
                }
            }
        ),
        Tool(
            name="get_repository_info",
            description="Get information about a specific repository",
            inputSchema={
                "type": "object",
                "properties": {
                    "repo_slug": {
                        "type": "string",
                        "description": "Repository slug/name"
                    },
                    "workspace": {
                        "type": "string",
                        "description": "Workspace name (optional, uses default from config)"
                    }
                },
                "required": ["repo_slug"]
            }
        ),
        # Git tools
        Tool(
            name="clone_repository",
            description="Clone a repository from Bitbucket",
            inputSchema={
                "type": "object",
                "properties": {
                    "repo_slug": {
                        "type": "string",
                        "description": "Repository slug/name to clone"
                    },
                    "workspace": {
                        "type": "string",
                        "description": "Workspace name (optional, uses default from config)"
                    },
                    "local_path": {
                        "type": "string",
                        "description": "Local path to clone to (optional, uses default repos directory)"
                    }
                },
                "required": ["repo_slug"]
            }
        ),
        Tool(
            name="create_branch",
            description="Create a new git branch (optionally based on Jira issue)",
            inputSchema={
                "type": "object",
                "properties": {
                    "repo_path": {
                        "type": "string",
                        "description": "Path to the git repository"
                    },
                    "branch_name": {
                        "type": "string",
                        "description": "Name of the new branch"
                    },
                    "issue_key": {
                        "type": "string",
                        "description": "Jira issue key to base branch name on (optional)"
                    },
                    "base_branch": {
                        "type": "string",
                        "description": "Base branch to create from (optional, defaults to main)"
                    }
                },
                "required": ["repo_path"]
            }
        ),
        Tool(
            name="git_status",
            description="Get git status of a repository",
            inputSchema={
                "type": "object",
                "properties": {
                    "repo_path": {
                        "type": "string",
                        "description": "Path to the git repository"
                    }
                },
                "required": ["repo_path"]
            }
        ),
        Tool(
            name="commit_changes",
            description="Commit changes to git repository",
            inputSchema={
                "type": "object",
                "properties": {
                    "repo_path": {
                        "type": "string",
                        "description": "Path to the git repository"
                    },
                    "message": {
                        "type": "string",
                        "description": "Commit message"
                    },
                    "issue_key": {
                        "type": "string",
                        "description": "Jira issue key to reference in commit (optional)"
                    }
                },
                "required": ["repo_path", "message"]
            }
        ),
        # Workflow tools
        Tool(
            name="create_feature_branch_for_issue",
            description="Create a feature branch for a Jira issue and clone repo if needed",
            inputSchema={
                "type": "object",
                "properties": {
                    "issue_key": {
                        "type": "string",
                        "description": "Jira issue key"
                    },
                    "repo_slug": {
                        "type": "string",
                        "description": "Repository slug/name"
                    },
                    "workspace": {
                        "type": "string",
                        "description": "Workspace name (optional, uses default from config)"
                    }
                },
                "required": ["issue_key", "repo_slug"]
            }
        )
    ]

@server.call_tool()
async def handle_call_tool(name: str, arguments: dict) -> list[types.TextContent]:
    """Handle tool calls"""
    
    try:
        if name == "search_issues":
            jql = arguments["jql"]
            max_results = arguments.get("max_results", 10)
            
            endpoint = f"search?jql={jql}&maxResults={max_results}"
            result = make_jira_request("GET", endpoint)
            
            issues = []
            for issue in result.get("issues", []):
                issues.append({
                    "key": issue["key"],
                    "summary": issue["fields"]["summary"],
                    "status": issue["fields"]["status"]["name"],
                    "assignee": issue["fields"]["assignee"]["displayName"] if issue["fields"]["assignee"] else "Unassigned",
                    "created": issue["fields"]["created"]
                })
            
            return [types.TextContent(
                type="text",
                text=f"Found {len(issues)} issues:\n" + json.dumps(issues, indent=2)
            )]
        
        elif name == "get_issue":
            issue_key = arguments["issue_key"]
            result = make_jira_request("GET", f"issue/{issue_key}")
            
            issue_info = {
                "key": result["key"],
                "summary": result["fields"]["summary"],
                "description": result["fields"]["description"],
                "status": result["fields"]["status"]["name"],
                "assignee": result["fields"]["assignee"]["displayName"] if result["fields"]["assignee"] else "Unassigned",
                "created": result["fields"]["created"],
                "updated": result["fields"]["updated"]
            }
            
            return [types.TextContent(
                type="text",
                text=json.dumps(issue_info, indent=2)
            )]
        
        elif name == "create_issue":
            project_key = arguments["project_key"]
            summary = arguments["summary"]
            description = arguments.get("description", "")
            issue_type = arguments.get("issue_type", "Task")
            
            issue_data = {
                "fields": {
                    "project": {"key": project_key},
                    "summary": summary,
                    "description": description,
                    "issuetype": {"name": issue_type}
                }
            }
            
            result = make_jira_request("POST", "issue", issue_data)
            
            return [types.TextContent(
                type="text",
                text=f"Created issue: {result['key']}\nURL: {JIRA_URL}/browse/{result['key']}"
            )]
        
        elif name == "list_repositories":
            workspace = arguments.get("workspace", BITBUCKET_WORKSPACE)
            if not workspace:
                raise ValueError("No workspace specified and no default workspace configured")
            
            bitbucket = get_bitbucket_client()
            repos = bitbucket.repo_list(workspace)
            
            repo_list = []
            for repo in repos.get("values", []):
                repo_list.append({
                    "name": repo["name"],
                    "slug": repo["slug"],
                    "full_name": repo["full_name"],
                    "clone_url": repo["links"]["clone"][0]["href"],
                    "updated": repo["updated_on"]
                })
            
            return [types.TextContent(
                type="text",
                text=f"Found {len(repo_list)} repositories:\n" + json.dumps(repo_list, indent=2)
            )]
        
        elif name == "clone_repository":
            repo_slug = arguments["repo_slug"]
            workspace = arguments.get("workspace", BITBUCKET_WORKSPACE)
            local_path = arguments.get("local_path")
            
            if not workspace:
                raise ValueError("No workspace specified and no default workspace configured")
            
            ensure_repos_directory()
            
            if not local_path:
                local_path = os.path.join(GIT_REPOS_PATH, repo_slug)
            
            # Use SSH for git operations (more reliable than HTTPS with auth)
            clone_url = f"git@bitbucket.org:{workspace}/{repo_slug}.git"
            
            try:
                repo = Repo.clone_from(clone_url, local_path)
                return [types.TextContent(
                    type="text",
                    text=f"Successfully cloned {repo_slug} to {local_path} using SSH"
                )]
            except GitCommandError as e:
                return [types.TextContent(
                    type="text",
                    text=f"Failed to clone repository: {str(e)}\nMake sure the repository exists and you have access to it."
                )]
        
        elif name == "create_branch":
            repo_path = arguments["repo_path"]
            branch_name = arguments.get("branch_name")
            issue_key = arguments.get("issue_key")
            base_branch = arguments.get("base_branch", GIT_DEFAULT_BRANCH)
            
            if not branch_name and issue_key:
                # Get issue details to create meaningful branch name
                issue_result = make_jira_request("GET", f"issue/{issue_key}")
                summary = issue_result["fields"]["summary"]
                # Create branch name from issue key and summary
                clean_summary = "".join(c for c in summary if c.isalnum() or c in (' ', '-', '_')).rstrip()
                clean_summary = clean_summary.replace(' ', '-').lower()[:30]
                branch_name = f"feature/{issue_key.lower()}-{clean_summary}"
            elif not branch_name:
                raise ValueError("Either branch_name or issue_key must be provided")
            
            try:
                repo = Repo(repo_path)
                
                # Checkout base branch and pull latest
                repo.git.checkout(base_branch)
                repo.git.pull()
                
                # Create and checkout new branch
                new_branch = repo.create_head(branch_name)
                new_branch.checkout()
                
                return [types.TextContent(
                    type="text",
                    text=f"Created and checked out branch: {branch_name}"
                )]
            except Exception as e:
                return [types.TextContent(
                    type="text",
                    text=f"Failed to create branch: {str(e)}"
                )]
        
        elif name == "git_status":
            repo_path = arguments["repo_path"]
            
            try:
                repo = Repo(repo_path)
                status = repo.git.status()
                current_branch = repo.active_branch.name
                
                return [types.TextContent(
                    type="text",
                    text=f"Current branch: {current_branch}\n\nStatus:\n{status}"
                )]
            except Exception as e:
                return [types.TextContent(
                    type="text",
                    text=f"Failed to get git status: {str(e)}"
                )]
        
        elif name == "commit_changes":
            repo_path = arguments["repo_path"]
            message = arguments["message"]
            issue_key = arguments.get("issue_key")
            
            if issue_key:
                message = f"{message}\n\nRefs: {issue_key}"
            
            try:
                repo = Repo(repo_path)
                
                # Add all changes
                repo.git.add(A=True)
                
                # Commit
                repo.index.commit(message)
                
                return [types.TextContent(
                    type="text",
                    text=f"Successfully committed changes with message: {message}"
                )]
            except Exception as e:
                return [types.TextContent(
                    type="text",
                    text=f"Failed to commit changes: {str(e)}"
                )]
        
        elif name == "create_feature_branch_for_issue":
            issue_key = arguments["issue_key"]
            repo_slug = arguments["repo_slug"]
            workspace = arguments.get("workspace", BITBUCKET_WORKSPACE)
            
            # Get issue details
            issue_result = make_jira_request("GET", f"issue/{issue_key}")
            issue_summary = issue_result["fields"]["summary"]
            
            # Check if repo exists locally
            local_repo_path = os.path.join(GIT_REPOS_PATH, repo_slug)
            
            if not os.path.exists(local_repo_path):
                # Clone the repository using SSH
                ensure_repos_directory()
                clone_url = f"git@bitbucket.org:{workspace}/{repo_slug}.git"
                
                try:
                    Repo.clone_from(clone_url, local_repo_path)
                except GitCommandError as e:
                    return [types.TextContent(
                        type="text",
                        text=f"Failed to clone repository: {str(e)}\nMake sure the repository '{repo_slug}' exists and you have access to it."
                    )]
            
            # Create feature branch
            try:
                repo = Repo(local_repo_path)
                
                # Checkout main and pull latest
                repo.git.checkout(GIT_DEFAULT_BRANCH)
                repo.git.pull()
                
                # Create branch name
                clean_summary = "".join(c for c in issue_summary if c.isalnum() or c in (' ', '-', '_')).rstrip()
                clean_summary = clean_summary.replace(' ', '-').lower()[:30]
                branch_name = f"feature/{issue_key.lower()}-{clean_summary}"
                
                # Create and checkout new branch
                new_branch = repo.create_head(branch_name)
                new_branch.checkout()
                
                return [types.TextContent(
                    type="text",
                    text=f"Successfully set up development environment:\n"
                         f"- Repository: {repo_slug}\n"
                         f"- Local path: {local_repo_path}\n"
                         f"- Branch: {branch_name}\n"
                         f"- Issue: {issue_key} - {issue_summary}\n\n"
                         f"Ready to start development!"
                )]
            except Exception as e:
                return [types.TextContent(
                    type="text",
                    text=f"Failed to create feature branch: {str(e)}"
                )]
        
        else:
            return [types.TextContent(
                type="text",
                text=f"Unknown tool: {name}"
            )]
    
    except Exception as e:
        return [types.TextContent(
            type="text",
            text=f"Error executing {name}: {str(e)}"
        )]

async def main():
    # Run the server using stdin/stdout streams
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="jira-bitbucket-git-server",
                server_version="1.0.0",
                capabilities=server.get_capabilities(),
            ),
        )

if __name__ == "__main__":
    asyncio.run(main())
