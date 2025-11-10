#!/usr/bin/env python3
"""Demo of enhanced keyword extraction."""
import json
import sys
from pathlib import Path

sys.path.insert(0, 'scripts')
from advanced_keywords import extract_enhanced_keywords, extract_tfidf_keywords, NER_AVAILABLE

# Load briefing
with open('research/2025-11-09-briefing.json', encoding='utf-8') as f:
    briefing = json.load(f)

articles = []
for story in briefing.get('trending_stories', []):
    for article in story.get('articles', []):
        articles.append(article)

print(f"\nLoaded {len(articles)} articles from today's briefing\n")
print("="*70)

# Old method
print("\nOLD METHOD (Basic TF-IDF):")
print("-"*70)
old_keywords = extract_tfidf_keywords(articles, top_n=15)
old_list = []
for i, (keyword, score) in enumerate(old_keywords, 1):
    old_list.append(keyword)
    print(f"{i:2d}. {keyword:25s} score: {score:.2f}")

# New method
print("\n\nNEW METHOD (Enhanced TF-IDF + Phrases + Boosting):")
print("-"*70)
if not NER_AVAILABLE:
    print("NOTE: spaCy NER not available - using enhanced TF-IDF only\n")

new_keywords = extract_enhanced_keywords(articles, top_n=15)
new_list = []
for i, (keyword, score, source) in enumerate(new_keywords, 1):
    new_list.append(keyword)
    source_label = {
        'entity': 'ENTITY',
        'keyword': 'KEYWORD',
        'phrase': 'PHRASE'
    }.get(source, 'OTHER')
    print(f"{i:2d}. {keyword:30s} [{source_label:7s}] score: {score:.2f}")

# Comparison
print("\n" + "="*70)
print("COMPARISON:")
print("-"*70)

# What disappeared (good!)
disappeared = set(old_list) - set(new_list)
if disappeared:
    print(f"\nREMOVED (generic/noise): {', '.join(sorted(disappeared)[:10])}")

# What's new (good!)
appeared = set(new_list) - set(old_list)
if appeared:
    print(f"\nADDED (meaningful): {', '.join(sorted(appeared)[:10])}")

print("\n" + "="*70)
print("\nKEY IMPROVEMENTS:")
print("  - HTML/URLs stripped (no more 'https', 'article', 'preview')")
print("  - Geopolitical terms boosted 1.5x (ukraine, nato, sanctions)")
print("  - Meaningful 2-word phrases extracted (white house, peace talks)")
print("  - Multi-method combination with diversity bonus")
if not NER_AVAILABLE:
    print("\n  [Future] Add spaCy NER for entity extraction (Trump, Biden, etc)")
print()
