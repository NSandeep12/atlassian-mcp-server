#!/usr/bin/env python3
"""
Test Bitbucket connection with OAuth, API token, or app password
"""

import os
import requests
from requests.auth import HTTPBasicAuth
from dotenv import load_dotenv
from atlassian import Bitbucket

# Load environment variables
load_dotenv()

BITBUCKET_USERNAME = os.getenv("BITBUCKET_USERNAME")
BITBUCKET_APP_PASSWORD = os.getenv("BITBUCKET_APP_PASSWORD")
BITBUCKET_API_TOKEN = os.getenv("BITBUCKET_API_TOKEN")
BITBUCKET_OAUTH_KEY = os.getenv("BITBUCKET_OAUTH_KEY")
BITBUCKET_OAUTH_SECRET = os.getenv("BITBUCKET_OAUTH_SECRET")
BITBUCKET_WORKSPACE = os.getenv("BITBUCKET_WORKSPACE")

def test_bitbucket_oauth():
    """Test Bitbucket connection using OAuth key and secret"""
    print("Testing Bitbucket OAuth connection...")
    
    if not all([BITBUCKET_OAUTH_KEY, BITBUCKET_OAUTH_SECRET]):
        print("❌ No OAuth key/secret found")
        return False
    
    try:
        # Test OAuth with direct API call using basic auth
        url = f"https://api.bitbucket.org/2.0/repositories/{BITBUCKET_WORKSPACE}"
        auth = HTTPBasicAuth(BITBUCKET_OAUTH_KEY, BITBUCKET_OAUTH_SECRET)
        
        response = requests.get(url, auth=auth)
        response.raise_for_status()
        
        data = response.json()
        repo_count = len(data.get("values", []))
        
        print(f"✅ OAuth authentication successful!")
        print(f"✅ Found {repo_count} repositories in workspace '{BITBUCKET_WORKSPACE}'")
        
        if repo_count > 0:
            print("\nFirst few repositories:")
            for repo in data.get("values", [])[:3]:
                print(f"  - {repo['name']} ({repo['full_name']})")
        
        return True
        
    except Exception as e:
        print(f"❌ OAuth authentication failed: {str(e)}")
        return False

def test_bitbucket_api_token():
    """Test Bitbucket connection using API token"""
    print("Testing Bitbucket API Token connection...")
    
    if not BITBUCKET_API_TOKEN:
        print("❌ No API token found")
        return False
    
    try:
        # Test API token with direct API call
        url = f"https://api.bitbucket.org/2.0/repositories/{BITBUCKET_WORKSPACE}"
        headers = {
            "Authorization": f"Bearer {BITBUCKET_API_TOKEN}",
            "Content-Type": "application/json"
        }
        
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        data = response.json()
        repo_count = len(data.get("values", []))
        
        print(f"✅ API Token authentication successful!")
        print(f"✅ Found {repo_count} repositories in workspace '{BITBUCKET_WORKSPACE}'")
        
        if repo_count > 0:
            print("\nFirst few repositories:")
            for repo in data.get("values", [])[:3]:
                print(f"  - {repo['name']} ({repo['full_name']})")
        
        return True
        
    except Exception as e:
        print(f"❌ API Token authentication failed: {str(e)}")
        return False

def test_bitbucket_app_password():
    """Test Bitbucket connection using app password"""
    print("Testing Bitbucket App Password connection...")
    
    if not all([BITBUCKET_USERNAME, BITBUCKET_APP_PASSWORD]):
        print("❌ Missing username or app password")
        return False
    
    try:
        bitbucket = Bitbucket(
            username=BITBUCKET_USERNAME,
            password=BITBUCKET_APP_PASSWORD,
            cloud=True
        )
        
        repos = bitbucket.repo_list(BITBUCKET_WORKSPACE)
        repo_count = len(repos.get("values", []))
        
        print(f"✅ App Password authentication successful!")
        print(f"✅ Found {repo_count} repositories in workspace '{BITBUCKET_WORKSPACE}'")
        
        if repo_count > 0:
            print("\nFirst few repositories:")
            for repo in repos.get("values", [])[:3]:
                print(f"  - {repo['name']} ({repo['full_name']})")
        
        return True
        
    except Exception as e:
        print(f"❌ App Password authentication failed: {str(e)}")
        return False

def test_bitbucket_connection():
    print("Testing Bitbucket connection...")
    print(f"Username: {BITBUCKET_USERNAME}")
    print(f"Workspace: {BITBUCKET_WORKSPACE}")
    print(f"OAuth Key: {'*' * len(BITBUCKET_OAUTH_KEY) if BITBUCKET_OAUTH_KEY else 'NOT SET'}")
    print(f"OAuth Secret: {'*' * len(BITBUCKET_OAUTH_SECRET) if BITBUCKET_OAUTH_SECRET else 'NOT SET'}")
    print(f"API Token: {'*' * len(BITBUCKET_API_TOKEN) if BITBUCKET_API_TOKEN else 'NOT SET'}")
    print(f"App Password: {'*' * len(BITBUCKET_APP_PASSWORD) if BITBUCKET_APP_PASSWORD else 'NOT SET'}")
    print("-" * 50)
    
    success = False
    
    # Try OAuth first
    if BITBUCKET_OAUTH_KEY and BITBUCKET_OAUTH_SECRET:
        success = test_bitbucket_oauth()
    
    # Try API token if OAuth fails
    if not success and BITBUCKET_API_TOKEN:
        print("\nFalling back to API Token authentication...")
        success = test_bitbucket_api_token()
    
    # Fall back to app password if others fail
    if not success and BITBUCKET_APP_PASSWORD:
        print("\nFalling back to App Password authentication...")
        success = test_bitbucket_app_password()
    
    if not success:
        print("\n❌ All authentication methods failed!")
        print("\nTo fix this:")
        print("1. For OAuth: Check your key and secret from OAuth consumer")
        print("2. For API Token: Get token from repository or workspace settings")
        print("3. For App Password: Get from https://bitbucket.org/account/settings/app-passwords/")
        print("4. Verify your username and workspace name are correct")
    
    return success

if __name__ == "__main__":
    test_bitbucket_connection()
