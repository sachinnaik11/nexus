# ============================================================
# NEXUS — AUTONOMOUS YOUTUBE GROWTH & MEME STUDIO
# Viral SEO, Autonomous Content Creation, and Reminders
# ============================================================

import os
import json
import webbrowser
import subprocess
from datetime import datetime

from memory.store import get_memory, add_memory
from core.permissions import permission_gate

from dotenv import load_dotenv
from google import genai
import requests

load_dotenv()
_GEMINI_KEY = os.getenv("GEMINI_API_KEY")

try:
    from PIL import Image, ImageDraw, ImageFont
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False


def _query_ai(prompt: str) -> str:
    """Query Gemini 3.5 or local Qwen 8B fallback directly."""
    if _GEMINI_KEY:
        try:
            client = genai.Client(api_key=_GEMINI_KEY)
            chat = client.chats.create(model="gemini-3.5-flash-lite")
            return chat.send_message(prompt).text.strip()
        except Exception:
            pass

    # Local Ollama Fallback
    try:
        r = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "qwen3:8b",
                "prompt": prompt,
                "stream": False,
            },
            timeout=45,
        )
        return r.json().get("response", "").strip()
    except Exception as e:
        return f"AI generation unavailable: {e}"


# ============================================================
# NICHE MANAGER
# ============================================================

def get_channel_niche() -> str:
    """Retrieve the active channel niche from channel switcher, memory, or analyzed profile."""
    # 0. Check active multi-channel configuration
    try:
        from tools.channel_switcher import get_active_channel_config
        cfg = get_active_channel_config()
        if cfg and cfg.get("niche"):
            return cfg["niche"]
    except Exception:
        pass

    # 1. Check if an analyzed channel profile exists
    profile_path = os.path.join("memory", "channel_profile.json")
    if os.path.exists(profile_path):
        try:
            with open(profile_path, "r", encoding="utf-8") as f:
                pdata = json.load(f)
                if pdata.get("style_summary"):
                    return pdata["style_summary"]
        except Exception:
            pass

    # 2. Check for explicit channel niche in memory (newest first)
    memories = get_memory()
    for mem in reversed(memories):
        lower = str(mem).lower()
        if "channel niche is" in lower or "youtube channel niche is" in lower:
            return mem.split("niche is")[-1].strip()
        elif "niche is" in lower and "game" not in lower:
            return mem.split("niche is")[-1].strip()

    return "Viral Memes & Relatable Comedy"


def set_channel_niche(niche: str) -> str:
    """Save the user's preferred YouTube channel niche to permanent memory."""
    clean_niche = str(niche).strip()
    add_memory(f"My YouTube channel niche is {clean_niche}")
    return f"YouTube channel niche updated to '{clean_niche}'."


# ============================================================
# VIRAL SEO ENGINE (TITLES, DESCRIPTIONS, TAGS)
# ============================================================

def generate_viral_seo(topic_or_draft: str) -> dict:
    """
    Generate viral high-CTR titles, high-retention descriptions,
    trending tags, and thumbnail concepts for YouTube.
    """
    topic = str(topic_or_draft).strip()
    niche = get_channel_niche()

    prompt = f"""
You are the world's #1 viral meme creator and YouTube algorithm growth strategist (managing top 10M+ sub meme channels).
Channel Focus: {niche} (Pure Internet Memes, Relatable Comedy, Trending Reels/Shorts)
Video Topic or Draft: {topic}

Generate an ultra-viral MEME OPTIMIZATION PACKAGE engineered for maximum click-through rate (CTR) and watch retention:
1. THREE ULTRA-VIRAL MEME TITLES:
   - Must use proven viral meme formulas (e.g. "POV:", "When you...", "Bro really thought 💀", "Wait for the plot twist 😭")
   - High emotion, curiosity-gap, punchy, under 60 characters with #shorts #meme
2. HIGH-RETENTION MEME DESCRIPTION:
   - 2-line relatable hook that gets people into comments ("Tag that friend who...", "What would you do here?")
   - Engagement question to boost comment count
   - Essential hashtags: #shorts #meme #memes #funny #relatable #viral #comedy
3. TOP 15 ALGORITHM-OPTIMIZED TAGS:
   - Comma-separated list of top search and suggestion tags for YouTube algorithm recommendation.
4. THUMBNAIL / FIRST FRAME HOOK:
   - Description of the perfect freeze-frame thumbnail with zoom-in face or red arrow text overlay.

Respond in clean, well-formatted markdown.
"""
    try:
        response = _query_ai(prompt)
    except Exception as e:
        response = f"Could not generate viral SEO: {e}"

    return {
        "topic": topic,
        "niche": niche,
        "seo_package": response,
    }


