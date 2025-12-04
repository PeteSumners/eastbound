#!/usr/bin/env python3
"""
YouTube Upload for Eastbound Reports

Uploads videos to YouTube with metadata, thumbnails, and scheduling.

Setup:
    pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client

    1. Create project at https://console.cloud.google.com/
    2. Enable YouTube Data API v3
    3. Create OAuth 2.0 credentials (Desktop app)
    4. Download credentials.json to this directory
    5. First run will open browser for authorization

Usage:
    from upload_youtube import upload_to_youtube
    video_id = upload_to_youtube("video.mp4", "Title", "Description", ["tag1", "tag2"])
"""

import os
import pickle
import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Optional

# Try to import Google API libraries
GOOGLE_API_AVAILABLE = False
try:
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from google.auth.transport.requests import Request
    from googleapiclient.discovery import build
    from googleapiclient.http import MediaFileUpload
    from googleapiclient.errors import HttpError
    GOOGLE_API_AVAILABLE = True
except ImportError:
    pass


# YouTube API scopes
SCOPES = ['https://www.googleapis.com/auth/youtube.upload']

# File paths
CREDENTIALS_FILE = 'config/youtube_credentials.json'
TOKEN_FILE = 'config/youtube_token.pickle'

# Default video settings
DEFAULT_CATEGORY = '25'  # News & Politics
DEFAULT_PRIVACY = 'public'
DEFAULT_LANGUAGE = 'en'


def get_credentials():
    """
    Get valid YouTube API credentials.

    First run will open browser for OAuth authorization.
    Subsequent runs use cached token.
    """
    if not GOOGLE_API_AVAILABLE:
        raise ImportError("Google API libraries not installed. Run: pip install google-auth google-auth-oauthlib google-api-python-client")

    creds = None

    # Load cached token if exists
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, 'rb') as token:
            creds = pickle.load(token)

    # If no valid creds, get new ones
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not os.path.exists(CREDENTIALS_FILE):
                raise FileNotFoundError(
                    f"YouTube credentials not found at {CREDENTIALS_FILE}\n"
                    "Download from Google Cloud Console and save as youtube_credentials.json"
                )

            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)

        # Save credentials for next run
        Path(TOKEN_FILE).parent.mkdir(parents=True, exist_ok=True)
        with open(TOKEN_FILE, 'wb') as token:
            pickle.dump(creds, token)

    return creds


def upload_to_youtube(
    video_file: str,
    title: str,
    description: str,
    tags: List[str] = None,
    category: str = DEFAULT_CATEGORY,
    privacy: str = DEFAULT_PRIVACY,
    thumbnail_file: str = None,
    scheduled_time: datetime = None
) -> str:
    """
    Upload video to YouTube.

    Args:
        video_file: Path to video file
        title: Video title (max 100 chars)
        description: Video description (max 5000 chars)
        tags: List of tags (optional)
        category: YouTube category ID (default: News & Politics)
        privacy: 'public', 'private', or 'unlisted'
        thumbnail_file: Path to thumbnail image (optional)
        scheduled_time: When to publish (for scheduled uploads)

    Returns:
        YouTube video ID
    """
    if not GOOGLE_API_AVAILABLE:
        raise ImportError("Google API libraries not installed")

    if not os.path.exists(video_file):
        raise FileNotFoundError(f"Video file not found: {video_file}")

    # Validate inputs
    title = title[:100]  # Max 100 chars
    description = description[:5000]  # Max 5000 chars
    tags = tags or []

    print(f"Uploading to YouTube: {title}")

    # Build YouTube API client
    youtube = build('youtube', 'v3', credentials=get_credentials())

    # Video metadata
    body = {
        'snippet': {
            'title': title,
            'description': description,
            'tags': tags,
            'categoryId': category,
            'defaultLanguage': DEFAULT_LANGUAGE,
            'defaultAudioLanguage': DEFAULT_LANGUAGE
        },
        'status': {
            'privacyStatus': privacy,
            'selfDeclaredMadeForKids': False,
            'embeddable': True,
            'publicStatsViewable': True
        }
    }

    # Add scheduled publish time if provided
    if scheduled_time and privacy == 'private':
        body['status']['publishAt'] = scheduled_time.isoformat()
        body['status']['privacyStatus'] = 'private'

    # Create media upload
    media = MediaFileUpload(
        video_file,
        mimetype='video/mp4',
        resumable=True,
        chunksize=1024*1024  # 1MB chunks
    )

    # Upload video
    try:
        request = youtube.videos().insert(
            part='snippet,status',
            body=body,
            media_body=media
        )

        response = None
        while response is None:
            status, response = request.next_chunk()
            if status:
                print(f"Upload progress: {int(status.progress() * 100)}%")

        video_id = response['id']
        print(f"Video uploaded: https://youtube.com/watch?v={video_id}")

        # Upload thumbnail if provided
        if thumbnail_file and os.path.exists(thumbnail_file):
            upload_thumbnail(youtube, video_id, thumbnail_file)

        return video_id

    except HttpError as e:
        print(f"YouTube API error: {e}")
        raise


