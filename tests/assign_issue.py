#!/usr/bin/env python3
"""
Assign a Jira issue to yourself
"""

import os
import requests
from requests.auth import HTTPBasicAuth
from dotenv import load_dotenv

load_dotenv()

JIRA_URL = os.getenv("JIRA_URL")
JIRA_EMAIL = os.getenv("JIRA_EMAIL")
JIRA_API_TOKEN = os.getenv("JIRA_API_TOKEN")

def assign_issue_to_self(issue_key):
    """Assign an issue to the current user"""
    url = f"{JIRA_URL}/rest/api/2/issue/{issue_key}/assignee"
    headers = {"Content-Type": "application/json"}
    
    # Get current user account ID first
    user_url = f"{JIRA_URL}/rest/api/2/myself"
    user_response = requests.get(user_url, auth=HTTPBasicAuth(JIRA_EMAIL, JIRA_API_TOKEN), headers=headers)
    
    if user_response.status_code != 200:
        print(f"❌ Failed to get user info: {user_response.text}")
        return False
    
    user_data = user_response.json()
    account_id = user_data.get("accountId")
    
    if not account_id:
        print("❌ Could not get account ID")
        return False
    
    # Assign the issue
    assign_data = {"accountId": account_id}
    
    try:
        response = requests.put(
            url, 
            auth=HTTPBasicAuth(JIRA_EMAIL, JIRA_API_TOKEN), 
            headers=headers, 
            json=assign_data
        )
        
        if response.status_code == 204:
            print(f"✅ Successfully assigned {issue_key} to {user_data.get('displayName', 'you')}")
            return True
        else:
            print(f"❌ Failed to assign issue: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error assigning issue: {e}")
        return False

if __name__ == "__main__":
    success = assign_issue_to_self("SCRUM-5")
    if success:
        print("\n🎉 SCRUM-5 is now assigned to you!")
    else:
        print("\n❌ Failed to assign SCRUM-5")