# ============================================================
# AUTONOMOUS MEME SHORT GENERATOR
# ============================================================

def generate_niche_meme_short(custom_niche: str = None) -> dict:
    """
    Autonomously generate a viral meme video script, visual concept,
    and text captions for YouTube Shorts when the user is busy.
    """
    niche = custom_niche or get_channel_niche()

    prompt = f"""
You are a viral YouTube Shorts and meme creator.
Channel Niche: {niche}

Generate a hilarious, highly relatable 15-second YouTube Shorts meme concept that performs virally.
Include:
1. VIRAL SHORT TITLE (with #Shorts #meme)
2. VISUAL SETUP (What appears on screen for the first 3 seconds)
3. ON-SCREEN TEXT OVERLAY (Punchy caption in top/bottom text style)
4. AUDIO / MUSIC SUGGESTION (Trending meme sound or voice tone)
5. PUNCHLINE / CLIMAX (The funny conclusion at 12-15 seconds)

Keep it short, punchy, and modern.
"""
    try:
        meme_plan = _query_ai(prompt)
    except Exception as e:
        meme_plan = f"Could not generate meme short: {e}"

    # Generate a sample meme caption image card if PIL is available
    meme_image_path = None
    if PIL_AVAILABLE:
        try:
            meme_image_path = _create_meme_card(niche)
        except Exception:
            pass

    return {
        "niche": niche,
        "meme_plan": meme_plan,
        "image_asset": meme_image_path,
    }


def _create_meme_card(niche: str) -> str:
    """Creates a 1080x1920 vertical Shorts meme card banner."""
    width, height = 720, 1280
    image = Image.new("RGB", (width, height), color=(15, 23, 42))
    draw = ImageDraw.Draw(image)

    # Header banner
    draw.rectangle([(0, 0), (width, 160)], fill=(0, 229, 255))
    draw.text((40, 60), f"NEXUS MEME SHORT // {niche.upper()[:25]}", fill=(10, 15, 25))

    # Center box
    draw.rectangle([(50, 400), (width - 50, 880)], outline=(0, 229, 255), width=3)
    draw.text((80, 490), "WHEN YOU POST A RANDOM MEME", fill=(255, 255, 255))
    draw.text((80, 550), "AND IT GOES VIRAL OVERNIGHT:", fill=(0, 229, 255))
    draw.text((80, 670), "• Status: +500K Views 🚀", fill=(148, 163, 184))
    draw.text((80, 730), "• Notifications: 999+ Comments 💀", fill=(244, 63, 94))
    draw.text((80, 790), "• Algorithm: You're on the For You page!", fill=(52, 211, 153))

    save_path = "nexus_meme_short.png"
    image.save(save_path)
    return os.path.abspath(save_path)


# ============================================================
# STUDIO & CAPCUT LAUNCHERS
# ============================================================

def open_youtube_studio() -> str:
    """Open YouTube Studio in the default browser."""
    webbrowser.open("https://studio.youtube.com")
    return "Opened YouTube Studio."


def open_capcut() -> str:
    """Open CapCut for video editing."""
    from core.pc import open_app
    return open_app("capcut")


# ============================================================
# BUSY REMINDER & QUEUE SYSTEM
# ============================================================

def check_upload_reminder(phone_number: str = None) -> str:
    """
    Check if the user is overdue for an upload, and alert their phone.
    """
    niche = get_channel_niche()
    message = (
        f"Hey Sachin, upload reminder! It's time to post for your YouTube channel ({niche}). "
        "If you're busy, tell me 'create meme short' and I'll generate one for you!"
    )

    # Register with security gate if phone alert is requested
    if phone_number:
        permission_gate.request_permission(
            action_name="YOUTUBE_SCHEDULE_REMINDER",
            description=message,
            phone_number=phone_number,
        )

    return message
