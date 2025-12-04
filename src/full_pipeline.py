#!/usr/bin/env python3
"""
Full Eastbound Pipeline

Orchestrates the complete daily automation:
1. Fetch articles from Eastern media sources
2. Generate AI summary (Claude)
3. Create voiceover (ElevenLabs or local TTS)
4. Create video (HeyGen or MoviePy)
5. Upload to YouTube
6. Post to Twitter/LinkedIn
7. Commit to GitHub

Usage:
    python full_pipeline.py              # Run full pipeline
    python full_pipeline.py --text-only  # Skip video generation
    python full_pipeline.py --test       # Test mode (no posting)
"""

import os
import sys
import argparse
from pathlib import Path
from datetime import datetime

# Add src directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import Eastbound modules
try:
    from daily_summary import fetch_articles, create_prompt, save_data
except ImportError:
    print("Warning: daily_summary module not found")
    fetch_articles = None

try:
    from automate import call_claude_code, post_to_twitter, post_to_linkedin, git_commit_push
except ImportError:
    print("Warning: automate module not found")
    call_claude_code = None

from generate_voice import generate_voiceover, estimate_audio_duration
from create_video import create_video, create_thumbnail
from upload_youtube import upload_to_youtube, create_video_metadata


class EastboundPipeline:
    """Full Eastbound automation pipeline."""

    def __init__(self, test_mode: bool = False):
        self.test_mode = test_mode
        self.timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        self.output_dir = Path('temp') / self.timestamp
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Track outputs
        self.articles = None
        self.summary = None
        self.audio_file = None
        self.video_file = None
        self.thumbnail_file = None
        self.video_id = None

    def log(self, message: str):
        """Log message with timestamp."""
        timestamp = datetime.now().strftime('%H:%M:%S')
        prefix = "[TEST] " if self.test_mode else ""
        print(f"[{timestamp}] {prefix}{message}")

    def step_1_fetch_articles(self) -> bool:
        """Step 1: Fetch articles from Eastern media sources."""
        self.log("Step 1: Fetching articles from Eastern media...")

        if fetch_articles is None:
            self.log("Using sample data (daily_summary module not available)")
            self.articles = self._get_sample_articles()
            return True

        try:
            self.articles = fetch_articles()
            self.log(f"Fetched {len(self.articles)} articles")
            return True
        except Exception as e:
            self.log(f"Error fetching articles: {e}")
            return False

    def step_2_generate_summary(self) -> bool:
        """Step 2: Generate AI summary using Claude."""
        self.log("Step 2: Generating AI summary...")

        if call_claude_code is None:
            self.log("Using sample summary (automate module not available)")
            self.summary = self._get_sample_summary()
            return True

        try:
            prompt = create_prompt(self.articles)
            self.summary = call_claude_code(prompt)
            self.log(f"Generated summary: {len(self.summary)} chars")
            return True
        except Exception as e:
            self.log(f"Error generating summary: {e}")
            return False

    def step_3_generate_voice(self) -> bool:
        """Step 3: Generate voiceover from summary."""
        self.log("Step 3: Generating voiceover...")

        try:
            self.audio_file = str(self.output_dir / 'voice.mp3')
            duration = estimate_audio_duration(self.summary)
            self.log(f"Estimated audio duration: {duration:.1f}s")

            generate_voiceover(self.summary, self.audio_file)
            self.log(f"Voice generated: {self.audio_file}")
            return True
        except Exception as e:
            self.log(f"Error generating voice: {e}")
            return False

    def step_4_create_video(self) -> bool:
        """Step 4: Create video with voiceover."""
        self.log("Step 4: Creating video...")

        try:
            self.video_file = str(self.output_dir / 'video.mp4')
            create_video(self.summary, self.audio_file, self.video_file)
            self.log(f"Video created: {self.video_file}")

            # Also create thumbnail
            self.thumbnail_file = str(self.output_dir / 'thumbnail.jpg')
            create_thumbnail(self.summary[:100], self.thumbnail_file)

            return True
        except Exception as e:
            self.log(f"Error creating video: {e}")
            return False

    def step_5_upload_youtube(self) -> bool:
        """Step 5: Upload video to YouTube."""
        self.log("Step 5: Uploading to YouTube...")

        if self.test_mode:
            self.log("Test mode - skipping YouTube upload")
            self.video_id = "TEST_VIDEO_ID"
            return True

        try:
            metadata = create_video_metadata(
                self.summary,
                sources=['TASS', 'RT', 'Xinhua', 'NHK', 'Yonhap']
            )

            self.video_id = upload_to_youtube(
                self.video_file,
                title=metadata['title'],
                description=metadata['description'],
                tags=metadata['tags'],
                thumbnail_file=self.thumbnail_file
            )

            self.log(f"Video uploaded: https://youtube.com/watch?v={self.video_id}")
            return True
        except Exception as e:
            self.log(f"Error uploading to YouTube: {e}")
            return False

    def step_6_post_social(self) -> bool:
        """Step 6: Post to Twitter and LinkedIn."""
        self.log("Step 6: Posting to social media...")

        if self.test_mode:
            self.log("Test mode - skipping social media posts")
            return True

        if post_to_twitter is None:
            self.log("Social posting not available (automate module not found)")
            return True

        try:
            # Append YouTube link to summary for social
            social_text = self.summary
            if self.video_id:
                social_text += f"\n\nWatch: https://youtube.com/watch?v={self.video_id}"

            post_to_twitter(social_text, self.articles)
            post_to_linkedin(social_text, self.articles)
            self.log("Posted to Twitter and LinkedIn")
            return True
        except Exception as e:
            self.log(f"Error posting to social: {e}")
            return False

    def step_7_commit_git(self) -> bool:
        """Step 7: Commit and push to GitHub."""
        self.log("Step 7: Committing to GitHub...")

        if self.test_mode:
            self.log("Test mode - skipping git commit")
            return True

        try:
            # Save summary to posts directory
            post_file = Path('posts') / f"{datetime.now().strftime('%Y-%m-%d-%H%M%S')}-summary.md"
            post_file.parent.mkdir(exist_ok=True)

            with open(post_file, 'w') as f:
                f.write(f"# Eastbound Report - {datetime.now().strftime('%B %d, %Y')}\n\n")
                f.write(self.summary)
                if self.video_id:
                    f.write(f"\n\n[Watch on YouTube](https://youtube.com/watch?v={self.video_id})\n")

            if git_commit_push:
                git_commit_push()
                self.log("Committed and pushed to GitHub")

            return True
        except Exception as e:
            self.log(f"Error with git: {e}")
            return False

    def run(self, skip_video: bool = False) -> bool:
        """
        Run the full pipeline.

        Args:
            skip_video: Skip video generation (text-only mode)

        Returns:
            True if successful, False otherwise
        """
        self.log("=" * 60)
        self.log("EASTBOUND FULL PIPELINE")
        self.log("=" * 60)

        steps = [
            ("Fetch Articles", self.step_1_fetch_articles),
            ("Generate Summary", self.step_2_generate_summary),
        ]

        if not skip_video:
            steps.extend([
                ("Generate Voice", self.step_3_generate_voice),
                ("Create Video", self.step_4_create_video),
                ("Upload YouTube", self.step_5_upload_youtube),
            ])

        steps.extend([
            ("Post Social", self.step_6_post_social),
            ("Commit Git", self.step_7_commit_git),
        ])

        for step_name, step_func in steps:
            if not step_func():
                self.log(f"FAILED at: {step_name}")
                return False

        self.log("=" * 60)
        self.log("PIPELINE COMPLETE!")
        self.log("=" * 60)

        if self.video_id and self.video_id != "TEST_VIDEO_ID":
            self.log(f"YouTube: https://youtube.com/watch?v={self.video_id}")

        return True

    def _get_sample_articles(self) -> list:
        """Return sample articles for testing."""
        return [
            {"title": "Russia-China energy deal", "source": "TASS"},
            {"title": "Belt and Road investment", "source": "Xinhua"},
            {"title": "Japan semiconductor update", "source": "NHK"},
        ]

    def _get_sample_summary(self) -> str:
        """Return sample summary for testing."""
        return """
        Today's Eastbound Financial Analysis.

        Russian energy markets showed significant movement as TASS reported
        new pipeline agreements with Asian partners, strengthening Eastern
        energy corridors.

        Chinese state media emphasized continued Belt and Road investments,
        with particular focus on Central Asian infrastructure development.

        Japanese semiconductor developments signal shifting supply chain
        dynamics, with NHK reporting increased domestic production capacity.

        Key takeaway: Eastern markets are positioning for increased regional
        economic cooperation, with energy and technology as primary drivers.
        """


def main():
    parser = argparse.ArgumentParser(
        description="Eastbound Full Pipeline - Daily automation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python full_pipeline.py              # Run full pipeline
    python full_pipeline.py --test       # Test mode (no posting)
    python full_pipeline.py --text-only  # Skip video generation
        """
    )

    parser.add_argument('--test', action='store_true',
                       help='Test mode - no actual posting')
    parser.add_argument('--text-only', action='store_true',
                       help='Skip video generation (text/social only)')

    args = parser.parse_args()

    pipeline = EastboundPipeline(test_mode=args.test)
    success = pipeline.run(skip_video=args.text_only)

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
