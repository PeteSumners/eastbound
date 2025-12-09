#!/usr/bin/env python3
"""
Eastbound Video Generation
Generates AI anchor videos from newscast scripts using HeyGen API.
Optionally uses ElevenLabs for custom voice cloning.
"""

import os
import sys
import time
import json
import requests
from pathlib import Path
from datetime import datetime, UTC

# Load environment variables
try:
    from dotenv import load_dotenv
    env_path = Path(__file__).parent.parent / '.env'
    load_dotenv(env_path)
except ImportError:
    pass


# =============================================================================
# CONFIGURATION - Customize your anchor here!
# =============================================================================

# HeyGen Avatar Settings
# Browse avatars: https://app.heygen.com/avatars
HEYGEN_AVATAR_ID = os.getenv('HEYGEN_AVATAR_ID', 'Angela-inblackskirt-20220820')  # Professional female anchor
HEYGEN_VOICE_ID = os.getenv('HEYGEN_VOICE_ID', '1bd001e7e50f421d891986aad5158bc8')  # Default HeyGen voice

# ElevenLabs Voice Settings (optional - for custom/cloned voices)
# Browse voices: https://elevenlabs.io/voice-library
ELEVENLABS_VOICE_ID = os.getenv('ELEVENLABS_VOICE_ID', '')  # Leave empty to use HeyGen voice

# Video Settings
VIDEO_DIMENSION = {"width": 1920, "height": 1080}  # 1080p landscape
VIDEO_BACKGROUND = "#1a1a2e"  # Dark blue news desk background

# Voice Style Settings (based on your psychology research!)
VOICE_SETTINGS = {
    "stability": 0.3,        # Lower = more expressive/varied (your research: variability matters!)
    "similarity_boost": 0.8,  # Keep recognizable
    "style": 0.7,            # Higher = more energetic (your research: energy drives engagement!)
    "use_speaker_boost": True
}


# =============================================================================
# API CLIENTS
# =============================================================================

def get_heygen_client():
    """Initialize HeyGen API client."""
    api_key = os.getenv('HEYGEN_API_KEY')
    if not api_key:
        print("❌ HEYGEN_API_KEY not set in .env")
        return None
    return {
        'base_url': 'https://api.heygen.com/v2',
        'headers': {
            'X-Api-Key': api_key,
            'Content-Type': 'application/json'
        }
    }


def get_elevenlabs_client():
    """Initialize ElevenLabs API client."""
    api_key = os.getenv('ELEVENLABS_API_KEY')
    if not api_key:
        return None
    return {
        'base_url': 'https://api.elevenlabs.io/v1',
        'headers': {
            'xi-api-key': api_key,
            'Content-Type': 'application/json'
        }
    }


# =============================================================================
# ELEVENLABS FUNCTIONS (Optional - for custom voice)
# =============================================================================

def generate_audio_elevenlabs(script: str, output_path: Path) -> bool:
    """Generate audio using ElevenLabs API."""
    client = get_elevenlabs_client()
    if not client or not ELEVENLABS_VOICE_ID:
        return False

    print(f"🎙️  Generating audio with ElevenLabs...")

    url = f"{client['base_url']}/text-to-speech/{ELEVENLABS_VOICE_ID}"

    payload = {
        "text": script,
        "model_id": "eleven_turbo_v2_5",  # Fast, high quality
        "voice_settings": VOICE_SETTINGS
    }

    response = requests.post(url, headers=client['headers'], json=payload)

    if response.status_code == 200:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'wb') as f:
            f.write(response.content)
        print(f"✓ Audio saved to {output_path}")
        return True
    else:
        print(f"❌ ElevenLabs error: {response.status_code} - {response.text}")
        return False


# =============================================================================
# HEYGEN FUNCTIONS
# =============================================================================

