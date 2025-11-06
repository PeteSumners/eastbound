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

PREVIOUS DIGESTS (for narrative continuity):
{previous_digests}

IMPORTANT: Use previous digests to:
- Track how narratives are evolving
- Note any shifts in messaging
- Reference previous coverage if relevant
- Maintain analytical consistency

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
    """Load previous N days of published digests for context."""
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
                        'content': content[:2000]  # First 2000 chars
                    })
        except Exception as e:
            continue

    return previous_digests[:5]  # Last 5 digests max

def format_previous_digests(digests):
    """Format previous digests for prompt."""
    if not digests:
        return "No previous digests available."

    text = "PREVIOUS DIGESTS (for narrative continuity):\n\n"
    for digest in digests:
        text += f"Date: {digest['date']}\n"
        text += f"Preview: {digest['content'][:500]}...\n\n"

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

def generate_draft_with_claude(story, briefing, api_key):
    """Use Claude API to generate analysis with expanded context."""
    client = Anthropic(api_key=api_key)

    # Load previous digests for context
    print("📚 Loading previous digests for narrative context...")
    previous_digests = load_previous_digests(days=7)
    digests_text = format_previous_digests(previous_digests)
    print(f"  ✓ Found {len(previous_digests)} previous digests")

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
        previous_digests=digests_text,
        total_articles=total_articles
    )

    print(f"📝 Generating draft with Claude API...")
    print(f"  - Using {total_articles} articles from briefing")
    print(f"  - Including {len(previous_digests)} previous digests for context")

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
        print("✅ Draft generated successfully")

        # Validate and fix common hallucinations
        print("🔍 Validating content and fixing hallucinations...")
        source_list = [article['source'] for article in story['articles'][:5]]
        draft_content = validate_and_fix_content(draft_content, now, source_list)

        # Check structure
        if validate_structure(draft_content):
            print("✅ Content structure validated")
        else:
            print("⚠️  Warning: Some sections may be missing")

        return draft_content

    except Exception as e:
        print(f"❌ Error calling Claude API: {e}")
        return None

def create_markdown_file(draft_content, story, output_dir):
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

    # Add source links
    for article in story['articles'][:5]:
        frontmatter += f"- [{article['source']}]({article['link']}): {article['title']}\n"

    # Write file
    os.makedirs(output_dir, exist_ok=True)

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(frontmatter)

    print(f"✅ Draft saved to: {filepath}")
    return filepath

def main():
    parser = argparse.ArgumentParser(description='Generate AI draft from briefing')
    parser.add_argument('--briefing', required=True, help='Path to briefing JSON')
    parser.add_argument('--output', required=True, help='Output directory for draft')
    args = parser.parse_args()

    # Get API key from environment
    api_key = os.getenv('ANTHROPIC_API_KEY')
    if not api_key:
        print("❌ Error: ANTHROPIC_API_KEY environment variable not set")
        return

    # Load briefing
    print(f"📖 Loading briefing from {args.briefing}")
    briefing = load_briefing(args.briefing)

    # Select top story
    story = select_top_story(briefing)
    if not story:
        print("❌ No suitable stories found in briefing")
        return

    print(f"📰 Selected story: {story.get('keyword', 'Top headline')}")
    print(f"   Covered by {story.get('source_count', 1)} sources")

    # Generate draft with expanded briefing context
    draft_content = generate_draft_with_claude(story, briefing, api_key)

    if not draft_content:
        print("❌ Failed to generate draft")
        return

    # Save as markdown
    filepath = create_markdown_file(draft_content, story, args.output)

    print(f"\n🎉 Draft ready for review!")
    print(f"   File: {filepath}")
    print(f"   Status: draft (requires approval to publish)")

if __name__ == '__main__':
    main()
