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
        print("[OK] Loaded API keys from .env file")
except ImportError:
    print("[WARNING] python-dotenv not installed. Install with: pip install python-dotenv")
    print("          (API keys can still be set via environment variables)")


def run_command(cmd, description, timeout=None, check=True, verbose=False):
    """Run a command and handle errors."""
    print(f"\n{'='*60}")
    print(f"STEP: {description}")
    print(f"{'='*60}")

    if verbose:
        print(f"[VERBOSE] Command: {cmd}")
        print(f"[VERBOSE] Timeout: {timeout if timeout else 'None'}")
        print(f"[VERBOSE] Starting execution...")

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

            print(f"[VERBOSE] Process PID: {process.pid}")

            # Read output character by character to handle progress bars
            while True:
                char = process.stdout.read(1)
                if not char:
                    break
                print(char, end='', flush=True)

            process.wait(timeout=timeout)
            elapsed = time.time() - start_time

            print(f"[VERBOSE] Execution time: {elapsed:.2f}s")
            print(f"[VERBOSE] Return code: {process.returncode}")

            if process.returncode == 0:
                print(f"[OK] {description} completed successfully")
                return True
            else:
                print(f"[FAILED] {description} failed with exit code {process.returncode}")
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
                print(result.stdout)

            if result.returncode == 0:
                print(f"[OK] {description} completed successfully")
            else:
                print(f"[FAILED] {description} failed with exit code {result.returncode}")
                if result.stderr:
                    print(f"Error: {result.stderr}")

            return result.returncode == 0

    except subprocess.TimeoutExpired:
        print(f"[FAILED] {description} timed out after {timeout}s")
        return False
    except Exception as e:
        print(f"[FAILED] {description} failed: {e}")
        import traceback
        if verbose:
            print("[VERBOSE] Traceback:")
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
        print("\n[ERROR] Media monitoring failed. Exiting.")
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
            print("\n[WARNING]  Visualization generation failed, but continuing...")
    else:
        print("\n[SKIP]  Skipping visualizations (--skip-visuals)")

    # Step 3: Generate content using Claude Code (FREE!)
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
5. Include proper frontmatter in Jekyll format with these required fields:
   - title, date, author, categories, tags, excerpt
   - **IMPORTANT**: categories must be from [Analysis, News, Translation] and ONE region [Russia, Ukraine, EasternEurope, CentralAsia, Caucasus] - NO SPACES in category names
   - **IMPORTANT**: image: /images/{date}-generated.png (plain path in frontmatter - Jekyll handles baseurl)
