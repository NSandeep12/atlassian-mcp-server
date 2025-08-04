#!/usr/bin/env python3
"""
Test the Jira MCP Server
"""

import json
import subprocess
import sys
import time

def test_mcp_server():
    """Test the MCP server"""
    print("🧪 Testing Jira MCP Server...")
    
    # Start the server
    server_process = subprocess.Popen(
        ["/home/sandynal/jira-mcp-server/venv/bin/python", "/home/sandynal/jira-mcp-server/jira_mcp_server.py"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    try:
        # Test 1: Initialize
        print("\n1. Testing initialize...")
        request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "test-client", "version": "1.0.0"}
            }
        }
        
        server_process.stdin.write(json.dumps(request) + "\n")
        server_process.stdin.flush()
        
        response_line = server_process.stdout.readline()
        if response_line:
            response = json.loads(response_line.strip())
            print(f"✅ Initialize response: {response.get('result', {}).get('serverInfo', {}).get('name')}")
        
        # Test 2: List tools
        print("\n2. Testing tools/list...")
        request = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/list"
        }
        
        server_process.stdin.write(json.dumps(request) + "\n")
        server_process.stdin.flush()
        
        response_line = server_process.stdout.readline()
        if response_line:
            response = json.loads(response_line.strip())
            tools = response.get("result", {}).get("tools", [])
            print(f"✅ Found {len(tools)} tools:")
            for tool in tools:
                print(f"   - {tool['name']}: {tool['description']}")
        
        print("\n🎉 MCP Server test completed successfully!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
    
    finally:
        server_process.terminate()
        server_process.wait()

if __name__ == "__main__":
    test_mcp_server()
