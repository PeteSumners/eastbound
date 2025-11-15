#!/usr/bin/env python3
"""
Extract knowledge base entries from published Eastbound analysis articles.

This script automatically converts published articles into structured knowledge
base entries, allowing the AI to reference its own previous analysis and build
on accumulated understanding of Russian media narratives over time.

Usage:
    python extract_knowledge_from_posts.py --input _posts/ --output knowledge_base/analysis/
    python extract_knowledge_from_posts.py --post _posts/2025-11-14-analysis.md
"""

import argparse
import json
import re
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional


def parse_frontmatter(content: str) -> tuple:
    """Extract frontmatter and body from markdown file."""
    if not content.startswith('---'):
        return {}, content

    parts = content.split('---', 2)
    if len(parts) < 3:
        return {}, content

    frontmatter_text = parts[1]
    body = parts[2].strip()

    # Parse YAML-like frontmatter
    frontmatter = {}
    for line in frontmatter_text.strip().split('\n'):
        if ':' in line:
            key, value = line.split(':', 1)
            key = key.strip()
            value = value.strip().strip('"\'[]')

            # Handle lists
            if key in ['categories', 'tags']:
                value = [v.strip() for v in value.split(',')]

            frontmatter[key] = value

    return frontmatter, body


def extract_key_narratives(body: str) -> List[str]:
    """Extract main narrative themes from article body."""
    narratives = []

    # Look for sections about Russian narratives/framing
    narrative_patterns = [
        r'Russian (?:media|state media|outlets?) (?:is|are) (?:framing|portraying|presenting|emphasizing) (.+?)(?:\.|,|\n)',
        r'(?:Moscow|Kremlin|Russian) narrative[s]? (?:about|on|regarding) (.+?)(?:\.|,|\n)',
        r'The (?:Russian|Kremlin|Moscow) (?:message|framing|emphasis) (?:is|focuses on) (.+?)(?:\.|,|\n)',
        r'Russian media[\'s]? (?:treatment|coverage|framing) of (.+?) (?:is|emphasizes|highlights)',
    ]

    for pattern in narrative_patterns:
        matches = re.findall(pattern, body, re.IGNORECASE)
        narratives.extend(matches[:3])  # Limit to 3 per pattern

    return narratives[:10]  # Max 10 narratives


def extract_key_quotes(body: str) -> List[Dict[str, str]]:
    """Extract quoted statements from Russian sources."""
    quotes = []

    # Pattern: "According to [source], 'quote'"
    pattern = r'According to ([^,]+?),\s+["\']([^"\']+?)["\']'
    matches = re.findall(pattern, body)

    for source, quote in matches[:5]:  # Limit to 5 quotes
        quotes.append({
            'source': source.strip(),
            'quote': quote.strip()
        })

    return quotes


def extract_sources_cited(body: str, frontmatter: Dict) -> List[str]:
    """Extract list of Russian media sources cited."""
    sources = set()

    # Common Russian sources
    common_sources = [
        'TASS', 'RT', 'RIA Novosti', 'Interfax', 'Sputnik',
        'Kommersant', 'Vedomosti', 'RBC', 'Izvestia', 'Pravda',
        'Kremlin.ru', 'MID Russia', 'ITAR-TASS'
    ]

    for source in common_sources:
        if source.lower() in body.lower():
            sources.add(source)

    return sorted(list(sources))


def extract_key_figures(body: str) -> List[str]:
    """Extract mentions of key political figures."""
    figures = set()

    # Common figures
    common_figures = [
        'Putin', 'Zelensky', 'Lavrov', 'Peskov', 'Zakharova',
        'Medvedev', 'Shoigu', 'Trump', 'Biden', 'Orban',
        'Macron', 'Scholz', 'Duda', 'Kallas'
    ]

    for figure in common_figures:
        if figure.lower() in body.lower():
            figures.add(figure)

    return sorted(list(figures))[:10]  # Max 10


def extract_key_topics(frontmatter: Dict, body: str) -> List[str]:
    """Extract main topics/keywords from article."""
    topics = set()

    # From tags
    if 'tags' in frontmatter:
        tags = frontmatter['tags']
        if isinstance(tags, list):
            topics.update(tags[:8])
        elif isinstance(tags, str):
            topics.update([t.strip() for t in tags.split(',')[:8]])

    # From categories
    if 'categories' in frontmatter:
        cats = frontmatter['categories']
        if isinstance(cats, list):
            topics.update(cats)
        elif isinstance(cats, str):
            topics.update([c.strip() for c in cats.split(',')])

    return sorted(list(topics))


def extract_western_comparison(body: str) -> Optional[str]:
    """Extract how Western media coverage differs."""
    # Look for comparison sections
    comparison_patterns = [
        r'## (?:What )?Western [Mm]edia (?:Misses|Coverage)(.*?)(?:##|\Z)',
        r'## Comparison (?:with|to) Western (?:Media|Coverage)(.*?)(?:##|\Z)',
        r'(?:Western|Anglo-American|U\.S\.) (?:media|coverage|outlets?).*?(?:tends to|focuses on|emphasizes)(.*?)(?:\.|$)'
    ]

    for pattern in comparison_patterns:
        match = re.search(pattern, body, re.DOTALL | re.IGNORECASE)
        if match:
            text = match.group(1).strip()
            # Return first paragraph
            first_para = text.split('\n\n')[0]
            return first_para[:500]  # Limit length

    return None


