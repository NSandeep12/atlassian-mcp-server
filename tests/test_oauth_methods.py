#!/usr/bin/env python3
"""
Test different OAuth authentication methods for Bitbucket
"""

import os
import requests
from requests.auth import HTTPBasicAuth
from dotenv import load_dotenv
from atlassian import Bitbucket

# Load environment variables
load_dotenv()

BITBUCKET_USERNAME = os.getenv("BITBUCKET_USERNAME")
BITBUCKET_OAUTH_KEY = os.getenv("BITBUCKET_OAUTH_KEY")
BITBUCKET_OAUTH_SECRET = os.getenv("BITBUCKET_OAUTH_SECRET")
BITBUCKET_WORKSPACE = os.getenv("BITBUCKET_WORKSPACE")

def test_oauth_as_basic_auth():
    """Test using OAuth key as username and secret as password"""
    print("Method 1: OAuth Key as username, Secret as password")
    try:
        url = f"https://api.bitbucket.org/2.0/repositories/{BITBUCKET_WORKSPACE}"
        auth = HTTPBasicAuth(BITBUCKET_OAUTH_KEY, BITBUCKET_OAUTH_SECRET)
        response = requests.get(url, auth=auth)
        response.raise_for_status()
        
        data = response.json()
        print(f"✅ Success! Found {len(data.get('values', []))} repositories")
        return True
    except Exception as e:
        print(f"❌ Failed: {e}")
        return False

def test_oauth_with_username():
    """Test using username and OAuth secret as password"""
    print("Method 2: Username and OAuth Secret as password")
    try:
        url = f"https://api.bitbucket.org/2.0/repositories/{BITBUCKET_WORKSPACE}"
        auth = HTTPBasicAuth(BITBUCKET_USERNAME, BITBUCKET_OAUTH_SECRET)
        response = requests.get(url, auth=auth)
        response.raise_for_status()
        
        data = response.json()
        print(f"✅ Success! Found {len(data.get('values', []))} repositories")
        return True
    except Exception as e:
        print(f"❌ Failed: {e}")
        return False

def test_oauth_with_atlassian_library():
    """Test using Atlassian library with OAuth secret"""
    print("Method 3: Atlassian library with OAuth secret")
    try:
        bitbucket = Bitbucket(
            username=BITBUCKET_USERNAME,
            password=BITBUCKET_OAUTH_SECRET,
            cloud=True
        )
        repos = bitbucket.repo_list(BITBUCKET_WORKSPACE)
        print(f"✅ Success! Found {len(repos.get('values', []))} repositories")
        return True
    except Exception as e:
        print(f"❌ Failed: {e}")
        return False

def test_oauth_with_key_as_username():
    """Test using OAuth key as username with Atlassian library"""
    print("Method 4: Atlassian library with OAuth key as username")
    try:
        bitbucket = Bitbucket(
            username=BITBUCKET_OAUTH_KEY,
            password=BITBUCKET_OAUTH_SECRET,
            cloud=True
        )
        repos = bitbucket.repo_list(BITBUCKET_WORKSPACE)
        print(f"✅ Success! Found {len(repos.get('values', []))} repositories")
        return True
    except Exception as e:
        print(f"❌ Failed: {e}")
        return False

def test_user_endpoint():
    """Test the user endpoint to verify credentials"""
    print("Method 5: Test user endpoint")
    try:
        url = "https://api.bitbucket.org/2.0/user"
        auth = HTTPBasicAuth(BITBUCKET_USERNAME, BITBUCKET_OAUTH_SECRET)
        response = requests.get(url, auth=auth)
        response.raise_for_status()
        
        data = response.json()
        print(f"✅ User endpoint success! User: {data.get('display_name', 'Unknown')}")
        return True
    except Exception as e:
        print(f"❌ Failed: {e}")
        return False

def main():
    print("Testing different OAuth authentication methods...")
    print(f"Username: {BITBUCKET_USERNAME}")
    print(f"Workspace: {BITBUCKET_WORKSPACE}")
    print(f"OAuth Key: {BITBUCKET_OAUTH_KEY[:8]}...")
    print(f"OAuth Secret: {BITBUCKET_OAUTH_SECRET[:8]}...")
    print("-" * 60)
    
    methods = [
        test_oauth_as_basic_auth,
        test_oauth_with_username,
        test_oauth_with_atlassian_library,
        test_oauth_with_key_as_username,
        test_user_endpoint
    ]
    
    for i, method in enumerate(methods, 1):
        print(f"\n{i}. {method.__doc__}")
        success = method()
        if success:
            print(f"🎉 Found working method: {method.__name__}")
            return method.__name__
    
    print("\n❌ None of the OAuth methods worked.")
    print("\nPossible issues:")
    print("1. OAuth consumer might need different permissions")
    print("2. OAuth consumer might need to be configured differently")
    print("3. Might need to use App Password instead of OAuth")
    
    return None

if __name__ == "__main__":
    main()
