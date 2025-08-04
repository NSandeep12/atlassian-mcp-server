#!/usr/bin/env python3
"""
Jira MCP Server - Proper implementation for Q CLI integration
"""

import asyncio
import json
import sys
import os
from typing import Any, Dict, List
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

class JiraMCPServer:
    def __init__(self):
        self.tools = [
            {
                "name": "create_issue",
                "description": "Create a new Jira issue",
                "inputSchema": {
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
            },
            {
                "name": "get_issue",
                "description": "Get details of a Jira issue",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "issue_key": {
                            "type": "string",
                            "description": "The issue key (e.g., 'PROJ-123')"
                        }
                    },
                    "required": ["issue_key"]
                }
            },
            {
                "name": "search_issues",
                "description": "Search for Jira issues using JQL",
                "inputSchema": {
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
            }
        ]

    async def handle_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle MCP protocol requests"""
        method = request.get("method")
        params = request.get("params", {})
        request_id = request.get("id")

        try:
            if method == "initialize":
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {
                        "protocolVersion": "2024-11-05",
                        "capabilities": {
                            "tools": {}
                        },
                        "serverInfo": {
                            "name": "jira-server",
                            "version": "1.0.0"
                        }
                    }
                }
            
            elif method == "initialized":
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {}
                }
            
            elif method == "tools/list":
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {
                        "tools": self.tools
                    }
                }
            
            elif method == "tools/call":
                tool_name = params.get("name")
                arguments = params.get("arguments", {})
                
                if tool_name == "create_issue":
                    result = await self.create_issue(arguments)
                elif tool_name == "get_issue":
                    result = await self.get_issue(arguments)
                elif tool_name == "search_issues":
                    result = await self.search_issues(arguments)
                else:
                    return {
                        "jsonrpc": "2.0",
                        "id": request_id,
                        "error": {
                            "code": -32601,
                            "message": f"Unknown tool: {tool_name}"
                        }
                    }
                
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": result
                }
            
            else:
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "error": {
                        "code": -32601,
                        "message": f"Method not found: {method}"
                    }
                }
        
        except Exception as e:
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {
                    "code": -32603,
                    "message": f"Internal error: {str(e)}"
                }
            }

    async def create_issue(self, args: Dict[str, Any]) -> Dict[str, Any]:
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
            return {
                "content": [
                    {
                        "type": "text",
                        "text": f"❌ Error creating issue: {result['error']}"
                    }
                ]
            }
        
        issue_key = result.get("key", "Unknown")
        return {
            "content": [
                {
                    "type": "text",
                    "text": f"✅ Issue created successfully: {issue_key}\n🔗 URL: {JIRA_URL}/browse/{issue_key}"
                }
            ]
        }

    async def get_issue(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Get Jira issue details"""
        issue_key = args["issue_key"]
        result = make_jira_request("GET", f"issue/{issue_key}")
        
        if "error" in result:
            return {
                "content": [
                    {
                        "type": "text",
                        "text": f"❌ Error getting issue: {result['error']}"
                    }
                ]
            }
        
        fields = result.get("fields", {})
        summary = fields.get("summary", "N/A")
        status = fields.get("status", {}).get("name", "N/A")
        assignee = fields.get("assignee", {})
        assignee_name = assignee.get("displayName", "Unassigned") if assignee else "Unassigned"
        priority = fields.get("priority", {}).get("name", "N/A")
        description = fields.get("description", "No description")
        
        response = f"""📋 **Issue Details: {issue_key}**
📝 **Summary:** {summary}
🏷️ **Status:** {status}
👤 **Assignee:** {assignee_name}
⚡ **Priority:** {priority}
📄 **Description:** {description}
🔗 **URL:** {JIRA_URL}/browse/{issue_key}"""
        
        return {
            "content": [
                {
                    "type": "text",
                    "text": response
                }
            ]
        }

    async def search_issues(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Search for Jira issues"""
        jql = args["jql"]
        max_results = args.get("max_results", 10)
        
        result = make_jira_request("GET", f"search?jql={jql}&maxResults={max_results}")
        
        if "error" in result:
            return {
                "content": [
                    {
                        "type": "text",
                        "text": f"❌ Error searching issues: {result['error']}"
                    }
                ]
            }
        
        issues = result.get("issues", [])
        total = result.get("total", 0)
        
        if not issues:
            return {
                "content": [
                    {
                        "type": "text",
                        "text": f"🔍 No issues found for query: `{jql}`"
                    }
                ]
            }
        
        response = f"🔍 **Search Results** ({len(issues)} of {total} total)\n**Query:** `{jql}`\n\n"
        
        for issue in issues:
            key = issue["key"]
            fields = issue["fields"]
            summary = fields.get("summary", "N/A")
            status = fields.get("status", {}).get("name", "N/A")
            assignee = fields.get("assignee", {})
            assignee_name = assignee.get("displayName", "Unassigned") if assignee else "Unassigned"
            
            response += f"• **{key}:** {summary}\n  📊 Status: {status} | 👤 Assignee: {assignee_name}\n\n"
        
        return {
            "content": [
                {
                    "type": "text",
                    "text": response
                }
            ]
        }

async def main():
    """Main server loop"""
    server = JiraMCPServer()
    
    # Read from stdin and write to stdout for MCP protocol
    while True:
        try:
            line = await asyncio.get_event_loop().run_in_executor(None, sys.stdin.readline)
            if not line:
                break
            
            line = line.strip()
            if not line:
                continue
            
            request = json.loads(line)
            response = await server.handle_request(request)
            
            # Write response to stdout
            print(json.dumps(response), flush=True)
            
        except json.JSONDecodeError:
            # Invalid JSON, ignore
            continue
        except Exception as e:
            # Send error response
            error_response = {
                "jsonrpc": "2.0",
                "id": None,
                "error": {
                    "code": -32603,
                    "message": f"Server error: {str(e)}"
                }
            }
            print(json.dumps(error_response), flush=True)

if __name__ == "__main__":
    asyncio.run(main())
