#!/usr/bin/env python3
"""
Test SSH-based Bitbucket operations
"""

import os
import subprocess
import tempfile
from git import Repo, GitCommandError
from dotenv import load_dotenv

load_dotenv()

BITBUCKET_USERNAME = os.getenv("BITBUCKET_USERNAME")
BITBUCKET_WORKSPACE = os.getenv("BITBUCKET_WORKSPACE")

def test_ssh_connection():
    """Test SSH connection to Bitbucket"""
    print("1. Testing SSH connection to Bitbucket...")
    try:
        result = subprocess.run(['ssh', '-T', 'git@bitbucket.org'], 
                              capture_output=True, text=True, timeout=10)
        if "authenticated via ssh key" in result.stdout:
            print("✅ SSH authentication successful!")
            return True
        else:
            print(f"❌ SSH authentication failed: {result.stdout}")
            return False
    except subprocess.TimeoutExpired:
        print("❌ SSH connection timed out")
        return False
    except Exception as e:
        print(f"❌ SSH test failed: {e}")
        return False

def create_test_repository():
    """Create a test repository on Bitbucket"""
    print("\n2. Creating a test repository...")
    print("Since we can't create repos via API without proper auth, let's create one manually:")
    print(f"   Go to: https://bitbucket.org/{BITBUCKET_WORKSPACE}/")
    print("   Click 'Create repository'")
    print("   Name it: 'test-mcp-repo'")
    print("   Make it private")
    print("   Initialize with README")
    print("   Then come back and tell me when it's created!")
    return "test-mcp-repo"

def test_clone_repository(repo_name):
    """Test cloning a repository via SSH"""
    print(f"\n3. Testing SSH clone of repository '{repo_name}'...")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        clone_path = os.path.join(temp_dir, repo_name)
        clone_url = f"git@bitbucket.org:{BITBUCKET_WORKSPACE}/{repo_name}.git"
        
        try:
            print(f"   Cloning: {clone_url}")
            repo = Repo.clone_from(clone_url, clone_path)
            print(f"✅ Successfully cloned {repo_name}!")
            
            # Check repo info
            print(f"   Repository path: {clone_path}")
            print(f"   Current branch: {repo.active_branch.name}")
            print(f"   Remote URL: {repo.remotes.origin.url}")
            
            return True
        except GitCommandError as e:
            print(f"❌ Failed to clone repository: {e}")
            print(f"   This might mean the repository doesn't exist yet.")
            return False
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
            return False

def test_common_repo_names():
    """Test cloning some common repository names"""
    print("\n4. Testing common repository names...")
    
    common_names = [
        "test-repo",
        "hello-world", 
        "my-project",
        "demo",
        "test-mcp-repo"
    ]
    
    for repo_name in common_names:
        print(f"\n   Trying: {repo_name}")
        clone_url = f"git@bitbucket.org:{BITBUCKET_WORKSPACE}/{repo_name}.git"
        
        try:
            # Just test if we can access the repo without actually cloning
            result = subprocess.run(['git', 'ls-remote', clone_url], 
                                  capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                print(f"   ✅ Repository '{repo_name}' exists and is accessible!")
                return repo_name
            else:
                print(f"   ❌ Repository '{repo_name}' not found or not accessible")
        except Exception as e:
            print(f"   ❌ Error checking '{repo_name}': {e}")
    
    print("\n   No existing repositories found with common names.")
    return None

def main():
    print("SSH Bitbucket Integration Test")
    print("=" * 40)
    print(f"Username: {BITBUCKET_USERNAME}")
    print(f"Workspace: {BITBUCKET_WORKSPACE}")
    print("=" * 40)
    
    # Test SSH connection
    if not test_ssh_connection():
        print("\n❌ SSH connection failed. Please check your SSH key setup.")
        return
    
    # Look for existing repositories
    existing_repo = test_common_repo_names()
    
    if existing_repo:
        print(f"\n🎉 Found existing repository: {existing_repo}")
        test_clone_repository(existing_repo)
    else:
        print("\n📝 No existing repositories found.")
        suggested_repo = create_test_repository()
        print(f"\nOnce you create '{suggested_repo}', run this test again!")
    
    print(f"\n" + "=" * 50)
    print("NEXT STEPS:")
    print("=" * 50)
    
    if existing_repo:
        print(f"✅ SSH setup is working!")
        print(f"✅ You can now use the MCP server with repository: {existing_repo}")
        print(f"\nTry this command:")
        print(f"q chat \"Use jira-bitbucket-git-server___clone_repository with repo_slug '{existing_repo}'\"")
    else:
        print("1. Create a test repository at: https://bitbucket.org/nsandeep12/")
        print("2. Name it 'test-mcp-repo' or any name you prefer")
        print("3. Initialize it with a README")
        print("4. Run this test again to verify it works")
        print("5. Then you can use the MCP server!")

if __name__ == "__main__":
    main()