6. **IMPORTANT**: Do NOT include an H1 heading (# Title) after the frontmatter. The Jekyll layout displays the title automatically from the frontmatter.
7. **IMPORTANT**: Immediately after the frontmatter, before the first paragraph, include this image caption for transparency:

   <p style="text-align: center; font-size: 0.9em; color: #666; font-style: italic; margin-top: -10px; margin-bottom: 20px;">
   Hero image: AI-generated illustration created with Stable Diffusion XL
   </p>

   Then start the content with the first paragraph.
8. **IMPORTANT**: Before the "## Key Articles Referenced" section, include a "## Data Visualizations" section with smaller embedded images:

   ---

   ## Data Visualizations

   <div style="display: flex; flex-wrap: wrap; gap: 20px; justify-content: space-between;">
     <div style="flex: 1; min-width: 300px;">
       <h3>Trending Topics</h3>
       <img src="{{{{site.baseurl}}}}/images/{date}-keywords.png" alt="Keyword Trends" style="width: 100%; max-width: 500px;">
     </div>

     <div style="flex: 1; min-width: 300px;">
       <h3>Source Distribution</h3>
       <img src="{{{{site.baseurl}}}}/images/{date}-sources.png" alt="Source Distribution" style="width: 100%; max-width: 500px;">
     </div>
   </div>

   <div style="margin-top: 20px;">
     <h3>By The Numbers</h3>
     <img src="{{{{site.baseurl}}}}/images/{date}-stats.png" alt="Statistics" style="width: 100%; max-width: 600px;">
   </div>

   ---
9. **IMPORTANT**: Include a "## Stakeholder Perspectives: Real-World Impact" section before the "Key Articles Referenced" section

   This section demonstrates how abstract geopolitical narratives affect real people around the world. Generate 4 random stakeholder personas using the script at scripts/generate_stakeholder_personas.py with the briefing file.

   **Section Introduction (include this explanation verbatim):**
   "*The following section presents randomly generated personas from around the world who have material stakes in today's Russian media narratives. These are NOT representative samples or opinion polls—they're concrete examples of how abstract geopolitics affects real people with real interests. Each persona is randomly selected from a global pool representing diverse countries, occupations, and socioeconomic backgrounds. The goal is to humanize complex narratives by showing who is affected and how.*"

   **Format for each persona:**
   ### Stakeholder [N]: [Name]

   **Profile:**
   - **Age:** [age]
   - **Location:** [city, country]
   - **Occupation:** [occupation]
   - **Background:** [descriptors]

   **Personal Stakes:**
   - [stake 1]
   - [stake 2]

   **Perspective:** [perspective]

   **What Today's Russian Media Means for [Name]:**
   [Write 2-3 sentences analyzing how today's SPECIFIC trending narratives from the briefing affect this persona's material interests, decisions, or worldview. Reference specific stories from today's coverage.]

   ---

10. **IMPORTANT**: Include a "## Key Articles Referenced" section at the end with links to the original articles from the briefing
   - Extract article URLs from the briefing JSON
   - Format as a bulleted list with article titles and links
   - Group by source (TASS, RT, Kommersant, etc.)
11. Be saved to content/drafts/{date}-analysis.md

Use the Write tool to create the article file."""

    # Save prompt to temp file to avoid shell escaping issues
    prompt_file = Path('temp_prompt.txt')
    prompt_file.write_text(claude_prompt, encoding='utf-8')

    # Run Claude Code in non-interactive mode
    try:
        result = subprocess.run(
            'claude --print --output-format text --tools Read,Write,Glob < temp_prompt.txt',
            shell=True,
            capture_output=True,
            text=True,
            timeout=300  # 5 minutes
        )

        # Clean up temp file
        prompt_file.unlink(missing_ok=True)

        if result.returncode == 0:
            print("[OK] Content generation completed successfully")
            if result.stdout:
                print("[STDOUT]", result.stdout[:500])  # First 500 chars
        else:
            print("[FAILED] Content generation failed")
            print(f"[DEBUG] Return code: {result.returncode}")
            if result.stdout:
                print(f"[DEBUG] Stdout: {result.stdout}")
            if result.stderr:
                print(f"[DEBUG] Stderr: {result.stderr}")
            else:
                print("[DEBUG] Stderr was empty")
            print("\n[ERROR] Content generation failed. Exiting.")
            return 1
    except Exception as e:
        prompt_file.unlink(missing_ok=True)
        print(f"[ERROR] Claude Code execution failed: {e}")
        return 1

    # Step 4: Generate SDXL image locally with intelligent LoRA selection (AFTER content, for better coherence)
    if not args.skip_image:
        print("\n" + "="*60)
        print("STEP: Generate AI image with SDXL + Intelligent LoRA Selection")
        print("="*60)
        print("Using intelligent LoRA selector for optimal photographic style...")

        # Load briefing data for keyword analysis
        briefing_data = {}
        trending_keywords = []
        try:
            with open(briefing_path, 'r', encoding='utf-8') as f:
                briefing_data = json.load(f)
                trending_keywords = [story['keyword'] for story in briefing_data.get('trending_stories', [])[:5]]
                print(f"[INFO] Loaded {len(trending_keywords)} trending keywords from briefing")
        except Exception as e:
            print(f"[WARNING] Could not load briefing for keywords: {e}")

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
                        print(f"[INFO] Extracted article title: {article_title}")
                        break
            except Exception as e:
                print(f"[WARNING] Could not extract article title: {e}")

        # Use intelligent LoRA selector
        if article_title or trending_keywords:
            print("\n[LORA-SELECT] Analyzing content for optimal LoRA combination...")

            strategy = select_lora_strategy(
                article_title=article_title or "",
                trending_keywords=trending_keywords,
                verbose=True
            )

            print(f"\n[LORA-SELECT] Selected: {strategy['combo_name']}")
            print(f"[LORA-SELECT] Description: {strategy['description']}")
            print(f"[LORA-SELECT] Match Score: {strategy['score']:.2f}")
            print(f"[LORA-SELECT] LoRAs: {len(strategy['loras'])} models")

            # Generate optimized prompt from strategy
            subject = article_title if article_title else "breaking news from Russia"
            image_prompt, negative_prompt = generate_prompt(strategy, subject)

            print(f"\n[LORA-SELECT] Generated prompt: {image_prompt[:100]}...")

            # Generate image with intelligent LoRA combo
            success = run_command(
                f'python scripts/generate_images_local.py --prompt "{image_prompt}" --negative "{negative_prompt}" --output "images/{date}-generated.png" --lora-combo {strategy["combo_name"]} --steps 50',
                f"Generate SDXL image with {strategy['combo_name']} LoRA combo (25-30 minutes)",
                timeout=2400,  # 40 minutes (generous for CPU)
                verbose=args.verbose
            )
        else:
            # Fallback to default if no title or keywords
            print("[WARNING] No article title or keywords found, using default photojournalism LoRA...")
            image_prompt = "Professional news photography: Russian political scene, editorial style, dramatic lighting, photorealistic, 8k quality"

            success = run_command(
                f'python scripts/generate_images_local.py --prompt "{image_prompt}" --output "images/{date}-generated.png" --lora-combo photojournalism --steps 50',
                "Generate SDXL image with default LoRA combo (25-30 minutes)",
                timeout=2400,  # 40 minutes
                verbose=args.verbose
            )

        if not success:
            print("\n[WARNING] Image generation failed, but continuing...")
    else:
        print("\n[SKIP] Skipping image generation (--skip-image)")

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

            print(f"[OK] Published: {published_path.name}")
        else:
            print("[WARNING]  No drafts found to publish")
    else:
        print("\n[SKIP]  Skipping auto-publish (--draft-only)")

    # Step 6: Commit and push to GitHub
    print("\n[INFO] Attempting to commit and push to GitHub...")
    success = run_command(
        f'git add content/ research/ images/ _posts/ && git commit -m "AI content: {date} [automated - local]" && git push',
        "Commit and push to GitHub",
        timeout=120,  # 2 minutes
        check=False,  # Don't fail if nothing to commit
        verbose=args.verbose
    )

    if not success:
        print("\n[WARNING] ⚠️  Git push may have failed!")
        print("[WARNING] If running from Task Scheduler, you may need to configure GitHub credentials.")
        print("[WARNING] See FIX_GIT_CREDENTIALS.md for instructions.")
        print("[WARNING] Content has been created locally but NOT pushed to GitHub.")
    else:
        print("\n[OK] ✓ Successfully pushed to GitHub!")

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
                print("\n[WARNING]  Twitter API keys not set, skipping Twitter post")

            if linkedin_keys:
                run_command(
                    f'python scripts/post_to_linkedin.py --file "{latest_post}"',
                    "Post to LinkedIn",
                    timeout=60,
                    check=False,
                    verbose=args.verbose
                )
            else:
                print("\n[WARNING]  LinkedIn API keys not set, skipping LinkedIn post")
        else:
            print("\n[WARNING]  No published posts found for social media")
    else:
        print("\n[SKIP]  Skipping social media posting")

    # Summary
    print("\n" + "="*60)
    print("[OK] AUTOMATION COMPLETE!")
    print("="*60)
    print(f"""
Summary:
- Briefing: {briefing_path}
- Image: Generated locally with SDXL + Intelligent LoRA Selection (FREE)
- LoRAs: Automatically selected optimal photographic style based on content
- Content: Generated with Claude Code (FREE)
- Cost: $0 (completely free, runs on your laptop)

Next steps:
- Check _posts/ for published content
- Review on GitHub Pages
- Monitor social media engagement

System Status:
- All processing done locally with cron scheduling
- No GitHub Actions (removed - using local cron only)
- Full SDXL at 50 steps (~25-30 minutes per image)
- 8 intelligent LoRA strategies for optimal visual quality
    """)

    return 0


if __name__ == '__main__':
    sys.exit(main())
