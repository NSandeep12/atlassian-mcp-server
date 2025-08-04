#!/usr/bin/env python3
"""
Test Bitbucket App Password authentication
"""

import os
import requests
from requests.auth import HTTPBasicAuth
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

BITBUCKET_USERNAME = os.getenv("BITBUCKET_USERNAME")
BITBUCKET_APP_PASSWORD = os.getenv("BITBUCKET_APP_PASSWORD")
BITBUCKET_WORKSPACE = os.getenv("BITBUCKET_WORKSPACE")

def test_app_password():
    print("Testing Bitbucket App Password...")
    print(f"Username: {BITBUCKET_USERNAME}")
    print(f"Workspace: {BITBUCKET_WORKSPACE}")
    print(f"App Password: {'*' * len(BITBUCKET_APP_PASSWORD) if BITBUCKET_APP_PASSWORD else 'NOT SET'}")
    
    if not BITBUCKET_APP_PASSWORD or BITBUCKET_APP_PASSWORD == "YOUR_APP_PASSWORD_HERE":
        print("❌ App password not set. Please update YOUR_APP_PASSWORD_HERE in .env file")
        return False
    
    try:
        # Test user endpoint first
        print("\n1. Testing user endpoint...")
        url = "https://api.bitbucket.org/2.0/user"
        auth = HTTPBasicAuth(BITBUCKET_USERNAME, BITBUCKET_APP_PASSWORD)
        response = requests.get(url, auth=auth)
        response.raise_for_status()
        
        user_data = response.json()
        print(f"✅ User authentication successful!")
        print(f"   Display Name: {user_data.get('display_name', 'Unknown')}")
        print(f"   Username: {user_data.get('username', 'Unknown')}")
        
        # Test repositories endpoint
        print("\n2. Testing repositories endpoint...")
        url = f"https://api.bitbucket.org/2.0/repositories/{BITBUCKET_WORKSPACE}"
        response = requests.get(url, auth=auth)
        response.raise_for_status()
        
        repo_data = response.json()
        repo_count = len(repo_data.get("values", []))
        
        print(f"✅ Repository access successful!")
        print(f"   Found {repo_count} repositories in workspace '{BITBUCKET_WORKSPACE}'")
        
        if repo_count > 0:
            print("\n   First few repositories:")
            for repo in repo_data.get("values", [])[:3]:
                print(f"   - {repo['name']} ({repo['full_name']})")
        else:
            print("   No repositories found. This might be normal if you don't have any repos yet.")
        
        return True
        
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 401:
            print("❌ Authentication failed (401 Unauthorized)")
            print("   Please check your username and app password")
        elif e.response.status_code == 403:
            print("❌ Access forbidden (403 Forbidden)")
            print("   App password might not have required permissions")
        else:
            print(f"❌ HTTP Error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

if __name__ == "__main__":
    success = test_app_password()
    if success:
        print("\n🎉 Bitbucket App Password authentication is working!")
        print("You can now use the MCP server with Bitbucket integration.")
    else:
        print("\n❌ App Password authentication failed.")
        print("Please create an app password at: https://bitbucket.org/account/settings/app-passwords/")
