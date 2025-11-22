#!/usr/bin/env python3
"""
Eastbound Financial Analysis
Core functions for fetching articles from Eastern international media sources
(Russian, Chinese, Japanese, Korean, North Korean) and creating finance-focused summaries.
"""

import feedparser
import json
from datetime import datetime, UTC
from pathlib import Path
import sys
import io
import requests
import urllib3

# Suppress SSL warnings for sources with cert issues
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Fix Windows console encoding for emojis
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# Russian media RSS feeds
RSS_SOURCES = {
    'TASS': 'https://tass.com/rss/v2.xml',
    'RT': 'https://www.rt.com/rss/',
    'Sputnik': 'https://sputniknews.com/export/rss2/archive/index.xml',
    'RIAN': 'https://rian.ru/export/rss2/archive/index.xml',
}

# CJK (Chinese, Japanese, Korean) + North Korea media RSS feeds
CJK_SOURCES = {
    'Xinhua': 'http://www.xinhuanet.com/english/rss/worldrss.xml',
    'People\'s Daily': 'http://en.people.cn/rss/World.xml',
    'CGTN': 'https://www.cgtn.com/subscribe/rss/section/world.xml',
    'NHK': 'https://www3.nhk.or.jp/rss/news/cat6.xml',
    'Japan Times': 'https://www.japantimes.co.jp/feed/',
    'Yonhap': 'https://en.yna.co.kr/RSS/news.xml',
    '38 North': 'https://www.38north.org/feed/',
    'Daily NK': 'https://www.dailynk.com/english/feed/',
}

# Feeds that require SSL verification bypass due to cert issues
SSL_BYPASS_SOURCES = {'RIAN', 'NHK'}

# Combine all sources
ALL_SOURCES = {**RSS_SOURCES, **CJK_SOURCES}

def fetch_articles(max_retries=2):
    """Fetch latest articles (with full content) from all media sources."""
    print("📰 Fetching articles from international media sources...\n")

    all_articles = []
    failed_sources = []

    for source_name, feed_url in ALL_SOURCES.items():
        success = False
        last_error = None

        for attempt in range(max_retries):
            try:
                if attempt > 0:
                    print(f"  → {source_name} (retry {attempt})...", end=" ")
                else:
                    print(f"  → {source_name}...", end=" ")

                # For sources with SSL cert issues, fetch with verify=False
                if source_name in SSL_BYPASS_SOURCES:
                    response = requests.get(feed_url, timeout=10, verify=False)
                    response.raise_for_status()
                    feed = feedparser.parse(response.content)
                else:
                    # Parse feed normally
                    feed = feedparser.parse(feed_url)

                # Check for feed errors (but ignore harmless encoding warnings)
                if hasattr(feed, 'bozo') and feed.bozo:
                    if hasattr(feed, 'bozo_exception'):
                        exception = feed.bozo_exception
                        # Ignore CharacterEncodingOverride - it's harmless
                        if not isinstance(exception, feedparser.CharacterEncodingOverride):
                            # Check if we still got entries despite the error
                            if not hasattr(feed, 'entries') or len(feed.entries) == 0:
                                raise exception

                if not hasattr(feed, 'entries') or len(feed.entries) == 0:
                    raise ValueError("No entries found in feed")

                for entry in feed.entries[:10]:  # Get 10 most recent from each
                    # Get full content from summary/description/content fields
                    content = ""
                    if hasattr(entry, 'content') and entry.content:
                        content = entry.content[0].value
                    elif hasattr(entry, 'summary') and entry.summary:
                        content = entry.summary
                    elif hasattr(entry, 'description') and entry.description:
                        content = entry.description

                    article = {
                        'source': source_name,
                        'title': entry.get('title', 'No title'),
                        'link': entry.get('link', ''),
                        'published': entry.get('published', ''),
                        'content': content[:1000] if content else '',  # Limit to 1000 chars per article
                    }
                    all_articles.append(article)

                print(f"✓ ({len(feed.entries[:10])} articles)")
                success = True
                break  # Success, no need to retry

            except Exception as e:
                last_error = e
                if attempt < max_retries - 1:
                    continue  # Retry
                else:
                    print(f"✗ Failed after {max_retries} attempts: {type(e).__name__}")

        if not success:
            failed_sources.append((source_name, str(last_error)))

    print(f"\n✓ Total: {len(all_articles)} articles collected from {len(ALL_SOURCES) - len(failed_sources)}/{len(ALL_SOURCES)} sources")

    if failed_sources:
        print(f"⚠️  Failed sources ({len(failed_sources)}):")
        for source, error in failed_sources:
            print(f"   - {source}: {error[:80]}")

    print()
    return all_articles

