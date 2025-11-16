#!/usr/bin/env python3
"""
Test social media posting with current .env credentials.
This helps verify your API keys are working before running full automation.
"""

import os
import sys
from pathlib import Path

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("❌ python-dotenv not installed. Run: pip install python-dotenv")
    sys.exit(1)

def check_credentials():
    """Check if all required credentials are present."""
    print("Checking credentials...\n")

    twitter_keys = [
        'TWITTER_API_KEY',
        'TWITTER_API_SECRET',
        'TWITTER_ACCESS_TOKEN',
        'TWITTER_ACCESS_TOKEN_SECRET',
        'TWITTER_BEARER_TOKEN'
    ]

    linkedin_keys = [
        'LINKEDIN_ACCESS_TOKEN',
        'LINKEDIN_USER_URN'
    ]

    twitter_ok = all(os.getenv(key) for key in twitter_keys)
    linkedin_ok = all(os.getenv(key) for key in linkedin_keys)

    if twitter_ok:
        print("✓ Twitter credentials found")
    else:
        print("❌ Twitter credentials missing")
        for key in twitter_keys:
            if not os.getenv(key):
                print(f"   Missing: {key}")

    print()

    if linkedin_ok:
        print("✓ LinkedIn credentials found")
    else:
        print("❌ LinkedIn credentials missing")
        for key in linkedin_keys:
            if not os.getenv(key):
                print(f"   Missing: {key}")

    print()

    return twitter_ok, linkedin_ok

def test_twitter():
    """Test Twitter API connection."""
    print("Testing Twitter API...\n")

    try:
        import tweepy

        api_key = os.getenv('TWITTER_API_KEY')
        api_secret = os.getenv('TWITTER_API_SECRET')
        access_token = os.getenv('TWITTER_ACCESS_TOKEN')
        access_token_secret = os.getenv('TWITTER_ACCESS_TOKEN_SECRET')
        bearer_token = os.getenv('TWITTER_BEARER_TOKEN')

        client = tweepy.Client(
            bearer_token=bearer_token,
            consumer_key=api_key,
            consumer_secret=api_secret,
            access_token=access_token,
            access_token_secret=access_token_secret
        )

        # Get authenticated user info
        me = client.get_me()
        print(f"✓ Connected as: @{me.data.username}")
        print(f"✓ Twitter API is working!")
        return True

    except Exception as e:
        print(f"❌ Twitter API test failed: {e}")
        return False

def test_linkedin():
    """Test LinkedIn API connection."""
    print("\nTesting LinkedIn API...\n")

    try:
        import requests

        access_token = os.getenv('LINKEDIN_ACCESS_TOKEN')

        headers = {
            'Authorization': f'Bearer {access_token}',
            'LinkedIn-Version': '202210'
        }

        # Test with a simple user info request
        response = requests.get(
            'https://api.linkedin.com/v2/userinfo',
            headers=headers
        )

        if response.status_code == 200:
            data = response.json()
            print(f"✓ Connected as: {data.get('name', 'Unknown')}")
            print(f"✓ LinkedIn API is working!")
            return True
        else:
            print(f"❌ LinkedIn API test failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False

    except Exception as e:
        print(f"❌ LinkedIn API test failed: {e}")
        return False

def main():
    print("=" * 60)
    print("SOCIAL MEDIA API TEST")
    print("=" * 60)
    print()

    if not Path(".env").exists():
        print("❌ No .env file found!")
        print()
        print("Create a .env file using .env.template as a guide:")
        print("  1. Copy .env.template to .env")
        print("  2. Fill in your API credentials")
        print()
        return

    twitter_ok, linkedin_ok = check_credentials()

    if twitter_ok:
        test_twitter()
    else:
        print("⚠️  Skipping Twitter test (credentials missing)\n")

    if linkedin_ok:
        test_linkedin()
    else:
        print("⚠️  Skipping LinkedIn test (credentials missing)\n")

    print()
    print("=" * 60)
    if twitter_ok or linkedin_ok:
        print("✓ Ready to post! Run: python automate.py")
    else:
        print("⚠️  Set up your .env file to enable social posting")
    print("=" * 60)

if __name__ == '__main__':
    main()
