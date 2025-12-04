#!/usr/bin/env python3
"""
Voice Generation for Eastbound Reports

Uses ElevenLabs API or local TTS fallback to generate voiceovers.

Setup:
    pip install elevenlabs pyttsx3

    # Add to .env:
    ELEVENLABS_API_KEY=your_api_key
    ELEVENLABS_VOICE_ID=your_cloned_voice_id

Usage:
    from generate_voice import generate_voiceover
    audio_file = generate_voiceover("Today's financial summary...", "output.mp3")
"""

import os
from pathlib import Path
from datetime import datetime

# Try ElevenLabs first, fall back to pyttsx3
ELEVENLABS_AVAILABLE = False
PYTTSX3_AVAILABLE = False

try:
    from elevenlabs import generate, set_api_key, Voice, VoiceSettings
    ELEVENLABS_AVAILABLE = True
except ImportError:
    pass

try:
    import pyttsx3
    PYTTSX3_AVAILABLE = True
except ImportError:
    pass


def get_elevenlabs_key():
    """Get ElevenLabs API key from environment."""
    return os.getenv('ELEVENLABS_API_KEY')


def get_voice_id():
    """Get cloned voice ID or use default."""
    return os.getenv('ELEVENLABS_VOICE_ID', 'pNInz6obpgDQGcFmaJgB')  # Adam (default)


def generate_voiceover_elevenlabs(text: str, output_file: str) -> str:
    """Generate voiceover using ElevenLabs API."""
    if not ELEVENLABS_AVAILABLE:
        raise ImportError("elevenlabs package not installed. Run: pip install elevenlabs")

    api_key = get_elevenlabs_key()
    if not api_key:
        raise ValueError("ELEVENLABS_API_KEY not set in environment")

    set_api_key(api_key)

    # Voice settings for news-style delivery
    voice_settings = VoiceSettings(
        stability=0.75,          # More consistent for news
        similarity_boost=0.75,   # Stay close to cloned voice
        style=0.0,               # Neutral style
        use_speaker_boost=True
    )

    print(f"Generating voice with ElevenLabs ({len(text)} chars)...")

    audio = generate(
        text=text,
        voice=get_voice_id(),
        model="eleven_monolingual_v1",  # Fast, good quality
        voice_settings=voice_settings
    )

    # Ensure output directory exists
    Path(output_file).parent.mkdir(parents=True, exist_ok=True)

    with open(output_file, 'wb') as f:
        f.write(audio)

    print(f"Voice generated: {output_file}")
    return output_file


def generate_voiceover_local(text: str, output_file: str) -> str:
    """Generate voiceover using local TTS (pyttsx3)."""
    if not PYTTSX3_AVAILABLE:
        raise ImportError("pyttsx3 package not installed. Run: pip install pyttsx3")

    print(f"Generating voice locally ({len(text)} chars)...")

    engine = pyttsx3.init()

    # Configure voice settings
    engine.setProperty('rate', 150)     # Words per minute
    engine.setProperty('volume', 0.9)   # Volume 0-1

    # Try to get a natural-sounding voice
    voices = engine.getProperty('voices')
    for voice in voices:
        if 'david' in voice.name.lower() or 'zira' in voice.name.lower():
            engine.setProperty('voice', voice.id)
            break

    # Ensure output directory exists
    Path(output_file).parent.mkdir(parents=True, exist_ok=True)

    # Generate audio file
    engine.save_to_file(text, output_file)
    engine.runAndWait()

    print(f"Voice generated (local): {output_file}")
    return output_file


def generate_voiceover(text: str, output_file: str = None, prefer_elevenlabs: bool = True) -> str:
    """
    Generate voiceover from text.

    Args:
        text: The script to convert to speech
        output_file: Output audio file path (default: temp/voice_TIMESTAMP.mp3)
        prefer_elevenlabs: Use ElevenLabs if available (default: True)

    Returns:
        Path to generated audio file
    """
    if output_file is None:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_file = f"temp/voice_{timestamp}.mp3"

    # Clean text for TTS
    text = clean_text_for_tts(text)

    # Try ElevenLabs first
    if prefer_elevenlabs and ELEVENLABS_AVAILABLE and get_elevenlabs_key():
        try:
            return generate_voiceover_elevenlabs(text, output_file)
        except Exception as e:
            print(f"ElevenLabs failed: {e}, falling back to local TTS")

    # Fall back to local TTS
    if PYTTSX3_AVAILABLE:
        # Local TTS outputs WAV, not MP3
        if output_file.endswith('.mp3'):
            output_file = output_file.replace('.mp3', '.wav')
        return generate_voiceover_local(text, output_file)

    raise RuntimeError("No TTS engine available. Install: pip install elevenlabs OR pip install pyttsx3")


def clean_text_for_tts(text: str) -> str:
    """Clean text for better TTS pronunciation."""
    # Remove markdown
    text = text.replace('**', '')
    text = text.replace('*', '')
    text = text.replace('#', '')

    # Replace problematic characters
    text = text.replace('—', '-')
    text = text.replace('–', '-')
    text = text.replace('"', '"')
    text = text.replace('"', '"')
    text = text.replace(''', "'")
    text = text.replace(''', "'")

    # Add pauses for better pacing
    text = text.replace('. ', '... ')
    text = text.replace(': ', '... ')

    return text.strip()


def estimate_audio_duration(text: str, wpm: int = 150) -> float:
    """Estimate audio duration in seconds."""
    word_count = len(text.split())
    return (word_count / wpm) * 60


def get_character_count(text: str) -> int:
    """Get character count for billing estimation."""
    return len(text)


# Main script for testing
if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        test_text = ' '.join(sys.argv[1:])
    else:
        test_text = """
        Today's Eastbound financial analysis.

        Russian markets showed mixed signals as TASS reported new energy agreements.
        Chinese state media emphasized continued Belt and Road investments.
        Japan's NHK covered semiconductor supply chain developments.

        Key takeaway: Eastern markets are positioning for increased regional cooperation.
        """

    print(f"Text length: {get_character_count(test_text)} chars")
    print(f"Estimated duration: {estimate_audio_duration(test_text):.1f} seconds")

    output = generate_voiceover(test_text)
    print(f"Output: {output}")
