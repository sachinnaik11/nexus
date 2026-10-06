"""
NEXUS 24/7 Channel Guard & Autonomous Optimizer
Monitors YouTube channel @memesworld21 continuously.
Detects new uploads in real-time, inspects frames visually with Gemini Vision,
and applies 100% video-accurate viral titles, tags, and descriptions automatically.
"""

import os
import sys
import time
import json
import logging
from datetime import datetime

# Configure UTF-8 for Windows console
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from tools.youtube_automation import youtube_automator
from tools.meme_channel_db import get_current_channel_db

LOG_FILE = os.path.join("data", "channel_guard.log")
os.makedirs("data", exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] ChannelGuard: %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE, encoding="utf-8"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("ChannelGuard")

CHECK_INTERVAL_SECONDS = 90
STATS_CHECK_INTERVAL_SECONDS = 900  # Check view counts every 15 mins

def check_new_uploads():
    """Checks for newly uploaded videos and automatically optimizes them."""
    try:
        current_db = get_current_channel_db()
        latest = youtube_automator.get_latest_video()
        if not latest.get("success"):
            logger.warning(f"Could not fetch latest video: {latest.get('message')}")
            return

        vid_id = latest.get("video_id")
        title = latest.get("title", "")
        if not vid_id:
            return

        processed = set(current_db.get_processed_videos())
        if vid_id not in processed:
            logger.info(f"🚨 NEW UPLOAD DETECTED: {vid_id} ('{title}')")
            logger.info("Waiting 30 seconds for YouTube thumbnail processing...")
            time.sleep(30)

            logger.info(f"Running Gemini Vision visual analysis on {vid_id}...")
            result = youtube_automator.auto_optimize_latest_video()
            logger.info(f"Optimization Result:\n{result}")

            current_db.mark_video_processed(vid_id, title)
            logger.info(f"✅ Video {vid_id} successfully protected and marked processed.")
        else:
            logger.debug(f"Latest video {vid_id} already optimized. Standing by.")
    except Exception as e:
        logger.error(f"Error checking uploads: {e}", exc_info=True)

def monitor_view_stats():
    """Logs view counts for top and recently updated videos."""
    try:
        ids = ["U-rBSKdkW0A", "Q5qysL0vyoo", "F3dZs5xRlTc", "Lux0xjjtjIk", "XSxI9FpSbow", "edu3WpQf9d4", "Q9Uq_9FUW5s"]
        url = f"{youtube_automator.YOUTUBE_API_BASE}/videos?part=snippet,statistics&id=" + ",".join(ids)
        headers = youtube_automator._get_headers()
        import requests
        r = requests.get(url, headers=headers, timeout=10).json()
        items = r.get("items", [])
        summary = []
        for item in items:
            v_id = item["id"]
            title = item["snippet"]["title"]
            stats = item.get("statistics", {})
            views = stats.get("viewCount", "0")
            likes = stats.get("likeCount", "0")
            summary.append(f"{v_id}: {views} views, {likes} likes ('{title[:30]}...')")
        logger.info("📊 RECENT VIDEOS STATUS: " + " | ".join(summary))
    except Exception as e:
        logger.warning(f"Could not refresh stats: {e}")

def main():
    logger.info("=" * 60)
    logger.info("🛡️ NEXUS 24/7 CHANNEL GUARD STARTED FOR @memesworld21")
    logger.info(f"Checking every {CHECK_INTERVAL_SECONDS}s. Logging to {LOG_FILE}")
    logger.info("=" * 60)

    last_stats_check = 0
    while True:
        try:
            # Refresh token proactively
            youtube_automator.refresh_access_token()
            
            # Check uploads
            check_new_uploads()

            # Check stats periodically
            now = time.time()
            if now - last_stats_check > STATS_CHECK_INTERVAL_SECONDS:
                monitor_view_stats()
                last_stats_check = now

        except Exception as e:
            logger.error(f"Loop iteration error: {e}")

        time.sleep(CHECK_INTERVAL_SECONDS)

if __name__ == "__main__":
    main()
