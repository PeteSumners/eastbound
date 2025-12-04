#!/usr/bin/env python3
"""
Video Creation for Eastbound Reports

Creates videos using either:
1. HeyGen API (AI avatar) - Higher engagement, requires subscription
2. MoviePy (slides + voiceover) - Free, simpler

Setup:
    pip install moviepy pillow requests

    # For HeyGen, add to .env:
    HEYGEN_API_KEY=your_api_key
    HEYGEN_AVATAR_ID=your_avatar_id

Usage:
    from create_video import create_video
    video_file = create_video("summary text", "voice.mp3", "output.mp4")
"""

import os
import time
import json
import requests
from pathlib import Path
from datetime import datetime
from typing import Optional

# Try to import MoviePy for local video creation
MOVIEPY_AVAILABLE = False
try:
    from moviepy.editor import (
        TextClip, CompositeVideoClip, ColorClip,
        AudioFileClip, concatenate_videoclips, ImageClip
    )
    MOVIEPY_AVAILABLE = True
except ImportError:
    pass

# Try PIL for thumbnail generation
PIL_AVAILABLE = False
try:
    from PIL import Image, ImageDraw, ImageFont
    PIL_AVAILABLE = True
except ImportError:
    pass


# Video settings
VIDEO_WIDTH = 1920
VIDEO_HEIGHT = 1080
FPS = 24
BACKGROUND_COLOR = (15, 15, 35)  # Dark blue
TEXT_COLOR = 'white'
ACCENT_COLOR = '#4ECDC4'  # Teal accent


def get_heygen_key():
    """Get HeyGen API key from environment."""
    return os.getenv('HEYGEN_API_KEY')


def get_avatar_id():
    """Get HeyGen avatar ID from environment."""
    return os.getenv('HEYGEN_AVATAR_ID')


def create_video_heygen(text: str, audio_url: str, output_file: str) -> str:
    """
    Create video using HeyGen AI avatar.

    Args:
        text: Script for the avatar to speak
        audio_url: URL to uploaded audio file (or local path)
        output_file: Output video file path

    Returns:
        Path to generated video
    """
    api_key = get_heygen_key()
    avatar_id = get_avatar_id()

    if not api_key:
        raise ValueError("HEYGEN_API_KEY not set in environment")
    if not avatar_id:
        raise ValueError("HEYGEN_AVATAR_ID not set in environment")

    headers = {
        "X-Api-Key": api_key,
        "Content-Type": "application/json"
    }

    # Create video request
    payload = {
        "video_inputs": [{
            "character": {
                "type": "avatar",
                "avatar_id": avatar_id,
                "avatar_style": "normal"
            },
            "voice": {
                "type": "audio",
                "audio_url": audio_url
            },
            "background": {
                "type": "color",
                "value": "#0f0f23"
            }
        }],
        "dimension": {
            "width": VIDEO_WIDTH,
            "height": VIDEO_HEIGHT
        },
        "aspect_ratio": "16:9"
    }

    print("Requesting HeyGen video generation...")
    response = requests.post(
        "https://api.heygen.com/v2/video/generate",
        headers=headers,
        json=payload
    )

    if response.status_code != 200:
        raise Exception(f"HeyGen API error: {response.text}")

    video_id = response.json()['data']['video_id']
    print(f"Video ID: {video_id}")

    # Poll for completion
    video_url = poll_heygen_status(video_id, headers)

    # Download video
    print("Downloading video...")
    video_response = requests.get(video_url)
    Path(output_file).parent.mkdir(parents=True, exist_ok=True)
    with open(output_file, 'wb') as f:
        f.write(video_response.content)

    print(f"Video created: {output_file}")
    return output_file


def poll_heygen_status(video_id: str, headers: dict, timeout: int = 600) -> str:
    """Poll HeyGen API until video is ready."""
    start_time = time.time()

    while time.time() - start_time < timeout:
        response = requests.get(
            f"https://api.heygen.com/v1/video_status.get?video_id={video_id}",
            headers=headers
        )

        data = response.json()['data']
        status = data['status']

        if status == 'completed':
            return data['video_url']
        elif status == 'failed':
            raise Exception(f"Video generation failed: {data.get('error', 'Unknown error')}")

        print(f"Status: {status}... waiting 10s")
        time.sleep(10)

    raise TimeoutError("Video generation timed out")


