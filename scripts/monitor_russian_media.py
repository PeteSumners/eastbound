#!/usr/bin/env python3
"""
Monitor Russian media sources via RSS feeds and identify top stories.

Usage:
    python monitor_russian_media.py --output research/YYYY-MM-DD-briefing.json
"""

import argparse
import feedparser
import json
import sys
from datetime import datetime
from collections import defaultdict
import re

# Import advanced TF-IDF keyword extraction
try:
    from advanced_keywords import extract_tfidf_keywords, extract_bigram_tfidf
    TFIDF_AVAILABLE = True
except ImportError:
    TFIDF_AVAILABLE = False
    print("[WARNING] advanced_keywords module not found, using basic keyword extraction")

# Russian media RSS feeds (EXPANDED)
RSS_SOURCES = {
    'TASS': 'https://tass.com/rss/v2.xml',
    'RIA Novosti': 'https://ria.ru/export/rss2/archive/index.xml',
    'Interfax': 'https://www.interfax.ru/rss.asp',
    'RT': 'https://www.rt.com/rss/',
    'RT News': 'https://www.rt.com/rss/news/',
    'RT Russia': 'https://www.rt.com/rss/russia/',
    'RT Business': 'https://www.rt.com/rss/business/',
    'Kommersant': 'https://www.kommersant.ru/RSS/main.xml',
    'Kommersant Politics': 'https://www.kommersant.ru/RSS/politics.xml',
    'Kommersant Economics': 'https://www.kommersant.ru/RSS/economics.xml',
    'TASS Politics': 'https://tass.com/politics/rss',
    'TASS Economy': 'https://tass.com/economy/rss',
    'TASS World': 'https://tass.com/world/rss',
}

# Note: Removed duplicate 'TASS English' which was same URL as 'TASS'

def fetch_feed(url, source_name, max_articles=50, retries=2):
    """
    Fetch and parse RSS feed with retries.

    Args:
        url: RSS feed URL
        source_name: Name of source
        max_articles: Maximum articles to fetch
        retries: Number of retry attempts

    Returns:
        List of article dicts, or empty list on failure
    """
    import time

    for attempt in range(retries + 1):
        try:
            # Set user agent to avoid blocks
            feedparser.USER_AGENT = "Eastbound Reports RSS Monitor/1.0"

            # Note: feedparser.parse() doesn't accept timeout parameter in all versions
            # It uses urllib internally which has default timeout handling
            feed = feedparser.parse(url)

            # Check if feed parsed successfully
            if hasattr(feed, 'bozo_exception') and feed.bozo:
                raise Exception(f"Feed parsing error: {feed.bozo_exception}")

            articles = []

            # Fetch up to max_articles
            for entry in feed.entries[:max_articles]:
                # Validate entry has minimum required fields
                if not entry.get('title') or not entry.get('link'):
                    continue

                articles.append({
                    'source': source_name,
                    'title': entry.get('title', '').strip(),
                    'link': entry.get('link', '').strip(),
                    'published': entry.get('published', ''),
                    'summary': entry.get('summary', '')[:1000],
                })

            if len(articles) == 0 and len(feed.entries) == 0:
                raise Exception(f"No articles found in feed")

            return articles

        except Exception as e:
            if attempt < retries:
                wait_time = 2 ** attempt  # Exponential backoff
                print(f"    [RETRY] {source_name} failed (attempt {attempt + 1}/{retries + 1}), waiting {wait_time}s: {e}")
                time.sleep(wait_time)
            else:
                print(f"    [ERROR] {source_name}: {e}")
                return []

    return []

