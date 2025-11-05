#!/usr/bin/env python3
"""Test Twitter API credentials."""

import os
import tweepy

def test_twitter_api():
    print("Testing Twitter API credentials...")

    # Get credentials from environment
    api_key = os.getenv('TWITTER_API_KEY')
    api_secret = os.getenv('TWITTER_API_SECRET')
    access_token = os.getenv('TWITTER_ACCESS_TOKEN')
    access_token_secret = os.getenv('TWITTER_ACCESS_TOKEN_SECRET')
    bearer_token = os.getenv('TWITTER_BEARER_TOKEN')

    if not all([api_key, api_secret, access_token, access_token_secret, bearer_token]):
        print("ERROR: Missing Twitter API credentials")
        return False

    print("All 5 Twitter credentials found")
    print("Connecting to Twitter API...")

    try:
        client = tweepy.Client(
            bearer_token=bearer_token,
            consumer_key=api_key,
            consumer_secret=api_secret,
            access_token=access_token,
            access_token_secret=access_token_secret
        )

        # Get authenticated user info
        me = client.get_me()

        print(f"SUCCESS: Connected as @{me.data.username}")
        print(f"Account: {me.data.name}")
        print("Twitter API is working correctly!")

        return True

    except Exception as e:
        print(f"ERROR: Twitter API Error: {e}")
        return False

if __name__ == '__main__':
    success = test_twitter_api()
    exit(0 if success else 1)
