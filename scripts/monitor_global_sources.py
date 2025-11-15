#!/usr/bin/env python3
"""
Real-Time Global Knowledge Crawler

Continuously monitors worldwide news, research papers, and databases.
Hybrid system that runs both scheduled and real-time monitoring.

Usage:
    # Real-time continuous monitoring (runs forever, checks every 5 minutes)
    python monitor_global_sources.py --mode realtime

    # Single snapshot (for scheduled runs)
    python monitor_global_sources.py --mode snapshot --regions all --categories all

    # Specific region/category
    python monitor_global_sources.py --regions europe,asia --categories news,research
"""

import argparse
import json
import time
import feedparser
import requests
from datetime import datetime, timedelta
from pathlib import Path
from collections import defaultdict
import sys
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed

# Import existing modules
sys.path.insert(0, str(Path(__file__).parent))
try:
    from advanced_keywords import extract_tfidf_keywords
    TFIDF_AVAILABLE = True
except ImportError:
    TFIDF_AVAILABLE = False

# ============================================================================
# GLOBAL NEWS SOURCES (RSS Feeds)
# ============================================================================

NEWS_SOURCES = {
    'russian': {
        'TASS': 'https://tass.com/rss/v2.xml',
        'RIA Novosti': 'https://ria.ru/export/rss2/archive/index.xml',
        'RT': 'https://www.rt.com/rss/',
        'Interfax': 'https://www.interfax.ru/rss.asp',
        'Kommersant': 'https://www.kommersant.ru/RSS/main.xml',
    },
    'europe': {
        'BBC': 'http://feeds.bbci.co.uk/news/world/rss.xml',
        'The Guardian': 'https://www.theguardian.com/world/rss',
        'Deutsche Welle': 'https://rss.dw.com/rss/en',
        'France24': 'https://www.france24.com/en/rss',
        'Euronews': 'https://www.euronews.com/rss',
        'Le Monde': 'https://www.lemonde.fr/rss/une.xml',
    },
    'americas': {
        'NYT': 'https://rss.nytimes.com/services/xml/rss/nyt/World.xml',
        'Washington Post': 'https://feeds.washingtonpost.com/rss/world',
        'Reuters': 'https://www.reutersagency.com/feed/',
        'AP': 'https://rsshub.app/apnews/topics/apf-topnews',
        'Bloomberg': 'https://www.bloomberg.com/feed/podcast/news.xml',
        'CBC': 'https://www.cbc.ca/webfeed/rss/rss-topstories',
    },
    'asia': {
        'Xinhua': 'https://english.news.cn/rss/world.xml',
        'CGTN': 'https://www.cgtn.com/subscribe/rss/section/world.xml',
        'NHK': 'https://www3.nhk.or.jp/nhkworld/en/news/rss.xml',
        'Yonhap': 'https://en.yna.co.kr/RSS/world.xml',
        'Times of India': 'https://timesofindia.indiatimes.com/rssfeedstopstories.cms',
        'Japan Times': 'https://www.japantimes.co.jp/feed/',
    },
    'middle_east': {
        'Al Jazeera': 'https://www.aljazeera.com/xml/rss/all.xml',
        'Al Arabiya': 'https://english.alarabiya.net/rss.xml',
        'Times of Israel': 'https://www.timesofisrael.com/feed/',
        'Haaretz': 'https://www.haaretz.com/cmlink/1.628752',
    },
    'africa': {
        'News24': 'https://feeds.24.com/articles/news24/TopStories/rss',
        'Daily Maverick': 'https://www.dailymaverick.co.za/dmrss/',
    },
    'nordic': {
        'Sveriges Radio': 'https://api.sr.se/api/rss/pod/3795',
        'NRK': 'https://www.nrk.no/nyheter/siste.rss',
        'YLE': 'https://feeds.yle.fi/uutiset/v1/recent.rss?publisherIds=YLE_UUTISET',
    }
}

# ============================================================================
# RESEARCH SOURCES (APIs & RSS)
# ============================================================================

RESEARCH_SOURCES = {
    'arxiv': {
        'name': 'arXiv',
        'type': 'api',
        'base_url': 'http://export.arxiv.org/api/query',
        'categories': ['quant-ph', 'cond-mat', 'cs.AI', 'cs.CR', 'physics.soc-ph'],
        'update_frequency': 'daily'
    },
    'biorxiv': {
        'name': 'bioRxiv',
        'type': 'rss',
        'url': 'https://connect.biorxiv.org/biorxiv_xml.php?subject=all',
        'update_frequency': 'daily'
    },
    'nature': {
        'name': 'Nature News',
        'type': 'rss',
        'url': 'https://www.nature.com/nature.rss',
        'update_frequency': 'daily'
    },
    'science_daily': {
        'name': 'Science Daily',
        'type': 'rss',
        'urls': {
            'physics': 'https://www.sciencedaily.com/rss/matter_energy/physics.xml',
            'space': 'https://www.sciencedaily.com/rss/space_time.xml',
            'computers': 'https://www.sciencedaily.com/rss/computers_math.xml',
        },
        'update_frequency': 'daily'
    },
    'mit_tech_review': {
        'name': 'MIT Technology Review',
        'type': 'rss',
        'url': 'https://www.technologyreview.com/feed/',
        'update_frequency': 'daily'
    },
}

