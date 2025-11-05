#!/usr/bin/env python3
"""
Post to Twitter/X with auto-generated thread from content.

Usage:
    python post_to_twitter.py --file content/published/2024-11-05-my-post.md
    python post_to_twitter.py --file content/published/2024-11-05-my-post.md --dry-run
"""

import argparse
import os
import re
from pathlib import Path
import yaml
import tweepy


def parse_frontmatter(content):
    """Extract YAML frontmatter and content from markdown file."""
    pattern = r'^---\s*\n(.*?\n)---\s*\n(.*)$'
    match = re.match(pattern, content, re.DOTALL)

    if match:
        frontmatter = yaml.safe_load(match.group(1))
        body = match.group(2)
        return frontmatter, body
    else:
        return {}, content


def extract_key_sections(content, content_type):
    """Extract key sections from markdown content for Twitter thread."""

    # Remove markdown links but keep text
    content = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', content)

    if content_type == 'weekly-analysis':
        # Extract hook section
        hook_match = re.search(r'## Hook:.*?\n\n(.*?)(?=\n##|\Z)', content, re.DOTALL)
        hook = hook_match.group(1).strip() if hook_match else ""

        # Extract bottom line
        bottom_line_match = re.search(r'## Bottom Line\n\n(.*?)(?=\n##|\Z)', content, re.DOTALL)
        bottom_line = bottom_line_match.group(1).strip() if bottom_line_match else ""

        # Extract key implications
        implications_match = re.search(r'## Implications\n\n.*?\*\*Policy:\*\*\s*(.*?)(?=\n\*\*|\n##|\Z)', content, re.DOTALL)
        policy_implication = implications_match.group(1).strip() if implications_match else ""

        return {
            'hook': hook,
            'bottom_line': bottom_line,
            'policy_implication': policy_implication
        }

    elif content_type == 'translation':
        # Extract introduction
        intro_match = re.search(r'## Introduction: Why This Matters\n\n(.*?)(?=\n##|\Z)', content, re.DOTALL)
        intro = intro_match.group(1).strip() if intro_match else ""

        # Extract key quotes from translation (first 2-3 paragraphs)
        translation_match = re.search(r'## Translation\n\n(.*?)(?=\n##|\Z)', content, re.DOTALL)
        if translation_match:
            translation_text = translation_match.group(1).strip()
            # Get first few paragraphs
            paragraphs = [p.strip() for p in translation_text.split('\n\n') if p.strip()]
            key_quotes = paragraphs[:2]  # First 2 paragraphs
        else:
            key_quotes = []

        # Extract what this reveals
        reveals_match = re.search(r'### What This Reveals\n\n(.*?)(?=\n###|\n##|\Z)', content, re.DOTALL)
        reveals = reveals_match.group(1).strip() if reveals_match else ""

        return {
            'intro': intro,
            'key_quotes': key_quotes,
            'reveals': reveals
        }

    return {}


def create_thread(frontmatter, sections, substack_url):
    """Create a Twitter thread from content sections."""

    title = frontmatter.get('title', '')
    content_type = frontmatter.get('type', '')

    tweets = []

    if content_type == 'weekly-analysis':
        # Tweet 1: Hook + link
        tweet1 = f"🧵 {title}\n\n{sections.get('hook', '')[:200]}...\n\n{substack_url}"
        tweets.append(tweet1)

        # Tweet 2: Policy implication
        if sections.get('policy_implication'):
            tweet2 = f"Policy implications: {sections['policy_implication'][:260]}"
            tweets.append(tweet2)

        # Tweet 3: Bottom line
        if sections.get('bottom_line'):
            tweet3 = f"Bottom line: {sections['bottom_line'][:270]}"
            tweets.append(tweet3)

    elif content_type == 'translation':
        # Tweet 1: Intro + link
        intro_preview = sections.get('intro', '')[:180]
        tweet1 = f"🧵 New translation: {title}\n\n{intro_preview}...\n\n{substack_url}"
        tweets.append(tweet1)

        # Tweets 2-3: Key quotes
        for i, quote in enumerate(sections.get('key_quotes', [])[:2]):
            if len(quote) > 270:
                quote = quote[:267] + "..."
            tweets.append(f'"{quote}"')

        # Tweet 4: What this reveals
        if sections.get('reveals'):
            reveals_preview = sections['reveals'][:260]
            tweet4 = f"What this reveals: {reveals_preview}"
            if len(reveals_preview) < len(sections['reveals']):
                tweet4 += "..."
            tweets.append(tweet4)

    # Add final tweet: Read more + tags
    tweets.append(f"Read the full analysis:\n{substack_url}\n\n#Russia #MediaAnalysis #Geopolitics")

    return tweets


