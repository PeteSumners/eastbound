#!/usr/bin/env python3
"""Test Claude API connection."""

import os
from anthropic import Anthropic

def test_claude_api():
    api_key = os.getenv('ANTHROPIC_API_KEY')

    if not api_key:
        print("ERROR: ANTHROPIC_API_KEY not set in environment")
        return False

    print("API key found (first 20 chars):", api_key[:20] + "...")
    print("Testing Claude API connection...")

    try:
        client = Anthropic(api_key=api_key)

        message = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=100,
            messages=[{
                "role": "user",
                "content": "Respond with exactly: 'Eastbound Reports API test successful!'"
            }]
        )

        response = message.content[0].text
        print(f"SUCCESS: Claude API Response: {response}")

        if "successful" in response.lower():
            print("SUCCESS: Claude API is working correctly!")
            return True
        else:
            print("WARNING: Got unexpected response")
            return False

    except Exception as e:
        print(f"ERROR: Claude API Error: {e}")
        return False

if __name__ == '__main__':
    success = test_claude_api()
    exit(0 if success else 1)