def get_utc_date():
    """Get current UTC date from online API with proper error handling."""
    errors = []

    # Try worldtimeapi.org first
    try:
        response = requests.get('http://worldtimeapi.org/api/timezone/Etc/UTC', timeout=5)
        if response.status_code == 200:
            data = response.json()
            utc_datetime = datetime.fromisoformat(data['datetime'].replace('Z', '+00:00'))
            return utc_datetime.strftime("%Y-%m-%d")
        else:
            errors.append(f"worldtimeapi.org returned status {response.status_code}")
    except requests.RequestException as e:
        errors.append(f"worldtimeapi.org request failed: {type(e).__name__}")
    except (KeyError, ValueError) as e:
        errors.append(f"worldtimeapi.org parse error: {type(e).__name__}")

    # Fallback to timeapi.io
    try:
        response = requests.get('https://timeapi.io/api/Time/current/zone?timeZone=UTC', timeout=5)
        if response.status_code == 200:
            data = response.json()
            return f"{data['year']}-{data['month']:02d}-{data['day']:02d}"
        else:
            errors.append(f"timeapi.io returned status {response.status_code}")
    except requests.RequestException as e:
        errors.append(f"timeapi.io request failed: {type(e).__name__}")
    except (KeyError, ValueError) as e:
        errors.append(f"timeapi.io parse error: {type(e).__name__}")

    # Last resort: use system UTC (might be wrong)
    print("⚠️  Warning: All time APIs failed, using system UTC time (may be incorrect)")
    for error in errors:
        print(f"   - {error}")

    return datetime.now(UTC).strftime("%Y-%m-%d")

def save_data(articles, summary_text):
    """Save articles and summary to files."""
    # Use UTC for consistency
    utc_date = get_utc_date()
    utc_now = datetime.now(UTC)
    timestamp = utc_now.strftime("%Y-%m-%d-%H%M%S")  # Include time to avoid overwriting

    # Get project root (parent of src/)
    project_root = Path(__file__).parent.parent

    # Create directories
    data_dir = project_root / "data"
    posts_dir = project_root / "posts"
    data_dir.mkdir(exist_ok=True)
    posts_dir.mkdir(exist_ok=True)

    # Save raw data with timestamp to avoid overwriting
    data_file = data_dir / f"{timestamp}-articles.json"
    with open(data_file, 'w', encoding='utf-8') as f:
        json.dump({
            'date': utc_date,
            'timestamp': timestamp,
            'articles': articles,
            'summary': summary_text
        }, f, indent=2, ensure_ascii=False)

    print(f"✓ Saved data to {data_file}")

    # Save formatted post with timestamp to avoid overwriting
    post_file = posts_dir / f"{timestamp}-summary.md"
    with open(post_file, 'w', encoding='utf-8') as f:
        f.write(f"# Eastbound Financial Analysis - {utc_date} ({utc_now.strftime('%H:%M:%S')} UTC)\n\n")
        f.write(f"## Economic & Financial Summary\n\n")
        f.write(f"{summary_text}\n\n")
        f.write("---\n\n")
        f.write(f"**Generated:** {utc_now.strftime('%Y-%m-%d at %H:%M:%S UTC')}\n\n")
        f.write(f"**Coverage:** Russian, Chinese, Japanese, Korean, and North Korean media sources\n\n")
        f.write("## Sources\n\n")
        for article in articles[:30]:  # Show first 30
            f.write(f"- **{article['source']}**: [{article['title']}]({article['link']})\n")

    print(f"✓ Saved post to {post_file}")

    return post_file

def create_prompt(articles):
    """Create prompt for Claude Code to summarize the articles with finance/economic focus."""
    prompt = """Analyze these international media articles (Russian, Chinese, Japanese, Korean, North Korean) and provide a 1-2 sentence summary focused specifically on ECONOMIC and FINANCIAL implications, trends, and developments.

Prioritize:
- Economic policy changes and monetary decisions
- Trade relationships and sanctions
- Energy markets and commodities
- Currency movements and financial markets
- Corporate developments and business activity
- Infrastructure and investment projects

Do not include any preamble, thinking process, or meta-commentary. Start directly with the financially-focused summary.

Articles:

"""

    for article in articles:
        prompt += f"=== {article['source']}: {article['title']} ===\n"
        prompt += f"{article['content']}\n"
        prompt += f"URL: {article['link']}\n\n"

    prompt += "\nProvide ONLY the 1-2 sentence finance-focused summary, nothing else:"

    return prompt
