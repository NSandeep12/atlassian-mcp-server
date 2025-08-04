#!/usr/bin/env python3
"""
Test complete Jira + Bitbucket + Git workflow
"""

import os
import sys
import asyncio
from dotenv import load_dotenv

# Add the current directory to Python path to import our server
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

load_dotenv()

BITBUCKET_WORKSPACE = os.getenv("BITBUCKET_WORKSPACE")

async def test_workflow():
    """Test the complete workflow"""
    print("Complete Workflow Test")
    print("=" * 30)
    
    # Import our server functions
    try:
        from jira_bitbucket_server import handle_call_tool
        print("✅ Server module imported successfully")
    except Exception as e:
        print(f"❌ Failed to import server: {e}")
        return
    
    # Test 1: Search for Jira issues
    print("\n1. Testing Jira issue search...")
    try:
        result = await handle_call_tool("search_issues", {
            "jql": "assignee = currentUser() ORDER BY created DESC",
            "max_results": 5
        })
        print("✅ Jira search successful")
        print(f"   Result: {result[0].text[:100]}...")
    except Exception as e:
        print(f"❌ Jira search failed: {e}")
    
    # Test 2: Clone repository
    print("\n2. Testing repository clone...")
    repo_name = "online-shop"  # Using the existing online-shop repository
    try:
        result = await handle_call_tool("clone_repository", {
            "repo_slug": repo_name,
            "workspace": BITBUCKET_WORKSPACE
        })
        print("✅ Repository clone successful")
        print(f"   Result: {result[0].text}")
    except Exception as e:
        print(f"❌ Repository clone failed: {e}")
        print(f"   Make sure repository '{repo_name}' exists in your Bitbucket workspace")
    
    # Test 3: Git status
    print("\n3. Testing git status...")
    try:
        repo_path = f"/home/sandynal/repos/{repo_name}"
        result = await handle_call_tool("git_status", {
            "repo_path": repo_path
        })
        print("✅ Git status successful")
        print(f"   Result: {result[0].text[:200]}...")
    except Exception as e:
        print(f"❌ Git status failed: {e}")
    
    # Test 4: Create branch
    print("\n4. Testing branch creation...")
    try:
        repo_path = f"/home/sandynal/repos/{repo_name}"
        result = await handle_call_tool("create_branch", {
            "repo_path": repo_path,
            "branch_name": "feature/test-branch"
        })
        print("✅ Branch creation successful")
        print(f"   Result: {result[0].text}")
    except Exception as e:
        print(f"❌ Branch creation failed: {e}")
    
    print("\n" + "=" * 50)
    print("WORKFLOW TEST COMPLETE!")
    print("=" * 50)
    
    print("\nIf all tests passed, your MCP server is ready to use!")
    print("\nExample commands you can now use with Q CLI:")
    print(f"q chat \"Use jira-bitbucket-git-server___search_issues with JQL 'assignee = currentUser()'\"")
    print(f"q chat \"Use jira-bitbucket-git-server___clone_repository with repo_slug '{repo_name}'\"")
    print(f"q chat \"Use jira-bitbucket-git-server___create_feature_branch_for_issue with issue_key 'DEV-123' and repo_slug '{repo_name}'\"")

if __name__ == "__main__":
    asyncio.run(test_workflow())
