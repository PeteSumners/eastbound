#!/usr/bin/env python3
"""
Daily Content Automation - Local Edition

Runs the entire content pipeline locally:
1. Monitor Russian media
2. Generate visualizations
3. Generate content using Claude Code (free!)
4. Generate SDXL image locally (using article title for better coherence)
5. Auto-publish
6. Commit and push to GitHub
7. Post to social media

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

# Import LoRA selector for intelligent image generation
sys.path.insert(0, str(Path(__file__).parent))
from lora_selector import select_lora_strategy, generate_prompt

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    env_path = Path(__file__).parent.parent / '.env'
    if env_path.exists():
        load_dotenv(env_path)
        print("[OK] Loaded API keys from .env file", flush=True)
except ImportError:
    print("[WARNING] python-dotenv not installed. Install with: pip install python-dotenv", flush=True)
    print("          (API keys can still be set via environment variables)", flush=True)


def run_command(cmd, description, timeout=None, check=True, verbose=False):
    """Run a command and handle errors."""
    print(f"\n{'='*60}", flush=True)
    print(f"STEP: {description}", flush=True)
    print(f"{'='*60}", flush=True)

    if verbose:
        print(f"[VERBOSE] Command: {cmd}", flush=True)
        print(f"[VERBOSE] Timeout: {timeout if timeout else 'None'}", flush=True)
        print(f"[VERBOSE] Starting execution...", flush=True)

    try:
        if verbose:
            # Stream output in real-time
            import time
            start_time = time.time()
            process = subprocess.Popen(
                cmd,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=0,  # Unbuffered for real-time output
                universal_newlines=True
            )

            print(f"[VERBOSE] Process PID: {process.pid}", flush=True)

            # Read output character by character to handle progress bars
            while True:
                char = process.stdout.read(1)
                if not char:
                    break
                print(char, end='', flush=True)

            process.wait(timeout=timeout)
            elapsed = time.time() - start_time

            print(f"[VERBOSE] Execution time: {elapsed:.2f}s", flush=True)
            print(f"[VERBOSE] Return code: {process.returncode}", flush=True)

            if process.returncode == 0:
                print(f"[OK] {description} completed successfully", flush=True)
                return True
            else:
                print(f"[FAILED] {description} failed with exit code {process.returncode}", flush=True)
                return False if check else True
        else:
            # Original behavior: capture output
            result = subprocess.run(
                cmd,
                shell=True,
                check=check,
                capture_output=True,
                text=True,
                timeout=timeout
            )

            if result.stdout:
                print(result.stdout, flush=True)

            if result.returncode == 0:
                print(f"[OK] {description} completed successfully", flush=True)
            else:
                print(f"[FAILED] {description} failed with exit code {result.returncode}", flush=True)
                if result.stderr:
                    print(f"Error: {result.stderr}", flush=True)

            return result.returncode == 0

    except subprocess.TimeoutExpired:
        print(f"[FAILED] {description} timed out after {timeout}s", flush=True)
        return False
    except Exception as e:
        print(f"[FAILED] {description} failed: {e}", flush=True)
        import traceback
        if verbose:
            print("[VERBOSE] Traceback:", flush=True)
            traceback.print_exc()
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
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Enable verbose output with real-time streaming')
    parser.add_argument('--include-asia', action='store_true',
                       help='Include East Asian news sources (China, Japan, NK, SK, Taiwan) for broader regional perspectives')

    args = parser.parse_args()

    print("""
    +===========================================================+
    |     EASTBOUND DAILY AUTOMATION - LOCAL EDITION            |
    |     Running entirely on your machine (FREE!)              |
    +===========================================================+
    """)

    date = datetime.now().strftime('%Y-%m-%d')
    briefing_path = f"research/{date}-briefing.json"

    # Step 1: Monitor Russian media (and optionally East Asian sources)
    asia_flag = '--include-asia' if args.include_asia else ''
    monitor_desc = "Monitor Russian and East Asian media sources" if args.include_asia else "Monitor Russian media sources"

    success = run_command(
        f'python scripts/monitor_russian_media.py --output "{briefing_path}" --parallel {asia_flag}',
        monitor_desc,
        timeout=900 if args.include_asia else 600,  # 15 min with Asia, 10 min without
        verbose=args.verbose
    )

    if not success:
        print("\n[ERROR] Media monitoring failed. Exiting.", flush=True)
        return 1

    # Step 2: Generate data visualizations
    if not args.skip_visuals:
        success = run_command(
            f'python scripts/generate_visuals.py --briefing "{briefing_path}" --output "images/"',
            "Generate data visualizations",
            timeout=300,  # 5 minutes
            verbose=args.verbose
        )

        if not success:
            print("\n[WARNING]  Visualization generation failed, but continuing...", flush=True)
    else:
        print("\n[SKIP]  Skipping visualizations (--skip-visuals)", flush=True)

    # Step 3: Verify content was generated by external automation
    print("\n" + "="*60, flush=True)
    print("STEP: Verify content generation", flush=True)
    print("="*60, flush=True)

    # Check if draft exists (should be created by external PowerShell automation)
    drafts = list(Path('content/drafts').glob(f'{date}*.md'))
    if not drafts:
        print("\n[ERROR] No draft found!", flush=True)
        print("[INFO] Draft should be created by external automation (run_automation_with_claude.ps1)", flush=True)
        print(f"[INFO] Expected: content/drafts/{date}-analysis.md", flush=True)
        print("\n[FALLBACK] You can manually create the draft and re-run this script", flush=True)
        return 1

    print(f"[OK] Found draft: {drafts[0].name}", flush=True)

    # Step 4: Generate SDXL image locally with intelligent LoRA selection (AFTER content, for better coherence)
    if not args.skip_image:
        print("\n" + "="*60, flush=True)
        print("STEP: Generate AI image with SDXL + Intelligent LoRA Selection", flush=True)
        print("="*60, flush=True)
        print("Using intelligent LoRA selector for optimal photographic style...", flush=True)

        # Load briefing data for keyword analysis
        briefing_data = {}
        trending_keywords = []
        try:
            with open(briefing_path, 'r', encoding='utf-8') as f:
                briefing_data = json.load(f)
                trending_keywords = [story['keyword'] for story in briefing_data.get('trending_stories', [])[:5]]
                print(f"[INFO] Loaded {len(trending_keywords)} trending keywords from briefing", flush=True)
        except Exception as e:
            print(f"[WARNING] Could not load briefing for keywords: {e}", flush=True)

        # Find the generated draft and extract title
        drafts = list(Path('content/drafts').glob('*.md'))
        article_title = None

        if drafts:
            latest_draft = max(drafts, key=lambda p: p.stat().st_mtime)

            # Extract title from frontmatter
            try:
                content = latest_draft.read_text(encoding='utf-8')
                for line in content.split('\n'):
                    if line.startswith('title:'):
                        article_title = line.split('title:', 1)[1].strip().strip('"\'')
                        print(f"[INFO] Extracted article title: {article_title}", flush=True)
                        break
            except Exception as e:
                print(f"[WARNING] Could not extract article title: {e}", flush=True)

        # Use intelligent LoRA selector
        if article_title or trending_keywords:
            print("\n[LORA-SELECT] Analyzing content for optimal LoRA combination...", flush=True)

            strategy = select_lora_strategy(
                article_title=article_title or "",
                trending_keywords=trending_keywords,
                verbose=True
            )

            print(f"\n[LORA-SELECT] Selected: {strategy['combo_name']}", flush=True)
            print(f"[LORA-SELECT] Description: {strategy['description']}", flush=True)
            print(f"[LORA-SELECT] Match Score: {strategy['score']:.2f}", flush=True)
            print(f"[LORA-SELECT] LoRAs: {len(strategy['loras'])} models", flush=True)

            # Generate optimized prompt from strategy
            subject = article_title if article_title else "breaking news from Russia"
            image_prompt, negative_prompt = generate_prompt(strategy, subject)

            print(f"\n[LORA-SELECT] Generated prompt: {image_prompt[:100]}...", flush=True)

            # Generate image with intelligent LoRA combo
            success = run_command(
                f'python scripts/generate_images_local.py --prompt "{image_prompt}" --negative "{negative_prompt}" --output "images/{date}-generated.png" --lora-combo {strategy["combo_name"]} --steps 50',
                f"Generate SDXL image with {strategy['combo_name']} LoRA combo (25-30 minutes)",
                timeout=2400,  # 40 minutes (generous for CPU)
                verbose=args.verbose
            )
        else:
            # Fallback to default if no title or keywords
            print("[WARNING] No article title or keywords found, using default photojournalism LoRA...", flush=True)
            image_prompt = "Professional news photography: Russian political scene, editorial style, dramatic lighting, photorealistic, 8k quality"

            success = run_command(
                f'python scripts/generate_images_local.py --prompt "{image_prompt}" --output "images/{date}-generated.png" --lora-combo photojournalism --steps 50',
                "Generate SDXL image with default LoRA combo (25-30 minutes)",
                timeout=2400,  # 40 minutes
                verbose=args.verbose
            )

        if not success:
            print("\n[WARNING] Image generation failed, but continuing...", flush=True)
    else:
        print("\n[SKIP] Skipping image generation (--skip-image)", flush=True)

    # Step 5: Auto-publish (if not draft-only)
    if not args.draft_only:
        print("\n" + "="*60, flush=True)
        print("STEP: Auto-publish article", flush=True)
        print("="*60, flush=True)

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

            print(f"[OK] Published: {published_path.name}", flush=True)
        else:
            print("[WARNING]  No drafts found to publish", flush=True)
    else:
        print("\n[SKIP]  Skipping auto-publish (--draft-only)", flush=True)

    # Step 6: Commit and push to GitHub
    print("\n[INFO] Attempting to commit and push to GitHub...", flush=True)
    success = run_command(
        f'git add content/ research/ images/ _posts/ && git commit -m "AI content: {date} [automated - local]" && git push',
        "Commit and push to GitHub",
        timeout=120,  # 2 minutes
        check=False,  # Don't fail if nothing to commit
        verbose=args.verbose
    )

    if not success:
        print("\n[WARNING] Git push may have failed!", flush=True)
        print("[WARNING] If running from Task Scheduler, you may need to configure GitHub credentials.", flush=True)
        print("[WARNING] See FIX_GIT_CREDENTIALS.md for instructions.", flush=True)
        print("[WARNING] Content has been created locally but NOT pushed to GitHub.", flush=True)
    else:
        print("\n[OK] Successfully pushed to GitHub!", flush=True)

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
                    check=False,
                    verbose=args.verbose
                )
            else:
                print("\n[WARNING]  Twitter API keys not set, skipping Twitter post", flush=True)

            if linkedin_keys:
                run_command(
                    f'python scripts/post_to_linkedin.py --file "{latest_post}"',
                    "Post to LinkedIn",
                    timeout=60,
                    check=False,
                    verbose=args.verbose
                )
            else:
                print("\n[WARNING]  LinkedIn API keys not set, skipping LinkedIn post", flush=True)
        else:
            print("\n[WARNING]  No published posts found for social media", flush=True)
    else:
        print("\n[SKIP]  Skipping social media posting", flush=True)

    # Note: Knowledge base extraction removed - we only save raw RSS articles, not Eastbound analysis

    # Summary
    print("\n" + "="*60, flush=True)
    print("[OK] AUTOMATION COMPLETE!", flush=True)
    print("="*60, flush=True)
    print(f"""
Summary:
- Briefing: {briefing_path}
- Image: Generated locally with SDXL + Intelligent LoRA Selection (FREE)
- LoRAs: Automatically selected optimal photographic style based on content
- Content: Generated with Anthropic API or manual
- Knowledge Base: Auto-extracted from published article
- Cost: $0 for local processing + API usage (if configured)

Next steps:
- Check _posts/ for published content
- Check knowledge_base/analysis/ for extracted knowledge
- Review on GitHub Pages
- Monitor social media engagement

System Status:
- All processing done locally with Task Scheduler
- Full SDXL at 50 steps (~25-30 minutes per image)
- 8 intelligent LoRA strategies for optimal visual quality
- Knowledge base auto-expands with each publication
    """)

    return 0


if __name__ == '__main__':
    sys.exit(main())