def create_knowledge_entry(post_path: Path, output_dir: Path) -> Optional[Path]:
    """Convert a published post into a knowledge base entry."""

    # Read post
    try:
        with open(post_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"[ERROR] Failed to read {post_path}: {e}")
        return None

    # Parse
    frontmatter, body = parse_frontmatter(content)

    if not frontmatter:
        print(f"[SKIP] No frontmatter in {post_path}")
        return None

    # Extract date from filename (YYYY-MM-DD-slug.md)
    date_match = re.match(r'(\d{4}-\d{2}-\d{2})', post_path.name)
    if not date_match:
        print(f"[SKIP] No date in filename {post_path.name}")
        return None

    date = date_match.group(1)

    # Create knowledge entry
    entry_id = f"analysis-{date}"

    entry = {
        "id": entry_id,
        "title": frontmatter.get('title', 'Untitled Analysis'),
        "date": date,
        "category": "analysis",
        "summary": frontmatter.get('excerpt', frontmatter.get('description', 'Russian media analysis')),
        "source_article": f"/_posts/{post_path.name}",

        "russian_perspective": {
            "key_narratives": extract_key_narratives(body),
            "key_quotes": extract_key_quotes(body),
            "sources_cited": extract_sources_cited(body, frontmatter),
            "media_framing": "See full article for detailed analysis",
        },

        "western_perspective": {
            "comparison": extract_western_comparison(body),
            "key_differences": "See article for Western vs Russian framing comparison"
        },

        "topics": extract_key_topics(frontmatter, body),
        "key_figures": extract_key_figures(body),

        "auto_generated": True,
        "generated_date": datetime.now().strftime('%Y-%m-%d'),

        "related_entries": [],  # Could be auto-populated by topic matching

        "metadata": {
            "author": frontmatter.get('author', 'Unknown'),
            "tags": frontmatter.get('tags', []),
            "categories": frontmatter.get('categories', [])
        }
    }

    # Create output directory
    output_dir.mkdir(parents=True, exist_ok=True)

    # Write JSON
    output_path = output_dir / f"{entry_id}.json"
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(entry, f, indent=2, ensure_ascii=False)

        print(f"[OK] Created knowledge entry: {output_path.name}")
        return output_path

    except Exception as e:
        print(f"[ERROR] Failed to write {output_path}: {e}")
        return None


def update_knowledge_base_categories(kb_root: Path):
    """Update knowledge base to include 'analysis' category."""

    # Check if science category exists
    science_dir = kb_root / 'science'
    if science_dir.exists():
        print(f"[OK] Science category exists with {len(list(science_dir.glob('*.json')))} entries")

    # Check if analysis category exists
    analysis_dir = kb_root / 'analysis'
    if not analysis_dir.exists():
        analysis_dir.mkdir(parents=True)
        print(f"[OK] Created analysis category directory")
    else:
        print(f"[OK] Analysis category exists with {len(list(analysis_dir.glob('*.json')))} entries")


def main():
    parser = argparse.ArgumentParser(description='Extract knowledge from published articles')
    parser.add_argument('--input', default='_posts/', help='Directory with published posts')
    parser.add_argument('--output', default='knowledge_base/analysis/', help='Output directory for knowledge entries')
    parser.add_argument('--post', help='Process single post file')
    parser.add_argument('--limit', type=int, help='Limit number of posts to process')
    parser.add_argument('--recent', type=int, help='Process only N most recent posts')

    args = parser.parse_args()

    # Resolve paths
    script_dir = Path(__file__).parent
    project_root = script_dir.parent

    if args.post:
        # Process single post
        post_path = Path(args.post)
        output_dir = project_root / args.output

        print(f"[PROCESS] Extracting knowledge from: {post_path.name}")
        create_knowledge_entry(post_path, output_dir)

    else:
        # Process all posts in directory
        posts_dir = project_root / args.input
        output_dir = project_root / args.output

        if not posts_dir.exists():
            print(f"[ERROR] Posts directory not found: {posts_dir}")
            return

        # Get all posts
        posts = sorted(posts_dir.glob('*.md'), key=lambda p: p.stat().st_mtime, reverse=True)

        if args.recent:
            posts = posts[:args.recent]
            print(f"[INFO] Processing {args.recent} most recent posts")

        if args.limit:
            posts = posts[:args.limit]

        print(f"[START] Processing {len(posts)} posts from {posts_dir}")

        # Ensure categories exist
        update_knowledge_base_categories(project_root / 'knowledge_base')

        # Process each post
        success_count = 0
        for post_path in posts:
            result = create_knowledge_entry(post_path, output_dir)
            if result:
                success_count += 1

        print(f"\n[DONE] Created {success_count}/{len(posts)} knowledge entries")
        print(f"[SAVED] Knowledge entries in: {output_dir}")


if __name__ == '__main__':
    main()
