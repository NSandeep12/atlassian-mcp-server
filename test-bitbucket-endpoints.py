#!/usr/bin/env python3
"""
Test various Bitbucket endpoints now that authentication is working
"""
import os

import requests
from requests.auth import HTTPBasicAuth

def test_endpoints():
    username = os.getenv("BITBUCKET_USERNAME", "your-username")
    app_password = os.getenv("BITBUCKET_APP_PASSWORD", "your-app-password")
    
    if username == "your-username" or app_password == "your-app-password":
        print("❌ Please set BITBUCKET_USERNAME and BITBUCKET_APP_PASSWORD environment variables")
        return
    
    auth = HTTPBasicAuth(username, app_password)
    
    print("🧪 Testing Bitbucket endpoints with working credentials")
    print("=" * 55)
    
    endpoints = [
        ("User info", "https://api.bitbucket.org/2.0/user"),
        ("Workspaces", "https://api.bitbucket.org/2.0/workspaces"),
        ("User repositories", f"https://api.bitbucket.org/2.0/repositories/{username}"),
        ("Workspace repositories", f"https://api.bitbucket.org/2.0/repositories/{username}"),
        ("Specific repository", f"https://api.bitbucket.org/2.0/repositories/{username}/online-shop"),
        ("Repository branches", f"https://api.bitbucket.org/2.0/repositories/{username}/online-shop/refs/branches"),
        ("Pull requests", f"https://api.bitbucket.org/2.0/repositories/{username}/online-shop/pullrequests"),
        ("Commits", f"https://api.bitbucket.org/2.0/repositories/{username}/online-shop/commits"),
    ]
    
    for name, url in endpoints:
        print(f"\n🔍 Testing: {name}")
        print(f"URL: {url}")
        
        try:
            response = requests.get(url, auth=auth, timeout=10)
            print(f"Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                if 'values' in data:
                    print(f"Results: {len(data['values'])} items")
                    if data['values']:
                        first_item = data['values'][0]
                        if 'name' in first_item:
                            print(f"First item: {first_item['name']}")
                        elif 'full_name' in first_item:
                            print(f"First item: {first_item['full_name']}")
                elif 'display_name' in data:
                    print(f"User: {data['display_name']}")
                elif 'name' in data:
                    print(f"Name: {data['name']}")
                else:
                    print("✅ Success - Data received")
            else:
                print(f"❌ Error: {response.text[:200]}")
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Request failed: {e}")
        
        print("-" * 40)

if __name__ == "__main__":
    test_endpoints()
