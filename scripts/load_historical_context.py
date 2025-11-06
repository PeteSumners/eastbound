#!/usr/bin/env python3
"""
Load historical briefings and digests with logarithmic temporal decay.

This creates a "temporal weighting" where:
- Last 1 day: All articles (100% weight)
- Last 7 days: 75% of articles
- Last 30 days: 50% of articles
- Last 90 days: 25% of articles
- Last 365 days: 10% of articles (just key events)

Usage:
    python load_historical_context.py --output research/historical_context.json
"""

import argparse
import json
from datetime import datetime, timedelta
from pathlib import Path
import math


def get_temporal_buckets():
    """Define logarithmic time buckets for historical sampling."""
    now = datetime.now()

    buckets = [
        {
            'name': 'today',
            'days_back': 1,
            'sample_rate': 1.0,  # Include everything
            'max_articles': None,
            'start_date': now - timedelta(days=1),
            'end_date': now
        },
        {
            'name': 'last_week',
            'days_back': 7,
            'sample_rate': 0.75,  # 75% of articles
            'max_articles': 100,
            'start_date': now - timedelta(days=7),
            'end_date': now - timedelta(days=1)
        },
        {
            'name': 'last_month',
            'days_back': 30,
            'sample_rate': 0.5,  # 50% of articles
            'max_articles': 50,
            'start_date': now - timedelta(days=30),
            'end_date': now - timedelta(days=7)
        },
        {
            'name': 'last_quarter',
            'days_back': 90,
            'sample_rate': 0.25,  # 25% of articles
            'max_articles': 25,
            'start_date': now - timedelta(days=90),
            'end_date': now - timedelta(days=30)
        },
        {
            'name': 'last_year',
            'days_back': 365,
            'sample_rate': 0.10,  # 10% of articles (key events only)
            'max_articles': 10,
            'start_date': now - timedelta(days=365),
            'end_date': now - timedelta(days=90)
        }
    ]

    return buckets


def load_briefings_in_bucket(bucket, research_dir):
    """Load briefings within a time bucket."""
    briefing_files = []

    for briefing_file in sorted(research_dir.glob('*-briefing.json')):
        try:
            # Extract date from filename: YYYY-MM-DD-briefing.json
            date_str = '-'.join(briefing_file.stem.split('-')[:3])
            briefing_date = datetime.strptime(date_str, '%Y-%m-%d')

            if bucket['start_date'] <= briefing_date < bucket['end_date']:
                with open(briefing_file, 'r', encoding='utf-8') as f:
                    briefing = json.load(f)
                    briefing_files.append({
                        'date': date_str,
                        'filename': briefing_file.name,
                        'briefing': briefing
                    })
        except Exception as e:
            continue

    return briefing_files


def sample_articles(articles, sample_rate, max_articles):
    """Sample articles based on rate and max limit."""
    if not articles:
        return []

    # Calculate how many to include
    target_count = int(len(articles) * sample_rate)

    if max_articles:
        target_count = min(target_count, max_articles)

    # Sample evenly across the list
    if target_count >= len(articles):
        return articles

    step = len(articles) / target_count
    sampled = []

    for i in range(target_count):
        idx = int(i * step)
        sampled.append(articles[idx])

    return sampled


def load_digests_in_bucket(bucket, posts_dir):
    """Load published digests within a time bucket."""
    digest_files = []

    if not posts_dir.exists():
        return []

    for post_file in sorted(posts_dir.glob('*.md'), reverse=True):
        try:
            # Extract date from filename: YYYY-MM-DD-slug.md
            date_str = '-'.join(post_file.stem.split('-')[:3])
            post_date = datetime.strptime(date_str, '%Y-%m-%d')

            if bucket['start_date'] <= post_date < bucket['end_date']:
                with open(post_file, 'r', encoding='utf-8') as f:
                    content = f.read()

                    # Extract sections based on sample rate
                    max_chars = int(3000 * bucket['sample_rate'])

                    digest_files.append({
                        'date': date_str,
                        'filename': post_file.name,
                        'content': content[:max_chars],
                        'weight': bucket['sample_rate']
                    })
        except Exception as e:
            continue

    # Limit digests per bucket
    if bucket['max_articles']:
        digest_files = digest_files[:bucket['max_articles']]

    return digest_files