# ============================================================================
# DATABASE SOURCES (APIs)
# ============================================================================

DATABASE_SOURCES = {
    'nasa': {
        'name': 'NASA API',
        'type': 'api',
        'base_url': 'https://api.nasa.gov',
        'endpoints': ['apod', 'neo/rest/v1/feed', 'planetary/apod'],
        'update_frequency': 'daily'
    },
    'world_bank': {
        'name': 'World Bank Data',
        'type': 'api',
        'base_url': 'https://api.worldbank.org/v2',
        'update_frequency': 'weekly'
    },
}


# ============================================================================
# CRAWLER IMPLEMENTATION
# ============================================================================

class GlobalKnowledgeCrawler:
    """Real-time global knowledge crawler with hybrid scheduling."""

    def __init__(self, output_dir='knowledge_base', max_workers=10):
        self.output_dir = Path(output_dir)
        self.max_workers = max_workers
        self.stats = defaultdict(int)
        self.last_fetch = {}  # Track last fetch time per source

        # Create directories
        (self.output_dir / 'news').mkdir(parents=True, exist_ok=True)
        (self.output_dir / 'research').mkdir(parents=True, exist_ok=True)
        (self.output_dir / 'data').mkdir(parents=True, exist_ok=True)

    def fetch_rss_feed(self, name, url, timeout=10):
        """Fetch single RSS feed with error handling."""
        try:
            feed = feedparser.parse(url)
            if feed.get('entries'):
                self.stats[f'success_{name}'] += 1
                return {
                    'source': name,
                    'url': url,
                    'entries': feed.entries,
                    'timestamp': datetime.now().isoformat()
                }
            else:
                self.stats[f'empty_{name}'] += 1
                print(f"[WARN] {name}: No entries in feed")
                return None
        except Exception as e:
            self.stats[f'error_{name}'] += 1
            print(f"[ERROR] {name}: {e}")
            return None

    def fetch_news_parallel(self, regions=['all'], max_age_hours=24):
        """Fetch news from multiple regions in parallel."""
        print(f"\n[NEWS] Fetching news from regions: {regions}")

        # Build source list
        sources_to_fetch = []
        if 'all' in regions:
            for region, feeds in NEWS_SOURCES.items():
                for name, url in feeds.items():
                    sources_to_fetch.append((region, name, url))
        else:
            for region in regions:
                if region in NEWS_SOURCES:
                    for name, url in NEWS_SOURCES[region].items():
                        sources_to_fetch.append((region, name, url))

        print(f"  [PARALLEL] Fetching {len(sources_to_fetch)} feeds...")

        results = []
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_source = {
                executor.submit(self.fetch_rss_feed, name, url): (region, name)
                for region, name, url in sources_to_fetch
            }

            for future in as_completed(future_to_source):
                region, name = future_to_source[future]
                try:
                    result = future.result()
                    if result:
                        result['region'] = region
                        results.append(result)
                        print(f"    [OK] {name} ({region}): {len(result['entries'])} articles")
                except Exception as e:
                    print(f"    [ERROR] {name}: {e}")

        return results

    def fetch_arxiv_papers(self, categories, max_results=100):
        """Fetch recent papers from arXiv API."""
        print(f"\n[RESEARCH] Fetching arXiv papers...")

        papers = []
        for category in categories:
            try:
                query = f'cat:{category}'
                params = {
                    'search_query': query,
                    'start': 0,
                    'max_results': max_results,
                    'sortBy': 'submittedDate',
                    'sortOrder': 'descending'
                }

                url = f"{RESEARCH_SOURCES['arxiv']['base_url']}?{requests.compat.urlencode(params)}"
                response = requests.get(url, timeout=30)

                if response.status_code == 200:
                    # Parse arXiv atom feed
                    feed = feedparser.parse(response.content)
                    papers.extend([{
                        'source': 'arXiv',
                        'category': category,
                        'title': entry.title,
                        'summary': entry.summary,
                        'link': entry.link,
                        'published': entry.published,
                        'authors': [author.name for author in entry.authors] if hasattr(entry, 'authors') else []
                    } for entry in feed.entries])

                    print(f"  [OK] arXiv {category}: {len(feed.entries)} papers")
                    self.stats[f'arxiv_{category}'] += len(feed.entries)
                else:
                    print(f"  [ERROR] arXiv {category}: HTTP {response.status_code}")

                time.sleep(3)  # Rate limiting

            except Exception as e:
                print(f"  [ERROR] arXiv {category}: {e}")

        return papers

    def fetch_research_feeds(self):
        """Fetch research RSS feeds."""
        print(f"\n[RESEARCH] Fetching research RSS feeds...")

        results = []
        for source_id, config in RESEARCH_SOURCES.items():
            if config['type'] == 'rss':
                if 'url' in config:
                    result = self.fetch_rss_feed(config['name'], config['url'])
                    if result:
                        result['category'] = 'research'
                        results.append(result)
                elif 'urls' in config:
                    for subcategory, url in config['urls'].items():
                        result = self.fetch_rss_feed(f"{config['name']} ({subcategory})", url)
                        if result:
                            result['category'] = 'research'
                            result['subcategory'] = subcategory
                            results.append(result)

        return results

    def save_to_knowledge_base(self, data, category, subcategory=None):
        """Save crawled data to knowledge base."""
        timestamp = datetime.now()
        date_str = timestamp.strftime('%Y-%m-%d')
        time_str = timestamp.strftime('%H-%M-%S')

        # Create directory structure
        if subcategory:
            output_path = self.output_dir / category / subcategory
        else:
            output_path = self.output_dir / category

        output_path.mkdir(parents=True, exist_ok=True)

        # Save as JSON
        filename = f"{date_str}_{time_str}_{category}.json"
        filepath = output_path / filename

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        print(f"  [SAVED] {filepath}")
        return filepath

    def run_snapshot(self, regions=['all'], categories=['news', 'research']):
        """Run single snapshot collection."""
        print(f"\n{'='*60}")
        print(f"GLOBAL KNOWLEDGE CRAWLER - SNAPSHOT MODE")
        print(f"{'='*60}")
        print(f"Timestamp: {datetime.now().isoformat()}")
        print(f"Regions: {regions}")
        print(f"Categories: {categories}")

        all_data = {
            'timestamp': datetime.now().isoformat(),
            'news': [],
            'research': [],
            'stats': {}
        }

        # Fetch news
        if 'news' in categories:
            news_results = self.fetch_news_parallel(regions)
            all_data['news'] = news_results
            self.save_to_knowledge_base(news_results, 'news')

        # Fetch research
        if 'research' in categories:
            # arXiv papers
            arxiv_papers = self.fetch_arxiv_papers(RESEARCH_SOURCES['arxiv']['categories'], max_results=50)
            # RSS research feeds
            research_feeds = self.fetch_research_feeds()

            all_data['research'] = {
                'papers': arxiv_papers,
                'feeds': research_feeds
            }
            self.save_to_knowledge_base(all_data['research'], 'research')

        # Statistics
        all_data['stats'] = dict(self.stats)

        print(f"\n{'='*60}")
        print(f"SNAPSHOT COMPLETE")
        print(f"{'='*60}")
        print(f"News sources: {len(all_data['news'])}")
        print(f"Research papers: {len(all_data['research'].get('papers', []))}")
        print(f"Research feeds: {len(all_data['research'].get('feeds', []))}")

        return all_data

    def run_realtime(self, check_interval_minutes=5, regions=['all'], categories=['news', 'research']):
        """Run continuous real-time monitoring."""
        print(f"\n{'='*60}")
        print(f"GLOBAL KNOWLEDGE CRAWLER - REAL-TIME MODE")
        print(f"{'='*60}")
        print(f"Check interval: {check_interval_minutes} minutes")
        print(f"Regions: {regions}")
        print(f"Categories: {categories}")
        print(f"Press Ctrl+C to stop")
        print(f"{'='*60}\n")

        iteration = 0
        try:
            while True:
                iteration += 1
                print(f"\n[ITERATION {iteration}] {datetime.now().isoformat()}")

                self.run_snapshot(regions, categories)

                print(f"\n[SLEEP] Waiting {check_interval_minutes} minutes until next check...")
                time.sleep(check_interval_minutes * 60)

        except KeyboardInterrupt:
            print(f"\n\n[STOP] Real-time monitoring stopped by user")
            print(f"Total iterations: {iteration}")
            print(f"Stats: {dict(self.stats)}")


