#!/usr/bin/env python3
"""
Generate AI draft using Anthropic API (non-interactive)

This script reads a briefing file and generates an analysis article
using the Anthropic API. It's designed to run from Task Scheduler
without requiring user interaction.

Usage:
    python scripts/generate_ai_draft.py --briefing research/2025-11-15-briefing.json
"""

import argparse
import json
import os
import sys
from pathlib import Path
from datetime import datetime

# Anthropic API client
try:
    from anthropic import Anthropic
except ImportError:
    print("[ERROR] anthropic package not installed. Run: pip install anthropic", flush=True)
    sys.exit(1)


def generate_draft(briefing_path, output_path=None):
    """Generate draft article from briefing using Anthropic API."""

    # Load API key
    api_key = os.getenv('ANTHROPIC_API_KEY')
    if not api_key:
        print("[ERROR] ANTHROPIC_API_KEY not found in environment", flush=True)
        print("[INFO] Add ANTHROPIC_API_KEY to .env file", flush=True)
        return False

    # Load briefing
    try:
        with open(briefing_path, 'r', encoding='utf-8') as f:
            briefing = json.load(f)
    except Exception as e:
        print(f"[ERROR] Failed to load briefing: {e}", flush=True)
        return False

    # Extract date from briefing
    date = briefing.get('date', datetime.now().strftime('%Y-%m-%d'))

    # Set output path if not provided
    if not output_path:
        output_path = f"content/drafts/{date}-analysis.md"

    # Create prompt for Claude
    prompt = f"""You are a content writer for Eastbound, a Russian media analysis service.

I have a briefing file with {briefing['total_articles_scanned']} articles from Russian media.

Generate a high-quality analysis article following this format:

**FRONTMATTER (YAML):**
```yaml
---
layout: post
title: "[Descriptive title based on top trending story]"
date: {date}
author: Eastbound Analysis
categories: [Analysis, Russia]
tags: [trending keywords from briefing]
excerpt: "Brief summary of the main story"
image: /images/{date}-generated.png
status: draft
---
```

**ARTICLE STRUCTURE:**

## Overview
[2-3 paragraphs introducing the main story and why it matters]

## Russian Media Coverage
[Analysis of how Russian sources are covering this, with specific quotes]

## Context for Western Audiences
[What Western audiences might be missing]

## Implications
[What this means for policy/business/culture]

## Data Visualizations
[Reference to charts in /images/ directory]

*Note: Article illustration generated using AI (SDXL)*

## Key Articles Referenced
[Bulleted list of 5-10 key sources with links]

---

**TRENDING STORIES:**
{json.dumps(briefing.get('trending_stories', [])[:3], indent=2)}

**SENTIMENT:**
{json.dumps(briefing.get('sentiment_analysis', {}), indent=2)}

Please generate the complete article markdown with frontmatter."""

    # Call Anthropic API
    print(f"[API] Calling Anthropic API to generate draft...", flush=True)

    try:
        client = Anthropic(api_key=api_key)

        message = client.messages.create(
            model="claude-sonnet-4-5-20250929",
            max_tokens=4000,
            messages=[{
                "role": "user",
                "content": prompt
            }]
        )

        # Extract text content
        article_content = message.content[0].text

        # Save to file
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(article_content)

        print(f"[OK] Draft generated: {output_path}", flush=True)
        print(f"[API] Tokens used: {message.usage.input_tokens + message.usage.output_tokens}", flush=True)

        return True

    except Exception as e:
        print(f"[ERROR] API call failed: {e}", flush=True)
        return False


def main():
    parser = argparse.ArgumentParser(description='Generate AI draft using Anthropic API')
    parser.add_argument('--briefing', required=True, help='Path to briefing JSON file')
    parser.add_argument('--output', help='Output path for draft (default: content/drafts/{date}-analysis.md)')

    args = parser.parse_args()

    success = generate_draft(args.briefing, args.output)
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
