#!/usr/bin/env python3
"""Show keyword extraction comparison - ASCII safe."""
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

# Extract keywords
old_keywords = extract_tfidf_keywords(articles, top_n=15)
new_keywords = extract_enhanced_keywords(articles, top_n=15)

# Save to file with UTF-8 encoding
with open('keyword_results.txt', 'w', encoding='utf-8') as f:
    f.write(f"\nAnalyzed {len(articles)} articles from today's briefing\n")
    f.write("="*70 + "\n\n")

    f.write("OLD METHOD (Basic TF-IDF):\n")
    f.write("-"*70 + "\n")
    for i, (keyword, score) in enumerate(old_keywords, 1):
        f.write(f"{i:2d}. {keyword:25s} score: {score:.2f}\n")

    f.write("\n\nNEW METHOD (Enhanced TF-IDF + Phrases + Boosting):\n")
    f.write("-"*70 + "\n")
    if not NER_AVAILABLE:
        f.write("NOTE: spaCy NER not available - using enhanced TF-IDF only\n\n")

    for i, (keyword, score, source) in enumerate(new_keywords, 1):
        source_label = {
            'entity': 'ENTITY',
            'keyword': 'KEYWORD',
            'phrase': 'PHRASE'
        }.get(source, 'OTHER')
        f.write(f"{i:2d}. {keyword:30s} [{source_label:7s}] score: {score:.2f}\n")

    f.write("\n" + "="*70 + "\n")
    f.write("KEY IMPROVEMENTS:\n")
    f.write("  * HTML/URLs stripped (no more 'https', 'article', 'preview')\n")
    f.write("  * Geopolitical terms boosted 1.5x (ukraine, nato, sanctions)\n")
    f.write("  * Meaningful 2-word phrases extracted\n")
    f.write("  * Multi-method combination with diversity bonus\n")

print("\nKeyword comparison saved to: keyword_results.txt")
print("Opening file...")
