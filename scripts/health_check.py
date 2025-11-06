#!/usr/bin/env python3
"""
Health check for Eastbound automated system.

Checks:
- RSS feeds accessibility
- Recent briefing generation
- Draft creation
- Knowledge base availability
- Historical context availability

Usage:
    python health_check.py
"""

import json
import sys
from pathlib import Path
from datetime import datetime, timedelta
import feedparser

def check_rss_feeds():
    """Test RSS feed accessibility."""
    print("\n[CHECK] Testing RSS feeds...")

    feeds = {
        'TASS': 'https://tass.com/rss/v2.xml',
        'RT': 'https://www.rt.com/rss/',
        'RIA Novosti': 'https://ria.ru/export/rss2/archive/index.xml',
    }

    working = 0
    failed = []

    for name, url in feeds.items():
        try:
            feed = feedparser.parse(url)
            if len(feed.entries) > 0:
                print(f"  [OK] {name}: {len(feed.entries)} articles")
                working += 1
            else:
                print(f"  [WARN] {name}: No articles found")
                failed.append(name)
        except Exception as e:
            print(f"  [ERROR] {name}: {e}")
            failed.append(name)

    return working, failed

def check_recent_briefings():
    """Check if briefings are being generated."""
    print("\n[CHECK] Recent briefing files...")

    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    research_dir = project_root / 'research'

    if not research_dir.exists():
        print("  [ERROR] Research directory not found")
        return False

    # Check for briefings in last 7 days
    cutoff = datetime.now() - timedelta(days=7)
    recent_briefings = []

    for briefing_file in research_dir.glob('*-briefing.json'):
        try:
            date_str = '-'.join(briefing_file.stem.split('-')[:3])
            briefing_date = datetime.strptime(date_str, '%Y-%m-%d')

            if briefing_date >= cutoff:
                # Check file size and validity
                with open(briefing_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    article_count = data.get('total_articles_scanned', 0)
                    recent_briefings.append({
                        'date': date_str,
                        'articles': article_count,
                        'file': briefing_file.name
                    })
        except Exception as e:
            print(f"  [WARN] Failed to parse {briefing_file.name}: {e}")

    if recent_briefings:
        print(f"  [OK] Found {len(recent_briefings)} recent briefings")
        for b in sorted(recent_briefings, key=lambda x: x['date'], reverse=True)[:3]:
            print(f"    - {b['date']}: {b['articles']} articles")
        return True
    else:
        print("  [WARN] No recent briefings found (last 7 days)")
        return False

def check_recent_drafts():
    """Check if drafts are being created."""
    print("\n[CHECK] Recent draft files...")

    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    drafts_dir = project_root / 'content' / 'drafts'

    if not drafts_dir.exists():
        print("  [ERROR] Drafts directory not found")
        return False

    # Check for drafts in last 7 days
    cutoff = datetime.now() - timedelta(days=7)
    recent_drafts = []

    for draft_file in drafts_dir.glob('*.md'):
        try:
            date_str = '-'.join(draft_file.stem.split('-')[:3])
            draft_date = datetime.strptime(date_str, '%Y-%m-%d')

            if draft_date >= cutoff:
                recent_drafts.append({
                    'date': date_str,
                    'file': draft_file.name
                })
        except Exception:
            continue

    if recent_drafts:
        print(f"  [OK] Found {len(recent_drafts)} recent drafts")
        for d in sorted(recent_drafts, key=lambda x: x['date'], reverse=True)[:3]:
            print(f"    - {d['date']}: {d['file']}")
        return True
    else:
        print("  [WARN] No recent drafts found (last 7 days)")
        return False

def check_knowledge_base():
    """Check if knowledge base is populated."""
    print("\n[CHECK] Knowledge Base status...")

    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    kb_root = project_root / 'knowledge_base'

    if not kb_root.exists():
        print("  [ERROR] Knowledge base directory not found")
        return False

    categories = ['events', 'figures', 'policies', 'narratives', 'context']
    total_entries = 0
    category_counts = {}

    for category in categories:
        category_dir = kb_root / category
        if category_dir.exists():
            count = len(list(category_dir.glob('*.json')))
            category_counts[category] = count
            total_entries += count

    if total_entries > 0:
        print(f"  [OK] Knowledge base has {total_entries} entries")
        for cat, count in category_counts.items():
            if count > 0:
                print(f"    - {cat}: {count}")
        return True
    else:
        print("  [WARN] Knowledge base is empty")
        return False

def check_published_posts():
    """Check recent published posts."""
    print("\n[CHECK] Recent published posts...")

    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    posts_dir = project_root / '_posts'

    if not posts_dir.exists():
        print("  [ERROR] Posts directory not found")
        return False

    # Check for posts in last 30 days
    cutoff = datetime.now() - timedelta(days=30)
    recent_posts = []

    for post_file in posts_dir.glob('*.md'):
        try:
            date_str = '-'.join(post_file.stem.split('-')[:3])
            post_date = datetime.strptime(date_str, '%Y-%m-%d')

            if post_date >= cutoff:
                recent_posts.append({
                    'date': date_str,
                    'file': post_file.name
                })
        except Exception:
            continue

    if recent_posts:
        print(f"  [OK] Found {len(recent_posts)} published posts (last 30 days)")
        for p in sorted(recent_posts, key=lambda x: x['date'], reverse=True)[:5]:
            print(f"    - {p['date']}: {p['file']}")
        return True
    else:
        print("  [WARN] No recent published posts (last 30 days)")
        return False

def main():
    print("=" * 70)
    print("EASTBOUND SYSTEM HEALTH CHECK")
    print("=" * 70)

    checks = {
        'RSS Feeds': check_rss_feeds,
        'Recent Briefings': check_recent_briefings,
        'Recent Drafts': check_recent_drafts,
        'Knowledge Base': check_knowledge_base,
        'Published Posts': check_published_posts
    }

    results = {}

    # Run all checks
    for check_name, check_func in checks.items():
        try:
            result = check_func()
            if isinstance(result, tuple):
                # RSS check returns (working, failed)
                results[check_name] = result[0] > 0
            else:
                results[check_name] = result
        except Exception as e:
            print(f"  [ERROR] Check failed: {e}")
            results[check_name] = False

    # Summary
    print("\n" + "=" * 70)
    print("HEALTH CHECK SUMMARY")
    print("=" * 70)

    passed = sum(1 for v in results.values() if v)
    total = len(results)

    for check_name, result in results.items():
        status = "[OK]" if result else "[FAIL]"
        print(f"{status} {check_name}")

    print(f"\nOverall: {passed}/{total} checks passed")

    if passed == total:
        print("\n[SUCCESS] All systems operational!")
        return 0
    elif passed >= total * 0.75:
        print("\n[WARNING] Some issues detected, but core systems working")
        return 0
    else:
        print("\n[CRITICAL] Multiple system failures detected!")
        return 1

if __name__ == '__main__':
    sys.exit(main())
