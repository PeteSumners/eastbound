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
import sys
import io
from pathlib import Path
import yaml
import tweepy
from config import generate_post_url, TWITTER_HASHTAGS

# Force UTF-8 encoding for Windows console (fixes emoji support)
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    env_path = Path(__file__).parent.parent / '.env'
    if env_path.exists():
        load_dotenv(env_path)
except ImportError:
    pass  # dotenv not installed, rely on system environment variables


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


def create_thread(frontmatter, sections, post_url):
    """Create a Twitter thread from content sections."""

    title = frontmatter.get('title', '')
    excerpt = frontmatter.get('excerpt', '')
    content_type = frontmatter.get('type', '')

    tweets = []

    if content_type == 'weekly-analysis':
        # Tweet 1: Hook + link
        tweet1 = f"🧵 {title}\n\n{sections.get('hook', '')[:200]}...\n\n{post_url}"
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
        tweet1 = f"🧵 New translation: {title}\n\n{intro_preview}...\n\n{post_url}"
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

    # If no specific content type or no tweets created yet, create simple post with excerpt
    if not tweets and excerpt:
        # Simple tweet with title and excerpt
        tweet = f"{title}\n\n{excerpt}\n\nRead more: {post_url}\n\n{TWITTER_HASHTAGS}"
        # Truncate if too long (280 char limit)
        if len(tweet) > 280:
            max_excerpt_len = 280 - len(title) - len(post_url) - len(TWITTER_HASHTAGS) - 20  # 20 for formatting
            truncated_excerpt = excerpt[:max_excerpt_len] + "..."
            tweet = f"{title}\n\n{truncated_excerpt}\n\nRead more: {post_url}\n\n{TWITTER_HASHTAGS}"
        tweets.append(tweet)
    elif not tweets:
        # Fallback if no excerpt
        tweets.append(f"Read the full analysis:\n{post_url}\n\n{TWITTER_HASHTAGS}")

    return tweets


def upload_image(api_v1, image_path):
    """Upload image to Twitter using v1.1 API."""
    try:
        media = api_v1.media_upload(filename=image_path)
        print(f"   [OK] Image uploaded (media_id: {media.media_id})")
        return media.media_id
    except Exception as e:
        print(f"   [WARNING] Image upload failed: {e}")
        return None


def post_thread(tweets, api_client, api_v1=None, image_path=None):
    """Post a thread to Twitter using API v2, with optional image for first tweet."""

    print(f"[TWITTER] Posting thread with {len(tweets)} tweets...")

    # Upload image if provided (for first tweet)
    media_id = None
    if image_path and api_v1 and Path(image_path).exists():
        print(f"[TWITTER] Uploading image: {image_path}")
        media_id = upload_image(api_v1, str(image_path))

    previous_tweet_id = None

    for i, tweet_text in enumerate(tweets, 1):
        try:
            # Ensure tweet is under 280 chars
            if len(tweet_text) > 280:
                print(f"[WARNING]  Warning: Tweet {i} is {len(tweet_text)} chars, truncating...")
                tweet_text = tweet_text[:277] + "..."

            # Attach image to first tweet only
            tweet_params = {'text': tweet_text}
            if i == 1 and media_id:
                tweet_params['media_ids'] = [media_id]

            # Post tweet as reply to previous if this is a thread
            if previous_tweet_id:
                tweet_params['in_reply_to_tweet_id'] = previous_tweet_id

            response = api_client.create_tweet(**tweet_params)

            tweet_id = response.data['id']
            previous_tweet_id = tweet_id

            print(f"   [OK] Tweet {i}/{len(tweets)} posted (ID: {tweet_id})")

        except Exception as e:
            print(f"   [ERROR] Error posting tweet {i}: {e}")
            return False

    print(f"[SUCCESS] Thread posted successfully!")
    return True


def main():
    parser = argparse.ArgumentParser(description='Post content to Twitter/X as a thread')
    parser.add_argument('--file', required=True, help='Path to markdown file')
    parser.add_argument('--url', help='URL to post (if different from auto-generated)')
    parser.add_argument('--dry-run', action='store_true', help='Preview thread without posting')

    args = parser.parse_args()

    file_path = Path(args.file)

    if not file_path.exists():
        print(f"[ERROR] File not found: {file_path}")
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

    # Generate post URL
    post_url = args.url if args.url else generate_post_url(file_path)

    # Extract key sections
    content_type = frontmatter.get('type', '')
    sections = extract_key_sections(body, content_type)

    # Create thread
    tweets = create_thread(frontmatter, sections, post_url)

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
        print("[ERROR] Missing Twitter API credentials")
        print("Required environment variables:")
        print("- TWITTER_API_KEY")
        print("- TWITTER_API_SECRET")
        print("- TWITTER_ACCESS_TOKEN")
        print("- TWITTER_ACCESS_TOKEN_SECRET")
        print("- TWITTER_BEARER_TOKEN")
        print("\nSet these in .env file or environment variables.")
        return

    # Initialize Twitter API v2 client
    client = tweepy.Client(
        bearer_token=bearer_token,
        consumer_key=api_key,
        consumer_secret=api_secret,
        access_token=access_token,
        access_token_secret=access_token_secret
    )

    # Initialize Twitter API v1.1 for media upload
    auth = tweepy.OAuth1UserHandler(api_key, api_secret, access_token, access_token_secret)
    api_v1 = tweepy.API(auth)

    # Determine image path from post date
    # Extract date from filename: YYYY-MM-DD-slug.md
    filename = file_path.stem
    date_parts = filename.split('-', 3)
    if len(date_parts) >= 3:
        date_str = '-'.join(date_parts[:3])  # YYYY-MM-DD
        image_path = Path(f"images/{date_str}-generated.png")
    else:
        image_path = None

    # Post thread with image
    post_thread(tweets, client, api_v1, image_path)


if __name__ == '__main__':
    main()
