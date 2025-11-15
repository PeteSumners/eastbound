#!/usr/bin/env python3
"""
Query the Eastbound Knowledge Base for relevant historical context.

This module provides intelligent searching across events, figures, policies,
narratives, and context to enhance AI-generated analysis with factual grounding.

Usage:
    python query_knowledge_base.py --keywords "ukraine nato" --output context.json
"""

import argparse
import json
import re
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import glob


class KnowledgeBase:
    """Query and manage the Eastbound knowledge base."""

    def __init__(self, kb_root: Path):
        self.kb_root = kb_root
        self.cache = {}
        self._load_all_entries()

    def _load_all_entries(self):
        """Load all knowledge base entries into memory."""
        print("[KB] Loading knowledge base...")

        categories = ['events', 'figures', 'policies', 'narratives', 'context', 'analysis', 'science']

        for category in categories:
            category_dir = self.kb_root / category
            if not category_dir.exists():
                continue

            for json_file in category_dir.glob('*.json'):
                try:
                    with open(json_file, 'r', encoding='utf-8') as f:
                        entry = json.load(f)
                        entry_id = entry.get('id', json_file.stem)
                        self.cache[entry_id] = entry
                except Exception as e:
                    print(f"Warning: Failed to load {json_file}: {e}")

        print(f"  [OK] Loaded {len(self.cache)} entries")

    def search(self,
               keywords: List[str] = None,
               categories: List[str] = None,
               date_range: tuple = None,
               limit: int = 10) -> List[Dict]:
        """
        Search knowledge base for relevant entries.

        Args:
            keywords: List of keywords to search for
            categories: Filter by category (event, figure, policy, narrative, context)
            date_range: Tuple of (start_date, end_date) as strings "YYYY-MM-DD"
            limit: Maximum number of results

        Returns:
            List of matching entries, sorted by relevance
        """
        results = []

        for entry_id, entry in self.cache.items():
            score = 0

            # Category filter
            if categories and entry.get('category') not in categories:
                continue

            # Date range filter
            if date_range:
                entry_date = entry.get('date')
                if entry_date:
                    if not self._in_date_range(entry_date, date_range):
                        continue

            # Keyword matching
            if keywords:
                entry_text = json.dumps(entry).lower()
                for keyword in keywords:
                    keyword = keyword.lower()
                    # Count occurrences (weight by frequency)
                    count = entry_text.count(keyword)
                    score += count

                    # Bonus for title match
                    if keyword in entry.get('title', '').lower():
                        score += 10

                    # Bonus for summary match
                    if keyword in entry.get('summary', '').lower():
                        score += 5

            # Only include if we found keywords
            if keywords and score == 0:
                continue

            results.append({
                'entry': entry,
                'score': score
            })

        # Sort by relevance score
        results.sort(key=lambda x: x['score'], reverse=True)

        return [r['entry'] for r in results[:limit]]

    def get(self, entry_id: str) -> Optional[Dict]:
        """Get specific entry by ID."""
        return self.cache.get(entry_id)

    def get_related(self, entry_id: str) -> List[Dict]:
        """Get entries related to the given entry."""
        entry = self.get(entry_id)
        if not entry:
            return []

        related_ids = entry.get('related_entries', [])
        return [self.get(rid) for rid in related_ids if self.get(rid)]

    def get_by_date_proximity(self, target_date: str, limit: int = 5) -> List[Dict]:
        """Get entries close to a specific date."""
        target = datetime.strptime(target_date, '%Y-%m-%d')

        dated_entries = []
        for entry in self.cache.values():
            entry_date = entry.get('date')
            if entry_date and entry_date != 'ongoing':
                try:
                    date = datetime.strptime(entry_date, '%Y-%m-%d')
                    days_diff = abs((target - date).days)
                    dated_entries.append({
                        'entry': entry,
                        'days_diff': days_diff
                    })
                except:
                    continue

        dated_entries.sort(key=lambda x: x['days_diff'])
        return [e['entry'] for e in dated_entries[:limit]]

    def _in_date_range(self, entry_date: str, date_range: tuple) -> bool:
        """Check if entry date falls within range."""
        if entry_date == 'ongoing':
            return True

        try:
            entry_dt = datetime.strptime(entry_date, '%Y-%m-%d')
            start_dt = datetime.strptime(date_range[0], '%Y-%m-%d')
            end_dt = datetime.strptime(date_range[1], '%Y-%m-%d')
            return start_dt <= entry_dt <= end_dt
        except:
            return False


def extract_keywords_from_briefing(briefing: Dict) -> List[str]:
    """Extract relevant keywords from a media briefing."""
    keywords = set()

    # From trending stories
    for story in briefing.get('trending_stories', []):
        keywords.add(story.get('keyword', ''))

    # From article titles
    for article in briefing.get('top_headlines', [])[:20]:
        title = article.get('title', '').lower()

        # Extract significant words (4+ characters)
        words = re.findall(r'\b\w{4,}\b', title)
        keywords.update(words)

    # Common stopwords to remove
    stopwords = {'this', 'that', 'with', 'from', 'have', 'been',
                 'will', 'said', 'says', 'more', 'about', 'after',
                 'their', 'which', 'when', 'where', 'there'}

    return [k for k in keywords if k and k not in stopwords]