def extract_keywords(text):
    """Extract key terms (unigrams) and important phrases (bigrams) from text."""
    text = text.lower()
    words = re.findall(r'\b\w{4,}\b', text)

    # Comprehensive stopword list
    stopwords = {
        # Common English words
        'this', 'that', 'with', 'from', 'have', 'been', 'will', 'said', 'says',
        'more', 'about', 'after', 'their', 'which', 'when', 'where', 'there',
        'what', 'some', 'than', 'into', 'very', 'just', 'over', 'also', 'only',
        'many', 'most', 'such', 'other', 'would', 'could', 'should', 'these',
        'those', 'them', 'then', 'both', 'each', 'does', 'were', 'make', 'made',

        # Generic Russian media words
        'russia', 'russian', 'moscow', 'kremlin', 'media', 'tass', 'reported',
        'reports', 'according', 'statement', 'official', 'officials', 'news',
        'world', 'national', 'international', 'chief', 'head', 'minister',
        'president', 'government', 'country', 'state', 'says', 'told', 'plan',
        'plans', 'year', 'years', 'talks', 'meeting', 'held', 'announced',
        'military', 'report', 'full', 'political', 'economic', 'social',
        'foreign', 'domestic', 'federal', 'regional', 'local', 'global'
    }

    # Filter unigrams (single words)
    keywords = []
    for word in words:
        # Skip stopwords
        if word in stopwords:
            continue

        # Skip years (1900-2099)
        if re.match(r'^(19|20)\d{2}$', word):
            continue

        # Skip pure numbers
        if word.isdigit():
            continue

        keywords.append(word)

    # Extract bigrams (2-word phrases) - captures names, places, compound terms
    bigrams = []
    for i in range(len(words) - 1):
        word1, word2 = words[i], words[i+1]

        # Skip if either word is a stopword
        if word1 in stopwords or word2 in stopwords:
            continue

        # Skip if either is a year or number
        if re.match(r'^(19|20)\d{2}$', word1) or re.match(r'^(19|20)\d{2}$', word2):
            continue
        if word1.isdigit() or word2.isdigit():
            continue

        # Create bigram
        bigram = f"{word1} {word2}"
        bigrams.append(bigram)

    # Combine unigrams and bigrams, prioritizing bigrams
    return bigrams + keywords

def identify_trending_stories(all_articles, use_tfidf=True):
    """
    Identify stories covered by multiple sources.

    Args:
        all_articles: List of article dicts
        use_tfidf: Whether to use TF-IDF scoring (more sophisticated)

    Returns:
        List of trending story dicts with keywords, source counts, and articles
    """
    if use_tfidf and TFIDF_AVAILABLE:
        # Enhanced TF-IDF approach
        print("  [TFIDF] Using TF-IDF keyword extraction...")

        # Get TF-IDF keywords and bigrams
        tfidf_keywords = extract_tfidf_keywords(all_articles, top_n=50, min_df=2)
        tfidf_bigrams = extract_bigram_tfidf(all_articles, top_n=30, min_df=2)

        # Combine and normalize scores
        tfidf_terms = {}
        max_score = max([score for _, score in tfidf_keywords + tfidf_bigrams]) if (tfidf_keywords + tfidf_bigrams) else 1

        for term, score in tfidf_keywords + tfidf_bigrams:
            tfidf_terms[term] = score / max_score  # Normalize to 0-1

        print(f"  [TFIDF] Extracted {len(tfidf_terms)} significant terms")

        # Map terms back to articles
        keyword_counts = defaultdict(list)

        for article in all_articles:
            text = (article['title'] + ' ' + article['summary']).lower()

            # Check which TF-IDF terms appear in this article
            for term in tfidf_terms.keys():
                if term in text:
                    keyword_counts[term].append(article)

        # Build trending stories with combined scoring
        trending = {}
        for keyword, articles in keyword_counts.items():
            sources = set(a['source'] for a in articles)

            # Require at least 3 sources (multi-source verification)
            if len(sources) >= 3:
                # Combined score: TF-IDF score * source count
                tfidf_score = tfidf_terms[keyword]
                combined_score = tfidf_score * len(sources)

                trending[keyword] = {
                    'keyword': keyword,
                    'source_count': len(sources),
                    'tfidf_score': round(tfidf_score, 4),
                    'combined_score': round(combined_score, 4),
                    'articles': articles[:10]
                }

        # Sort by combined score (TF-IDF importance * source coverage)
        sorted_trending = sorted(trending.values(), key=lambda x: x['combined_score'], reverse=True)

    else:
        # Fallback: Basic keyword extraction
        print("  [BASIC] Using basic keyword extraction...")

        keyword_counts = defaultdict(list)

        for article in all_articles:
            keywords = extract_keywords(article['title'] + ' ' + article['summary'])
            for keyword in set(keywords):  # Unique keywords per article
                keyword_counts[keyword].append(article)

        # Find keywords mentioned by multiple sources
        trending = {}
        for keyword, articles in keyword_counts.items():
            sources = set(a['source'] for a in articles)
            if len(sources) >= 3:  # Covered by 3+ sources (more significant)
                if keyword not in trending or len(sources) > len(set(a['source'] for a in trending[keyword]['articles'])):
                    trending[keyword] = {
                        'keyword': keyword,
                        'source_count': len(sources),
                        'articles': articles[:10]  # Top 10 articles per trending topic (increased from 5)
                    }

        # Sort by source count (most covered)
        sorted_trending = sorted(trending.values(), key=lambda x: x['source_count'], reverse=True)

    return sorted_trending[:10]  # Top 10 trending topics (increased from 5)

