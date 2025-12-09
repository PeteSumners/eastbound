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


def create_text_frame(text: str, width: int, height: int,
                      title: str = None, date_str: str = None) -> Image.Image:
    """Create a single frame with text using PIL (no ImageMagick needed)."""
    if not PIL_AVAILABLE:
        raise ImportError("PIL not installed. Run: pip install pillow")

    # Create image
    img = Image.new('RGB', (width, height), color=BACKGROUND_COLOR)
    draw = ImageDraw.Draw(img)

    # Try to load fonts
    try:
        font_title = ImageFont.truetype("arial.ttf", 60)
        font_date = ImageFont.truetype("arial.ttf", 30)
        font_text = ImageFont.truetype("arial.ttf", 36)
    except:
        font_title = ImageFont.load_default()
        font_date = font_title
        font_text = font_title

    # Draw title
    if title:
        draw.text((width // 2, 80), title, fill=ACCENT_COLOR, font=font_title, anchor="mm")

    # Draw date
    if date_str:
        draw.text((width // 2, 150), date_str, fill='gray', font=font_date, anchor="mm")

    # Draw main text - word wrap
    if text:
        # Simple word wrap
        words = text.split()
        lines = []
        current_line = []
        max_width = width - 200

        for word in words:
            test_line = ' '.join(current_line + [word])
            try:
                bbox = draw.textbbox((0, 0), test_line, font=font_text)
                line_width = bbox[2] - bbox[0]
            except:
                line_width = len(test_line) * 20  # Fallback

            if line_width < max_width:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                current_line = [word]

        if current_line:
            lines.append(' '.join(current_line))

        # Draw lines centered
        y_start = height // 2 - (len(lines) * 45) // 2
        for i, line in enumerate(lines):
            y = y_start + i * 45
            draw.text((width // 2, y), line, fill='white', font=font_text, anchor="mm")

    return img


def create_video_moviepy(text: str, audio_file: str, output_file: str) -> str:
    """
    Create simple video using MoviePy + PIL (no ImageMagick needed).

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
    if not PIL_AVAILABLE:
        raise ImportError("PIL not installed. Run: pip install pillow")

    print("Creating video with MoviePy + PIL...")

    import numpy as np

    # Load audio to get duration
    audio = AudioFileClip(audio_file)
    duration = audio.duration

    # Split text into slides
    paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
    if not paragraphs:
        paragraphs = [text]

    # Time per slide
    time_per_slide = duration / len(paragraphs)
    date_text = datetime.now().strftime('%B %d, %Y')

    # Create frames for each slide
    clips = []

    for i, paragraph in enumerate(paragraphs):
        # Create PIL image
        img = create_text_frame(
            text=paragraph,
            width=VIDEO_WIDTH,
            height=VIDEO_HEIGHT,
            title="EASTBOUND REPORTS",
            date_str=date_text
        )

        # Convert PIL image to numpy array
        frame = np.array(img)

        # Create ImageClip
        clip = ImageClip(frame).set_duration(time_per_slide)
        clips.append(clip)

    # Concatenate all clips
    video = concatenate_videoclips(clips, method="compose")
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
