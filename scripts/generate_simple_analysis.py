#!/usr/bin/env python3
"""
Simple Analysis Generator - Russian News Only

Reads briefing, generates unbiased analysis, saves to _posts.
No complex features - just clean, professional journalism.
"""

import argparse
import json
import os
import sys
from pathlib import Path
from datetime import datetime

try:
    from anthropic import Anthropic
except ImportError:
    print("[ERROR] anthropic package not installed. Run: pip install anthropic", flush=True)
    sys.exit(1)


def generate_analysis(briefing_path, output_path):
    """Generate simple, unbiased analysis from Russian news briefing."""

    # Load API key
    api_key = os.getenv('ANTHROPIC_API_KEY')
    if not api_key:
        print("[ERROR] ANTHROPIC_API_KEY not found in environment", flush=True)
        return False

    # Load briefing
    with open(briefing_path, 'r', encoding='utf-8') as f:
        briefing = json.load(f)

    date = briefing.get('date', datetime.now().strftime('%Y-%m-%d'))

    # Create simple, focused prompt
    prompt = f"""You are a professional journalist analyzing Russian media coverage.

Today's briefing ({date}):
- {briefing['total_articles_scanned']} articles scanned
- Top trending stories: {', '.join([s['keyword'] for s in briefing.get('trending_stories', [])[:3]])}

Generate a concise, unbiased analysis article following this EXACT format:

---
layout: post
title: "[Create compelling title based on main story]"
date: {date}
author: Eastbound Analysis
categories: [Analysis, Russia]
tags: [key, topics, from, briefing]
excerpt: "One-sentence summary of main story"
---

## Overview

[2-3 paragraphs: What are Russian media sources reporting today? What's the main narrative?]

## Key Stories

### [Story 1 Title]
[What Russian sources are saying, with specific quotes and links]

### [Story 2 Title]
[What Russian sources are saying, with specific quotes and links]

### [Story 3 Title - if relevant]
[What Russian sources are saying, with specific quotes and links]

## Context

[What might Western audiences not understand about this coverage? What's important to know?]

## Analysis

[What does this tell us about Russian priorities, concerns, or narratives right now?]

---

**CRITICAL REQUIREMENTS:**
1. Be factual and unbiased - report what Russian media is saying, don't editorialize
2. Use direct quotes from the briefing articles
3. Include actual links to source articles
4. Keep it under 1000 words total
5. Professional, journalistic tone
6. NO H1 headers (Jekyll handles title)

Here are the top 3 trending stories with articles:

{json.dumps(briefing.get('trending_stories', [])[:3], indent=2)}

Generate the complete markdown article now."""

    print(f"[API] Generating analysis...", flush=True)

    try:
        client = Anthropic(api_key=api_key)
        message = client.messages.create(
            model="claude-sonnet-4-5-20250929",
            max_tokens=3000,
            messages=[{"role": "user", "content": prompt}]
        )

        article = message.content[0].text

        # Save to file
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(article)

        print(f"[OK] Analysis saved: {output_path}", flush=True)
        print(f"[API] Tokens: {message.usage.input_tokens + message.usage.output_tokens}", flush=True)

        return True

    except Exception as e:
        print(f"[ERROR] {e}", flush=True)
        return False


def main():
    parser = argparse.ArgumentParser(description='Generate simple Russian news analysis')
    parser.add_argument('--briefing', required=True, help='Briefing JSON file')
    parser.add_argument('--output', required=True, help='Output markdown file')

    args = parser.parse_args()

    success = generate_analysis(args.briefing, args.output)
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
