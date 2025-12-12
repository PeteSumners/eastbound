#!/usr/bin/env python3
"""
Eastbound Financial Analysis
Core functions for fetching articles from international media sources
covering Russia, China, Japan, Korea, Ukraine, Eastern Europe, Middle East,
South Asia, Southeast Asia, and Central Asia. Creates finance-focused summaries.
Runs daily.
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
RUSSIAN_SOURCES = {
    'TASS': 'https://tass.com/rss/v2.xml',
    'RT': 'https://www.rt.com/rss/',
    'Sputnik': 'https://sputniknews.com/export/rss2/archive/index.xml',
    'RIAN': 'https://rian.ru/export/rss2/archive/index.xml',
}

# Ukrainian media RSS feeds
UKRAINIAN_SOURCES = {
    'Kyiv Independent': 'https://kyivindependent.com/feed/rss/',
    'Ukrinform': 'https://www.ukrinform.net/rss/block-lastnews',
    'Interfax-Ukraine': 'https://en.interfax.com.ua/news/last.rss',
}

# Eastern European / Post-Soviet media RSS feeds
EASTERN_EUROPE_SOURCES = {
    'Belta (Belarus)': 'https://eng.belta.by/rss',
}

# Middle East media RSS feeds
MIDDLE_EAST_SOURCES = {
    'Tehran Times': 'https://www.tehrantimes.com/rss',
    'Anadolu Agency': 'https://www.aa.com.tr/en/rss/default?cat=economy',
    'Daily Sabah': 'https://www.dailysabah.com/rssFeed/economy',
    'Jerusalem Post': 'https://www.jpost.com/rss/rssfeedsheadlines.aspx',
}

# South Asian media RSS feeds
SOUTH_ASIA_SOURCES = {
    'The Hindu': 'https://www.thehindu.com/business/feeder/default.rss',
    'Times of India': 'https://timesofindia.indiatimes.com/rssfeeds/1898055.cms',
    'NDTV': 'https://feeds.feedburner.com/ndtvprofit-latest',
}

# Southeast Asian media RSS feeds
SOUTHEAST_ASIA_SOURCES = {
    'VNExpress': 'https://vnexpress.net/rss/tin-moi-nhat.rss',
    'Bangkok Post': 'https://www.bangkokpost.com/rss/data/business.xml',
}

# Central Asian media RSS feeds
CENTRAL_ASIA_SOURCES = {
    'Gazeta.uz (Uzbekistan)': 'https://www.gazeta.uz/en/rss/',
    'Asia-Plus (Tajikistan)': 'https://asiaplustj.info/en/rss',
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
SSL_BYPASS_SOURCES = {'RIAN', 'NHK', 'Belta (Belarus)', 'Asia-Plus (Tajikistan)', 'VNExpress'}

# User-Agent header to avoid 403 blocks
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

# Combine all sources
ALL_SOURCES = {
    **RUSSIAN_SOURCES,
    **UKRAINIAN_SOURCES,
    **EASTERN_EUROPE_SOURCES,
    **MIDDLE_EAST_SOURCES,
    **SOUTH_ASIA_SOURCES,
    **SOUTHEAST_ASIA_SOURCES,
    **CENTRAL_ASIA_SOURCES,
    **CJK_SOURCES,
}

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

                # Use requests with User-Agent for all sources to avoid 403 blocks
                if source_name in SSL_BYPASS_SOURCES:
                    response = requests.get(feed_url, headers=HEADERS, timeout=15, verify=False)
                else:
                    response = requests.get(feed_url, headers=HEADERS, timeout=15)
                response.raise_for_status()
                feed = feedparser.parse(response.content)

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
        f.write(f"**Coverage:** Russia, Ukraine, Eastern Europe, Middle East, South Asia, Southeast Asia, Central Asia, China, Japan, Korea\n\n")
        f.write("## Sources\n\n")

        # Show articles from all sources by taking proportional samples
        # Group articles by source
        from collections import defaultdict
        by_source = defaultdict(list)
        for article in articles:
            by_source[article['source']].append(article)

        # Take up to 3 articles from each source to ensure geographic diversity
        displayed_articles = []
        for source_name in sorted(by_source.keys()):
            displayed_articles.extend(by_source[source_name][:3])

        for article in displayed_articles:
            f.write(f"- **{article['source']}**: [{article['title']}]({article['link']})\n")

    print(f"✓ Saved post to {post_file}")

    return post_file

def create_prompt(articles):
    """Create prompt for Claude Code to generate a newscast script with finance/economic focus."""

    # Count articles by region
    from collections import Counter
    source_counts = Counter(article['source'] for article in articles)

    # Build region summary
    russian_count = sum(source_counts[s] for s in ['TASS', 'RT', 'Sputnik', 'RIAN'] if s in source_counts)
    ukrainian_count = sum(source_counts[s] for s in ['Kyiv Independent', 'Ukrinform', 'Interfax-Ukraine'] if s in source_counts)
    eastern_europe_count = sum(source_counts[s] for s in ['Belta (Belarus)'] if s in source_counts)
    middle_east_count = sum(source_counts[s] for s in ['Tehran Times', 'Anadolu Agency', 'Daily Sabah', 'Jerusalem Post'] if s in source_counts)
    south_asia_count = sum(source_counts[s] for s in ['The Hindu', 'Times of India', 'NDTV'] if s in source_counts)
    southeast_asia_count = sum(source_counts[s] for s in ['VNExpress', 'Bangkok Post'] if s in source_counts)
    central_asia_count = sum(source_counts[s] for s in ['Gazeta.uz (Uzbekistan)', 'Asia-Plus (Tajikistan)'] if s in source_counts)
    chinese_count = sum(source_counts[s] for s in ['Xinhua', "People's Daily", 'CGTN'] if s in source_counts)
    japanese_count = sum(source_counts[s] for s in ['NHK', 'Japan Times'] if s in source_counts)
    korean_count = sum(source_counts[s] for s in ['Yonhap'] if s in source_counts)
    nk_count = sum(source_counts[s] for s in ['38 North', 'Daily NK'] if s in source_counts)

    prompt = f"""You are a news anchor for Eastbound Reports, a daily financial briefing covering Eastern and emerging markets worldwide.

