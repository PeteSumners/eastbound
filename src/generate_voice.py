#!/usr/bin/env python3
"""
Voice Generation for Eastbound Reports

Uses Edge TTS (free), ElevenLabs (paid), or pyttsx3 (offline fallback).

Setup:
    pip install edge-tts elevenlabs pyttsx3

    # Optional - Add to .env for ElevenLabs:
    ELEVENLABS_API_KEY=your_api_key
    ELEVENLABS_VOICE_ID=your_cloned_voice_id

Usage:
    from generate_voice import generate_voiceover
    audio_file = generate_voiceover("Today's financial summary...", "output.mp3")
"""

import os
import asyncio
from pathlib import Path
from datetime import datetime

# Check available TTS engines
EDGE_TTS_AVAILABLE = False
GTTS_AVAILABLE = False
ELEVENLABS_AVAILABLE = False
PYTTSX3_AVAILABLE = False

try:
    import edge_tts
    EDGE_TTS_AVAILABLE = True
except ImportError:
    pass

try:
    from gtts import gTTS
    GTTS_AVAILABLE = True
except ImportError:
    pass

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


# Edge TTS voice options (free, high quality)
EDGE_VOICES = {
    'news_male': 'en-US-GuyNeural',        # Professional male voice
    'news_female': 'en-US-JennyNeural',    # Professional female voice
    'british_male': 'en-GB-RyanNeural',    # British accent
    'british_female': 'en-GB-SoniaNeural', # British female
}
DEFAULT_EDGE_VOICE = 'en-US-GuyNeural'  # Good for news/finance content


def get_elevenlabs_key():
    """Get ElevenLabs API key from environment."""
    return os.getenv('ELEVENLABS_API_KEY')


def get_voice_id():
    """Get cloned voice ID or use default."""
    return os.getenv('ELEVENLABS_VOICE_ID', 'pNInz6obpgDQGcFmaJgB')  # Adam (default)


def get_edge_voice():
    """Get Edge TTS voice from environment or use default."""
    return os.getenv('EDGE_TTS_VOICE', DEFAULT_EDGE_VOICE)


async def _generate_edge_tts_async(text: str, output_file: str, voice: str) -> str:
    """Async implementation of Edge TTS generation."""
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(output_file)
    return output_file


def generate_voiceover_edge(text: str, output_file: str, voice: str = None) -> str:
    """
    Generate voiceover using Edge TTS (free, high quality).

    Args:
        text: Text to convert to speech
        output_file: Output audio file path
        voice: Voice ID (default: en-US-GuyNeural)

    Returns:
        Path to generated audio file
    """
    if not EDGE_TTS_AVAILABLE:
        raise ImportError("edge-tts not installed. Run: pip install edge-tts")

    voice = voice or get_edge_voice()
    print(f"Generating voice with Edge TTS ({len(text)} chars, voice: {voice})...")

    # Ensure output directory exists
    Path(output_file).parent.mkdir(parents=True, exist_ok=True)

    # Handle Windows event loop policy
    if os.name == 'nt':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    # Run async function - create new event loop if needed
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            # If loop is already running, create a new one
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(_generate_edge_tts_async(text, output_file, voice))
        else:
            asyncio.run(_generate_edge_tts_async(text, output_file, voice))
    except RuntimeError:
        # No event loop exists
        asyncio.run(_generate_edge_tts_async(text, output_file, voice))

    print(f"Voice generated (Edge TTS): {output_file}")
    return output_file


def generate_voiceover_gtts(text: str, output_file: str) -> str:
    """
    Generate voiceover using Google Text-to-Speech (free, reliable).

    Args:
        text: Text to convert to speech
        output_file: Output audio file path

    Returns:
        Path to generated audio file
    """
    if not GTTS_AVAILABLE:
        raise ImportError("gtts not installed. Run: pip install gtts")

    print(f"Generating voice with gTTS ({len(text)} chars)...")

    # Ensure output directory exists
    Path(output_file).parent.mkdir(parents=True, exist_ok=True)

    # Generate audio
    tts = gTTS(text=text, lang='en', slow=False)
    tts.save(output_file)

    print(f"Voice generated (gTTS): {output_file}")
    return output_file


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