def create_historical_context():
    """Create comprehensive historical context with temporal weighting."""
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    research_dir = project_root / 'research'
    posts_dir = project_root / '_posts'

    buckets = get_temporal_buckets()

    historical_context = {
        'generated_at': datetime.now().isoformat(),
        'temporal_buckets': []
    }

    total_briefings = 0
    total_articles = 0
    total_digests = 0

    for bucket in buckets:
        print(f"\n📅 Processing {bucket['name']} bucket...")
        print(f"   Date range: {bucket['start_date'].strftime('%Y-%m-%d')} to {bucket['end_date'].strftime('%Y-%m-%d')}")
        print(f"   Sample rate: {bucket['sample_rate']*100}%")

        # Load briefings
        briefings = load_briefings_in_bucket(bucket, research_dir)
        print(f"   Found {len(briefings)} briefings")

        # Load digests
        digests = load_digests_in_bucket(bucket, posts_dir)
        print(f"   Found {len(digests)} digests")

        # Sample articles from briefings
        sampled_briefings = []
        for briefing_data in briefings:
            briefing = briefing_data['briefing']
            all_articles = briefing.get('all_articles', briefing.get('top_headlines', []))

            sampled_articles = sample_articles(
                all_articles,
                bucket['sample_rate'],
                bucket['max_articles']
            )

            sampled_briefings.append({
                'date': briefing_data['date'],
                'total_articles': len(all_articles),
                'sampled_articles': sampled_articles,
                'weight': bucket['sample_rate']
            })

            total_articles += len(sampled_articles)

        total_briefings += len(sampled_briefings)
        total_digests += len(digests)

        bucket_data = {
            'name': bucket['name'],
            'days_back': bucket['days_back'],
            'sample_rate': bucket['sample_rate'],
            'date_range': {
                'start': bucket['start_date'].strftime('%Y-%m-%d'),
                'end': bucket['end_date'].strftime('%Y-%m-%d')
            },
            'briefings': sampled_briefings,
            'digests': digests
        }

        historical_context['temporal_buckets'].append(bucket_data)
        print(f"   ✓ Sampled {len(sampled_articles)} articles")

    historical_context['summary'] = {
        'total_briefings': total_briefings,
        'total_articles_sampled': total_articles,
        'total_digests': total_digests
    }

    return historical_context


def format_for_ai_prompt(historical_context):
    """Format historical context for AI prompt with temporal weighting."""
    prompt_text = "=== HISTORICAL CONTEXT (Logarithmically Weighted) ===\n\n"

    summary = historical_context['summary']
    prompt_text += f"Total historical data: {summary['total_briefings']} briefings, "
    prompt_text += f"{summary['total_articles_sampled']} articles, {summary['total_digests']} digests\n\n"

    for bucket in historical_context['temporal_buckets']:
        prompt_text += f"\n## {bucket['name'].upper()} (Weight: {bucket['sample_rate']*100}%)\n"
        prompt_text += f"Date Range: {bucket['date_range']['start']} to {bucket['date_range']['end']}\n\n"

        # Add digests from this period
        if bucket['digests']:
            prompt_text += "Published Analysis:\n"
            for digest in bucket['digests']:
                prompt_text += f"\n**{digest['date']}** (weight: {digest['weight']})\n"
                prompt_text += f"{digest['content'][:500]}...\n"

        # Add key articles from this period
        if bucket['briefings']:
            prompt_text += "\nKey Articles:\n"
            for briefing in bucket['briefings']:
                prompt_text += f"\n{briefing['date']} ({briefing['total_articles']} total, {len(briefing['sampled_articles'])} sampled):\n"
                for i, article in enumerate(briefing['sampled_articles'][:5], 1):
                    prompt_text += f"{i}. [{article['source']}] {article['title']}\n"

    return prompt_text


def main():
    parser = argparse.ArgumentParser(description='Load historical context with temporal weighting')
    parser.add_argument('--output', required=True, help='Output JSON file path')
    parser.add_argument('--prompt-output', help='Optional: Output AI prompt text file')
    args = parser.parse_args()

    print("=" * 70)
    print("📚 LOADING HISTORICAL CONTEXT WITH LOGARITHMIC TEMPORAL DECAY")
    print("=" * 70)

    historical_context = create_historical_context()

    # Save JSON
    with open(args.output, 'w', encoding='utf-8') as f:
        json.dump(historical_context, f, indent=2, ensure_ascii=False)

    print(f"\n✅ Historical context saved to: {args.output}")

    # Save prompt text if requested
    if args.prompt_output:
        prompt_text = format_for_ai_prompt(historical_context)
        with open(args.prompt_output, 'w', encoding='utf-8') as f:
            f.write(prompt_text)
        print(f"✅ AI prompt text saved to: {args.prompt_output}")

    # Print summary
    summary = historical_context['summary']
    print(f"\n📊 SUMMARY:")
    print(f"   Total briefings: {summary['total_briefings']}")
    print(f"   Total articles sampled: {summary['total_articles_sampled']}")
    print(f"   Total digests: {summary['total_digests']}")

    print("\n🎯 Temporal Distribution:")
    for bucket in historical_context['temporal_buckets']:
        briefing_count = len(bucket['briefings'])
        digest_count = len(bucket['digests'])
        print(f"   {bucket['name']:15} {bucket['sample_rate']*100:5.0f}% - {briefing_count} briefings, {digest_count} digests")


if __name__ == '__main__':
    main()
