#!/usr/bin/env python3
"""Minimal Q CLI MCP Wrapper for AWS Lambda"""

import json
import sys
import subprocess
import tempfile
import os

def invoke_lambda(payload):
    """Invoke AWS Lambda function"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(payload, f)
        payload_file = f.name
    
    response_file = tempfile.mktemp(suffix='.json')
    
    cmd = [
        "aws", "lambda", "invoke",
        "--function-name", "atlassian-mcp-server",
        "--region", "us-west-2",
        "--profile", "AdministratorAccess-542754948868",
        "--cli-binary-format", "raw-in-base64-out",
        "--payload", f"file://{payload_file}",
        response_file
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode != 0:
        return {"statusCode": 500, "body": json.dumps({"error": result.stderr})}
    
    with open(response_file, 'r') as f:
        response = json.load(f)
    
    os.unlink(payload_file)
    os.unlink(response_file)
    
    return response

def handle_request(request):
    """Handle MCP request"""
    method = request.get("method")
    params = request.get("params", {})
    request_id = request.get("id")
    
    if method == "initialize":
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {
                "protocolVersion": "2024-11-05",
                "capabilities": {"tools": {}},
                "serverInfo": {"name": "atlassian-mcp-server", "version": "1.0.0"}
            }
        }
    
    elif method == "tools/list":
        response = invoke_lambda({"action": "list_tools"})
        if response.get("statusCode") == 200:
            body = json.loads(response.get("body", "{}"))
            return {"jsonrpc": "2.0", "id": request_id, "result": {"tools": body.get("tools", [])}}
    
    elif method == "tools/call":
        payload = {
            "action": "call_tool",
            "tool_name": params.get("name"),
            "arguments": params.get("arguments", {})
        }
        response = invoke_lambda(payload)
        if response.get("statusCode") == 200:
            body = json.loads(response.get("body", "{}"))
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {"content": [{"type": "text", "text": body.get("result", "")}]}
            }
    
    return {
        "jsonrpc": "2.0",
        "id": request_id,
        "error": {"code": -32601, "message": f"Method not found: {method}"}
    }

if __name__ == "__main__":
    for line in sys.stdin:
        if line.strip():
            try:
                request = json.loads(line.strip())
                response = handle_request(request)
                print(json.dumps(response))
                sys.stdout.flush()
            except:
                continue
