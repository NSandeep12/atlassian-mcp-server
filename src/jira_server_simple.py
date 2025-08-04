#!/usr/bin/env python3
"""
Simple Jira MCP Server - Provides Jira integration tools for Q CLI
"""

import asyncio
import os
import json
from typing import Any, Sequence
from dotenv import load_dotenv
import requests
from requests.auth import HTTPBasicAuth

# Load environment variables
load_dotenv()

# Jira configuration
JIRA_URL = os.getenv("JIRA_URL", "https://your-domain.atlassian.net")
JIRA_EMAIL = os.getenv("JIRA_EMAIL", "your-email@company.com")
JIRA_API_TOKEN = os.getenv("JIRA_API_TOKEN", "your-api-token")

def get_jira_auth():
    """Get Jira authentication"""
    return HTTPBasicAuth(JIRA_EMAIL, JIRA_API_TOKEN)

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
        return {"error": str(e), "status_code": getattr(e.response, 'status_code', None)}

async def handle_mcp_request(request):
    """Handle MCP protocol requests"""
    try:
        if request.get("method") == "tools/list":
            return {
                "tools": [
                    {
                        "name": "create_issue",
                        "description": "Create a new Jira issue",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "project_key": {"type": "string", "description": "Project key (e.g., 'PROJ')"},
                                "summary": {"type": "string", "description": "Issue summary"},
                                "description": {"type": "string", "description": "Issue description"},
                                "issue_type": {"type": "string", "default": "Task"}
                            },
                            "required": ["project_key", "summary"]
                        }
                    },
                    {
                        "name": "get_issue",
                        "description": "Get Jira issue details",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "issue_key": {"type": "string", "description": "Issue key (e.g., 'PROJ-123')"}
                            },
                            "required": ["issue_key"]
                        }
                    },
                    {
                        "name": "search_issues",
                        "description": "Search Jira issues with JQL",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "jql": {"type": "string", "description": "JQL query"},
                                "max_results": {"type": "integer", "default": 10}
                            },
                            "required": ["jql"]
                        }
                    }
                ]
            }
        
        elif request.get("method") == "tools/call":
            tool_name = request.get("params", {}).get("name")
            arguments = request.get("params", {}).get("arguments", {})
            
            if tool_name == "create_issue":
                return await create_issue(arguments)
            elif tool_name == "get_issue":
                return await get_issue(arguments)
            elif tool_name == "search_issues":
                return await search_issues(arguments)
            else:
                return {"error": f"Unknown tool: {tool_name}"}
        
        else:
            return {"error": f"Unknown method: {request.get('method')}"}
    
    except Exception as e:
        return {"error": str(e)}

async def create_issue(args: dict):
    """Create a new Jira issue"""
    payload = {
        "fields": {
            "project": {"key": args["project_key"]},
            "summary": args["summary"],
            "description": args.get("description", ""),
            "issuetype": {"name": args.get("issue_type", "Task")}
        }
    }
    
    result = make_jira_request("POST", "issue", payload)
    
    if "error" in result:
        return {"content": [{"type": "text", "text": f"Error creating issue: {result['error']}"}]}
    
    issue_key = result.get("key", "Unknown")
    return {"content": [{"type": "text", "text": f"✅ Issue created: {issue_key}\nURL: {JIRA_URL}/browse/{issue_key}"}]}

async def get_issue(args: dict):
    """Get Jira issue details"""
    issue_key = args["issue_key"]
    result = make_jira_request("GET", f"issue/{issue_key}")
    
    if "error" in result:
        return {"content": [{"type": "text", "text": f"Error getting issue: {result['error']}"}]}
    
    fields = result.get("fields", {})
    summary = fields.get("summary", "N/A")
    status = fields.get("status", {}).get("name", "N/A")
    assignee = fields.get("assignee", {})
    assignee_name = assignee.get("displayName", "Unassigned") if assignee else "Unassigned"
    
    response = f"""📋 Issue: {issue_key}
Summary: {summary}
Status: {status}
Assignee: {assignee_name}
URL: {JIRA_URL}/browse/{issue_key}"""
    
    return {"content": [{"type": "text", "text": response}]}

async def search_issues(args: dict):
    """Search Jira issues"""
    jql = args["jql"]
    max_results = args.get("max_results", 10)
    
    result = make_jira_request("GET", f"search?jql={jql}&maxResults={max_results}")
    
    if "error" in result:
        return {"content": [{"type": "text", "text": f"Error searching: {result['error']}"}]}
    
    issues = result.get("issues", [])
    if not issues:
        return {"content": [{"type": "text", "text": f"No issues found for: {jql}"}]}
    
    response = f"🔍 Found {len(issues)} issues:\n\n"
    for issue in issues:
        key = issue["key"]
        summary = issue["fields"].get("summary", "N/A")
        status = issue["fields"].get("status", {}).get("name", "N/A")
        response += f"• {key}: {summary} ({status})\n"
    
    return {"content": [{"type": "text", "text": response}]}

async def main():
    """Main server loop"""
    print("🚀 Jira MCP Server starting...")
    print(f"📡 Connecting to: {JIRA_URL}")
    
    # Simple stdio-based MCP server
    import sys
    
    while True:
        try:
            # Read JSON-RPC request from stdin
            line = await asyncio.get_event_loop().run_in_executor(None, sys.stdin.readline)
            if not line:
                break
            
            request = json.loads(line.strip())
            response = await handle_mcp_request(request)
            
            # Send JSON-RPC response to stdout
            json_response = json.dumps({
                "jsonrpc": "2.0",
                "id": request.get("id"),
                "result": response
            })
            print(json_response, flush=True)
            
        except json.JSONDecodeError:
            continue
        except Exception as e:
            error_response = json.dumps({
                "jsonrpc": "2.0",
                "id": request.get("id") if 'request' in locals() else None,
                "error": {"code": -1, "message": str(e)}
            })
            print(error_response, flush=True)

if __name__ == "__main__":
    asyncio.run(main())
