#!/usr/bin/env python3
"""Test the enhanced keyword extraction on today's briefing."""

import json
import sys
from pathlib import Path

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent))

from advanced_keywords import extract_enhanced_keywords, extract_tfidf_keywords, NER_AVAILABLE

# Load briefing
briefing_path = Path('research/2025-11-09-briefing.json')
if not briefing_path.exists():
    print(f"Briefing not found: {briefing_path}")
    sys.exit(1)

with open(briefing_path, encoding='utf-8') as f:
    briefing = json.load(f)

articles = []
for story in briefing.get('trending_stories', []):
    for article in story.get('articles', []):
        articles.append(article)

print(f"Loaded {len(articles)} articles from briefing\n")
print("=" * 60)

# Test old method
print("\nOLD METHOD (TF-IDF only):")
print("=" * 60)
old_keywords = extract_tfidf_keywords(articles, top_n=15)
for i, (keyword, score) in enumerate(old_keywords, 1):
    print(f"{i:2d}. {keyword:20s} (score: {score:.2f})")

# Test new method
print("\n\nNEW METHOD (Enhanced - NER + TF-IDF + Phrases + Boosting):")
print("=" * 60)
if not NER_AVAILABLE:
    print("[INFO] spaCy not installed - using TF-IDF + phrase extraction only")
    print("[INFO] Run 'scripts/install_spacy.bat' for full NER capabilities\n")

new_keywords = extract_enhanced_keywords(articles, top_n=15)
for i, (keyword, score, source) in enumerate(new_keywords, 1):
    source_label = {
        'entity': '[ENTITY]',
        'keyword': '[KEYWORD]',
        'phrase': '[PHRASE]'
    }.get(source, '[OTHER]')
    print(f"{i:2d}. {keyword:25s} {source_label:12s} (score: {score:.2f})")

print("\n" + "=" * 60)
print("\nKEY IMPROVEMENTS:")
print("- Named entities (people, places, orgs) are prioritized")
print("- Geopolitical terms get boosted scores")
print("- Meaningful phrases are extracted")
print("- Keywords from multiple methods are combined")
print("- Diversity bonus for appearing in multiple extraction methods")
