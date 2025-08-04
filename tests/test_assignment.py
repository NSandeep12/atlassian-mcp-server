#!/usr/bin/env python3

import requests
import os
from dotenv import load_dotenv

load_dotenv()

JIRA_URL = os.getenv('JIRA_URL')
JIRA_EMAIL = os.getenv('JIRA_EMAIL')
JIRA_API_TOKEN = os.getenv('JIRA_API_TOKEN')

def test_assignment():
    """Test issue assignment"""
    
    issue_key = "SCRUM-23"
    account_id = "712020:86cf6352-6505-4372-b685-a6c70e311e4e"
    
    print(f"Testing assignment of {issue_key} to {account_id}...")
    
    # Try API v3
    print("\nTrying API v3...")
    response = requests.put(
        f"{JIRA_URL}/rest/api/3/issue/{issue_key}/assignee",
        json={"accountId": account_id},
        auth=(JIRA_EMAIL, JIRA_API_TOKEN),
        headers={"Accept": "application/json", "Content-Type": "application/json"}
    )
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text}")
    
    # Try API v2
    print("\nTrying API v2...")
    response = requests.put(
        f"{JIRA_URL}/rest/api/2/issue/{issue_key}/assignee",
        json={"accountId": account_id},
        auth=(JIRA_EMAIL, JIRA_API_TOKEN),
        headers={"Accept": "application/json", "Content-Type": "application/json"}
    )
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text}")

if __name__ == "__main__":
    test_assignment()
