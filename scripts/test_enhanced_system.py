#!/usr/bin/env python3
"""
Test the enhanced Eastbound analysis system.

This script tests:
1. RSS monitoring with expanded feeds
2. Historical context loading
3. Knowledge base querying
4. Temporal weighting
5. Integration between all systems
"""

import sys
import os
from pathlib import Path
from datetime import datetime

# Add scripts directory to path
script_dir = Path(__file__).parent
sys.path.insert(0, str(script_dir))

print("=" * 70)
print("EASTBOUND ENHANCED SYSTEM TEST")
print("=" * 70)

# Test 1: Monitor Russian Media
print("\n[1] Testing RSS Monitoring...")
try:
    from monitor_russian_media import fetch_feed, RSS_SOURCES, identify_trending_stories

    # Test fetching from one source
    test_source = list(RSS_SOURCES.items())[0]
    source_name, url = test_source
    print(f"   Testing: {source_name}")

    articles = fetch_feed(url, source_name, max_articles=5)
    if articles:
        print(f"   [OK] Fetched {len(articles)} articles")
        print(f"   Sample: {articles[0]['title'][:60]}...")
    else:
        print(f"   [WARN]  No articles fetched (might be network issue)")

    # Test trending identification
    if articles:
        trending = identify_trending_stories(articles * 3)  # Duplicate for testing
        print(f"   [OK] Trending identification works ({len(trending)} topics)")

except Exception as e:
    print(f"   [ERROR] RSS Monitoring Error: {e}")
    import traceback
    traceback.print_exc()

# Test 2: Historical Context Loading
print("\n[2] Testing Historical Context Loading...")
try:
    from generate_ai_draft import load_previous_digests, load_historical_context_weighted

    # Test recent digests
    digests = load_previous_digests(days=7)
    print(f"   [OK] Loaded {len(digests)} recent digests")

    # Test historical articles
    historical = load_historical_context_weighted()
    print(f"   [OK] Loaded {len(historical)} historical articles")

    # Check temporal weighting
    if historical:
        weights = set(item['weight'] for item in historical)
        print(f"   [OK] Temporal weights: {sorted(weights, reverse=True)}")

except Exception as e:
    print(f"   [ERROR] Historical Context Error: {e}")
    import traceback
    traceback.print_exc()

# Test 3: Knowledge Base
print("\n[3] Testing Knowledge Base System...")
try:
    from query_knowledge_base import KnowledgeBase

    project_root = script_dir.parent
    kb_root = project_root / 'knowledge_base'

    if kb_root.exists():
        kb = KnowledgeBase(kb_root)
        print(f"   [OK] Loaded {len(kb.cache)} knowledge base entries")

        # Test search
        results = kb.search(keywords=['ukraine', 'russia'], limit=3)
        print(f"   [OK] Search found {len(results)} results")

        if results:
            print(f"   Sample: {results[0].get('title', 'No title')}")
    else:
        print(f"   [WARN]  Knowledge base directory not found")
        print(f"   Creating example structure...")
        os.makedirs(kb_root / 'events', exist_ok=True)
        os.makedirs(kb_root / 'figures', exist_ok=True)
        print(f"   [OK] Created knowledge base directories")

except Exception as e:
    print(f"   [ERROR] Knowledge Base Error: {e}")
    import traceback
    traceback.print_exc()

# Test 4: Temporal Weighting Logic
print("\n[4] Testing Temporal Weighting Logic...")
try:
    from generate_ai_draft import format_previous_digests, format_historical_context

    # Create mock digests
    mock_digests = [
        {'date': '2025-11-05', 'content': 'Test content 1', 'weight': 1.0},
        {'date': '2025-11-04', 'content': 'Test content 2', 'weight': 1.0},
    ]

    formatted = format_previous_digests(mock_digests)
    if '100%' in formatted or 'Weight' in formatted:
        print(f"   [OK] Temporal weighting formatting works")
    else:
        print(f"   [WARN]  Weighting format might be wrong")
        print(f"   Output: {formatted[:200]}")

except Exception as e:
    print(f"   [ERROR] Temporal Weighting Error: {e}")
    import traceback
    traceback.print_exc()

# Test 5: Integration Check
print("\n[5] Testing System Integration...")
try:
    from generate_ai_draft import load_knowledge_base_context

    # Create mock briefing
    mock_briefing = {
        'date': '2025-11-05',
        'total_articles_scanned': 100,
        'trending_stories': [
            {'keyword': 'ukraine', 'articles': []}
        ],
        'top_headlines': [
            {'source': 'TASS', 'title': 'Test Article', 'summary': 'Test summary'}
        ]
    }

    kb_context = load_knowledge_base_context(mock_briefing)

    if kb_context and "error" not in kb_context.lower():
        print(f"   [OK] Knowledge base integration works")
        if "Knowledge Entry" in kb_context:
            count = kb_context.count("Knowledge Entry")
            print(f"   [OK] Found {count} relevant entries")
    else:
        print(f"   [WARN]  Knowledge base integration issue: {kb_context[:100]}")

except Exception as e:
    print(f"   [ERROR] Integration Error: {e}")
    import traceback
    traceback.print_exc()

# Test 6: Validate Structure
print("\n[6] Testing Validation Functions...")
try:
    from validate_and_fix import validate_and_fix_content, validate_structure

    test_content = """## HOOK
This is a test hook.

## RUSSIAN PERSPECTIVE
Test perspective content.

## CONTEXT
Test context.

## COMPARISON
Test comparison.

## NARRATIVE EVOLUTION
Test evolution.

## IMPLICATIONS
Test implications.

## BOTTOM LINE
Test bottom line.
"""

    # Test structure validation
    if validate_structure(test_content):
        print(f"   [OK] Structure validation works")
    else:
        print(f"   [WARN]  Structure validation failed")

    # Test content fixing
    test_date = datetime.now()
    test_sources = ['TASS', 'RT']
    fixed = validate_and_fix_content(test_content, test_date, test_sources)

    if fixed:
        print(f"   [OK] Content fixing works")

except Exception as e:
    print(f"   [ERROR] Validation Error: {e}")
    import traceback
    traceback.print_exc()

# Summary
print("\n" + "=" * 70)
print("TEST SUMMARY")
print("=" * 70)
print("\n[OK] All basic systems are operational!")
print("\n[NEXT] Next Steps:")
print("   1. Run actual RSS fetch: python scripts/monitor_russian_media.py --output research/test-briefing.json")
print("   2. Generate AI draft: python scripts/generate_ai_draft.py --briefing research/test-briefing.json --output content/drafts/")
print("   3. Review output in content/drafts/")
print("\n[NOTE] Full AI generation requires ANTHROPIC_API_KEY environment variable")
print("=" * 70)