def create_video_heygen(script: str, audio_url: str = None) -> dict:
    """
    Create video using HeyGen API.

    Args:
        script: The newscast script text
        audio_url: Optional URL to pre-generated audio (e.g., from ElevenLabs)

    Returns:
        dict with video_id and status
    """
    client = get_heygen_client()
    if not client:
        return None

    print(f"🎬 Creating video with HeyGen...")
    print(f"   Avatar: {HEYGEN_AVATAR_ID}")

    # Build the video request
    if audio_url:
        # Use custom audio (from ElevenLabs)
        voice_config = {
            "type": "audio",
            "audio_url": audio_url
        }
    else:
        # Use HeyGen's built-in voice
        voice_config = {
            "type": "text",
            "input_text": script,
            "voice_id": HEYGEN_VOICE_ID,
            "speed": 1.0
        }

    payload = {
        "video_inputs": [{
            "character": {
                "type": "avatar",
                "avatar_id": HEYGEN_AVATAR_ID,
                "avatar_style": "normal"
            },
            "voice": voice_config,
            "background": {
                "type": "color",
                "value": VIDEO_BACKGROUND
            }
        }],
        "dimension": VIDEO_DIMENSION,
        "test": False  # Set to True for free test videos (watermarked)
    }

    url = f"{client['base_url']}/video/generate"
    response = requests.post(url, headers=client['headers'], json=payload)

    if response.status_code == 200:
        data = response.json()
        video_id = data.get('data', {}).get('video_id')
        print(f"✓ Video generation started! ID: {video_id}")
        return {'video_id': video_id, 'status': 'processing'}
    else:
        print(f"❌ HeyGen error: {response.status_code} - {response.text}")
        return None


def check_video_status(video_id: str) -> dict:
    """Check the status of a HeyGen video generation."""
    client = get_heygen_client()
    if not client:
        return None

    url = f"{client['base_url']}/video_status.get"
    params = {'video_id': video_id}

    response = requests.get(url, headers=client['headers'], params=params)

    if response.status_code == 200:
        data = response.json()
        return data.get('data', {})
    return None


def wait_for_video(video_id: str, max_wait: int = 600, check_interval: int = 15) -> str:
    """
    Wait for video generation to complete.

    Args:
        video_id: The HeyGen video ID
        max_wait: Maximum seconds to wait (default 10 minutes)
        check_interval: Seconds between status checks

    Returns:
        Video URL if successful, None otherwise
    """
    print(f"⏳ Waiting for video generation (max {max_wait}s)...")

    start_time = time.time()
    while time.time() - start_time < max_wait:
        status = check_video_status(video_id)

        if not status:
            print("   Error checking status")
            time.sleep(check_interval)
            continue

        state = status.get('status')

        if state == 'completed':
            video_url = status.get('video_url')
            print(f"✓ Video ready: {video_url}")
            return video_url
        elif state == 'failed':
            error = status.get('error', 'Unknown error')
            print(f"❌ Video generation failed: {error}")
            return None
        else:
            elapsed = int(time.time() - start_time)
            print(f"   Status: {state} ({elapsed}s elapsed)")
            time.sleep(check_interval)

    print(f"❌ Timeout waiting for video after {max_wait}s")
    return None


def download_video(video_url: str, output_path: Path) -> bool:
    """Download the generated video."""
    print(f"📥 Downloading video...")

    response = requests.get(video_url, stream=True)
    if response.status_code == 200:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        print(f"✓ Video saved to {output_path}")
        return True
    else:
        print(f"❌ Download failed: {response.status_code}")
        return False


# =============================================================================
# MAIN PIPELINE
# =============================================================================

def generate_newscast_video(script: str, output_dir: Path = None) -> dict:
    """
    Full pipeline: Script -> Audio (optional) -> Video -> Download

    Args:
        script: The newscast script text
        output_dir: Directory to save outputs (default: project_root/videos/)

    Returns:
        dict with paths to generated files
    """
    if output_dir is None:
        output_dir = Path(__file__).parent.parent / "videos"

    output_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now(UTC).strftime("%Y-%m-%d-%H%M%S")
    results = {
        'timestamp': timestamp,
        'script': script,
        'audio_path': None,
        'video_path': None,
        'video_url': None
    }

    print("=" * 60)
    print("EASTBOUND VIDEO GENERATION")
    print("=" * 60)
    print(f"Timestamp: {timestamp}")
    print(f"Script length: {len(script)} chars (~{len(script.split())} words)")
    print()

    # Step 1: Generate audio with ElevenLabs (optional)
    audio_url = None
    if ELEVENLABS_VOICE_ID and get_elevenlabs_client():
        audio_path = output_dir / f"{timestamp}-audio.mp3"
        if generate_audio_elevenlabs(script, audio_path):
            results['audio_path'] = str(audio_path)
            # For HeyGen to use, you'd need to upload this to a public URL
            # For now, we'll use HeyGen's built-in voice
            print("   Note: Using HeyGen voice (audio upload requires hosting)")

    # Step 2: Generate video with HeyGen
    video_result = create_video_heygen(script, audio_url)
    if not video_result:
        print("❌ Failed to start video generation")
        return results

    video_id = video_result['video_id']

    # Step 3: Wait for video completion
    video_url = wait_for_video(video_id)
    if not video_url:
        return results

    results['video_url'] = video_url

    # Step 4: Download video
    video_path = output_dir / f"{timestamp}-newscast.mp4"
    if download_video(video_url, video_path):
        results['video_path'] = str(video_path)

    print()
    print("=" * 60)
    print("✓ VIDEO GENERATION COMPLETE")
    print("=" * 60)

    return results


# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

def list_heygen_avatars():
    """List available HeyGen avatars."""
    client = get_heygen_client()
    if not client:
        return

    url = f"{client['base_url']}/avatars"
    response = requests.get(url, headers=client['headers'])

    if response.status_code == 200:
        data = response.json()
        avatars = data.get('data', {}).get('avatars', [])
        print(f"\n📋 Available Avatars ({len(avatars)}):\n")
        for avatar in avatars[:20]:  # Show first 20
            print(f"  ID: {avatar.get('avatar_id')}")
            print(f"  Name: {avatar.get('avatar_name')}")
            print(f"  Gender: {avatar.get('gender')}")
            print()
    else:
        print(f"❌ Error: {response.status_code}")


def list_heygen_voices():
    """List available HeyGen voices."""
    client = get_heygen_client()
    if not client:
        return

    url = f"{client['base_url']}/voices"
    response = requests.get(url, headers=client['headers'])

    if response.status_code == 200:
        data = response.json()
        voices = data.get('data', {}).get('voices', [])
        print(f"\n🎙️ Available Voices ({len(voices)}):\n")
        for voice in voices[:20]:  # Show first 20
            print(f"  ID: {voice.get('voice_id')}")
            print(f"  Name: {voice.get('name')}")
            print(f"  Language: {voice.get('language')}")
            print()
    else:
        print(f"❌ Error: {response.status_code}")


def list_elevenlabs_voices():
    """List available ElevenLabs voices."""
    client = get_elevenlabs_client()
    if not client:
        print("❌ ELEVENLABS_API_KEY not set")
        return

    url = f"{client['base_url']}/voices"
    response = requests.get(url, headers=client['headers'])

    if response.status_code == 200:
        data = response.json()
        voices = data.get('voices', [])
        print(f"\n🎙️ Available ElevenLabs Voices ({len(voices)}):\n")
        for voice in voices:
            print(f"  ID: {voice.get('voice_id')}")
            print(f"  Name: {voice.get('name')}")
            print(f"  Category: {voice.get('category')}")
            labels = voice.get('labels', {})
            if labels:
                print(f"  Style: {labels.get('description', 'N/A')}")
            print()
    else:
        print(f"❌ Error: {response.status_code}")


# =============================================================================
# CLI
# =============================================================================

if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Generate Eastbound newscast videos')
    parser.add_argument('--list-avatars', action='store_true', help='List available HeyGen avatars')
    parser.add_argument('--list-voices', action='store_true', help='List available HeyGen voices')
    parser.add_argument('--list-elevenlabs', action='store_true', help='List available ElevenLabs voices')
    parser.add_argument('--script', type=str, help='Path to script file or script text')
    parser.add_argument('--test', action='store_true', help='Generate test video (watermarked, free)')

    args = parser.parse_args()

    if args.list_avatars:
        list_heygen_avatars()
    elif args.list_voices:
        list_heygen_voices()
    elif args.list_elevenlabs:
        list_elevenlabs_voices()
    elif args.script:
        # Read script from file or use as text
        if Path(args.script).exists():
            script = Path(args.script).read_text(encoding='utf-8')
        else:
            script = args.script

        generate_newscast_video(script)
    else:
        # Demo script
        demo_script = """
Good morning, I'm your host for Eastbound Reports, bringing you today's top financial stories from Eastern markets.

Our lead story: Russia's central bank has signaled a potential rate hike as inflation concerns mount, while China's export figures show a significant decline in trade with the United States.

In Japan, the finance ministry is pushing for emergency budget measures to stabilize the yen. Meanwhile, South Korea's tech sector faces regulatory scrutiny following a major data breach at e-commerce giant Coupang.

That's your Eastern markets update. Follow us for daily briefings, and remember: stay informed, stay ahead. I'm your Eastbound anchor, signing off.
        """.strip()

        print("No script provided. Use --script to generate a video.")
        print("\nDemo script:")
        print("-" * 40)
        print(demo_script)
        print("-" * 40)
        print("\nRun: python generate_video.py --script 'your script here'")