def upload_thumbnail(youtube, video_id: str, thumbnail_file: str):
    """Upload custom thumbnail for video."""
    try:
        youtube.thumbnails().set(
            videoId=video_id,
            media_body=MediaFileUpload(thumbnail_file, mimetype='image/jpeg')
        ).execute()
        print(f"Thumbnail uploaded for video {video_id}")
    except HttpError as e:
        print(f"Thumbnail upload failed: {e}")


def create_video_metadata(
    summary: str,
    date: datetime = None,
    sources: List[str] = None
) -> dict:
    """
    Generate YouTube metadata from summary.

    Args:
        summary: Daily summary text
        date: Date for title (default: today)
        sources: List of source names

    Returns:
        Dict with title, description, and tags
    """
    if date is None:
        date = datetime.now()

    date_str = date.strftime('%B %d, %Y')

    title = f"Eastbound Financial Analysis - {date_str}"

    description = f"""Daily financial intelligence from Eastern international media.

{summary}

---
SOURCES:
"""
    if sources:
        for source in sources:
            description += f"• {source}\n"
    else:
        description += """• TASS (Russia)
• RT (Russia)
• Xinhua (China)
• People's Daily (China)
• NHK (Japan)
• Yonhap (Korea)
"""

    description += """
---
Subscribe for daily updates on Eastern financial markets and geopolitics.

#Finance #Economics #Russia #China #Japan #Korea #Geopolitics #Markets
"""

    tags = [
        'finance', 'economics', 'geopolitics', 'russia', 'china',
        'japan', 'korea', 'markets', 'investing', 'news',
        'eastern markets', 'international finance', 'daily analysis',
        'TASS', 'Xinhua', 'emerging markets'
    ]

    return {
        'title': title,
        'description': description,
        'tags': tags
    }


def check_quota():
    """Check remaining YouTube API quota (10,000 units/day)."""
    # Note: Quota checking requires additional API calls
    # Video upload costs ~1,600 units
    # With 10,000/day quota, you can upload ~6 videos/day
    print("YouTube API quota: ~10,000 units/day")
    print("Video upload cost: ~1,600 units")
    print("Max uploads/day: ~6")


# Main script for testing
if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python upload_youtube.py <video_file> [title]")
        print("\nChecking API quota...")
        check_quota()
        sys.exit(0)

    video_file = sys.argv[1]
    title = sys.argv[2] if len(sys.argv) > 2 else f"Eastbound Test - {datetime.now().strftime('%Y-%m-%d')}"

    metadata = create_video_metadata("Test upload from Eastbound automation.")

    video_id = upload_to_youtube(
        video_file,
        title=metadata['title'],
        description=metadata['description'],
        tags=metadata['tags']
    )

    print(f"Success! Video ID: {video_id}")
    print(f"URL: https://youtube.com/watch?v={video_id}")
