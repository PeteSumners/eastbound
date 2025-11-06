#!/usr/bin/env python3
"""
Generate visual content for Eastbound Reports posts.

Creates:
1. Keyword trend charts
2. Source distribution charts
3. Featured images for social media
4. Data visualization cards

Usage:
    python generate_visuals.py --briefing research/YYYY-MM-DD-briefing.json --output images/
"""

import argparse
import json
from pathlib import Path
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend
import matplotlib.pyplot as plt
from collections import Counter
from datetime import datetime

# Set style
plt.style.use('seaborn-v0_8-darkgrid')

def create_keyword_chart(trending_stories, output_path):
    """
    Create horizontal bar chart of top trending keywords.

    Args:
        trending_stories: List of trending story dicts
        output_path: Path to save image
    """
    # Extract top 10 keywords and their source counts
    keywords = [story['keyword'] for story in trending_stories[:10]]
    source_counts = [story['source_count'] for story in trending_stories[:10]]

    # Create figure
    fig, ax = plt.subplots(figsize=(10, 6))

    # Horizontal bar chart
    y_pos = range(len(keywords))
    bars = ax.barh(y_pos, source_counts, color='#c74440')

    # Customize
    ax.set_yticks(y_pos)
    ax.set_yticklabels(keywords)
    ax.invert_yaxis()  # Top to bottom
    ax.set_xlabel('Number of Sources', fontsize=12, fontweight='bold')
    ax.set_title('Top Trending Topics in Russian Media',
                 fontsize=14, fontweight='bold', pad=20)

    # Add value labels on bars
    for i, (bar, count) in enumerate(zip(bars, source_counts)):
        width = bar.get_width()
        ax.text(width + 0.1, bar.get_y() + bar.get_height()/2,
                f'{count}',
                ha='left', va='center', fontweight='bold')

    # Add grid
    ax.grid(axis='x', alpha=0.3)

    # Tight layout
    plt.tight_layout()

    # Save
    plt.savefig(output_path, dpi=150, bbox_inches='tight',
                facecolor='white', edgecolor='none')
    plt.close()

    return output_path


def create_source_distribution(all_articles, output_path):
    """
    Create pie chart showing source distribution.

    Args:
        all_articles: List of all article dicts
        output_path: Path to save image
    """
    # Count articles per source
    source_counts = Counter(article['source'] for article in all_articles)

    # Get top sources (combine small ones into "Other")
    top_sources = source_counts.most_common(8)
    other_count = sum(count for source, count in source_counts.items()
                     if source not in dict(top_sources))

    if other_count > 0:
        top_sources.append(('Other', other_count))

    sources = [s[0] for s in top_sources]
    counts = [s[1] for s in top_sources]

    # Create figure
    fig, ax = plt.subplots(figsize=(10, 8))

    # Color palette
    colors = ['#c74440', '#e57373', '#ef5350', '#f44336',
              '#ff6f60', '#ff8a80', '#ffab91', '#ffccbc', '#d7ccc8']

    # Pie chart
    wedges, texts, autotexts = ax.pie(counts, labels=sources, autopct='%1.1f%%',
                                       colors=colors[:len(sources)],
                                       startangle=90)

    # Customize text
    for text in texts:
        text.set_fontsize(11)
        text.set_fontweight('bold')

    for autotext in autotexts:
        autotext.set_color('white')
        autotext.set_fontsize(10)
        autotext.set_fontweight('bold')

    ax.set_title('Article Distribution by Source',
                 fontsize=14, fontweight='bold', pad=20)

    plt.tight_layout()

    # Save
    plt.savefig(output_path, dpi=150, bbox_inches='tight',
                facecolor='white', edgecolor='none')
    plt.close()

    return output_path