def create_briefing(trending_stories, all_articles):
    """Create a briefing document with EXPANDED coverage."""
    today = datetime.now().strftime('%Y-%m-%d')

    briefing = {
        'date': today,
        'generated_at': datetime.now().isoformat(),
        'total_articles_scanned': len(all_articles),
        'trending_stories': trending_stories,
        'top_headlines': all_articles[:50],  # Top 50 overall (increased from 15)
        'all_articles': all_articles  # Include EVERYTHING for AI to analyze
    }

    return briefing

def deduplicate_articles(articles):
    """Remove duplicate articles based on URL and fuzzy title similarity."""
    from difflib import SequenceMatcher

    seen_urls = set()
    seen_titles = []  # Changed to list for fuzzy matching
    unique_articles = []
    duplicates = 0

    def title_similarity(title1, title2):
        """Calculate similarity ratio between two titles."""
        return SequenceMatcher(None, title1, title2).ratio()

    for article in articles:
        url = article.get('link', '')
        title = article.get('title', '').lower().strip()

        # Skip if we've seen this exact URL
        if url and url in seen_urls:
            duplicates += 1
            continue

        # Check for fuzzy title match (85% similarity threshold)
        is_duplicate = False
        if title:
            for seen_title in seen_titles:
                if title_similarity(title, seen_title) > 0.85:
                    duplicates += 1
                    is_duplicate = True
                    break

        if is_duplicate:
            continue

        # Add to unique set
        if url:
            seen_urls.add(url)
        if title:
            seen_titles.append(title)
        unique_articles.append(article)

    return unique_articles, duplicates

def main():
    from concurrent.futures import ThreadPoolExecutor, as_completed

    parser = argparse.ArgumentParser(description='Monitor Russian media sources')
    parser.add_argument('--output', required=True, help='Output JSON file path')
    parser.add_argument('--parallel', action='store_true', help='Use parallel fetching (faster)')
    args = parser.parse_args()

    print("[RSS] Monitoring Russian media sources...")

    all_articles = []

    if args.parallel:
        # Parallel fetching (much faster!)
        print("  [PARALLEL] Fetching feeds in parallel...")
        with ThreadPoolExecutor(max_workers=5) as executor:
            future_to_source = {
                executor.submit(fetch_feed, url, source_name, 50): source_name
                for source_name, url in RSS_SOURCES.items()
            }

            for future in as_completed(future_to_source):
                source_name = future_to_source[future]
                try:
                    articles = future.result()
                    all_articles.extend(articles)
                    print(f"    [OK] {source_name}: {len(articles)} articles")
                except Exception as e:
                    print(f"    [ERROR] {source_name}: {e}")
    else:
        # Sequential fetching (original)
        for source_name, url in RSS_SOURCES.items():
            print(f"  Fetching {source_name}...")
            articles = fetch_feed(url, source_name, max_articles=50)
            all_articles.extend(articles)
            print(f"    [OK] Found {len(articles)} articles")

    print(f"\n[STATS] Total articles fetched: {len(all_articles)}")

    # Deduplicate within this digest
    print("[DEDUP] Removing duplicates within digest...")
    all_articles, dup_count = deduplicate_articles(all_articles)
    print(f"  [OK] Removed {dup_count} duplicates")
    print(f"  [OK] {len(all_articles)} unique articles remaining")

    # Ensure minimum viable article count
    MIN_ARTICLES = 50
    if len(all_articles) < MIN_ARTICLES:
        print(f"\n[ERROR] Insufficient articles ({len(all_articles)} < {MIN_ARTICLES} minimum)")
        print(f"[ERROR] System requires at least {MIN_ARTICLES} articles for quality analysis")
        print(f"[ERROR] This may indicate RSS feed failures or network issues")
        sys.exit(1)

    print("\n[SEARCH] Identifying trending stories...")
    trending = identify_trending_stories(all_articles)
    print(f"  [OK] Found {len(trending)} trending topics")

    briefing = create_briefing(trending, all_articles)

    # Save briefing
    with open(args.output, 'w', encoding='utf-8') as f:
        json.dump(briefing, f, indent=2, ensure_ascii=False)

    print(f"\n[OK] Briefing saved to: {args.output}")

    # Print summary
    print("\n[SUMMARY] Top trending stories:")
    for i, story in enumerate(trending[:3], 1):
        print(f"\n{i}. Keyword: {story['keyword']}")
        print(f"   Sources: {story['source_count']}")
        for article in story['articles'][:2]:
            print(f"   - {article['source']}: {article['title'][:80]}...")

if __name__ == '__main__':
    main()
