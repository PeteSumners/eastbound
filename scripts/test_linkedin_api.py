#!/usr/bin/env python3
"""Test LinkedIn API credentials."""

import os
import sys
import requests
from datetime import datetime

def test_linkedin_api():
    print("Testing LinkedIn API credentials...")

    # Get credentials from environment
    access_token = os.getenv('LINKEDIN_ACCESS_TOKEN')
    user_urn = os.getenv('LINKEDIN_USER_URN')

    if not access_token:
        print("ERROR: LINKEDIN_ACCESS_TOKEN not set in environment")
        return False

    if not user_urn:
        print("ERROR: LINKEDIN_USER_URN not set in environment")
        return False

    print(f"Access Token: {access_token[:20]}...")
    print(f"User URN: {user_urn}")
    print("\nTesting API connection...")

    # Test 1: Get user info
    try:
        headers = {
            'Authorization': f'Bearer {access_token}'
        }

        response = requests.get(
            'https://api.linkedin.com/v2/userinfo',
            headers=headers
        )

        if response.status_code == 200:
            user_info = response.json()
            print(f"\nSUCCESS: Connected to LinkedIn")
            print(f"User: {user_info.get('name')}")
            print(f"Email: {user_info.get('email')}")
        else:
            print(f"\nERROR: Failed to get user info: {response.status_code}")
            print(response.text)
            return False

    except Exception as e:
        print(f"\nERROR: {e}")
        return False

    # Test 2: Post a test message
    print("\nPosting test message...")

    try:
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json',
            'LinkedIn-Version': '202210',
            'X-Restli-Protocol-Version': '2.0.0'
        }

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        test_text = f"Testing Eastbound Reports LinkedIn automation. Timestamp: {timestamp}"

        payload = {
            'author': f'urn:li:person:{user_urn}',
            'lifecycleState': 'PUBLISHED',
            'specificContent': {
                'com.linkedin.ugc.ShareContent': {
                    'shareCommentary': {
                        'text': test_text
                    },
                    'shareMediaCategory': 'NONE'
                }
            },
            'visibility': {
                'com.linkedin.ugc.MemberNetworkVisibility': 'PUBLIC'
            }
        }

        response = requests.post(
            'https://api.linkedin.com/v2/ugcPosts',
            headers=headers,
            json=payload
        )

        if response.status_code in [200, 201]:
            result = response.json()
            post_id = result.get('id', 'unknown')

            print(f"\nSUCCESS: Test post created!")
            print(f"Post ID: {post_id}")
            print(f"\nLinkedIn API is working correctly!")
            return True
        else:
            print(f"\nERROR: Failed to post: {response.status_code}")
            print(response.text)
            return False

    except Exception as e:
        print(f"\nERROR: {e}")
        return False

if __name__ == '__main__':
    success = test_linkedin_api()
    sys.exit(0 if success else 1)
