#!/usr/bin/env python3
"""
Eastbound Financial Analysis Automation
Fetches articles from Russian, Chinese, Japanese, Korean, and North Korean media sources,
generates finance-focused summary with Claude Code, and posts to social media.
Runs daily via Windows Task Scheduler.
"""

import subprocess
import json
from pathlib import Path
from datetime import datetime, UTC
import os
import sys
import traceback
import platform

# Import from daily_summary
from daily_summary import fetch_articles, create_prompt, save_data, get_utc_date

# Load environment variables
try:
    from dotenv import load_dotenv
    # Load .env from project root (parent directory)
    env_path = Path(__file__).parent.parent / '.env'
    load_dotenv(env_path)
except ImportError:
    pass

# Debug logging
def log_debug(message, error=None):
    """Log debug message with timestamp."""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
    log_msg = f"[{timestamp}] {message}"
    print(log_msg)

    if error:
        print(f"[{timestamp}] ERROR DETAILS: {str(error)}")
        print(f"[{timestamp}] TRACEBACK:")
        traceback.print_exc()

    return log_msg

def call_claude_code(prompt):
    """Call Claude Code CLI to generate summary."""
    log_debug("🤖 Calling Claude Code to generate summary...")

    try:
        # Get project root
        project_root = Path(__file__).parent.parent
        data_dir = project_root / "data"

        log_debug(f"Project root: {project_root}")
        log_debug(f"Data directory: {data_dir}")

        # Create data directory if it doesn't exist
        data_dir.mkdir(exist_ok=True)
        log_debug(f"Data directory created/verified")

        # Save prompt to temp file
        prompt_file = data_dir / "temp_prompt.txt"
        log_debug(f"Saving prompt to: {prompt_file}")
        log_debug(f"Prompt length: {len(prompt)} characters")

        with open(prompt_file, 'w', encoding='utf-8') as f:
            f.write(prompt)
        log_debug(f"Prompt saved successfully")

        # Call claude code with --print flag, reading prompt from stdin
        cmd = 'claude code --print'
        log_debug(f"Executing command: {cmd}")
        log_debug(f"Working directory: {os.getcwd()}")

        result = subprocess.run(
            cmd,
            input=prompt,
            capture_output=True,
            text=True,
            encoding='utf-8',
            shell=True
        )

        log_debug(f"Command completed with return code: {result.returncode}")
        log_debug(f"STDOUT length: {len(result.stdout)} chars")
        log_debug(f"STDERR length: {len(result.stderr)} chars")

        if result.returncode == 0:
            summary = result.stdout.strip()
            log_debug(f"✓ Summary generated successfully ({len(summary)} chars)")
            log_debug(f"Summary preview: {summary[:200]}...")
            return summary
        else:
            log_debug(f"❌ Claude Code failed with return code {result.returncode}")
            log_debug(f"STDERR: {result.stderr}")
            log_debug(f"STDOUT: {result.stdout}")
            return None

    except Exception as e:
        log_debug(f"❌ Exception in call_claude_code", error=e)
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

        # Create tweet with summary and UTC timestamp
        today = get_utc_date()
        utc_now = datetime.now(UTC)
        timestamp_str = utc_now.strftime("%H:%M UTC")
        gh_pages_link = "https://petesumners.github.io/eastbound/"
        tweet_text = f"Eastbound Financial Analysis ({today} {timestamp_str})\n\n{summary}\n\nSources: {source_list}\n\n{gh_pages_link}\n\n#Finance #Economics #EastAsia #Russia"

        # Truncate if needed
        if len(tweet_text) > 280:
            max_summary = 280 - len(f"Eastbound Financial Analysis ({today} {timestamp_str})\n\n\n\nSources: {source_list}\n\n{gh_pages_link}\n\n#Finance #Economics #EastAsia #Russia")
            tweet_text = f"Eastbound Financial Analysis ({today} {timestamp_str})\n\n{summary[:max_summary]}...\n\nSources: {source_list}\n\n{gh_pages_link}\n\n#Finance #Economics #EastAsia #Russia"

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

        today = get_utc_date()
        utc_now = datetime.now(UTC)
        timestamp_str = utc_now.strftime("%H:%M UTC")
        gh_pages_link = "https://petesumners.github.io/eastbound/"
        post_text = f"Eastbound Financial Analysis ({today} {timestamp_str})\n\nEconomic & Financial developments from Russian, Chinese, Japanese, Korean, and North Korean media:\n\n{summary}\n\nSources: {source_list}\n\nRead more: {gh_pages_link}\n\n#Finance #Economics #EastAsia #Russia #Markets #EastboundReports"

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
        today = get_utc_date()

        # Add all changes: posts/, index.html, and src/ (data/ is gitignored)
        subprocess.run(['git', 'add', 'posts/'], check=True)
        subprocess.run(['git', 'add', 'index.html'], check=True)
        subprocess.run(['git', 'add', 'src/'], check=True)

        # Commit with automated message
        commit_msg = f"Automated daily update: {today} Eastbound financial analysis"
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
    start_time = datetime.now()

    print("=" * 80)
    print("EASTBOUND FINANCIAL ANALYSIS - AUTOMATED RUN")
    print("=" * 80)
    print()

    # Log environment info
    log_debug("=== ENVIRONMENT INFO ===")
    log_debug(f"Script: {__file__}")
    log_debug(f"Working directory: {os.getcwd()}")
    log_debug(f"Python: {sys.version}")
    log_debug(f"Platform: {platform.platform()}")
    log_debug(f"User: {os.getenv('USERNAME', 'unknown')}")
    log_debug(f"Start time: {start_time.isoformat()}")
    log_debug(f"PATH: {os.getenv('PATH', 'not set')[:200]}...")

    # Check environment variables
    log_debug("=== CHECKING ENVIRONMENT VARIABLES ===")
    env_vars = ['ANTHROPIC_API_KEY', 'TWITTER_API_KEY', 'LINKEDIN_ACCESS_TOKEN']
    for var in env_vars:
        value = os.getenv(var)
        if value:
            log_debug(f"{var}: SET (length={len(value)})")
        else:
            log_debug(f"{var}: NOT SET")

    try:
        # 1. Fetch articles
        log_debug("=== STEP 1: FETCHING ARTICLES ===")
        articles = fetch_articles()

        if not articles:
            log_debug("❌ No articles fetched. Exiting.")
            return 1

        log_debug(f"✓ Fetched {len(articles)} articles")

        # 2. Create prompt
        log_debug("=== STEP 2: CREATING PROMPT ===")
        prompt = create_prompt(articles)
        log_debug(f"✓ Prompt created ({len(prompt)} chars)")

        # 3. Generate summary with Claude Code
        log_debug("=== STEP 3: GENERATING SUMMARY WITH CLAUDE CODE ===")
        summary = call_claude_code(prompt)

        if not summary:
            log_debug("❌ Failed to generate summary. Exiting.")
            return 1

        log_debug("📄 Summary:")
        log_debug("-" * 60)
        print(summary)
        log_debug("-" * 60)

        # 4. Save data
        log_debug("=== STEP 4: SAVING DATA ===")
        post_file = save_data(articles, summary)
        log_debug(f"✓ Data saved to: {post_file}")

        # 5. Post to social media
        log_debug("=== STEP 5: POSTING TO SOCIAL MEDIA ===")
        twitter_success = post_to_twitter(summary, post_file, articles)
        linkedin_success = post_to_linkedin(summary, post_file, articles)
        log_debug(f"Twitter: {'✓ Success' if twitter_success else '✗ Failed/Skipped'}")
        log_debug(f"LinkedIn: {'✓ Success' if linkedin_success else '✗ Failed/Skipped'}")

        # 6. Commit and push to GitHub
        log_debug("=== STEP 6: COMMITTING TO GITHUB ===")
        git_success = commit_and_push()
        log_debug(f"Git: {'✓ Success' if git_success else '✗ Failed'}")

        # Final summary
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()

        log_debug("=" * 80)
        log_debug("✓ AUTOMATION COMPLETE")
        log_debug(f"Duration: {duration:.2f} seconds")
        log_debug(f"End time: {end_time.isoformat()}")
        log_debug("=" * 80)

        return 0

    except Exception as e:
        log_debug("=" * 80)
        log_debug("❌ AUTOMATION FAILED WITH EXCEPTION", error=e)
        log_debug("=" * 80)
        return 1

if __name__ == '__main__':
    exit_code = main()
    sys.exit(exit_code)
