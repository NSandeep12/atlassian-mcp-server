#!/usr/bin/env python3
"""
Simple Atlassian MCP Server for testing Q CLI integration
"""

import asyncio
import json
import sys
from typing import Any, Dict, List

async def main():
    """Simple MCP server that responds to basic requests"""
    
    # Read from stdin
    while True:
        try:
            line = await asyncio.get_event_loop().run_in_executor(None, sys.stdin.readline)
            if not line:
                break
                
            # Parse JSON request
            try:
                request = json.loads(line.strip())
            except json.JSONDecodeError:
                continue
                
            # Handle different request types
            if request.get("method") == "initialize":
                response = {
                    "jsonrpc": "2.0",
                    "id": request.get("id"),
                    "result": {
                        "protocolVersion": "2024-11-05",
                        "capabilities": {
                            "tools": {
                                "listChanged": True
                            }
                        },
                        "serverInfo": {
                            "name": "atlassian-mcp-server",
                            "version": "1.0.0"
                        }
                    }
                }
                
            elif request.get("method") == "tools/list":
                response = {
                    "jsonrpc": "2.0", 
                    "id": request.get("id"),
                    "result": {
                        "tools": [
                            {
                                "name": "search_jira_issues",
                                "description": "Search for Jira issues using JQL",
                                "inputSchema": {
                                    "type": "object",
                                    "properties": {
                                        "jql": {
                                            "type": "string",
                                            "description": "JQL query string"
                                        }
                                    },
                                    "required": ["jql"]
                                }
                            }
                        ]
                    }
                }
                
            elif request.get("method") == "tools/call":
                tool_name = request.get("params", {}).get("name")
                if tool_name == "search_jira_issues":
                    response = {
                        "jsonrpc": "2.0",
                        "id": request.get("id"), 
                        "result": {
                            "content": [
                                {
                                    "type": "text",
                                    "text": "🔍 Atlassian MCP Server is working! This is a test response for Jira search."
                                }
                            ]
                        }
                    }
                else:
                    response = {
                        "jsonrpc": "2.0",
                        "id": request.get("id"),
                        "error": {
                            "code": -32601,
                            "message": f"Unknown tool: {tool_name}"
                        }
                    }
            else:
                response = {
                    "jsonrpc": "2.0", 
                    "id": request.get("id"),
                    "error": {
                        "code": -32601,
                        "message": f"Unknown method: {request.get('method')}"
                    }
                }
                
            # Send response
            print(json.dumps(response), flush=True)
            
        except Exception as e:
            error_response = {
                "jsonrpc": "2.0",
                "id": request.get("id") if 'request' in locals() else None,
                "error": {
                    "code": -32603,
                    "message": f"Internal error: {str(e)}"
                }
            }
            print(json.dumps(error_response), flush=True)

if __name__ == "__main__":
    asyncio.run(main())
