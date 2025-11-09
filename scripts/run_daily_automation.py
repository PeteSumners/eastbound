#!/usr/bin/env python3
"""
Daily Content Automation - Local Edition

Runs the entire content pipeline locally:
1. Monitor Russian media
2. Generate SDXL image locally
3. Generate visualizations
4. Generate content using Claude Code (free!)
5. Auto-publish
6. Post to social media
7. Commit and push to GitHub

All for FREE (no GitHub Actions, no API costs)!

Usage:
    python scripts/run_daily_automation.py
    python scripts/run_daily_automation.py --skip-image  # Skip image gen if already done
    python scripts/run_daily_automation.py --draft-only  # Create draft, don't publish
"""

import argparse
import subprocess
import sys
import json
from pathlib import Path
from datetime import datetime
import os

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    env_path = Path(__file__).parent.parent / '.env'
    if env_path.exists():
        load_dotenv(env_path)
        print(f"✓ Loaded API keys from .env file")
except ImportError:
    print("⚠️  python-dotenv not installed. Install with: pip install python-dotenv")
    print("   (API keys can still be set via environment variables)")


def run_command(cmd, description, timeout=None, check=True):
    """Run a command and handle errors."""
    print(f"\n{'='*60}")
    print(f"STEP: {description}")
    print(f"{'='*60}")

    try:
        result = subprocess.run(
            cmd,
            shell=True,
            check=check,
            capture_output=True,
            text=True,
            timeout=timeout
        )

        if result.stdout:
            print(result.stdout)

        if result.returncode == 0:
            print(f"✓ {description} completed successfully")
        else:
            print(f"✗ {description} failed with exit code {result.returncode}")
            if result.stderr:
                print(f"Error: {result.stderr}")

        return result.returncode == 0

    except subprocess.TimeoutExpired:
        print(f"✗ {description} timed out")
        return False
    except Exception as e:
        print(f"✗ {description} failed: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(description='Run daily content automation locally')
    parser.add_argument('--skip-image', action='store_true',
                       help='Skip image generation (if already generated)')
    parser.add_argument('--skip-social', action='store_true',
                       help='Skip social media posting')
    parser.add_argument('--draft-only', action='store_true',
                       help='Create draft only, do not auto-publish')
    parser.add_argument('--skip-visuals', action='store_true',
                       help='Skip data visualization generation')

    args = parser.parse_args()

    print("""
    ╔═══════════════════════════════════════════════════════════╗
    ║     EASTBOUND DAILY AUTOMATION - LOCAL EDITION            ║
    ║     Running entirely on your machine (FREE!)              ║
    ╚═══════════════════════════════════════════════════════════╝
    """)

    date = datetime.now().strftime('%Y-%m-%d')
    briefing_path = f"research/{date}-briefing.json"

    # Step 1: Monitor Russian media
    success = run_command(
        f'python scripts/monitor_russian_media.py --output "{briefing_path}" --parallel',
        "Monitor Russian media sources",
        timeout=600  # 10 minutes
    )

    if not success:
        print("\n❌ Media monitoring failed. Exiting.")
        return 1

    # Step 2: Generate SDXL image locally
    if not args.skip_image:
        success = run_command(
            f'python scripts/generate_images_local.py --briefing "{briefing_path}" --output "images/" --auto --steps 50',
            "Generate AI image with SDXL (this takes 15-20 minutes)",
            timeout=1800  # 30 minutes
        )

        if not success:
            print("\n⚠️  Image generation failed, but continuing...")
    else:
        print("\n⏭️  Skipping image generation (--skip-image)")

    # Step 3: Generate data visualizations
    if not args.skip_visuals:
        success = run_command(
            f'python scripts/generate_visuals.py --briefing "{briefing_path}" --output "images/"',
            "Generate data visualizations",
            timeout=300  # 5 minutes
        )

        if not success:
            print("\n⚠️  Visualization generation failed, but continuing...")
    else:
        print("\n⏭️  Skipping visualizations (--skip-visuals)")

    # Step 4: Generate content using Claude Code (FREE!)
    print("\n" + "="*60)
    print("STEP: Generate AI content using Claude Code")
    print("="*60)
    print("Using Claude Code CLI for FREE content generation...")

    # Create the prompt for Claude Code
    claude_prompt = f"""You are a content writer for Eastbound, a Russian media analysis service.

Read the briefing file at: {briefing_path}

Generate a high-quality analysis article following our content guidelines in CLAUDE.md.

The article should:
1. Analyze the top trending stories from Russian media
2. Provide cultural and political context for English-speaking audiences
3. Compare with Western media coverage
4. Be 1000-1500 words
5. Include proper frontmatter in Jekyll format
6. Be saved to content/drafts/{date}-analysis.md

Use the Write tool to create the article file."""

    # Run Claude Code in non-interactive mode
    result = subprocess.run(
        [
            'claude',
            '--print',
            '--output-format', 'text',
            '--tools', 'Read,Write,Glob',
            claude_prompt
        ],
        capture_output=True,
        text=True,
        timeout=300  # 5 minutes
    )

    if result.returncode == 0:
        print("✓ Content generation completed successfully")
        print(result.stdout)
    else:
        print("✗ Content generation failed")
        print(result.stderr)
        print("\n❌ Content generation failed. Exiting.")
        return 1

    # Step 5: Auto-publish (if not draft-only)
    if not args.draft_only:
        print("\n" + "="*60)
        print("STEP: Auto-publish article")
        print("="*60)

        # Find latest draft
        drafts = list(Path('content/drafts').glob('*.md'))
        if drafts:
            latest_draft = max(drafts, key=lambda p: p.stat().st_mtime)

            # Update frontmatter
            content = latest_draft.read_text(encoding='utf-8')
            content = content.replace('status: draft', 'status: published')

            # Move to _posts
            published_path = Path('_posts') / latest_draft.name
            published_path.write_text(content, encoding='utf-8')
            latest_draft.unlink()

            print(f"✓ Published: {published_path.name}")
        else:
            print("⚠️  No drafts found to publish")
    else:
        print("\n⏭️  Skipping auto-publish (--draft-only)")

    # Step 6: Commit and push to GitHub
    success = run_command(
        f'git add content/ research/ images/ _posts/ && git commit -m "AI content: {date} [automated - local]" && git push',
        "Commit and push to GitHub",
        timeout=120  # 2 minutes,
        check=False  # Don't fail if nothing to commit
    )

    # Step 7: Post to social media
    if not args.skip_social and not args.draft_only:
        # Find published post
        posts = list(Path('_posts').glob('*.md'))
        if posts:
            latest_post = max(posts, key=lambda p: p.stat().st_mtime)

            # Check if API keys are set
            twitter_keys = all([
                os.getenv('TWITTER_API_KEY'),
                os.getenv('TWITTER_API_SECRET'),
                os.getenv('TWITTER_ACCESS_TOKEN'),
                os.getenv('TWITTER_ACCESS_TOKEN_SECRET')
            ])

            linkedin_keys = all([
                os.getenv('LINKEDIN_ACCESS_TOKEN'),
                os.getenv('LINKEDIN_USER_URN')
            ])

            if twitter_keys:
                run_command(
                    f'python scripts/post_to_twitter.py --file "{latest_post}"',
                    "Post to Twitter",
                    timeout=60,
                    check=False
                )
            else:
                print("\n⚠️  Twitter API keys not set, skipping Twitter post")

            if linkedin_keys:
                run_command(
                    f'python scripts/post_to_linkedin.py --file "{latest_post}"',
                    "Post to LinkedIn",
                    timeout=60,
                    check=False
                )
            else:
                print("\n⚠️  LinkedIn API keys not set, skipping LinkedIn post")
        else:
            print("\n⚠️  No published posts found for social media")
    else:
        print("\n⏭️  Skipping social media posting")

    # Summary
    print("\n" + "="*60)
    print("✓ AUTOMATION COMPLETE!")
    print("="*60)
    print(f"""
Summary:
- Briefing: {briefing_path}
- Image: Generated locally with SDXL (FREE)
- Content: Generated with Claude Code (FREE)
- Cost: $0 (except social media API usage)

Next steps:
- Check _posts/ for published content
- Review on GitHub Pages
- Monitor social media engagement
    """)

    return 0


if __name__ == '__main__':
    sys.exit(main())