def query_for_current_briefing(briefing_path: str, kb_root: Path, limit: int = 5) -> Dict:
    """
    Query knowledge base for context relevant to current briefing.

    Args:
        briefing_path: Path to current briefing JSON
        kb_root: Root path to knowledge base
        limit: Max number of entries to return

    Returns:
        Dict with relevant knowledge base entries
    """
    # Load briefing
    with open(briefing_path, 'r', encoding='utf-8') as f:
        briefing = json.load(f)

    # Extract keywords
    keywords = extract_keywords_from_briefing(briefing)
    briefing_date = briefing.get('date')

    # Initialize knowledge base
    kb = KnowledgeBase(kb_root)

    # Search by keywords
    keyword_results = kb.search(keywords=keywords[:10], limit=limit)

    # Search by date proximity
    date_results = []
    if briefing_date:
        date_results = kb.get_by_date_proximity(briefing_date, limit=3)

    # Combine and deduplicate
    all_results = []
    seen_ids = set()

    for entry in keyword_results + date_results:
        entry_id = entry.get('id')
        if entry_id not in seen_ids:
            seen_ids.add(entry_id)
            all_results.append(entry)

    return {
        'briefing_date': briefing_date,
        'keywords_searched': keywords[:10],
        'total_entries_found': len(all_results),
        'relevant_entries': all_results[:limit]
    }


def format_for_ai_prompt(context: Dict) -> str:
    """Format knowledge base context for AI prompt."""
    text = "\n=== KNOWLEDGE BASE CONTEXT ===\n\n"

    text += f"Searched {len(context['keywords_searched'])} keywords from current briefing\n"
    text += f"Found {context['total_entries_found']} relevant historical entries\n\n"

    for i, entry in enumerate(context['relevant_entries'], 1):
        text += f"\n## Knowledge Entry {i}: {entry.get('title')}\n"
        text += f"Date: {entry.get('date')}\n"
        text += f"Category: {entry.get('category')}\n\n"

        text += f"**Summary:** {entry.get('summary', 'No summary')}\n\n"

        # Russian perspective
        russian = entry.get('russian_perspective', {})
        if isinstance(russian, dict):
            if 'official_narrative' in russian:
                text += f"**Russian Narrative:** {russian['official_narrative']}\n\n"

            if 'key_quotes' in russian:
                text += "**Key Quotes:**\n"
                for quote in russian['key_quotes'][:2]:
                    if isinstance(quote, dict):
                        text += f"- {quote.get('speaker', 'Unknown')}: \"{quote.get('quote', '')}\"\n"
                text += "\n"

        # Facts
        facts = entry.get('facts', {})
        if facts and isinstance(facts, dict):
            verified = facts.get('verified_claims', [])
            if verified:
                text += "**Verified Facts:**\n"
                for claim in verified[:3]:
                    text += f"- {claim}\n"
                text += "\n"

        # Related entries
        related = entry.get('related_entries', [])
        if related:
            text += f"**Related Topics:** {', '.join(related[:5])}\n\n"

        text += "---\n"

    text += "\n**IMPORTANT:** Use this knowledge base context to:\n"
    text += "1. Provide historical background for current narratives\n"
    text += "2. Compare current framing to past patterns\n"
    text += "3. Fact-check claims against verified information\n"
    text += "4. Identify recurring propaganda techniques\n"
    text += "5. Connect current events to broader historical context\n\n"

    return text


def main():
    parser = argparse.ArgumentParser(description='Query Eastbound knowledge base')
    parser.add_argument('--briefing', help='Path to current briefing JSON')
    parser.add_argument('--keywords', nargs='+', help='Keywords to search')
    parser.add_argument('--categories', nargs='+', help='Filter by categories')
    parser.add_argument('--date-range', nargs=2, help='Date range (start end)')
    parser.add_argument('--entry-id', help='Get specific entry by ID')
    parser.add_argument('--limit', type=int, default=5, help='Max results')
    parser.add_argument('--output', help='Output JSON file')
    parser.add_argument('--prompt-output', help='Output AI prompt text')

    args = parser.parse_args()

    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    kb_root = project_root / 'knowledge_base'

    kb = KnowledgeBase(kb_root)

    # Query based on briefing
    if args.briefing:
        print(f"[SEARCH] Querying knowledge base for briefing: {args.briefing}")
        context = query_for_current_briefing(args.briefing, kb_root, args.limit)

        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                json.dump(context, f, indent=2, ensure_ascii=False)
            print(f"[OK] Results saved to: {args.output}")

        if args.prompt_output:
            prompt_text = format_for_ai_prompt(context)
            with open(args.prompt_output, 'w', encoding='utf-8') as f:
                f.write(prompt_text)
            print(f"[OK] AI prompt saved to: {args.prompt_output}")

        # Print summary
        print(f"\n[STATS] Found {context['total_entries_found']} relevant entries:")
        for entry in context['relevant_entries']:
            print(f"  - {entry.get('title')} ({entry.get('date')})")

    # Query by keywords
    elif args.keywords:
        print(f"[SEARCH] Searching for keywords: {args.keywords}")
        results = kb.search(
            keywords=args.keywords,
            categories=args.categories,
            date_range=tuple(args.date_range) if args.date_range else None,
            limit=args.limit
        )

        print(f"\n[STATS] Found {len(results)} results:")
        for entry in results:
            print(f"  - {entry.get('title')} ({entry.get('category')}, {entry.get('date')})")

    # Get specific entry
    elif args.entry_id:
        entry = kb.get(args.entry_id)
        if entry:
            print(json.dumps(entry, indent=2, ensure_ascii=False))
        else:
            print(f"[ERROR] Entry not found: {args.entry_id}")

    else:
        print("[ERROR] Please specify --briefing, --keywords, or --entry-id")


if __name__ == '__main__':
    main()
