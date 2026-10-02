# ============================================================
# NEXUS — MULTI-CHANNEL YOUTUBE CONTROLLER & SWITCHER
# Seamlessly toggles between MemesWorld21 and FusionX_YT
# ============================================================

import os
import json
import logging
from typing import Dict, Any, Optional

from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger("NexusChannelSwitcher")

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ACTIVE_CHANNEL_FILE = os.path.join(BASE_DIR, "data", "active_channel.json")

CHANNELS = {
    "MemesWorld21": {
        "display_name": "MemesWorld21",
        "handle": "@MemesWorld21",
        "niche": "Viral Memes & Relatable Comedy",
        "category_id": "23", # Comedy
        "db_file": "meme_channel.json",
        "token_env_prefix": "MEMES_YOUTUBE",
        "default_tags": ["shorts", "meme", "memes", "funny", "relatable", "comedy", "viral", "dankmemes"]
    },
    "FusionX_YT": {
        "display_name": "FusionX_YT",
        "handle": "@FusionX_YT",
        "niche": "Interactive Puzzles, Logo Quizzes, Hidden Letters & Brain Teasers",
        "category_id": "24", # Entertainment / Puzzles
        "db_file": "fusion_channel.json",
        "token_env_prefix": "FUSION_YOUTUBE",
        "default_tags": ["shorts", "puzzle", "quiz", "riddle", "brainteaser", "findtheoddone", "logopuzzle", "countdown", "challenge"]
    }
}


def _ensure_active_file():
    os.makedirs(os.path.dirname(ACTIVE_CHANNEL_FILE), exist_ok=True)
    if not os.path.exists(ACTIVE_CHANNEL_FILE):
        with open(ACTIVE_CHANNEL_FILE, "w", encoding="utf-8") as f:
            json.dump({"active_channel": "MemesWorld21"}, f, indent=2)


def get_active_channel_name() -> str:
    """Return the currently selected YouTube channel name ('MemesWorld21' or 'FusionX_YT')."""
    _ensure_active_file()
    try:
        with open(ACTIVE_CHANNEL_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data.get("active_channel", "MemesWorld21")
    except Exception:
        return "MemesWorld21"


def get_active_channel_config() -> Dict[str, Any]:
    """Return the configuration dictionary for the active channel."""
    name = get_active_channel_name()
    return CHANNELS.get(name, CHANNELS["MemesWorld21"])


def get_active_channel_db_path() -> str:
    """Return the full file path to the active channel's JSON database."""
    cfg = get_active_channel_config()
    return os.path.join(BASE_DIR, "data", cfg["db_file"])


def switch_channel(target: str) -> Dict[str, Any]:
    """
    Switch NEXUS to manage a different YouTube channel.
    Target can be 'memes', 'fusion', 'MemesWorld21', 'FusionX_YT', etc.
    """
    _ensure_active_file()
    clean = target.strip().lower()

    if any(k in clean for k in ["fusion", "puzzle", "quiz", "brain"]):
        selected = "FusionX_YT"
    elif any(k in clean for k in ["meme", "memes", "world", "comedy"]):
        selected = "MemesWorld21"
    else:
        for k in CHANNELS:
            if k.lower() == clean:
                selected = k
                break
        else:
            return {
                "success": False,
                "message": f"Unknown channel '{target}'. Available channels: {', '.join(CHANNELS.keys())}"
            }

    with open(ACTIVE_CHANNEL_FILE, "w", encoding="utf-8") as f:
        json.dump({"active_channel": selected}, f, indent=2)

    cfg = CHANNELS[selected]
    logger.info(f"NEXUS switched active YouTube channel to: {selected} ({cfg['handle']})")

    # Update active credentials in memory if channel-specific tokens exist
    prefix = cfg["token_env_prefix"]
    chan_token = os.getenv(f"{prefix}_ACCESS_TOKEN")
    if chan_token:
        os.environ["YOUTUBE_ACCESS_TOKEN"] = chan_token

    return {
        "success": True,
        "active_channel": selected,
        "handle": cfg["handle"],
        "niche": cfg["niche"],
        "message": f"Switched active channel to '{selected}' ({cfg['handle']})!\nNiche: {cfg['niche']}"
    }


def list_channels() -> Dict[str, Any]:
    """List all configured YouTube channels and their current active status."""
    active = get_active_channel_name()
    result = {}
    for name, cfg in CHANNELS.items():
        db_path = os.path.join(BASE_DIR, "data", cfg["db_file"])
        has_db = os.path.exists(db_path)
        prefix = cfg["token_env_prefix"]
        has_token = bool(os.getenv(f"{prefix}_ACCESS_TOKEN") or (name == "MemesWorld21" and os.getenv("YOUTUBE_ACCESS_TOKEN")))
        result[name] = {
            "display_name": cfg["display_name"],
            "handle": cfg["handle"],
            "niche": cfg["niche"],
            "is_active": (name == active),
            "has_credentials": has_token,
            "has_database": has_db
        }
    return result
