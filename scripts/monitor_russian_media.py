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

# East Asian media RSS feeds - provides regional perspectives on Russian narratives
EAST_ASIA_SOURCES = {
    # China - State perspectives often align with or counter Russian narratives
    'CGTN': 'https://www.cgtn.com/subscribe/rss/section/world.xml',
    'Xinhua': 'https://english.news.cn/rss/world.xml',
    'Global Times': 'https://www.globaltimes.cn/rss/outbrain.xml',

    # Japan - Western-aligned perspective, often critical of Russian actions
    'NHK World': 'https://www3.nhk.or.jp/nhkworld/en/news/rss.xml',
    'The Japan Times': 'https://www.japantimes.co.jp/feed/',

    # South Korea - Balanced regional power perspective
    'Yonhap': 'https://en.yna.co.kr/RSS/world.xml',
    'Arirang News': 'https://www.arirang.com/xml/news_rss.xml',

    # Taiwan - Democratic perspective, often skeptical of authoritarian narratives
    'Focus Taiwan': 'https://focustaiwan.tw/rss/news/afav.xml',
    'Taipei Times': 'https://www.taipeitimes.com/xml/rss.xml',

    # North Korea - Provides rare perspective from DPRK (often pro-Russian)
    'KCNA': 'https://kcnawatch.org/feed/',
}

# Note: Removed duplicate 'TASS English' which was same URL as 'TASS'

def analyze_sentiment(text):
    """
    Simple sentiment analysis using keyword-based approach.

    Returns:
        tuple: (sentiment_label, sentiment_score)
        - sentiment_label: 'positive', 'negative', or 'neutral'
        - sentiment_score: float between -1.0 (very negative) and 1.0 (very positive)
    """
    text_lower = text.lower()

    # Positive keywords (weighted)
    positive_keywords = {
        'peace': 2, 'agreement': 2, 'cooperation': 2, 'success': 2, 'victory': 2,
        'growth': 1.5, 'development': 1.5, 'prosperity': 1.5, 'stability': 1.5,
        'positive': 1, 'good': 1, 'improved': 1, 'progress': 1, 'advanced': 1,
        'strong': 1, 'strengthening': 1, 'alliance': 1, 'partnership': 1,
    }

    # Negative keywords (weighted)
    negative_keywords = {
        'war': 2, 'conflict': 2, 'attack': 2, 'strike': 2, 'killed': 2, 'death': 2,
        'crisis': 1.5, 'threat': 1.5, 'danger': 1.5, 'sanctions': 1.5, 'violation': 1.5,
        'failed': 1, 'failure': 1, 'problem': 1, 'concern': 1, 'worried': 1,
        'accused': 1, 'condemned': 1, 'criticized': 1, 'protest': 1, 'opposition': 1,
    }

    # Count weighted occurrences
    positive_score = sum(weight for keyword, weight in positive_keywords.items() if keyword in text_lower)
    negative_score = sum(weight for keyword, weight in negative_keywords.items() if keyword in text_lower)

    # Calculate net sentiment
    total = positive_score + negative_score
    if total == 0:
        return 'neutral', 0.0

    net_score = (positive_score - negative_score) / total

    # Classify
    if net_score > 0.2:
        label = 'positive'
    elif net_score < -0.2:
        label = 'negative'
    else:
        label = 'neutral'

    return label, round(net_score, 3)


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

                # Analyze sentiment
                text_for_sentiment = entry.get('title', '') + ' ' + entry.get('summary', '')[:500]
                sentiment_label, sentiment_score = analyze_sentiment(text_for_sentiment)

                articles.append({
                    'source': source_name,
                    'title': entry.get('title', '').strip(),
                    'link': entry.get('link', '').strip(),
                    'published': entry.get('published', ''),
                    'summary': entry.get('summary', '')[:1000],
                    'sentiment': sentiment_label,
                    'sentiment_score': sentiment_score,
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
    """Create a briefing document with EXPANDED coverage and sentiment analysis."""
    today = datetime.now().strftime('%Y-%m-%d')

    # Calculate overall sentiment distribution
    sentiment_counts = {'positive': 0, 'negative': 0, 'neutral': 0}
    sentiment_scores = []

    for article in all_articles:
        sentiment = article.get('sentiment', 'neutral')
        sentiment_counts[sentiment] += 1
        sentiment_scores.append(article.get('sentiment_score', 0.0))

    avg_sentiment = sum(sentiment_scores) / len(sentiment_scores) if sentiment_scores else 0.0

    briefing = {
        'date': today,
        'generated_at': datetime.now().isoformat(),
        'total_articles_scanned': len(all_articles),
        'sentiment_analysis': {
            'distribution': sentiment_counts,
            'average_score': round(avg_sentiment, 3),
            'positive_percentage': round(100 * sentiment_counts['positive'] / len(all_articles), 1) if all_articles else 0,
            'negative_percentage': round(100 * sentiment_counts['negative'] / len(all_articles), 1) if all_articles else 0,
            'neutral_percentage': round(100 * sentiment_counts['neutral'] / len(all_articles), 1) if all_articles else 0,
        },
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

    parser = argparse.ArgumentParser(description='Monitor Russian and East Asian media sources')
    parser.add_argument('--output', required=True, help='Output JSON file path')
    parser.add_argument('--parallel', action='store_true', help='Use parallel fetching (faster)')
    parser.add_argument('--include-asia', action='store_true', help='Include East Asian news sources')
    args = parser.parse_args()

    print("[RSS] Monitoring Russian media sources...")

    all_articles = []

    # Combine Russian sources with Asian sources if requested
    sources_to_fetch = dict(RSS_SOURCES)
    if args.include_asia:
        print("[INFO] Including East Asian sources for regional perspective...")
        sources_to_fetch.update(EAST_ASIA_SOURCES)

    if args.parallel:
        # Parallel fetching (much faster!)
        print(f"  [PARALLEL] Fetching {len(sources_to_fetch)} feeds in parallel...")
        with ThreadPoolExecutor(max_workers=8) as executor:  # Increased from 5 to handle more sources
            future_to_source = {
                executor.submit(fetch_feed, url, source_name, 50): source_name
                for source_name, url in sources_to_fetch.items()
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
        for source_name, url in sources_to_fetch.items():
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

    # Print summary (with encoding safety for Windows console)
    try:
        print("\n[SUMMARY] Top trending stories:")
        for i, story in enumerate(trending[:3], 1):
            keyword = story['keyword'].encode('utf-8', errors='replace').decode('utf-8', errors='replace')
            print(f"\n{i}. Keyword: {keyword}")
            print(f"   Sources: {story['source_count']}")
            for article in story['articles'][:2]:
                title = article['title'][:80].encode('utf-8', errors='replace').decode('utf-8', errors='replace')
                print(f"   - {article['source']}: {title}...")

        # Print sentiment analysis summary
        print("\n[SENTIMENT] Overall sentiment distribution:")
        print(f"  Positive: {briefing['sentiment_analysis']['positive_percentage']}%")
        print(f"  Negative: {briefing['sentiment_analysis']['negative_percentage']}%")
        print(f"  Neutral:  {briefing['sentiment_analysis']['neutral_percentage']}%")
        print(f"  Average score: {briefing['sentiment_analysis']['average_score']:.3f} (-1.0 to 1.0)")

    except UnicodeEncodeError:
        print("\n[SUMMARY] Top trending stories saved to briefing (console encoding error prevented display)")

if __name__ == '__main__':
    main()
