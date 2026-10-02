# ============================================================
# NEXUS JARVIS NEURAL VOICE SYNTHESIS
# Authentic British Persona (en-GB-RyanNeural) with Offline Fallback
# ============================================================

import os
import sys
import asyncio
import tempfile
import threading

import re

# Optional neural edge-tts
try:
    import edge_tts
    import pygame
    pygame.mixer.init()
    HAS_EDGE_TTS = True
except Exception:
    HAS_EDGE_TTS = False

# Offline pyttsx3 fallback
try:
    import pyttsx3
    HAS_PYTTSX3 = True
except Exception:
    HAS_PYTTSX3 = False

JARVIS_VOICE = os.getenv("NEXUS_JARVIS_VOICE", "en-GB-RyanNeural")

_speech_lock = threading.Lock()


def _speak_offline(text: str):
    """Fallback offline TTS engine."""
    if not HAS_PYTTSX3:
        print(f"[JARVIS VOICE]: {text}")
        return
    try:
        engine = pyttsx3.init()
        engine.say(text)
        engine.runAndWait()
        engine.stop()
    except Exception as e:
        print(f"[JARVIS VOICE OFFLINE ERROR]: {e}")


def _speak_edge(text: str):
    """Generate and playback high-fidelity British neural speech."""
    try:
        temp_dir = tempfile.gettempdir()
        temp_path = os.path.join(temp_dir, f"nexus_speech_{os.getpid()}_{threading.get_ident()}.mp3")

        async def _generate():
            communicate = edge_tts.Communicate(text, JARVIS_VOICE)
            await communicate.save(temp_path)

        asyncio.run(_generate())

        if os.path.exists(temp_path):
            if not pygame.mixer.get_init():
                pygame.mixer.init()
            pygame.mixer.music.load(temp_path)
            pygame.mixer.music.play()
            while pygame.mixer.music.get_busy():
                pygame.time.Clock().tick(20)
            pygame.mixer.music.unload()
            try:
                os.remove(temp_path)
            except Exception:
                pass
            return True
    except Exception as e:
        # Fall back to offline
        return False
    return False


def speak(text: str, wait: bool = True):
    """
    Speak text using authentic British J.A.R.V.I.S. neural voice.
    Falls back gracefully to pyttsx3 when offline.
    """
    if not text or not str(text).strip():
        return

    # Strip HTML tags and entities so voice synthesis sounds clean and human
    clean_text = re.sub(r"<[^>]+>", " ", str(text))
    clean_text = re.sub(r"&[a-zA-Z0-9#]+;", " ", clean_text)
    clean_text = re.sub(r"\s+", " ", clean_text).strip()
    if not clean_text:
        return

    def _worker():
        with _speech_lock:
            success = False
            if HAS_EDGE_TTS:
                success = _speak_edge(clean_text)
            if not success:
                _speak_offline(clean_text)

    if wait:
        _worker()
    else:
        t = threading.Thread(target=_worker, daemon=True)
        t.start()