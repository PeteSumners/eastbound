#!/usr/bin/env python3
"""
Simple daily Russian media summary generator.
Core functions for fetching articles and creating summaries.
"""

import feedparser
import json
from datetime import datetime
from pathlib import Path
import sys
import io

# Fix Windows console encoding for emojis
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# Russian media RSS feeds
RSS_SOURCES = {
    'TASS': 'https://tass.com/rss/v2.xml',
    'RT': 'https://www.rt.com/rss/',
    'Sputnik': 'https://sputniknews.com/export/rss2/archive/index.xml',
    'Interfax': 'https://interfax.com/newsfeed.xml',
    'RIAN': 'https://rian.ru/export/rss2/archive/index.xml',
}

def fetch_articles():
    """Fetch latest articles (with full content) from Russian media sources."""
    print("📰 Fetching articles from Russian media...\n")

    all_articles = []

    for source_name, feed_url in RSS_SOURCES.items():
        try:
            print(f"  → {source_name}...", end=" ")
            feed = feedparser.parse(feed_url)

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
        except Exception as e:
            print(f"✗ Error: {e}")

    print(f"\n✓ Total: {len(all_articles)} articles collected\n")
    return all_articles

def save_data(articles, summary_text):
    """Save articles and summary to files."""
    today = datetime.now().strftime("%Y-%m-%d")

    # Create directories
    Path("data").mkdir(exist_ok=True)
    Path("posts").mkdir(exist_ok=True)

    # Save raw data
    data_file = Path(f"data/{today}-articles.json")
    with open(data_file, 'w', encoding='utf-8') as f:
        json.dump({
            'date': today,
            'articles': articles,
            'summary': summary_text
        }, f, indent=2, ensure_ascii=False)

    print(f"✓ Saved data to {data_file}")

    # Save formatted post
    post_file = Path(f"posts/{today}-summary.md")
    with open(post_file, 'w', encoding='utf-8') as f:
        f.write(f"# Russian Media Summary - {today}\n\n")
        f.write(f"{summary_text}\n\n")
        f.write("---\n\n")
        f.write("## Sources\n\n")
        for article in articles[:20]:  # Show first 20
            f.write(f"- **{article['source']}**: [{article['title']}]({article['link']})\n")

    print(f"✓ Saved post to {post_file}")

    return post_file

def create_prompt(articles):
    """Create prompt for Claude Code to summarize the articles."""
    prompt = """Summarize these Russian media articles in 1-2 concise sentences. Focus ONLY on the main themes. Do not include any preamble, thinking process, or meta-commentary. Start directly with the summary.

Articles:

"""

    for article in articles:
        prompt += f"=== {article['source']}: {article['title']} ===\n"
        prompt += f"{article['content']}\n"
        prompt += f"URL: {article['link']}\n\n"

    prompt += "\nProvide ONLY the 1-2 sentence summary, nothing else:"

    return prompt
