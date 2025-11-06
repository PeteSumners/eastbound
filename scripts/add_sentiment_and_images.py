#!/usr/bin/env python3
"""
Add sentiment analysis and real photos to Eastbound Reports.

This script shows you how to:
1. Analyze sentiment of articles over time
2. Fetch legal images from Unsplash
3. Generate sentiment timeline charts
4. Add images with proper attribution to posts

Usage:
    python add_sentiment_and_images.py --briefing research/YYYY-MM-DD-briefing.json
"""

import argparse
import json
from pathlib import Path
from datetime import datetime, timedelta
import re

# Try to import Anthropic for sentiment analysis
try:
    from anthropic import Anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False

# Import visualization and image fetching
try:
    from visualization_framework import create_chart
    from fetch_images import fetch_unsplash_image, fetch_wikipedia_image, get_image_attribution
    IMAGE_FETCH_AVAILABLE = True
except ImportError:
    IMAGE_FETCH_AVAILABLE = False


def analyze_sentiment_batch(articles, api_key=None):
    """
    Analyze sentiment of articles using Claude.

    Args:
        articles: List of article dicts with 'title' and 'summary'
        api_key: Anthropic API key (or from env)

    Returns:
        List of dicts with 'date', 'title', 'sentiment' (-1 to 1)
    """
    if not ANTHROPIC_AVAILABLE:
        print("[ERROR] Anthropic library not installed")
        return None

    client = Anthropic(api_key=api_key)

    results = []

    print(f"[SENTIMENT] Analyzing {len(articles)} articles...")

    for i, article in enumerate(articles[:10]):  # Limit to 10 for demo
        try:
            # Create prompt for sentiment analysis
            prompt = f"""Analyze the sentiment/tone of this Russian media article.

Title: {article.get('title', 'N/A')}
Summary: {article.get('summary', 'N/A')}

Rate the sentiment on a scale from -1.0 (very negative) to +1.0 (very positive).
Consider:
- Language tone (threatening, conciliatory, neutral)
- Framing of events (triumphant, defensive, matter-of-fact)
- References to adversaries (hostile, neutral, cooperative)

Respond with ONLY a number between -1.0 and +1.0. Nothing else."""

            response = client.messages.create(
                model="claude-3-haiku-20240307",  # Fast and cheap
                max_tokens=10,
                messages=[{"role": "user", "content": prompt}]
            )

            # Parse sentiment score
            sentiment_text = response.content[0].text.strip()
            sentiment = float(sentiment_text)

            # Clamp to valid range
            sentiment = max(-1.0, min(1.0, sentiment))

            # Parse date
            date_str = article.get('published', '')
            try:
                # Try various date formats
                for fmt in ['%a, %d %b %Y %H:%M:%S %z', '%Y-%m-%d']:
                    try:
                        date_obj = datetime.strptime(date_str, fmt)
                        date = date_obj.strftime('%Y-%m-%d')
                        break
                    except:
                        continue
                else:
                    date = datetime.now().strftime('%Y-%m-%d')
            except:
                date = datetime.now().strftime('%Y-%m-%d')

            results.append({
                'date': date,
                'title': article.get('title', ''),
                'sentiment': sentiment
            })

            print(f"  [{i+1}/{len(articles[:10])}] {sentiment:+.2f} - {article.get('title', '')[:50]}...")

        except Exception as e:
            print(f"  [ERROR] Failed to analyze article: {e}")
            continue

    return results


def fetch_topic_image(topic, output_dir='images/'):
    """
    Fetch a relevant image for a topic.

    Tries Wikipedia first, then Unsplash.
    """
    if not IMAGE_FETCH_AVAILABLE:
        print("[ERROR] Image fetching not available")
        return None

    print(f"[IMAGE] Fetching image for topic: {topic}")

    # Known entities that have good Wikipedia images
    wiki_topics = {
        'putin': 'Vladimir Putin',
        'zelensky': 'Volodymyr Zelenskyy',
        'kremlin': 'Moscow Kremlin',
        'ukraine': 'Ukraine',
        'russia': 'Russia',
        'moscow': 'Moscow',
        'kyiv': 'Kyiv',
        'nato': 'NATO',
    }

    topic_lower = topic.lower()

    # Try Wikipedia first
    for key, wiki_title in wiki_topics.items():
        if key in topic_lower:
            print(f"  [WIKI] Trying Wikipedia: {wiki_title}")
            img = fetch_wikipedia_image(wiki_title, output_dir)
            if img:
                return img

    # Fall back to Unsplash
    print(f"  [UNSPLASH] Trying Unsplash: {topic}")
    img = fetch_unsplash_image(f"{topic} russia news", output_dir)

    return img


