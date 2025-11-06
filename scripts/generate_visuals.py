#!/usr/bin/env python3
"""
Generate visual content for Eastbound Reports posts.

NOW USES VISUALIZATION FRAMEWORK!
See: visualization_framework.py and AI_VISUALIZATION_GUIDE.md

Creates:
1. Keyword trend charts
2. Source distribution charts
3. Featured images for social media
4. Data visualization cards
5. Optional: Internet-sourced images

Usage:
    python generate_visuals.py --briefing research/YYYY-MM-DD-briefing.json --output images/
    python generate_visuals.py --briefing briefing.json --output images/ --fetch-images
"""

import argparse
import json
from pathlib import Path
from datetime import datetime
import sys

# Import visualization framework
try:
    from visualization_framework import create_chart, CHART_REGISTRY
except ImportError:
    print("[ERROR] visualization_framework.py not found. Run from scripts/ directory.")
    sys.exit(1)

# Import image fetching (optional)
try:
    from fetch_images import fetch_relevant_image
    IMAGE_FETCH_AVAILABLE = True
except ImportError:
    IMAGE_FETCH_AVAILABLE = False


def main():
    parser = argparse.ArgumentParser(description='Generate visual content for Eastbound posts')
    parser.add_argument('--briefing', required=True, help='Path to briefing JSON')
    parser.add_argument('--output', required=True, help='Output directory for images')
    parser.add_argument('--fetch-images', action='store_true',
                       help='Fetch relevant images from internet sources')
    parser.add_argument('--charts', default='keyword_trend,source_distribution,social_card,stats_card',
                       help='Comma-separated list of chart types to generate (add timeline,word_cloud for more)')
    args = parser.parse_args()

    # Load briefing
    print(f"[VISUAL] Loading briefing: {args.briefing}")
    with open(args.briefing, 'r', encoding='utf-8') as f:
        briefing = json.load(f)

    # Create output directory
    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Generate date-based filenames
    date = briefing.get('date', datetime.now().strftime('%Y-%m-%d'))

    print("\n[VISUAL] Generating visualizations...")
    print(f"[INFO] Using framework with {len(CHART_REGISTRY)} available chart types")

    chart_types = [c.strip() for c in args.charts.split(',')]
    generated = []

    # Extract all articles from briefing (they're nested in trending_stories)
    all_articles = []
    for story in briefing.get('trending_stories', []):
        all_articles.extend(story.get('articles', []))

    # Generate each requested chart type
    for chart_type in chart_types:
        try:
            if chart_type == 'keyword_trend' and briefing.get('trending_stories'):
                chart = create_chart('keyword_trend')
                output_path = output_dir / f"{date}-keywords.png"
                chart.generate(briefing['trending_stories'], output_path)
                print(f"  [OK] Keyword chart: {output_path.name}")
                generated.append(output_path)

            elif chart_type == 'source_distribution' and all_articles:
                chart = create_chart('source_distribution')
                output_path = output_dir / f"{date}-sources.png"
                chart.generate(all_articles, output_path)
                print(f"  [OK] Source chart: {output_path.name}")
                generated.append(output_path)

            elif chart_type == 'social_card':
                chart = create_chart('social_card')
                output_path = output_dir / f"{date}-featured.png"
                # Prepare data for social card
                data = {
                    'date': date,
                    'total_articles': briefing.get('total_articles_scanned', 0),
                    'top_keyword': briefing['trending_stories'][0]['keyword'] if briefing.get('trending_stories') else 'Analysis'
                }
                chart.generate(data, output_path)
                print(f"  [OK] Social card: {output_path.name}")
                generated.append(output_path)

            elif chart_type == 'stats_card':
                chart = create_chart('stats_card')
                output_path = output_dir / f"{date}-stats.png"
                # Prepare data for stats card
                sources = len(set(article['source'] for article in all_articles)) if all_articles else 0
                data = {
                    'date': date,
                    'total_articles': briefing.get('total_articles_scanned', 0),
                    'sources': sources,
                    'trending_count': len(briefing.get('trending_stories', []))
                }
                chart.generate(data, output_path)
                print(f"  [OK] Stats card: {output_path.name}")
                generated.append(output_path)

            elif chart_type == 'timeline' and briefing.get('trending_stories'):
                # Generate timeline from trending stories
                chart = create_chart('timeline')
                output_path = output_dir / f"{date}-timeline.png"

                # Build timeline data from trending stories with publication dates
                from dateutil import parser as date_parser
                timeline_data = []

                for story in briefing['trending_stories'][:10]:  # Top 10 stories
                    keyword = story['keyword']
                    importance = story.get('source_count', 5)  # Use source count as importance

                    # Get first article's date if available
                    articles = story.get('articles', [])
                    if articles and articles[0].get('published'):
                        try:
                            # Parse published date
                            pub_date = date_parser.parse(articles[0]['published'])
                            date_str = pub_date.strftime('%Y-%m-%d')

                            timeline_data.append({
                                'date': date_str,
                                'event': keyword[:30],  # Truncate for readability
                                'importance': min(importance, 10)  # Cap at 10
                            })
                        except:
                            # If date parsing fails, use today's date
                            timeline_data.append({
                                'date': date,
                                'event': keyword[:30],
                                'importance': min(importance, 10)
                            })

                if timeline_data:
                    # Sort by date
                    timeline_data.sort(key=lambda x: x['date'])
                    chart.generate(timeline_data, output_path)
                    print(f"  [OK] Timeline chart: {output_path.name}")
                    generated.append(output_path)
                else:
                    print(f"  [SKIP] Timeline: No dated events found")

            elif chart_type == 'word_cloud' and briefing.get('trending_stories'):
                # Generate word cloud from keywords
                chart = create_chart('word_cloud')
                output_path = output_dir / f"{date}-wordcloud.png"

                # Build word frequency dict from trending stories
                word_freq = {}
                for story in briefing['trending_stories']:
                    keyword = story['keyword']
                    count = story.get('source_count', 1)
                    word_freq[keyword] = count

                if word_freq:
                    chart.generate(word_freq, output_path)
                    print(f"  [OK] Word cloud: {output_path.name}")
                    generated.append(output_path)
                else:
                    print(f"  [SKIP] Word cloud: No keywords found")

            elif chart_type in CHART_REGISTRY:
                # Generic handler for other chart types
                print(f"  [SKIP] Chart type '{chart_type}' requires custom data preparation")

            else:
                print(f"  [WARNING] Unknown chart type: {chart_type}")

        except Exception as e:
            print(f"  [ERROR] Failed to generate {chart_type}: {e}")

    # Optional: Fetch internet images
    if args.fetch_images:
        if IMAGE_FETCH_AVAILABLE:
            print("\n[VISUAL] Fetching internet images...")
            try:
                img_path = fetch_relevant_image(briefing, str(output_dir))
                if img_path:
                    print(f"  [OK] Fetched image: {img_path.name}")
                    generated.append(img_path)
                else:
                    print("  [WARNING] Could not fetch relevant image")
            except Exception as e:
                print(f"  [ERROR] Image fetch failed: {e}")
        else:
            print("\n[WARNING] Image fetching not available (fetch_images.py not found)")

    print(f"\n[SUCCESS] Generated {len(generated)} visualizations in: {output_dir}")
    print(f"[INFO] Available chart types: {', '.join(CHART_REGISTRY.keys())}")
    print(f"[INFO] See AI_VISUALIZATION_GUIDE.md to add more chart types")


if __name__ == '__main__':
    main()
