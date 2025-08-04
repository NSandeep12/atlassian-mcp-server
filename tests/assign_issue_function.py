# Add this function to your jira_server.py

@server.call_tool()
async def assign_issue(issue_key: str, assignee_account_id: str = None) -> list[types.TextContent]:
    """Assign a Jira issue to a user"""
    
    if not issue_key:
        return [types.TextContent(type="text", text="❌ Issue key is required")]
    
    # If no assignee provided, assign to current user
    if not assignee_account_id:
        # Get current user's account ID
        user_response = requests.get(
            f"{JIRA_URL}/rest/api/3/myself",
            auth=(JIRA_EMAIL, JIRA_API_TOKEN)
        )
        if user_response.status_code == 200:
            assignee_account_id = user_response.json().get('accountId')
        else:
            return [types.TextContent(type="text", text="❌ Failed to get current user info")]
    
    url = f"{JIRA_URL}/rest/api/3/issue/{issue_key}/assignee"
    
    payload = {
        "accountId": assignee_account_id
    }
    
    try:
        response = requests.put(
            url,
            json=payload,
            auth=(JIRA_EMAIL, JIRA_API_TOKEN),
            headers={"Accept": "application/json", "Content-Type": "application/json"}
        )
        
        if response.status_code == 204:
            return [types.TextContent(
                type="text", 
                text=f"✅ Issue {issue_key} assigned successfully"
            )]
        else:
            return [types.TextContent(
                type="text", 
                text=f"❌ Failed to assign issue: {response.status_code} - {response.text}"
            )]
            
    except Exception as e:
        return [types.TextContent(
            type="text", 
            text=f"❌ Error assigning issue: {str(e)}"
        )]