def create_video_moviepy(text: str, audio_file: str, output_file: str) -> str:
    """
    Create simple video using MoviePy (free, local).

    Creates animated text slides with voiceover.

    Args:
        text: Summary text to display
        audio_file: Path to audio file
        output_file: Output video file path

    Returns:
        Path to generated video
    """
    if not MOVIEPY_AVAILABLE:
        raise ImportError("moviepy not installed. Run: pip install moviepy")

    print("Creating video with MoviePy...")

    # Load audio to get duration
    audio = AudioFileClip(audio_file)
    duration = audio.duration

    # Create background
    background = ColorClip(
        size=(VIDEO_WIDTH, VIDEO_HEIGHT),
        color=BACKGROUND_COLOR,
        duration=duration
    )

    # Split text into slides
    paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
    if not paragraphs:
        paragraphs = [text]

    # Time per slide
    time_per_slide = duration / len(paragraphs)

    clips = [background]

    # Create title
    title_clip = TextClip(
        "EASTBOUND REPORTS",
        fontsize=60,
        color=ACCENT_COLOR,
        font='Arial-Bold',
        size=(VIDEO_WIDTH - 200, None)
    ).set_position(('center', 50)).set_duration(duration)
    clips.append(title_clip)

    # Create date
    date_text = datetime.now().strftime('%B %d, %Y')
    date_clip = TextClip(
        date_text,
        fontsize=30,
        color='gray',
        font='Arial',
        size=(VIDEO_WIDTH - 200, None)
    ).set_position(('center', 130)).set_duration(duration)
    clips.append(date_clip)

    # Create text slides
    for i, paragraph in enumerate(paragraphs):
        start_time = i * time_per_slide

        # Main text
        text_clip = TextClip(
            paragraph,
            fontsize=36,
            color=TEXT_COLOR,
            font='Arial',
            size=(VIDEO_WIDTH - 300, None),
            method='caption',
            align='center'
        ).set_position('center').set_start(start_time).set_duration(time_per_slide)

        clips.append(text_clip)

    # Compose all clips
    video = CompositeVideoClip(clips)
    video = video.set_audio(audio)

    # Export
    Path(output_file).parent.mkdir(parents=True, exist_ok=True)
    video.write_videofile(
        output_file,
        fps=FPS,
        codec='libx264',
        audio_codec='aac',
        threads=4,
        preset='medium'
    )

    print(f"Video created: {output_file}")
    return output_file


def create_thumbnail(text: str, output_file: str) -> str:
    """
    Create YouTube thumbnail.

    Args:
        text: Short title text
        output_file: Output image file path

    Returns:
        Path to generated thumbnail
    """
    if not PIL_AVAILABLE:
        raise ImportError("PIL not installed. Run: pip install pillow")

    # Create image
    img = Image.new('RGB', (1280, 720), color=BACKGROUND_COLOR)
    draw = ImageDraw.Draw(img)

    # Try to load a nice font, fall back to default
    try:
        font_large = ImageFont.truetype("arial.ttf", 72)
        font_small = ImageFont.truetype("arial.ttf", 36)
    except:
        font_large = ImageFont.load_default()
        font_small = ImageFont.load_default()

    # Draw title
    draw.text(
        (640, 200),
        "EASTBOUND",
        fill=ACCENT_COLOR,
        font=font_large,
        anchor="mm"
    )

    draw.text(
        (640, 300),
        "REPORTS",
        fill='white',
        font=font_large,
        anchor="mm"
    )

    # Draw date
    date_text = datetime.now().strftime('%B %d, %Y')
    draw.text(
        (640, 450),
        date_text,
        fill='gray',
        font=font_small,
        anchor="mm"
    )

    # Draw short text
    short_text = text[:50] + "..." if len(text) > 50 else text
    draw.text(
        (640, 550),
        short_text,
        fill='white',
        font=font_small,
        anchor="mm"
    )

    # Save
    Path(output_file).parent.mkdir(parents=True, exist_ok=True)
    img.save(output_file, 'JPEG', quality=95)

    print(f"Thumbnail created: {output_file}")
    return output_file


def create_video(
    text: str,
    audio_file: str,
    output_file: str = None,
    use_heygen: bool = None
) -> str:
    """
    Create video from text and audio.

    Args:
        text: Summary text
        audio_file: Path to audio file
        output_file: Output video path (default: temp/video_TIMESTAMP.mp4)
        use_heygen: Use HeyGen API if True, MoviePy if False, auto-detect if None

    Returns:
        Path to generated video
    """
    if output_file is None:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_file = f"temp/video_{timestamp}.mp4"

    # Auto-detect which method to use
    if use_heygen is None:
        use_heygen = bool(get_heygen_key() and get_avatar_id())

    if use_heygen:
        # Note: HeyGen needs audio URL, not local file
        # You'd need to upload the audio first
        print("HeyGen requires audio URL - falling back to MoviePy")
        use_heygen = False

    if use_heygen:
        return create_video_heygen(text, audio_file, output_file)
    else:
        return create_video_moviepy(text, audio_file, output_file)


# Main script for testing
if __name__ == "__main__":
    import sys

    test_text = """
    Today's Eastbound Financial Analysis

    Russian energy markets showed significant movement as TASS reported new pipeline agreements with Asian partners.

    Chinese state media emphasized continued investment in Belt and Road infrastructure, with focus on Central Asian corridors.

    Japanese semiconductor developments signal shifting supply chain dynamics in the region.

    Key takeaway: Eastern markets are positioning for increased regional economic cooperation.
    """

    # Check if audio file provided
    if len(sys.argv) > 1:
        audio_file = sys.argv[1]
    else:
        print("Usage: python create_video.py <audio_file.mp3>")
        print("Creating test thumbnail only...")
        create_thumbnail(test_text, "temp/thumbnail.jpg")
        sys.exit(0)

    output = create_video(test_text, audio_file)
    print(f"Output: {output}")
