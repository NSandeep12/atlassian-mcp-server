#!/usr/bin/env python3
"""
Jira MCP Server - Provides Jira integration tools for Q CLI
"""

import asyncio
import os
import json
from typing import Any, Sequence
from dotenv import load_dotenv
import requests
from requests.auth import HTTPBasicAuth

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

if not all([JIRA_URL, JIRA_EMAIL, JIRA_API_TOKEN]):
    raise ValueError("Missing required environment variables. Please check your .env file.")

# Initialize the server
server = Server("jira-server")

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

@server.list_tools()
async def handle_list_tools() -> list[Tool]:
    """List available Jira tools"""
    return [
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
                    },
                    "priority": {
                        "type": "string",
                        "description": "Priority level (Highest, High, Medium, Low, Lowest)",
                        "default": "Medium"
                    }
                },
                "required": ["project_key", "summary"]
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
            name="update_issue",
            description="Update a Jira issue",
            inputSchema={
                "type": "object",
                "properties": {
                    "issue_key": {
                        "type": "string",
                        "description": "The issue key (e.g., 'PROJ-123')"
                    },
                    "summary": {
                        "type": "string",
                        "description": "New summary/title"
                    },
                    "description": {
                        "type": "string",
                        "description": "New description"
                    }
                },
                "required": ["issue_key"]
            }
        ),
        Tool(
            name="transition_issue",
            description="Transition a Jira issue to a different status",
            inputSchema={
                "type": "object",
                "properties": {
                    "issue_key": {
                        "type": "string",
                        "description": "The issue key (e.g., 'PROJ-123')"
                    },
                    "transition_name": {
                        "type": "string",
                        "description": "Name of the transition (e.g., 'In Progress', 'Done', 'To Do')"
                    }
                },
                "required": ["issue_key", "transition_name"]
            }
        ),
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
                        "default": 50
                    }
                },
                "required": ["jql"]
            }
        ),
        Tool(
            name="add_comment",
            description="Add a comment to a Jira issue",
            inputSchema={
                "type": "object",
                "properties": {
                    "issue_key": {
                        "type": "string",
                        "description": "The issue key (e.g., 'PROJ-123')"
                    },
                    "comment": {
                        "type": "string",
                        "description": "Comment text to add"
                    }
                },
                "required": ["issue_key", "comment"]
            }
        )
    ]

@server.call_tool()
async def handle_call_tool(name: str, arguments: dict | None) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
    """Handle tool calls"""
    if arguments is None:
        arguments = {}
    
    try:
        if name == "create_issue":
            return await create_issue(arguments)
        elif name == "get_issue":
            return await get_issue(arguments)
        elif name == "update_issue":
            return await update_issue(arguments)
        elif name == "transition_issue":
            return await transition_issue(arguments)
        elif name == "search_issues":
            return await search_issues(arguments)
        elif name == "add_comment":
            return await add_comment(arguments)
        else:
            return [TextContent(type="text", text=f"Unknown tool: {name}")]
    except Exception as e:
        return [TextContent(type="text", text=f"Error executing {name}: {str(e)}")]

async def create_issue(args: dict) -> list[TextContent]:
    """Create a new Jira issue"""
    payload = {
        "fields": {
            "project": {"key": args["project_key"]},
            "summary": args["summary"],
            "description": args.get("description", ""),
            "issuetype": {"name": args.get("issue_type", "Task")},
            "priority": {"name": args.get("priority", "Medium")}
        }
    }
    
    result = make_jira_request("POST", "issue", payload)
    
    if "error" in result:
        return [TextContent(type="text", text=f"Error creating issue: {result['error']}")]
    
    issue_key = result.get("key", "Unknown")
    return [TextContent(type="text", text=f"✅ Issue created successfully: {issue_key}\nURL: {JIRA_URL}/browse/{issue_key}")]

async def get_issue(args: dict) -> list[TextContent]:
    """Get Jira issue details"""
    issue_key = args["issue_key"]
    result = make_jira_request("GET", f"issue/{issue_key}")
    
    if "error" in result:
        return [TextContent(type="text", text=f"Error getting issue: {result['error']}")]
    
    fields = result.get("fields", {})
    summary = fields.get("summary", "N/A")
    status = fields.get("status", {}).get("name", "N/A")
    assignee = fields.get("assignee", {})
    assignee_name = assignee.get("displayName", "Unassigned") if assignee else "Unassigned"
    priority = fields.get("priority", {}).get("name", "N/A")
    description = fields.get("description", "No description")
    
    response = f"""📋 Issue Details: {issue_key}
Summary: {summary}
Status: {status}
Assignee: {assignee_name}
Priority: {priority}
Description: {description}
URL: {JIRA_URL}/browse/{issue_key}"""
    
    return [TextContent(type="text", text=response)]

