#!/usr/bin/env python3
"""
Generate draft post using Claude API from media briefing.

Usage:
    python generate_ai_draft.py --briefing research/briefing.json --output content/drafts/
"""

import argparse
import json
import os
from datetime import datetime, timedelta
from pathlib import Path
from anthropic import Anthropic
from validate_and_fix import validate_and_fix_content, validate_structure

# Import knowledge base query system
try:
    from query_knowledge_base import KnowledgeBase, extract_keywords_from_briefing, format_for_ai_prompt as format_kb_for_prompt
    KNOWLEDGE_BASE_AVAILABLE = True
except ImportError:
    KNOWLEDGE_BASE_AVAILABLE = False
    print("[WARN] Knowledge base module not available")

# Impartial analysis prompt for Claude
ANALYSIS_PROMPT = """You are an objective analyst for Eastbound Reports, an independent platform that translates and analyzes Russian media for English-speaking audiences.

TODAY'S DATE: {today_date}
CURRENT MONTH AND YEAR: {month_year}

IMPORTANT - DO NOT HALLUCINATE:
- The current date is {today_date}. Do NOT reference any other month or year in your headline.
- ONLY cite sources from the briefing below. Do NOT invent sources.
- Do NOT make up quotes. Only use information from the briefing.
- Do NOT reference events not mentioned in the briefing.

CRITICAL PRINCIPLES:
- Maintain complete objectivity and impartiality
- Do NOT take sides in geopolitical conflicts
- Do NOT endorse or condemn any narrative
- EXPLAIN Russian perspectives without validating them
- Acknowledge biases in all sources (Russian and Western)
- Use neutral, analytical language
- Cite sources accurately
- Focus on WHAT Russian media is saying, not whether it's true

PREVIOUS DIGESTS, HISTORICAL CONTEXT & KNOWLEDGE BASE (MULTI-LAYERED):
{previous_digests}

CONTEXTUAL LAYERS:
1. KNOWLEDGE BASE: Historical events, verified facts, past narrative patterns
2. RECENT DIGESTS (last 7 days): 100% weight - Most important recent analysis
3. HISTORICAL ARTICLES (last 90 days): Logarithmically weighted - Trend context
4. CURRENT BRIEFING: Today's coverage - PRIMARY analysis target

TEMPORAL WEIGHTING SYSTEM:
- Today's articles: PRIMARY - What we're analyzing NOW
- Last 7 days: 100% weight - Immediate narrative evolution
- Last 30 days: 50% weight - Important trend context
- Last 90 days: 25% weight - Background patterns
- Knowledge Base: Timeless - Verified facts and historical precedents

IMPORTANT: Use multi-layered context appropriately:
1. GROUND analysis in Knowledge Base facts (verified claims, historical events)
2. PRIORITIZE recent articles and digests (higher temporal weight)
3. TRACK narrative evolution using historical articles
4. COMPARE current framing to Knowledge Base precedents
5. IDENTIFY if current narrative is new or recurring from history
6. FACT-CHECK claims against Knowledge Base verified data
7. NOTE propaganda techniques compared to historical examples
8. MAINTAIN analytical consistency across all time periods

Your task: Analyze the following Russian media story and create a post following the Eastbound Reports template.

STORY BRIEFING (EXPANDED with {total_articles} articles):
{briefing}

REQUIRED STRUCTURE (do NOT add your own title/header - it will be added programmatically):
1. HOOK (2-3 sentences): What happened and why English-speaking readers should care
2. RUSSIAN PERSPECTIVE (400-500 words): What Russian media sources are saying, with direct quotes from multiple sources
3. CONTEXT (400-500 words): Historical, cultural, or political background that Western audiences typically miss
4. COMPARISON (300-400 words): How Western media is covering this (note: you may need to infer or note if Western coverage is absent)
5. NARRATIVE EVOLUTION (200-300 words): How has Russian media's framing of this topic changed over time? Reference previous digests if relevant.
6. IMPLICATIONS: What this means for policy, business, and culture
7. BOTTOM LINE (2-3 sentences): Key takeaway

Start your response with "## HOOK" - do NOT add any title or date above this.

TONE: Professional, analytical, academic. Like a research briefing, not opinion journalism.

SOURCES: Cite each Russian source mentioned. Use format: "According to [Source], '[quote]'"

Generate a complete 1500-2000 word analysis following this structure exactly. Use the expanded article coverage to provide deeper insights."""