def create_featured_image(briefing, output_path):
    """
    Create featured image card for social media.

    Shows: Date, article count, top keyword
    """
    date = briefing.get('date', 'Unknown')
    total_articles = briefing.get('total_articles_scanned', 0)
    trending = briefing.get('trending_stories', [])
    top_keyword = trending[0]['keyword'] if trending else 'Analysis'

    # Create figure with dark background
    fig, ax = plt.subplots(figsize=(12, 6))
    fig.patch.set_facecolor('#1a1a1a')
    ax.set_facecolor('#1a1a1a')

    # Remove axes
    ax.axis('off')

    # Title
    ax.text(0.5, 0.75, 'EASTBOUND REPORTS',
            ha='center', va='center',
            fontsize=32, fontweight='bold',
            color='#c74440',
            transform=ax.transAxes)

    # Subtitle
    ax.text(0.5, 0.60, 'Russian Media Analysis',
            ha='center', va='center',
            fontsize=18,
            color='#ffffff',
            transform=ax.transAxes)

    # Date
    date_formatted = datetime.strptime(date, '%Y-%m-%d').strftime('%B %d, %Y')
    ax.text(0.5, 0.45, date_formatted,
            ha='center', va='center',
            fontsize=14,
            color='#aaaaaa',
            transform=ax.transAxes)

    # Stats
    ax.text(0.5, 0.30, f'{total_articles} ARTICLES ANALYZED',
            ha='center', va='center',
            fontsize=16, fontweight='bold',
            color='#ffffff',
            transform=ax.transAxes)

    # Top keyword
    ax.text(0.5, 0.15, f'Top Topic: {top_keyword.upper()}',
            ha='center', va='center',
            fontsize=14,
            color='#c74440',
            transform=ax.transAxes)

    plt.tight_layout()

    # Save
    plt.savefig(output_path, dpi=150, bbox_inches='tight',
                facecolor='#1a1a1a', edgecolor='none')
    plt.close()

    return output_path


def create_stats_card(briefing, output_path):
    """
    Create a data card showing key statistics.
    """
    date = briefing.get('date', 'Unknown')
    total_articles = briefing.get('total_articles_scanned', 0)
    trending = briefing.get('trending_stories', [])
    sources = len(set(article['source'] for article in briefing.get('all_articles', [])))

    # Create figure
    fig, ax = plt.subplots(figsize=(8, 10))
    fig.patch.set_facecolor('#f5f5f5')
    ax.set_facecolor('#f5f5f5')
    ax.axis('off')

    # Title
    ax.text(0.5, 0.95, 'BY THE NUMBERS',
            ha='center', va='top',
            fontsize=24, fontweight='bold',
            color='#1a1a1a',
            transform=ax.transAxes)

    date_formatted = datetime.strptime(date, '%Y-%m-%d').strftime('%B %d, %Y')
    ax.text(0.5, 0.90, date_formatted,
            ha='center', va='top',
            fontsize=12,
            color='#666666',
            transform=ax.transAxes)

    # Stats
    stats = [
        (total_articles, 'Articles Analyzed'),
        (sources, 'Media Sources'),
        (len(trending), 'Trending Topics'),
    ]

    y_start = 0.75
    y_step = 0.20

    for i, (number, label) in enumerate(stats):
        y = y_start - (i * y_step)

        # Number
        ax.text(0.5, y, f'{number}',
                ha='center', va='center',
                fontsize=48, fontweight='bold',
                color='#c74440',
                transform=ax.transAxes)

        # Label
        ax.text(0.5, y - 0.08, label,
                ha='center', va='center',
                fontsize=16,
                color='#1a1a1a',
                transform=ax.transAxes)

    # Footer
    ax.text(0.5, 0.05, 'eastboundreports.com',
            ha='center', va='bottom',
            fontsize=12,
            color='#666666',
            transform=ax.transAxes)

    plt.tight_layout()

    # Save
    plt.savefig(output_path, dpi=150, bbox_inches='tight',
                facecolor='#f5f5f5', edgecolor='none')
    plt.close()

    return output_path


def main():
    parser = argparse.ArgumentParser(description='Generate visual content for Eastbound posts')
    parser.add_argument('--briefing', required=True, help='Path to briefing JSON')
    parser.add_argument('--output', required=True, help='Output directory for images')
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

    # 1. Keyword chart
    if briefing.get('trending_stories'):
        keyword_chart = output_dir / f"{date}-keywords.png"
        create_keyword_chart(briefing['trending_stories'], keyword_chart)
        print(f"  [OK] Keyword chart: {keyword_chart}")

    # 2. Source distribution
    if briefing.get('all_articles'):
        source_chart = output_dir / f"{date}-sources.png"
        create_source_distribution(briefing['all_articles'], source_chart)
        print(f"  [OK] Source chart: {source_chart}")

    # 3. Featured image
    featured = output_dir / f"{date}-featured.png"
    create_featured_image(briefing, featured)
    print(f"  [OK] Featured image: {featured}")

    # 4. Stats card
    stats = output_dir / f"{date}-stats.png"
    create_stats_card(briefing, stats)
    print(f"  [OK] Stats card: {stats}")

    print(f"\n[SUCCESS] All visualizations created in: {output_dir}")


if __name__ == '__main__':
    main()
