#!/usr/bin/env python3
"""
Test script for Jira MCP Server
"""

import json
import subprocess
import sys
import time

def test_mcp_server():
    """Test the MCP server functionality"""
    print("🧪 Testing Jira MCP Server...")
    
    # Start the server process
    server_process = subprocess.Popen(
        [sys.executable, "jira_server_simple.py"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        cwd="/home/sandynal/jira-mcp-server"
    )
    
    try:
        # Test 1: List tools
        print("\n1. Testing tools/list...")
        request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/list"
        }
        
        server_process.stdin.write(json.dumps(request) + "\n")
        server_process.stdin.flush()
        
        # Read response
        response_line = server_process.stdout.readline()
        if response_line:
            response = json.loads(response_line.strip())
            tools = response.get("result", {}).get("tools", [])
            print(f"✅ Found {len(tools)} tools:")
            for tool in tools:
                print(f"   - {tool['name']}: {tool['description']}")
        else:
            print("❌ No response received")
        
        # Test 2: Test create_issue (will fail without real credentials, but should show structure)
        print("\n2. Testing create_issue...")
        request = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/call",
            "params": {
                "name": "create_issue",
                "arguments": {
                    "project_key": "TEST",
                    "summary": "Test issue from MCP server",
                    "description": "This is a test issue created via MCP"
                }
            }
        }
        
        server_process.stdin.write(json.dumps(request) + "\n")
        server_process.stdin.flush()
        
        response_line = server_process.stdout.readline()
        if response_line:
            response = json.loads(response_line.strip())
            print("✅ Create issue response received")
            print(f"   Response: {response}")
        else:
            print("❌ No response received")
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
    
    finally:
        # Clean up
        server_process.terminate()
        server_process.wait()
    
    print("\n🎉 Test completed!")

if __name__ == "__main__":
    test_mcp_server()
