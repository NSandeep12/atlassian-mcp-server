#!/usr/bin/env python3

import requests
import os
from dotenv import load_dotenv

load_dotenv()

JIRA_URL = os.getenv('JIRA_URL')
JIRA_EMAIL = os.getenv('JIRA_EMAIL')
JIRA_API_TOKEN = os.getenv('JIRA_API_TOKEN')

def test_permissions():
    """Test various Jira API permissions"""
    
    # Test 1: Get current user info
    print("Testing: Get current user...")
    response = requests.get(
        f"{JIRA_URL}/rest/api/3/myself",
        auth=(JIRA_EMAIL, JIRA_API_TOKEN)
    )
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        user_data = response.json()
        print(f"User: {user_data.get('displayName')} ({user_data.get('accountId')})")
    
    # Test 2: Check project permissions
    print("\nTesting: Project permissions...")
    response = requests.get(
        f"{JIRA_URL}/rest/api/3/mypermissions?projectKey=SCRUM",
        auth=(JIRA_EMAIL, JIRA_API_TOKEN)
    )
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        perms = response.json()
        print("Permissions:", perms.get('permissions', {}))
    
    # Test 3: Try to get a known issue
    print("\nTesting: Get issue access...")
    response = requests.get(
        f"{JIRA_URL}/rest/api/3/issue/SCRUM-23",
        auth=(JIRA_EMAIL, JIRA_API_TOKEN)
    )
    print(f"Status: {response.status_code}")
    if response.status_code != 200:
        print("Error:", response.text)

if __name__ == "__main__":
    test_permissions()