def add_images_to_post(post_path, topic, output_dir='images/'):
    """
    Add a relevant image to a post with proper attribution.
    """
    # Fetch image
    img_path = fetch_topic_image(topic, output_dir)

    if not img_path:
        print("[WARN] Could not fetch image")
        return False

    # Get attribution
    attribution = get_image_attribution(img_path)

    # Read post
    with open(post_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Find a good place to insert (after first paragraph)
    lines = content.split('\n')
    insert_line = 0

    # Find first paragraph after frontmatter
    in_frontmatter = False
    paragraph_count = 0

    for i, line in enumerate(lines):
        if line.strip() == '---':
            in_frontmatter = not in_frontmatter
            continue

        if not in_frontmatter and line.strip() and not line.startswith('#'):
            paragraph_count += 1
            if paragraph_count == 2:  # After first paragraph
                insert_line = i + 1
                break

    # Insert image and attribution
    image_block = [
        '',
        f'![{topic}]({img_path})',
        f'*{attribution}*' if attribution else '',
        ''
    ]

    lines = lines[:insert_line] + image_block + lines[insert_line:]

    # Write back
    with open(post_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))

    print(f"[OK] Added image to post: {img_path}")
    return True


def main():
    parser = argparse.ArgumentParser(description='Add sentiment analysis and images')
    parser.add_argument('--briefing', required=True, help='Briefing JSON file')
    parser.add_argument('--output-dir', default='images/', help='Image output directory')
    parser.add_argument('--post', help='Post file to add images to')
    parser.add_argument('--topic', help='Topic for image search')
    args = parser.parse_args()

    # Load briefing
    with open(args.briefing, 'r', encoding='utf-8') as f:
        briefing = json.load(f)

    print(f"[INFO] Loaded briefing with {briefing.get('total_articles_scanned', 0)} articles")

    # Get all articles
    all_articles = []
    for story in briefing.get('trending_stories', []):
        all_articles.extend(story.get('articles', []))

    print(f"[INFO] Processing {len(all_articles)} articles")

    # 1. Sentiment Analysis (if API key available)
    import os
    api_key = os.getenv('ANTHROPIC_API_KEY')

    if api_key and ANTHROPIC_AVAILABLE:
        print("\n[SENTIMENT] Starting sentiment analysis...")
        sentiment_data = analyze_sentiment_batch(all_articles, api_key)

        if sentiment_data:
            # Save sentiment data
            sentiment_file = Path(args.briefing).parent / f"{briefing['date']}-sentiment.json"
            with open(sentiment_file, 'w', encoding='utf-8') as f:
                json.dump(sentiment_data, f, indent=2)

            print(f"[OK] Saved sentiment data: {sentiment_file}")

            # Generate sentiment timeline chart
            from example_charts import SentimentTimelineChart

            chart = SentimentTimelineChart()
            chart_path = Path(args.output_dir) / f"{briefing['date']}-sentiment-timeline.png"
            chart.generate(sentiment_data, chart_path)

            print(f"[OK] Generated sentiment chart: {chart_path}")
    else:
        print("\n[SKIP] Sentiment analysis (no API key or library)")

    # 2. Fetch Images
    if args.post and args.topic:
        print(f"\n[IMAGE] Adding image for topic: {args.topic}")
        add_images_to_post(args.post, args.topic, args.output_dir)
    else:
        print("\n[SKIP] Image addition (no --post or --topic specified)")

    # 3. Fetch generic topic image
    if args.topic and not args.post:
        print(f"\n[IMAGE] Fetching standalone image for: {args.topic}")
        img = fetch_topic_image(args.topic, args.output_dir)
        if img:
            attribution = get_image_attribution(img)
            print(f"[OK] Image saved: {img}")
            print(f"[INFO] Attribution: {attribution}")

    print("\n[SUCCESS] Complete!")
    print("\n[NEXT STEPS]:")
    print("1. Set ANTHROPIC_API_KEY for sentiment analysis")
    print("2. Set UNSPLASH_ACCESS_KEY for more image options")
    print("3. Run with --post and --topic to add images to posts")


if __name__ == '__main__':
    main()
