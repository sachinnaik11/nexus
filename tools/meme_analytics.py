# ============================================================
# NEXUS — MEME CHANNEL ANALYTICS & DIAGNOSTIC REVIEWER
# Real YouTube API Metrics, Transparent Manual Logging & AI Post-Upload Diagnostics
# ============================================================

import os
import json
import logging
from typing import Dict, Any, List, Optional
import requests

from tools.youtube_manager import _query_ai
from tools.meme_channel_db import meme_db

logger = logging.getLogger("NexusMemeAnalytics")


class MemeChannelAnalytics:
    """
    Handles real YouTube Analytics when connected, transparent manual metric logging,
    and deep video diagnostic reviews. Never invents fake numbers.
    """

    YOUTUBE_API_BASE = "https://www.googleapis.com/youtube/v3"

    def __init__(self):
        self.access_token = os.getenv("YOUTUBE_ACCESS_TOKEN", "").strip()

    # ------------------------------------------------------------
    # 1. REAL API CHANNEL STATS (WHEN CONNECTED)
    # ------------------------------------------------------------
    def fetch_live_channel_stats(self) -> Dict[str, Any]:
        """
        Queries official YouTube Data API v3 for real subscriber and view counts.
        """
        token = os.getenv("YOUTUBE_ACCESS_TOKEN", "").strip()
        if not token:
            return {
                "connected": False,
                "message": (
                    "YouTube API is not currently connected.\n"
                    "Using local manual tracking mode. (Add YOUTUBE_ACCESS_TOKEN in .env to link live stats)."
                ),
            }

        headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/json",
        }

        try:
            url = f"{self.YOUTUBE_API_BASE}/channels?part=snippet,statistics&mine=true"
            res = requests.get(url, headers=headers, timeout=10)
            if res.status_code == 200:
                items = res.json().get("items", [])
                if items:
                    stats = items[0].get("statistics", {})
                    snippet = items[0].get("snippet", {})
                    return {
                        "connected": True,
                        "title": snippet.get("title", ""),
                        "subscribers": int(stats.get("subscriberCount", 0)),
                        "views": int(stats.get("viewCount", 0)),
                        "video_count": int(stats.get("videoCount", 0)),
                        "message": "Connected to official YouTube Data API v3.",
                    }
            return {
                "connected": False,
                "message": f"YouTube API returned status {res.status_code}: {res.text[:150]}",
            }
        except Exception as e:
            return {"connected": False, "message": f"Network error querying YouTube API: {e}"}

    # ------------------------------------------------------------
    # 2. VERIFIED MANUAL ENTRY (ZERO FAKE DATA)
    # ------------------------------------------------------------
    def record_manual_metrics(
        self,
        title: str,
        views: int,
        likes: int,
        comments: int,
        retention_percent: float,
    ) -> Dict[str, Any]:
        """
        Saves user-verified real metrics into local database.
        Clearly tags the entry as MANUAL ENTRY - VERIFIED.
        """
        entry = meme_db.log_video_metrics(
            title=title,
            views=views,
            likes=likes,
            comments=comments,
            retention_percent=retention_percent,
            source="MANUAL ENTRY - VERIFIED",
        )
        return {
            "success": True,
            "entry": entry,
            "message": f"Recorded verified metrics for '{title}' successfully.",
        }

    # ------------------------------------------------------------
    # 3. AI POST-UPLOAD VIDEO PERFORMANCE DIAGNOSTIC
    # ------------------------------------------------------------
    def diagnose_video_performance(
        self,
        title: str,
        views: int,
        likes: int,
        comments: int,
        retention_percent: float,
        format_type: str = "Shorts (9:16)",
    ) -> str:
        """
        Conducts an in-depth performance audit of a specific video:
        1. Retention Analysis (Shorts algorithm expects >100% through loops)
        2. Engagement Ratio (Likes/Views target: >8%, Comments target: >0.5%)
        3. Drop-off Diagnosis (Why viewers swiped or stayed)
        4. Concrete A/B Test Hypothesis for the next video
        """
        like_ratio = round((likes / max(views, 1)) * 100, 2)
        comment_ratio = round((comments / max(views, 1)) * 100, 2)

        prompt = f"""
You are the Lead Data Analyst for YouTube Meme Channel 'MemesWorld21'.
Analyze the performance of this YouTube Short:

Video Title: "{title}"
Format: {format_type}
Views: {views:,}
Likes: {likes:,} (Like-to-View Ratio: {like_ratio}%)
Comments: {comments:,} (Comment-to-View Ratio: {comment_ratio}%)
Average View Retention: {retention_percent}%

Benchmarks for YouTube Meme Shorts:
- Viral Retention Threshold: 100% - 120% (due to loop-replays)
- Strong Like Ratio: > 8%
- Strong Comment Ratio: > 0.5%

Provide a strict, professional Diagnostic Audit:
1. 📊 PERFORMANCE SUMMARY:
   - Grade the video (S / A / B / C / Flop) based strictly on retention and engagement.
2. 🪝 HOOK & RETENTION DIAGNOSIS:
   - If retention is under 100%, explain where and why viewers dropped off.
   - If retention is over 100%, explain what caused the loop rewatch.
3. 💬 ENGAGEMENT & ALGORITHM SIGNALS:
   - Evaluate whether the title and comments triggered algorithm distribution.
4. 🔬 ONE CONCRETE A/B EXPERIMENT FOR NEXT VIDEO:
   - Propose a single, specific variable to test on the next video (e.g., test a 2-second shorter setup, or a different punchline audio cue).

Format your response in crisp markdown.
"""
        return _query_ai(prompt)


# Global singleton instance
meme_analytics = MemeChannelAnalytics()
