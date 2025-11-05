#!/usr/bin/env python3
"""
Monitor Russian media sources via RSS feeds and identify top stories.

Usage:
    python monitor_russian_media.py --output research/YYYY-MM-DD-briefing.json
"""

import argparse
import feedparser
import json
from datetime import datetime
from collections import defaultdict
import re

# Russian media RSS feeds
RSS_SOURCES = {
    'TASS': 'https://tass.com/rss/v2.xml',
    'RIA Novosti': 'https://ria.ru/export/rss2/archive/index.xml',
    'Interfax': 'https://www.interfax.ru/rss.asp',
    'RT': 'https://www.rt.com/rss/',
    'Kommersant': 'https://www.kommersant.ru/RSS/main.xml',
    'TASS English': 'https://tass.com/rss/v2.xml',
}

def fetch_feed(url, source_name):
    """Fetch and parse RSS feed."""
    try:
        feed = feedparser.parse(url)
        articles = []

        for entry in feed.entries[:10]:  # Top 10 from each source
            articles.append({
                'source': source_name,
                'title': entry.get('title', ''),
                'link': entry.get('link', ''),
                'published': entry.get('published', ''),
                'summary': entry.get('summary', '')[:500],  # First 500 chars
            })

        return articles
    except Exception as e:
        print(f"Error fetching {source_name}: {e}")
        return []

def extract_keywords(text):
    """Extract key terms from text (simple implementation)."""
    # Remove common words and extract meaningful terms
    text = text.lower()
    words = re.findall(r'\b\w{4,}\b', text)

    # Filter out very common words
    stopwords = {'this', 'that', 'with', 'from', 'have', 'been', 'will', 'said', 'says', 'more', 'about', 'after'}
    keywords = [w for w in words if w not in stopwords]

    return keywords

def identify_trending_stories(all_articles):
    """Identify stories covered by multiple sources."""
    keyword_counts = defaultdict(list)

    for article in all_articles:
        keywords = extract_keywords(article['title'] + ' ' + article['summary'])
        for keyword in set(keywords):  # Unique keywords per article
            keyword_counts[keyword].append(article)

    # Find keywords mentioned by multiple sources
    trending = {}
    for keyword, articles in keyword_counts.items():
        sources = set(a['source'] for a in articles)
        if len(sources) >= 2:  # Covered by 2+ sources
            if keyword not in trending or len(sources) > len(set(a['source'] for a in trending[keyword]['articles'])):
                trending[keyword] = {
                    'keyword': keyword,
                    'source_count': len(sources),
                    'articles': articles[:5]  # Top 5 articles
                }

    # Sort by source count (most covered)
    sorted_trending = sorted(trending.values(), key=lambda x: x['source_count'], reverse=True)

    return sorted_trending[:5]  # Top 5 trending topics

def create_briefing(trending_stories, all_articles):
    """Create a briefing document."""
    today = datetime.now().strftime('%Y-%m-%d')

    briefing = {
        'date': today,
        'generated_at': datetime.now().isoformat(),
        'total_articles_scanned': len(all_articles),
        'trending_stories': trending_stories,
        'top_headlines': all_articles[:15]  # Top 15 overall
    }

    return briefing

def main():
    parser = argparse.ArgumentParser(description='Monitor Russian media sources')
    parser.add_argument('--output', required=True, help='Output JSON file path')
    args = parser.parse_args()

    print("📡 Monitoring Russian media sources...")

    all_articles = []
    for source_name, url in RSS_SOURCES.items():
        print(f"  Fetching {source_name}...")
        articles = fetch_feed(url, source_name)
        all_articles.extend(articles)
        print(f"    ✓ Found {len(articles)} articles")

    print(f"\n📊 Total articles: {len(all_articles)}")

    print("\n🔍 Identifying trending stories...")
    trending = identify_trending_stories(all_articles)
    print(f"  ✓ Found {len(trending)} trending topics")

    briefing = create_briefing(trending, all_articles)

    # Save briefing
    with open(args.output, 'w', encoding='utf-8') as f:
        json.dump(briefing, f, indent=2, ensure_ascii=False)

    print(f"\n✅ Briefing saved to: {args.output}")

    # Print summary
    print("\n📋 Top trending stories:")
    for i, story in enumerate(trending[:3], 1):
        print(f"\n{i}. Keyword: {story['keyword']}")
        print(f"   Sources: {story['source_count']}")
        for article in story['articles'][:2]:
            print(f"   - {article['source']}: {article['title'][:80]}...")

if __name__ == '__main__':
    main()