def generate_voiceover(text: str, output_file: str = None, engine: str = 'auto') -> str:
    """
    Generate voiceover from text.

    Args:
        text: The script to convert to speech
        output_file: Output audio file path (default: temp/voice_TIMESTAMP.mp3)
        engine: TTS engine to use:
                - 'auto': gTTS (free) > Edge TTS > ElevenLabs (if key) > pyttsx3 (offline)
                - 'gtts': Force Google TTS (free, reliable)
                - 'edge': Force Edge TTS (free, high quality)
                - 'elevenlabs': Force ElevenLabs (paid, premium quality)
                - 'local': Force pyttsx3 (offline, robotic)

    Returns:
        Path to generated audio file
    """
    if output_file is None:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_file = f"temp/voice_{timestamp}.mp3"

    # Clean text for TTS
    text = clean_text_for_tts(text)

    # Determine which engine to use
    if engine == 'elevenlabs':
        return generate_voiceover_elevenlabs(text, output_file)
    elif engine == 'local':
        if output_file.endswith('.mp3'):
            output_file = output_file.replace('.mp3', '.wav')
        return generate_voiceover_local(text, output_file)
    elif engine == 'edge':
        return generate_voiceover_edge(text, output_file)
    elif engine == 'gtts':
        return generate_voiceover_gtts(text, output_file)

    # Auto mode: Try engines in order of reliability/quality
    # 1. gTTS (free, reliable, good quality) - PRIMARY
    if GTTS_AVAILABLE:
        try:
            return generate_voiceover_gtts(text, output_file)
        except Exception as e:
            print(f"gTTS failed: {e}, trying fallback...")

    # 2. Edge TTS (free, high quality but may have issues)
    if EDGE_TTS_AVAILABLE:
        try:
            return generate_voiceover_edge(text, output_file)
        except Exception as e:
            print(f"Edge TTS failed: {e}, trying fallback...")

    # 3. ElevenLabs (paid, premium quality)
    if ELEVENLABS_AVAILABLE and get_elevenlabs_key():
        try:
            return generate_voiceover_elevenlabs(text, output_file)
        except Exception as e:
            print(f"ElevenLabs failed: {e}, trying fallback...")

    # 4. pyttsx3 (offline, robotic but works)
    if PYTTSX3_AVAILABLE:
        if output_file.endswith('.mp3'):
            output_file = output_file.replace('.mp3', '.wav')
        return generate_voiceover_local(text, output_file)

    raise RuntimeError("No TTS engine available. Install: pip install gtts")


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


def list_available_engines() -> dict:
    """List available TTS engines and their status."""
    return {
        'gtts': {
            'available': GTTS_AVAILABLE,
            'cost': 'FREE',
            'quality': 'Good',
            'note': 'Google TTS - reliable, recommended'
        },
        'edge_tts': {
            'available': EDGE_TTS_AVAILABLE,
            'cost': 'FREE',
            'quality': 'High',
            'note': 'Microsoft Edge voices'
        },
        'elevenlabs': {
            'available': ELEVENLABS_AVAILABLE and bool(get_elevenlabs_key()),
            'cost': '$5-11/month',
            'quality': 'Premium',
            'note': 'Best quality, requires API key'
        },
        'pyttsx3': {
            'available': PYTTSX3_AVAILABLE,
            'cost': 'FREE',
            'quality': 'Low',
            'note': 'Offline fallback, robotic voice'
        }
    }


async def list_edge_voices():
    """List all available Edge TTS voices."""
    if not EDGE_TTS_AVAILABLE:
        print("Edge TTS not available")
        return []

    voices = await edge_tts.list_voices()
    english_voices = [v for v in voices if v['Locale'].startswith('en-')]
    return english_voices


# Main script for testing
if __name__ == "__main__":
    import sys

    # Show available engines
    print("=" * 50)
    print("AVAILABLE TTS ENGINES:")
    print("=" * 50)
    engines = list_available_engines()
    for name, info in engines.items():
        status = "[OK]" if info['available'] else "[--]"
        print(f"  {status} {name}: {info['cost']} ({info['quality']} quality)")
        if not info['available']:
            print(f"        -> {info['note']}")
    print("=" * 50)

    if len(sys.argv) > 1 and sys.argv[1] == '--voices':
        print("\nAvailable Edge TTS English voices:")
        voices = asyncio.run(list_edge_voices())
        for v in voices[:20]:  # Show first 20
            print(f"  {v['ShortName']}: {v['Gender']}")
        sys.exit(0)

    if len(sys.argv) > 1 and sys.argv[1] != '--voices':
        test_text = ' '.join(sys.argv[1:])
    else:
        test_text = """
        Today's Eastbound financial analysis.

        Russian markets showed mixed signals as TASS reported new energy agreements.
        Chinese state media emphasized continued Belt and Road investments.
        Japan's NHK covered semiconductor supply chain developments.

        Key takeaway: Eastern markets are positioning for increased regional cooperation.
        """

    print(f"\nText length: {get_character_count(test_text)} chars")
    print(f"Estimated duration: {estimate_audio_duration(test_text):.1f} seconds")
    print(f"\nGenerating voice...")

    output = generate_voiceover(test_text)
    print(f"Output: {output}")
