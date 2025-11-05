#!/usr/bin/env python3
"""
Create a new draft from a template.

Usage:
    python create_draft.py --type weekly-analysis --title "Your Title"
    python create_draft.py --type translation --title "Translation Title" --original-url "https://..."
"""

import argparse
import os
from datetime import datetime, timedelta
from pathlib import Path
import re


def slugify(text):
    """Convert text to URL-safe slug."""
    text = text.lower()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[-\s]+', '-', text)
    return text.strip('-')


def create_draft(content_type, title, original_url=None, schedule_days=None):
    """Create a new draft from a template."""

    # Paths
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    template_path = project_root / "templates" / f"{content_type}.md"
    drafts_dir = project_root / "content" / "drafts"

    # Check if template exists
    if not template_path.exists():
        print(f"Error: Template not found at {template_path}")
        print(f"Available templates: weekly-analysis, translation")
        return

    # Read template
    with open(template_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Replace placeholders
    today = datetime.now()
    publish_date = today if not schedule_days else today + timedelta(days=schedule_days)

    content = content.replace('[Title: What Happened and Why It Matters]', title)
    content = content.replace('[Translation: Title of Original Article/Speech/Statement]', title)
    content = content.replace('[Title]', title)
    content = content.replace('YYYY-MM-DD', publish_date.strftime('%Y-%m-%d'))

    if original_url:
        content = content.replace('[URL to Russian original]', original_url)
        content = content.replace('original_url: ""', f'original_url: "{original_url}"')

    # Generate filename
    slug = slugify(title)
    filename = f"{publish_date.strftime('%Y-%m-%d')}-{slug}.md"
    output_path = drafts_dir / filename

    # Create drafts directory if it doesn't exist
    drafts_dir.mkdir(parents=True, exist_ok=True)

    # Write draft
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(content)

    print(f"✅ Draft created: {output_path}")
    print(f"📝 Edit your draft and change status from 'draft' to 'scheduled' when ready")

    return output_path


def main():
    parser = argparse.ArgumentParser(description='Create a new Eastbound draft from template')
    parser.add_argument('--type', required=True, choices=['weekly-analysis', 'translation'],
                        help='Type of content to create')
    parser.add_argument('--title', required=True, help='Title of the post')
    parser.add_argument('--original-url', help='URL of original Russian source (for translations)')
    parser.add_argument('--schedule-days', type=int, help='Schedule post N days from now')

    args = parser.parse_args()

    create_draft(args.type, args.title, args.original_url, args.schedule_days)


if __name__ == '__main__':
    main()
