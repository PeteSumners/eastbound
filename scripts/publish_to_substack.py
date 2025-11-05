#!/usr/bin/env python3
"""
Publish a markdown file to Substack.

Supports two methods:
1. Substack API (if available)
2. Email-based publishing (send to your-subdomain@substack.com)

Usage:
    python publish_to_substack.py --file content/scheduled/2024-11-05-my-post.md
"""

import argparse
import os
import re
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from pathlib import Path
import yaml
import markdown


def parse_frontmatter(content):
    """Extract YAML frontmatter and content from markdown file."""
    pattern = r'^---\s*\n(.*?\n)---\s*\n(.*)$'
    match = re.match(pattern, content, re.DOTALL)

    if match:
        frontmatter = yaml.safe_load(match.group(1))
        body = match.group(2)
        return frontmatter, body
    else:
        return {}, content


def markdown_to_html(md_content):
    """Convert markdown to HTML for email/Substack."""
    html = markdown.markdown(md_content, extensions=[
        'markdown.extensions.fenced_code',
        'markdown.extensions.tables',
        'markdown.extensions.nl2br',
    ])
    return html


def publish_via_email(frontmatter, content_html, content_md):
    """
    Publish to Substack via email.

    Substack accepts posts sent to: your-subdomain@substack.com
    Subject line becomes the title.
    Email body becomes the post content.

    Requires environment variables:
    - SUBSTACK_EMAIL: Your Substack publication email (subdomain@substack.com)
    - SMTP_SERVER: Your SMTP server (e.g., smtp.gmail.com)
    - SMTP_PORT: SMTP port (usually 587)
    - SMTP_USERNAME: Your email username
    - SMTP_PASSWORD: Your email password or app-specific password
    """

    substack_email = os.getenv('SUBSTACK_EMAIL')
    smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
    smtp_port = int(os.getenv('SMTP_PORT', '587'))
    smtp_username = os.getenv('SMTP_USERNAME')
    smtp_password = os.getenv('SMTP_PASSWORD')

    if not all([substack_email, smtp_username, smtp_password]):
        raise ValueError(
            "Missing required environment variables:\n"
            "- SUBSTACK_EMAIL (your-subdomain@substack.com)\n"
            "- SMTP_USERNAME (your email)\n"
            "- SMTP_PASSWORD (your email password)\n"
            "Set these in GitHub Secrets for automation."
        )

    # Create message
    msg = MIMEMultipart('alternative')
    msg['From'] = smtp_username
    msg['To'] = substack_email

    # Build subject line (set once to avoid multiple Subject headers)
    subject = frontmatter.get('title', 'Untitled Post')
    if frontmatter.get('subtitle'):
        subject += f" - {frontmatter['subtitle']}"
    msg['Subject'] = subject

    # Attach both plain text and HTML versions
    part_text = MIMEText(content_md, 'plain', 'utf-8')
    part_html = MIMEText(content_html, 'html', 'utf-8')

    msg.attach(part_text)
    msg.attach(part_html)

    # Send email
    print(f"📧 Sending post to Substack via email...")
    print(f"   To: {substack_email}")
    print(f"   Subject: {msg['Subject']}")

    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(smtp_username, smtp_password)
            server.send_message(msg)

        print(f"✅ Post sent successfully!")
        print(f"⚠️  Note: Check your Substack drafts to review and publish.")
        return True

    except Exception as e:
        print(f"❌ Error sending email: {e}")
        return False


def move_to_published(file_path):
    """Move file from scheduled to published folder."""
    published_dir = file_path.parent.parent / "published"
    published_dir.mkdir(parents=True, exist_ok=True)

    new_path = published_dir / file_path.name

    # Copy content with updated status
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Update status in frontmatter
    content = re.sub(
        r'status:\s*scheduled',
        'status: published',
        content
    )

    with open(new_path, 'w', encoding='utf-8') as f:
        f.write(content)

    # Remove original
    file_path.unlink()

    print(f"📁 Moved to: {new_path}")


def main():
    parser = argparse.ArgumentParser(description='Publish markdown file to Substack')
    parser.add_argument('--file', required=True, help='Path to markdown file to publish')
    parser.add_argument('--dry-run', action='store_true', help='Preview without publishing')

    args = parser.parse_args()

    file_path = Path(args.file)

    if not file_path.exists():
        print(f"❌ Error: File not found: {file_path}")
        return

    # Read file
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Parse frontmatter
    frontmatter, body = parse_frontmatter(content)

    # Check status
    if frontmatter.get('status') not in ['scheduled', 'published']:
        print(f"⚠️  Warning: Post status is '{frontmatter.get('status')}', not 'scheduled'")
        print(f"   Change status to 'scheduled' to publish automatically")
        return

    # Convert to HTML
    html = markdown_to_html(body)

    if args.dry_run:
        print("=== DRY RUN MODE ===")
        print(f"Title: {frontmatter.get('title')}")
        print(f"Subtitle: {frontmatter.get('subtitle')}")
        print(f"Type: {frontmatter.get('type')}")
        print(f"Status: {frontmatter.get('status')}")
        print(f"\nContent preview (first 200 chars):")
        print(body[:200] + "...")
        return

    # Publish via email
    success = publish_via_email(frontmatter, html, body)

    if success:
        # Move to published folder
        move_to_published(file_path)


if __name__ == '__main__':
    main()