def load_briefing(filepath):
    """Load the media briefing JSON."""
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

def select_top_story(briefing):
    """Select the most interesting story from briefing."""
    if briefing['trending_stories']:
        # Pick the most covered story
        return briefing['trending_stories'][0]
    elif briefing['top_headlines']:
        # Fallback to top headline
        return {'articles': [briefing['top_headlines'][0]]}
    else:
        return None

def load_previous_digests(days=7):
    """Load previous N days of published digests for context (LINEAR - for recent focus)."""
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    posts_dir = project_root / '_posts'

    if not posts_dir.exists():
        return []

    previous_digests = []
    cutoff_date = datetime.now() - timedelta(days=days)

    # Find recent posts
    for post_file in sorted(posts_dir.glob('*.md'), reverse=True):
        try:
            # Extract date from filename (YYYY-MM-DD-slug.md)
            date_str = '-'.join(post_file.stem.split('-')[:3])
            post_date = datetime.strptime(date_str, '%Y-%m-%d')

            if post_date >= cutoff_date:
                with open(post_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    # Extract title and key sections
                    previous_digests.append({
                        'date': date_str,
                        'filename': post_file.name,
                        'content': content[:2000],  # First 2000 chars
                        'weight': 1.0  # Full weight for recent
                    })
        except Exception as e:
            continue

    return previous_digests[:5]  # Last 5 digests max

def load_historical_context_weighted():
    """Load historical briefings with LOGARITHMIC temporal decay."""
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    research_dir = project_root / 'research'

    # Define temporal buckets with decreasing weights
    now = datetime.now()
    buckets = [
        {'days': 7, 'weight': 1.0, 'max_articles': 100},  # Last week: everything
        {'days': 30, 'weight': 0.5, 'max_articles': 50},   # Last month: 50%
        {'days': 90, 'weight': 0.25, 'max_articles': 25},  # Last quarter: 25%
    ]

    weighted_articles = []

    for bucket in buckets:
        start_date = now - timedelta(days=bucket['days'])
        articles_in_bucket = []

        # Scan briefing files
        for briefing_file in sorted(research_dir.glob('*-briefing.json')):
            try:
                date_str = '-'.join(briefing_file.stem.split('-')[:3])
                briefing_date = datetime.strptime(date_str, '%Y-%m-%d')

                if briefing_date >= start_date:
                    with open(briefing_file, 'r', encoding='utf-8') as f:
                        briefing = json.load(f)
                        articles = briefing.get('all_articles', briefing.get('top_headlines', []))

                        # Sample articles based on weight
                        sample_count = int(len(articles) * bucket['weight'])
                        sample_count = min(sample_count, bucket['max_articles'])

                        if sample_count > 0:
                            step = max(1, len(articles) // sample_count)
                            sampled = articles[::step][:sample_count]

                            for article in sampled:
                                articles_in_bucket.append({
                                    'date': date_str,
                                    'article': article,
                                    'weight': bucket['weight']
                                })
            except Exception:
                continue

        weighted_articles.extend(articles_in_bucket)

    return weighted_articles

def format_previous_digests(digests):
    """Format previous digests for prompt with TEMPORAL WEIGHTING."""
    if not digests:
        return "No previous digests available."

    text = "PREVIOUS DIGESTS (Temporally Weighted - Recent = Higher Priority):\n\n"
    for i, digest in enumerate(digests):
        # Calculate recency weight (most recent = 1.0, older = lower)
        recency_weight = 1.0 - (i * 0.15)
        recency_weight = max(recency_weight, 0.25)

        text += f"[DATE] {digest['date']} [Weight: {recency_weight:.0%}]\n"
        # More content for recent digests
        preview_length = int(500 * recency_weight)
        text += f"{digest['content'][:preview_length]}...\n\n"

    return text

def format_historical_context(weighted_articles):
    """Format historical articles with temporal weighting."""
    if not weighted_articles:
        return "No historical context available."

    text = "HISTORICAL ARTICLE CONTEXT (Logarithmically Sampled):\n\n"

    # Group by weight bucket
    by_weight = {}
    for item in weighted_articles:
        weight = item['weight']
        if weight not in by_weight:
            by_weight[weight] = []
        by_weight[weight].append(item)

    # Format each weight bucket
    for weight in sorted(by_weight.keys(), reverse=True):
        articles = by_weight[weight]
        text += f"\n[Weight {weight:.0%}] - {len(articles)} articles\n"

        for item in articles[:10]:  # Show first 10 from each bucket
            article = item['article']
            text += f"  {item['date']}: [{article['source']}] {article['title']}\n"

    return text

def format_story_for_prompt(story, briefing):
    """Format story data for Claude prompt with EXPANDED article coverage."""
    text = f"Topic: {story.get('keyword', 'Russian media coverage')}\n\n"
    text += "=== PRIMARY TRENDING COVERAGE ===\n\n"

    # Include more articles from the trending topic
    for article in story['articles'][:10]:  # Increased from 5 to 10
        text += f"SOURCE: {article['source']}\n"
        text += f"HEADLINE: {article['title']}\n"
        text += f"LINK: {article['link']}\n"
        if article.get('summary'):
            text += f"SUMMARY: {article['summary']}\n"
        text += "\n"

    # Add broader context from all articles
    text += "\n=== ADDITIONAL CONTEXT FROM ALL SOURCES ===\n"
    text += f"Total articles scanned: {briefing.get('total_articles_scanned', 0)}\n\n"

    # Include headlines from all articles for broader context
    if 'all_articles' in briefing:
        text += "All headlines (for context):\n"
        for i, article in enumerate(briefing['all_articles'][:100], 1):  # First 100 articles
            text += f"{i}. [{article['source']}] {article['title']}\n"

    return text

def load_knowledge_base_context(briefing):
    """Load relevant knowledge base entries for current briefing."""
    if not KNOWLEDGE_BASE_AVAILABLE:
        return "Knowledge base not available."

    try:
        script_dir = Path(__file__).parent
        project_root = script_dir.parent
        kb_root = project_root / 'knowledge_base'

        if not kb_root.exists():
            return "Knowledge base directory not found."

        # Extract keywords from briefing
        keywords = extract_keywords_from_briefing(briefing)

        # Initialize knowledge base
        kb = KnowledgeBase(kb_root)

        # Search for relevant entries
        results = kb.search(keywords=keywords[:15], limit=5)

        if not results:
            return "No relevant knowledge base entries found."

        # Format for AI
        context_data = {
            'keywords_searched': keywords[:15],
            'total_entries_found': len(results),
            'relevant_entries': results
        }

        return format_kb_for_prompt(context_data)

    except Exception as e:
        print(f"Warning: Failed to load knowledge base: {e}")
        return "Knowledge base error."

def generate_draft_with_claude(story, briefing, api_key):
    """Use Claude API to generate analysis with TEMPORALLY WEIGHTED + KNOWLEDGE BASE context."""
    client = Anthropic(api_key=api_key)

    # Load recent digests (last 7 days - LINEAR)
    print("[CONTEXT] Loading recent digests (last 7 days, linear)...")
    previous_digests = load_previous_digests(days=7)
    digests_text = format_previous_digests(previous_digests)
    print(f"  [OK] Found {len(previous_digests)} recent digests")

    # Load historical context (LOGARITHMIC decay)
    print("[HISTORY] Loading historical context (logarithmic sampling)...")
    historical_articles = load_historical_context_weighted()
    historical_text = format_historical_context(historical_articles)
    print(f"  [OK] Loaded {len(historical_articles)} historical articles across time")

    # Load knowledge base context (WORLD HISTORY & ANALYSIS)
    print("[KB] Querying knowledge base for relevant historical context...")
    knowledge_base_text = load_knowledge_base_context(briefing)
    if "Knowledge base" not in knowledge_base_text or "error" not in knowledge_base_text.lower():
        kb_count = knowledge_base_text.count('## Knowledge Entry')
        print(f"  [OK] Found {kb_count} relevant knowledge base entries")
    else:
        print(f"  [WARN] {knowledge_base_text}")

    # Combine ALL context with emphasis on temporal weighting
    combined_context = f"{digests_text}\n\n{historical_text}\n\n{knowledge_base_text}"

    # Format story with expanded article coverage
    story_text = format_story_for_prompt(story, briefing)
    now = datetime.now()
    today = now.strftime("%B %d, %Y")
    month_year = now.strftime("%B %Y")

    total_articles = briefing.get('total_articles_scanned', 0)

    full_prompt = ANALYSIS_PROMPT.format(
        briefing=story_text,
        today_date=today,
        month_year=month_year,
        previous_digests=combined_context,
        total_articles=total_articles
    )

    print(f"[DRAFT] Generating draft with Claude API...")
    print(f"  - Using {total_articles} current articles")
    print(f"  - Including {len(previous_digests)} recent digests (100% weight)")
    print(f"  - Including {len(historical_articles)} historical articles (logarithmically weighted)")
    kb_entries = knowledge_base_text.count('## Knowledge Entry')
    if kb_entries > 0:
        print(f"  - Including {kb_entries} knowledge base entries (world history context)")

    try:
        message = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=4000,
            temperature=0.7,
            messages=[{
                "role": "user",
                "content": full_prompt
            }]
        )

        draft_content = message.content[0].text
        print("[OK] Draft generated successfully")

        # Validate and fix common hallucinations
        print("[VALIDATE] Validating content and fixing hallucinations...")
        source_list = [article['source'] for article in story['articles'][:5]]
        draft_content = validate_and_fix_content(draft_content, now, source_list)

        # Check structure
        if validate_structure(draft_content):
            print("[OK] Content structure validated")
        else:
            print("[WARN] Warning: Some sections may be missing")

        return draft_content

    except Exception as e:
        print(f"[ERROR] Error calling Claude API: {e}")
        return None

def extract_cited_sources(draft_content, briefing):
    """Extract sources actually cited in the draft from the briefing."""
    import re

    # Find all "According to [SOURCE]" patterns
    citation_pattern = r'According to ([A-Z][A-Za-z\s]+?)(?:,|\s+reporting|\.)'
    cited_sources = re.findall(citation_pattern, draft_content)

    # Clean up source names
    cited_sources = [s.strip() for s in cited_sources]

    # Match to actual articles in briefing
    cited_articles = []
    seen_urls = set()

    for source_name in set(cited_sources):  # Unique sources
        # Find articles from this source
        for article in briefing.get('all_articles', []):
            if article['source'].lower() in source_name.lower() or source_name.lower() in article['source'].lower():
                if article['link'] not in seen_urls:
                    cited_articles.append(article)
                    seen_urls.add(article['link'])
                    break  # One article per source

    return cited_articles if cited_articles else None

def create_markdown_file(draft_content, story, briefing, output_dir):
    """Create markdown file with frontmatter."""
    now = datetime.now()
    today = now.strftime('%Y-%m-%d')
    today_long = now.strftime('%B %d, %Y')
    month_year = now.strftime('%B %Y')

    # Generate title from keyword or first article
    if story.get('keyword'):
        title_base = story['keyword'].replace('-', ' ').title()
    else:
        title_base = story['articles'][0]['title'][:50]

    # Create slug
    slug = title_base.lower().replace(' ', '-')
    slug = ''.join(c for c in slug if c.isalnum() or c == '-')[:50]

    filename = f"{today}-{slug}.md"
    filepath = os.path.join(output_dir, filename)

    # Programmatically add header with LOCKED-IN date (can't be hallucinated)
    header = f"""# EASTBOUND REPORTS ANALYSIS
## Russian Media Coverage: {month_year} Digest

*Analysis Date: {today_long}*

---

"""

    # Build frontmatter
    frontmatter = f"""---
title: "{title_base}"
subtitle: "AI-generated analysis of Russian media coverage"
date: "{today}"
publish_time: "12:00"
status: draft
type: weekly-analysis
tags:
  - ai-generated
  - russia
  - analysis
author: "Eastbound Reports (AI-Generated)"
twitter_thread: true
ai_generated: true
---

**⚠️ AI-GENERATED CONTENT:** This post was automatically generated using Claude AI based on Russian media monitoring. While we strive for accuracy and objectivity, this content should be reviewed critically. All source citations link to original Russian media.

---

{header}{draft_content}

---

## Disclaimer

This analysis was generated automatically by AI (Claude 3.5 Sonnet) as part of Eastbound Reports' experimental automated content system. The AI was prompted to:

- Analyze Russian media coverage objectively
- Maintain strict impartiality
- Cite sources accurately
- Provide context for English-speaking audiences
- Avoid partisan positions

Human review and editing may improve accuracy and nuance. Treat AI-generated analysis as a starting point for understanding Russian media narratives, not definitive interpretation.

## Sources

"""

    # Extract and add actually cited sources
    cited_articles = extract_cited_sources(draft_content, briefing)

    if cited_articles:
        # List sources that were actually cited
        for article in cited_articles[:10]:  # Max 10 sources
            frontmatter += f"- [{article['source']}]({article['link']}): {article['title']}\n"
    else:
        # Fallback to trending topic articles if extraction fails
        for article in story['articles'][:5]:
            frontmatter += f"- [{article['source']}]({article['link']}): {article['title']}\n"

    # Write file
    os.makedirs(output_dir, exist_ok=True)

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(frontmatter)

    print(f"[OK] Draft saved to: {filepath}")
    return filepath

def main():
    parser = argparse.ArgumentParser(description='Generate AI draft from briefing')
    parser.add_argument('--briefing', required=True, help='Path to briefing JSON')
    parser.add_argument('--output', required=True, help='Output directory for draft')
    args = parser.parse_args()

    # Get API key from environment
    api_key = os.getenv('ANTHROPIC_API_KEY')
    if not api_key:
        print("[ERROR] Error: ANTHROPIC_API_KEY environment variable not set")
        return

    # Load briefing
    print(f"[LOAD] Loading briefing from {args.briefing}")
    briefing = load_briefing(args.briefing)

    # Select top story
    story = select_top_story(briefing)
    if not story:
        print("[ERROR] No suitable stories found in briefing")
        return

    print(f"[STORY] Selected story: {story.get('keyword', 'Top headline')}")
    print(f"   Covered by {story.get('source_count', 1)} sources")

    # Generate draft with expanded briefing context
    draft_content = generate_draft_with_claude(story, briefing, api_key)

    if not draft_content:
        print("[ERROR] Failed to generate draft")
        return

    # Save as markdown
    filepath = create_markdown_file(draft_content, story, briefing, args.output)

    print(f"\n[DONE] Draft ready for review!")
    print(f"   File: {filepath}")
    print(f"   Status: draft (requires approval to publish)")

if __name__ == '__main__':
    main()