Write a SHORT, ENERGETIC newscast script (90-120 seconds when read aloud, approximately 200-280 words).

VOICE STYLE (optimized for engagement):
- HIGH ENERGY delivery - speak with enthusiasm and conviction
- VARIED PACING - mix short punchy sentences with longer explanations
- DYNAMIC TONE - modulate between serious and conversational
- CLEAR ARTICULATION - professional broadcast quality

SCRIPT STRUCTURE:
1. OPENING (1 sentence): Energetic greeting with date
2. TOP STORY (2-3 sentences): Most significant economic development
3. REGIONAL ROUNDUP (4-6 sentences): Quick hits from other regions
4. CLOSING (1 sentence): Sign-off with call to action

MANDATORY GEOGRAPHIC BALANCE (articles available):
- Russia: {russian_count} articles
- Ukraine: {ukrainian_count} articles
- Eastern Europe (Belarus): {eastern_europe_count} articles
- Middle East (Iran, Turkey, Israel): {middle_east_count} articles
- South Asia (India): {south_asia_count} articles
- Southeast Asia (Vietnam, Thailand): {southeast_asia_count} articles
- Central Asia (Uzbekistan, Tajikistan): {central_asia_count} articles
- China: {chinese_count} articles
- Japan: {japanese_count} articles
- Korea: {korean_count} articles
- North Korea: {nk_count} articles

You MUST cover AT LEAST 4 DIFFERENT REGIONS. Focus only on ECONOMIC/FINANCIAL news:
- Economic policy, monetary decisions, trade, sanctions
- Energy markets, commodities, currencies
- Corporate developments, infrastructure, investments

DO NOT include:
- Stage directions or [brackets]
- "Um", "uh", or filler words
- Meta-commentary about the script
- Non-economic news (military, political drama without economic angle)

Articles:

"""

    for article in articles:
        prompt += f"=== {article['source']}: {article['title']} ===\n"
        prompt += f"{article['content']}\n"
        prompt += f"URL: {article['link']}\n\n"

    prompt += "\nWrite the newscast script now, starting directly with the opening greeting:"

    return prompt
