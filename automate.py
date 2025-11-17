#!/usr/bin/env python3
"""
Complete automation: fetch articles, summarize with Claude Code, post to social media.
"""

import subprocess
import json
from pathlib import Path
from datetime import datetime
import os
import sys

# Import from daily_summary
from daily_summary import fetch_articles, create_prompt, save_data

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

def call_claude_code(prompt):
    """Call Claude Code CLI to generate summary."""
    print("🤖 Calling Claude Code to generate summary...\n")

    try:
        # Create data directory if it doesn't exist
        Path("data").mkdir(exist_ok=True)

        # Save prompt to temp file
        prompt_file = Path("data/temp_prompt.txt")
        with open(prompt_file, 'w', encoding='utf-8') as f:
            f.write(prompt)

        # Call claude code with --print flag, reading prompt from stdin
        result = subprocess.run(
            'claude code --print',
            input=prompt,
            capture_output=True,
            text=True,
            encoding='utf-8',
            shell=True
        )

        if result.returncode == 0:
            summary = result.stdout.strip()
            print("✓ Summary generated\n")
            return summary
        else:
            print(f"❌ Claude Code error: {result.stderr}")
            return None

    except Exception as e:
        print(f"❌ Error calling Claude Code: {e}")
        return None

def post_to_twitter(summary, post_file, articles):
    """Post summary to Twitter/X."""
    try:
        import tweepy

        api_key = os.getenv('TWITTER_API_KEY')
        api_secret = os.getenv('TWITTER_API_SECRET')
        access_token = os.getenv('TWITTER_ACCESS_TOKEN')
        access_token_secret = os.getenv('TWITTER_ACCESS_TOKEN_SECRET')
        bearer_token = os.getenv('TWITTER_BEARER_TOKEN')

        if not all([api_key, api_secret, access_token, access_token_secret, bearer_token]):
            print("⚠️  Twitter credentials not found, skipping...")
            return False

        client = tweepy.Client(
            bearer_token=bearer_token,
            consumer_key=api_key,
            consumer_secret=api_secret,
            access_token=access_token,
            access_token_secret=access_token_secret
        )

        # Get unique sources
        sources = sorted(set(article['source'] for article in articles))
        source_list = ", ".join(sources)

        # Create tweet with summary
        today = datetime.now().strftime("%Y-%m-%d")
        gh_pages_link = "https://petesumners.github.io/eastbound/"
        tweet_text = f"Russian Media Summary ({today})\n\n{summary}\n\nSources: {source_list}\n\n{gh_pages_link}\n\n#Russia #MediaAnalysis"

        # Truncate if needed
        if len(tweet_text) > 280:
            max_summary = 280 - len(f"Russian Media Summary ({today})\n\n\n\nSources: {source_list}\n\n{gh_pages_link}\n\n#Russia #MediaAnalysis")
            tweet_text = f"Russian Media Summary ({today})\n\n{summary[:max_summary]}...\n\nSources: {source_list}\n\n{gh_pages_link}\n\n#Russia #MediaAnalysis"

        response = client.create_tweet(text=tweet_text)
        print(f"✓ Posted to Twitter (ID: {response.data['id']})")
        return True

    except Exception as e:
        print(f"⚠️  Twitter posting failed: {e}")
        return False

def post_to_linkedin(summary, post_file, articles):
    """Post summary to LinkedIn."""
    try:
        import requests

        access_token = os.getenv('LINKEDIN_ACCESS_TOKEN')
        user_urn = os.getenv('LINKEDIN_USER_URN')

        if not all([access_token, user_urn]):
            print("⚠️  LinkedIn credentials not found, skipping...")
            return False

        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json',
            'LinkedIn-Version': '202210',
            'X-Restli-Protocol-Version': '2.0.0'
        }

        # Get unique sources
        sources = sorted(set(article['source'] for article in articles))
        source_list = ", ".join(sources)

        today = datetime.now().strftime("%Y-%m-%d")
        gh_pages_link = "https://petesumners.github.io/eastbound/"
        post_text = f"Russian Media Summary ({today})\n\n{summary}\n\nSources: {source_list}\n\nRead more: {gh_pages_link}\n\n#RussianMedia #MediaAnalysis #EastboundReports"

        payload = {
            'author': user_urn,
            'lifecycleState': 'PUBLISHED',
            'specificContent': {
                'com.linkedin.ugc.ShareContent': {
                    'shareCommentary': {'text': post_text},
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
            print(f"✓ Posted to LinkedIn")
            return True
        else:
            print(f"⚠️  LinkedIn posting failed: {response.status_code}")
            return False

    except Exception as e:
        print(f"⚠️  LinkedIn posting failed: {e}")
        return False

def commit_and_push():
    """Commit and push changes to GitHub."""
    try:
        today = datetime.now().strftime("%Y-%m-%d")

        # Add all changes in posts/ (data/ is gitignored)
        subprocess.run(['git', 'add', 'posts/'], check=True)

        # Commit with automated message
        commit_msg = f"Automated update: {today} Russian media summary"
        subprocess.run(['git', 'commit', '-m', commit_msg], check=True)

        # Push to main
        subprocess.run(['git', 'push', 'origin', 'main'], check=True)

        print("✓ Changes committed and pushed to GitHub")
        return True

    except subprocess.CalledProcessError as e:
        print(f"⚠️  Git operation failed: {e}")
        return False
    except Exception as e:
        print(f"⚠️  Error during git operations: {e}")
        return False

def main():
    print("=" * 60)
    print("RUSSIAN MEDIA AUTOMATION")
    print("=" * 60)
    print()

    # 1. Fetch articles
    articles = fetch_articles()

    if not articles:
        print("❌ No articles fetched. Exiting.")
        return

    # 2. Create prompt
    prompt = create_prompt(articles)

    # 3. Generate summary with Claude Code
    summary = call_claude_code(prompt)

    if not summary:
        print("❌ Failed to generate summary. Exiting.")
        return

    print("📄 Summary:")
    print("-" * 60)
    print(summary)
    print("-" * 60)
    print()

    # 4. Save data
    post_file = save_data(articles, summary)

    # 5. Post to social media
    print("\n📱 Posting to social media...\n")
    post_to_twitter(summary, post_file, articles)
    post_to_linkedin(summary, post_file, articles)

    # 6. Commit and push to GitHub
    print("\n📤 Pushing to GitHub...\n")
    commit_and_push()

    print("\n" + "=" * 60)
    print("✓ AUTOMATION COMPLETE")
    print("=" * 60)

if __name__ == '__main__':
    main()