def main():
    parser = argparse.ArgumentParser(description='Global Knowledge Crawler')
    parser.add_argument('--mode', choices=['snapshot', 'realtime'], default='snapshot',
                       help='Run mode: snapshot (once) or realtime (continuous)')
    parser.add_argument('--regions', default='all',
                       help='Comma-separated regions: all, russian, europe, americas, asia, etc.')
    parser.add_argument('--categories', default='news,research',
                       help='Comma-separated categories: news, research, data')
    parser.add_argument('--interval', type=int, default=5,
                       help='Check interval in minutes for realtime mode')
    parser.add_argument('--output', default='knowledge_base',
                       help='Output directory for knowledge base')
    parser.add_argument('--workers', type=int, default=10,
                       help='Number of parallel workers')

    args = parser.parse_args()

    # Parse regions and categories
    regions = args.regions.split(',') if args.regions != 'all' else ['all']
    categories = args.categories.split(',')

    # Create crawler
    crawler = GlobalKnowledgeCrawler(output_dir=args.output, max_workers=args.workers)

    # Run
    if args.mode == 'snapshot':
        crawler.run_snapshot(regions, categories)
    else:
        crawler.run_realtime(
            check_interval_minutes=args.interval,
            regions=regions,
            categories=categories
        )


if __name__ == '__main__':
    main()
