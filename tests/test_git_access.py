#!/usr/bin/env python3
"""
Test different ways to access Bitbucket
"""

import os
import subprocess
import requests
from dotenv import load_dotenv

load_dotenv()

BITBUCKET_USERNAME = os.getenv("BITBUCKET_USERNAME")
BITBUCKET_WORKSPACE = os.getenv("BITBUCKET_WORKSPACE")

def test_git_credentials():
    """Test if git has stored credentials for Bitbucket"""
    print("Testing git credentials...")
    try:
        # Check git config
        result = subprocess.run(['git', 'config', '--global', 'user.name'], 
                              capture_output=True, text=True)
        git_user = result.stdout.strip() if result.returncode == 0 else "Not set"
        
        result = subprocess.run(['git', 'config', '--global', 'user.email'], 
                              capture_output=True, text=True)
        git_email = result.stdout.strip() if result.returncode == 0 else "Not set"
        
        print(f"Git user: {git_user}")
        print(f"Git email: {git_email}")
        
        # Check if git credential helper is configured
        result = subprocess.run(['git', 'config', '--global', 'credential.helper'], 
                              capture_output=True, text=True)
        credential_helper = result.stdout.strip() if result.returncode == 0 else "Not set"
        print(f"Credential helper: {credential_helper}")
        
        return True
    except Exception as e:
        print(f"Error checking git config: {e}")
        return False

def test_public_api_access():
    """Test if we can access Bitbucket's public API without authentication"""
    print("\nTesting public API access...")
    try:
        # Try to access public user info
        url = f"https://api.bitbucket.org/2.0/users/{BITBUCKET_USERNAME}"
        response = requests.get(url)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Public user info accessible")
            print(f"   Display name: {data.get('display_name', 'Unknown')}")
            print(f"   Account type: {data.get('type', 'Unknown')}")
            return True
        else:
            print(f"❌ Public API returned: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error accessing public API: {e}")
        return False

def check_bitbucket_type():
    """Check if this is Bitbucket Cloud or Server"""
    print("\nChecking Bitbucket type...")
    try:
        # Bitbucket Cloud has a specific API endpoint
        url = "https://api.bitbucket.org/2.0/user"
        response = requests.get(url)
        
        if response.status_code == 401:
            print("✅ This appears to be Bitbucket Cloud (authentication required)")
            return "cloud"
        elif response.status_code == 404:
            print("❓ This might be Bitbucket Server or different setup")
            return "server"
        else:
            print(f"❓ Unexpected response: {response.status_code}")
            return "unknown"
    except Exception as e:
        print(f"❌ Error checking Bitbucket type: {e}")
        return "error"

def suggest_alternatives():
    """Suggest alternative authentication methods"""
    print("\n" + "="*50)
    print("ALTERNATIVE AUTHENTICATION OPTIONS:")
    print("="*50)
    
    print("\n1. SSH Key Authentication:")
    print("   - Add SSH key to your Bitbucket account")
    print("   - Use SSH URLs for git operations")
    print("   - Go to: https://bitbucket.org/account/settings/ssh-keys/")
    
    print("\n2. Personal Access Token (if available):")
    print("   - Check: https://bitbucket.org/account/settings/app-passwords/")
    print("   - Or: https://bitbucket.org/account/settings/access-management/")
    
    print("\n3. Repository Access Token:")
    print("   - Go to specific repo settings")
    print("   - Look for 'Access tokens' or 'Repository access tokens'")
    
    print("\n4. OAuth App (what you already tried):")
    print("   - Your OAuth consumer might need different configuration")
    print("   - Try enabling different permissions or callback URLs")
    
    print("\n5. Use HTTPS with username/password:")
    print("   - Some setups allow regular password authentication")
    print("   - Not recommended for security reasons")

def main():
    print("Bitbucket Access Diagnostic Tool")
    print("="*40)
    
    test_git_credentials()
    test_public_api_access()
    bitbucket_type = check_bitbucket_type()
    suggest_alternatives()
    
    print(f"\nDiagnostic Summary:")
    print(f"- Username: {BITBUCKET_USERNAME}")
    print(f"- Workspace: {BITBUCKET_WORKSPACE}")
    print(f"- Bitbucket Type: {bitbucket_type}")
    
    print(f"\nNext Steps:")
    print(f"1. Tell me what you see at: https://bitbucket.org/account/settings/")
    print(f"2. Check if you have any repositories at: https://bitbucket.org/{BITBUCKET_WORKSPACE}/")
    print(f"3. Try one of the alternative authentication methods above")

if __name__ == "__main__":
    main()