async def update_issue(args: dict) -> list[TextContent]:
    """Update a Jira issue"""
    issue_key = args["issue_key"]
    fields = {}
    
    if "summary" in args:
        fields["summary"] = args["summary"]
    if "description" in args:
        fields["description"] = args["description"]
    
    if not fields:
        return [TextContent(type="text", text="No fields to update specified")]
    
    payload = {"fields": fields}
    result = make_jira_request("PUT", f"issue/{issue_key}", payload)
    
    if "error" in result:
        return [TextContent(type="text", text=f"Error updating issue: {result['error']}")]
    
    return [TextContent(type="text", text=f"✅ Issue {issue_key} updated successfully")]

async def transition_issue(args: dict) -> list[TextContent]:
    """Transition a Jira issue"""
    issue_key = args["issue_key"]
    transition_name = args["transition_name"]
    
    # Get available transitions
    transitions_result = make_jira_request("GET", f"issue/{issue_key}/transitions")
    
    if "error" in transitions_result:
        return [TextContent(type="text", text=f"Error getting transitions: {transitions_result['error']}")]
    
    # Find the transition ID
    transition_id = None
    available_transitions = []
    
    for transition in transitions_result.get("transitions", []):
        available_transitions.append(transition["name"])
        if transition["name"].lower() == transition_name.lower():
            transition_id = transition["id"]
            break
    
    if not transition_id:
        return [TextContent(type="text", text=f"Transition '{transition_name}' not found. Available transitions: {', '.join(available_transitions)}")]
    
    # Perform the transition
    payload = {"transition": {"id": transition_id}}
    result = make_jira_request("POST", f"issue/{issue_key}/transitions", payload)
    
    if "error" in result:
        return [TextContent(type="text", text=f"Error transitioning issue: {result['error']}")]
    
    return [TextContent(type="text", text=f"✅ Issue {issue_key} transitioned to '{transition_name}'")]

async def search_issues(args: dict) -> list[TextContent]:
    """Search for Jira issues"""
    jql = args["jql"]
    max_results = args.get("max_results", 50)
    
    params = {
        "jql": jql,
        "maxResults": max_results,
        "fields": "key,summary,status,assignee,priority"
    }
    
    result = make_jira_request("GET", f"search?jql={jql}&maxResults={max_results}")
    
    if "error" in result:
        return [TextContent(type="text", text=f"Error searching issues: {result['error']}")]
    
    issues = result.get("issues", [])
    total = result.get("total", 0)
    
    if not issues:
        return [TextContent(type="text", text=f"No issues found for query: {jql}")]
    
    response = f"🔍 Search Results ({len(issues)} of {total} total):\n\n"
    
    for issue in issues:
        key = issue["key"]
        fields = issue["fields"]
        summary = fields.get("summary", "N/A")
        status = fields.get("status", {}).get("name", "N/A")
        assignee = fields.get("assignee", {})
        assignee_name = assignee.get("displayName", "Unassigned") if assignee else "Unassigned"
        
        response += f"• {key}: {summary}\n  Status: {status} | Assignee: {assignee_name}\n\n"
    
    return [TextContent(type="text", text=response)]

async def add_comment(args: dict) -> list[TextContent]:
    """Add a comment to a Jira issue"""
    issue_key = args["issue_key"]
    comment_text = args["comment"]
    
    payload = {
        "body": comment_text
    }
    
    result = make_jira_request("POST", f"issue/{issue_key}/comment", payload)
    
    if "error" in result:
        return [TextContent(type="text", text=f"Error adding comment: {result['error']}")]
    
    return [TextContent(type="text", text=f"✅ Comment added to issue {issue_key}")]

async def main():
    """Main function to run the server"""
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="jira-server",
                server_version="1.0.0",
                capabilities=server.get_capabilities(
                    notification_options=types.NotificationOptions(),
                    experimental_capabilities={}
                ),
            ),
        )

if __name__ == "__main__":
    asyncio.run(main())
