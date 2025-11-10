#!/usr/bin/env python3
"""Post content to LinkedIn."""

import os
import sys
import json
import argparse
import requests
import yaml
from pathlib import Path
from config import generate_post_url, LINKEDIN_HASHTAGS

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    env_path = Path(__file__).parent.parent / '.env'
    if env_path.exists():
        load_dotenv(env_path)
except ImportError:
    pass  # dotenv not installed, rely on system environment variables

def extract_post_content(file_path):
    """Extract title, content, and URL from markdown post."""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Parse frontmatter
    if content.startswith('---'):
        parts = content.split('---', 2)
        if len(parts) >= 3:
            frontmatter = yaml.safe_load(parts[1])
            body = parts[2].strip()

            title = frontmatter.get('title', '')
            subtitle = frontmatter.get('subtitle', '')

            # Extract first 300 chars of actual content for preview
            lines = [line for line in body.split('\n') if line.strip() and not line.startswith('#')]
            preview = ' '.join(lines[:3])[:300]

            return title, subtitle, preview

    return None, None, None

def delete_linkedin_post(access_token, post_id):
    """Delete a LinkedIn post by ID."""
    import urllib.parse

    headers = {
        'Authorization': f'Bearer {access_token}',
        'LinkedIn-Version': '202210',
        'X-Restli-Protocol-Version': '2.0.0'
    }

    # URL encode the full URN
    encoded_id = urllib.parse.quote(post_id, safe='')

    response = requests.delete(
        f'https://api.linkedin.com/v2/ugcPosts/{encoded_id}',
        headers=headers
    )

    if response.status_code in [200, 204]:
        return True
    else:
        raise Exception(f"LinkedIn delete error {response.status_code}: {response.text}")

def post_to_linkedin(access_token, user_urn, text, url=None):
    """Post to LinkedIn using API."""

    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json',
        'LinkedIn-Version': '202210',
        'X-Restli-Protocol-Version': '2.0.0'
    }

    # Build post payload
    payload = {
        'author': user_urn,  # URN should already be in correct format from .env
        'lifecycleState': 'PUBLISHED',
        'specificContent': {
            'com.linkedin.ugc.ShareContent': {
                'shareCommentary': {
                    'text': text
                },
                'shareMediaCategory': 'NONE'
            }
        },
        'visibility': {
            'com.linkedin.ugc.MemberNetworkVisibility': 'PUBLIC'
        }
    }

    # If URL provided, add as article
    if url:
        payload['specificContent']['com.linkedin.ugc.ShareContent']['shareMediaCategory'] = 'ARTICLE'
        payload['specificContent']['com.linkedin.ugc.ShareContent']['media'] = [{
            'status': 'READY',
            'originalUrl': url
        }]

    response = requests.post(
        'https://api.linkedin.com/v2/ugcPosts',
        headers=headers,
        json=payload
    )

    if response.status_code in [200, 201]:
        return response.json()
    else:
        raise Exception(f"LinkedIn API error {response.status_code}: {response.text}")

def main():
    parser = argparse.ArgumentParser(description='Post to LinkedIn')
    parser.add_argument('--file', required=True, help='Path to published markdown file')
    args = parser.parse_args()

    # Get credentials from environment
    access_token = os.getenv('LINKEDIN_ACCESS_TOKEN')
    user_urn = os.getenv('LINKEDIN_USER_URN')

    if not access_token or not user_urn:
        print("ERROR: LinkedIn credentials not found in environment")
        print("Required: LINKEDIN_ACCESS_TOKEN and LINKEDIN_USER_URN")
        sys.exit(1)

    # Extract content
    title, subtitle, preview = extract_post_content(args.file)

    if not title:
        print("ERROR: Could not extract content from file")
        sys.exit(1)

    # Build post URL
    post_url = generate_post_url(args.file)

    # Create LinkedIn post text
    post_text = f"{title}\n\n"
    if subtitle:
        post_text += f"{subtitle}\n\n"
    post_text += f"{preview}...\n\n"
    post_text += f"Read more: {post_url}\n\n"
    post_text += LINKEDIN_HASHTAGS

    print(f"Posting to LinkedIn...")
    print(f"Title: {title}")
    print(f"URL: {post_url}")

    try:
        result = post_to_linkedin(access_token, user_urn, post_text, post_url)

        post_id = result.get('id', 'unknown')
        print(f"\nSUCCESS: Posted to LinkedIn")
        print(f"Post ID: {post_id}")

    except Exception as e:
        print(f"\nERROR: LinkedIn posting failed: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