def post_thread(tweets, api_client):
    """Post a thread to Twitter using API v2."""

    print(f"🐦 Posting thread with {len(tweets)} tweets...")

    previous_tweet_id = None

    for i, tweet_text in enumerate(tweets, 1):
        try:
            # Ensure tweet is under 280 chars
            if len(tweet_text) > 280:
                print(f"⚠️  Warning: Tweet {i} is {len(tweet_text)} chars, truncating...")
                tweet_text = tweet_text[:277] + "..."

            # Post tweet as reply to previous if this is a thread
            if previous_tweet_id:
                response = api_client.create_tweet(
                    text=tweet_text,
                    in_reply_to_tweet_id=previous_tweet_id
                )
            else:
                response = api_client.create_tweet(text=tweet_text)

            tweet_id = response.data['id']
            previous_tweet_id = tweet_id

            print(f"   ✅ Tweet {i}/{len(tweets)} posted (ID: {tweet_id})")

        except Exception as e:
            print(f"   ❌ Error posting tweet {i}: {e}")
            return False

    print(f"✅ Thread posted successfully!")
    return True


def main():
    parser = argparse.ArgumentParser(description='Post content to Twitter/X as a thread')
    parser.add_argument('--file', required=True, help='Path to markdown file')
    parser.add_argument('--substack-url', help='URL to Substack post (if different from auto-generated)')
    parser.add_argument('--dry-run', action='store_true', help='Preview thread without posting')

    args = parser.parse_args()

    file_path = Path(args.file)

    if not file_path.exists():
        print(f"❌ Error: File not found: {file_path}")
        return

    # Read file
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Parse frontmatter
    frontmatter, body = parse_frontmatter(content)

    # Check if Twitter thread is enabled
    if not frontmatter.get('twitter_thread', True):
        print("ℹ️  Twitter thread is disabled for this post (twitter_thread: false)")
        return

    # Generate Substack URL
    substack_url = args.substack_url
    if not substack_url:
        # Auto-generate from filename and subdomain
        slug = file_path.stem.split('-', 3)[-1] if '-' in file_path.stem else file_path.stem
        substack_url = f"https://eastboundreports.substack.com/p/{slug}"

    # Extract key sections
    content_type = frontmatter.get('type', '')
    sections = extract_key_sections(body, content_type)

    # Create thread
    tweets = create_thread(frontmatter, sections, substack_url)

    if args.dry_run:
        print("=== DRY RUN MODE ===")
        print(f"Thread preview ({len(tweets)} tweets):\n")
        for i, tweet in enumerate(tweets, 1):
            print(f"--- Tweet {i} ({len(tweet)} chars) ---")
            print(tweet)
            print()
        return

    # Get Twitter API credentials from environment
    api_key = os.getenv('TWITTER_API_KEY')
    api_secret = os.getenv('TWITTER_API_SECRET')
    access_token = os.getenv('TWITTER_ACCESS_TOKEN')
    access_token_secret = os.getenv('TWITTER_ACCESS_TOKEN_SECRET')
    bearer_token = os.getenv('TWITTER_BEARER_TOKEN')

    if not all([api_key, api_secret, access_token, access_token_secret]):
        print("❌ Error: Missing Twitter API credentials")
        print("Required environment variables:")
        print("- TWITTER_API_KEY")
        print("- TWITTER_API_SECRET")
        print("- TWITTER_ACCESS_TOKEN")
        print("- TWITTER_ACCESS_TOKEN_SECRET")
        print("- TWITTER_BEARER_TOKEN")
        print("\nSet these in GitHub Secrets for automation.")
        return

    # Initialize Twitter API client
    client = tweepy.Client(
        bearer_token=bearer_token,
        consumer_key=api_key,
        consumer_secret=api_secret,
        access_token=access_token,
        access_token_secret=access_token_secret
    )

    # Post thread
    post_thread(tweets, client)


if __name__ == '__main__':
    main()
