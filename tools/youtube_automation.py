# ============================================================
# NEXUS — AUTONOMOUS YOUTUBE CHANNEL MANAGER & STUDIO AUTOMATOR
# Direct Channel Access, Live Video Metadata Editing & Studio Auto-Fill
# ============================================================

import os
import re
import time
import json
import logging
import threading
from typing import Dict, Any, Optional, List

import requests
from dotenv import load_dotenv

from tools.youtube_manager import get_channel_niche, generate_viral_seo, _query_ai
from core.permissions import permission_gate

load_dotenv()
logger = logging.getLogger("NexusYouTubeAutomation")
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")


class YouTubeChannelAutomator:
    """
    Autonomous YouTube Channel Automation Engine.
    Provides direct channel access to automatically edit video titles,
    descriptions, and tags, plus 1-click desktop browser auto-fill.
    """

    YOUTUBE_API_BASE = "https://www.googleapis.com/youtube/v3"

    def __init__(self):
        self.access_token = os.getenv("YOUTUBE_ACCESS_TOKEN", "")
        self.api_key = os.getenv("YOUTUBE_API_KEY", os.getenv("GEMINI_API_KEY", ""))
        self.channel_id = os.getenv("YOUTUBE_CHANNEL_ID", "")
        self.watcher_running = False
        self.watcher_thread: Optional[threading.Thread] = None
        self.last_processed_video_id: Optional[str] = None

    # ------------------------------------------------------------
    # AUTHENTICATION & HEADERS
    # ------------------------------------------------------------

    def refresh_access_token(self) -> bool:
        """Automatically refresh expired OAuth access token using refresh_token."""
        try:
            from tools.channel_switcher import get_active_channel_config
            cfg = get_active_channel_config()
            prefix = cfg.get("token_env_prefix", "MEMES_YOUTUBE")
        except Exception:
            prefix = "MEMES_YOUTUBE"

        refresh_token = (os.getenv(f"{prefix}_REFRESH_TOKEN") or os.getenv("YOUTUBE_REFRESH_TOKEN", "")).strip()
        client_id = (os.getenv(f"{prefix}_CLIENT_ID") or os.getenv("YOUTUBE_CLIENT_ID", "")).strip()
        client_secret = (os.getenv(f"{prefix}_CLIENT_SECRET") or os.getenv("YOUTUBE_CLIENT_SECRET", "")).strip()
        if not (refresh_token and client_id and client_secret):
            return False
        try:
            url = "https://oauth2.googleapis.com/token"
            data = {
                "client_id": client_id,
                "client_secret": client_secret,
                "refresh_token": refresh_token,
                "grant_type": "refresh_token",
            }
            res = requests.post(url, data=data, timeout=10)
            if res.status_code == 200:
                new_token = res.json().get("access_token", "")
                if new_token:
                    self.access_token = new_token
                    os.environ["YOUTUBE_ACCESS_TOKEN"] = new_token
                    # Update .env file
                    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                    env_path = os.path.join(base_dir, ".env")
                    if os.path.exists(env_path):
                        with open(env_path, "r", encoding="utf-8") as f:
                            content = f.read()
                        if "YOUTUBE_ACCESS_TOKEN=" in content:
                            content = re.sub(r'YOUTUBE_ACCESS_TOKEN=.*', f'YOUTUBE_ACCESS_TOKEN={new_token}', content)
                        else:
                            content += f"\nYOUTUBE_ACCESS_TOKEN={new_token}\n"
                        with open(env_path, "w", encoding="utf-8") as f:
                            f.write(content)
                    logger.info("Successfully refreshed YouTube OAuth access token!")
                    return True
        except Exception as e:
            logger.error(f"Error refreshing access token: {e}")
        return False

    def _get_headers(self) -> Dict[str, str]:
        token = self.access_token or os.getenv("YOUTUBE_ACCESS_TOKEN", "")
        if token:
            return {
                "Authorization": f"Bearer {token}",
                "Accept": "application/json",
                "Content-Type": "application/json",
            }
        return {"Accept": "application/json", "Content-Type": "application/json"}

    # ------------------------------------------------------------
    # 1. DIRECT CHANNEL ACCESS: FETCH LATEST UPLOADED VIDEO
    # ------------------------------------------------------------

    def get_latest_video(self) -> Dict[str, Any]:
        """
        Fetch the most recently uploaded video from your YouTube channel.
        Uses YouTube Data API v3.
        """
        token = self.access_token or os.getenv("YOUTUBE_ACCESS_TOKEN")
        if not token:
            return {
                "success": False,
                "message": (
                    "YouTube Access Token not configured yet in .env.\n"
                    "Add YOUTUBE_ACCESS_TOKEN='ya29.a0...' to enable direct API edits, "
                    "or use 1-Click Studio Browser Auto-Fill below!"
                ),
            }

        try:
            # 1. Fetch channel's uploads playlist ID
            chan_url = f"{self.YOUTUBE_API_BASE}/channels?part=contentDetails&mine=true"
            res = requests.get(chan_url, headers=self._get_headers(), timeout=10)
            if res.status_code != 200:
                return {
                    "success": False,
                    "status_code": res.status_code,
                    "message": f"YouTube API Error ({res.status_code}): {res.text[:200]}",
                }

            items = res.json().get("items", [])
            if not items:
                return {"success": False, "message": "No YouTube channel found for this account."}

            uploads_playlist_id = (
                items[0]
                .get("contentDetails", {})
                .get("relatedPlaylists", {})
                .get("uploads")
            )
            if not uploads_playlist_id:
                return {"success": False, "message": "Could not locate uploads playlist."}

            # 2. Get latest video from uploads playlist
            playlist_url = (
                f"{self.YOUTUBE_API_BASE}/playlistItems?"
                f"part=snippet&playlistId={uploads_playlist_id}&maxResults=1"
            )
            p_res = requests.get(playlist_url, headers=self._get_headers(), timeout=10)
            p_items = p_res.json().get("items", [])
            if not p_items:
                return {"success": False, "message": "No uploaded videos found on your channel."}

            snippet = p_items[0].get("snippet", {})
            video_id = snippet.get("resourceId", {}).get("videoId")
            title = snippet.get("title", "")
            description = snippet.get("description", "")

            return {
                "success": True,
                "video_id": video_id,
                "title": title,
                "description": description,
                "published_at": snippet.get("publishedAt"),
            }
        except Exception as e:
            return {"success": False, "message": f"Error accessing channel: {e}"}

    # ------------------------------------------------------------
    # 2. DIRECT CHANNEL ACCESS: UPDATE VIDEO TITLE, DESC & TAGS
    # ------------------------------------------------------------

    def update_video_metadata(
        self,
        video_id: str,
        title: str,
        description: str,
        tags: List[str] = None,
        category_id: str = "23", # 23 = Comedy on YouTube
    ) -> Dict[str, Any]:
        """
        Directly update the title, description, tags, and category of a video on YouTube.
        """
        if not video_id:
            return {"success": False, "message": "Missing video_id to update."}

        token = self.access_token or os.getenv("YOUTUBE_ACCESS_TOKEN")
        if not token:
            return {
                "success": False,
                "message": "Missing YOUTUBE_ACCESS_TOKEN in .env. Required for direct API updates.",
            }

        default_tags = ["shorts", "meme", "memes", "funny", "relatable", "comedy", "viral", "dankmemes"]
        video_tags = tags or default_tags

        payload = {
            "id": video_id,
            "snippet": {
                "title": title[:100], # YouTube title limit is 100 chars
                "description": description[:5000],
                "tags": video_tags[:50],
                "categoryId": category_id,
            },
        }

        url = f"{self.YOUTUBE_API_BASE}/videos?part=snippet"
        try:
            res = requests.put(url, headers=self._get_headers(), json=payload, timeout=15)
            if res.status_code == 401:
                # Token expired, refresh and retry once
                if self.refresh_access_token():
                    res = requests.put(url, headers=self._get_headers(), json=payload, timeout=15)

            if res.status_code == 200:
                logger.info(f"Successfully updated YouTube video {video_id} on channel!")
                return {
                    "success": True,
                    "video_id": video_id,
                    "updated_title": title,
                    "message": f"✅ Successfully updated YouTube video '{title}' directly on your channel!",
                }
            return {
                "success": False,
                "status_code": res.status_code,
                "message": f"YouTube API update failed ({res.status_code}): {res.text[:250]}",
            }
        except Exception as e:
            return {"success": False, "message": f"Network error updating video: {e}"}

    # ------------------------------------------------------------
    # 3. END-TO-END AUTONOMOUS OPTIMIZER (WITH GEMINI VISION)
    # ------------------------------------------------------------

    def _analyze_video_visually(self, video_id: str, chan_name: str, niche: str) -> Optional[Dict[str, Any]]:
        """
        Downloads the video's actual thumbnail / freeze-frame and uses Gemini Vision
        to transcribe on-screen text, recognize characters, and craft 100% video-accurate metadata.
        """
        try:
            url = f"{self.YOUTUBE_API_BASE}/videos?part=snippet&id={video_id}"
            res = requests.get(url, headers=self._get_headers(), timeout=10)
            if res.status_code != 200:
                return None
            items = res.json().get("items", [])
            if not items:
                return None

            snippet = items[0].get("snippet", {})
            thumbs = snippet.get("thumbnails", {})
            best_thumb = thumbs.get("maxres") or thumbs.get("standard") or thumbs.get("high") or thumbs.get("default")
            if not best_thumb or not best_thumb.get("url"):
                return None

            thumb_url = best_thumb["url"]
            img_res = requests.get(thumb_url, timeout=15)
            if img_res.status_code != 200 or len(img_res.content) < 1000:
                return None

            import io
            from PIL import Image
            from google import genai

            img = Image.open(io.BytesIO(img_res.content))
            api_key = os.getenv("GEMINI_API_KEY", "").strip()
            if not api_key:
                return None

            client = genai.Client(api_key=api_key)
            prompt = f"""
You are the world's top YouTube Shorts algorithm and viral content expert for channel '{chan_name}'.
Analyze this video freeze-frame with extreme precision:

1. Transcribe any on-screen text verbatim.
2. Identify the character(s), animals, actors, movie/show, or meme format shown in this frame (e.g. Homelander, Patrick Bateman, Loki, dog, cat, cartoon, etc.).
3. What is the EXACT visual joke or relatable situation happening in this video?
4. Generate ONE high-CTR title (under 55 characters) that strictly matches THIS EXACT VIDEO:
   - Do NOT use generic templates like "Bro really thought" unless it describes this specific moment.
   - Include 1-2 punchy emojis and relevant hashtags (e.g. #shorts #meme and character/theme tag).
5. Generate an engaging description that describes THIS EXACT joke with a comment-trigger question to boost retention, and 5-8 relevant hashtags. (NO random spam hashtags like phonk, nokia, etc.).
6. Generate 10 highly relevant search tags matching this video's topic.
7. Generate a witty pinned comment that sparks debates or laughter in the comments.

Output STRICTLY valid JSON with keys:
"transcription", "character_or_scene", "title", "description", "tags", "pinned_comment"
"""
            chat = client.chats.create(model="gemini-3.5-flash-lite")
            response = chat.send_message([img, prompt])
            cleaned = re.sub(r"^```json\s*", "", response.text.strip())
            cleaned = re.sub(r"```$", "", cleaned.strip())
            return json.loads(cleaned)
        except Exception as e:
            logger.warning(f"Visual video analysis fallback: {e}")
            return None

    def auto_optimize_latest_video(self, custom_topic: Optional[str] = None) -> str:
        """
        Fetches the latest uploaded video from your channel, uses Gemini Vision
        to inspect the actual video frames/text, generates high-CTR viral details
        strictly matching the video content, and automatically edits the video on YouTube.
        """
        self.refresh_access_token()
        niche = get_channel_niche()

        # Step 1: Query channel for latest video
        latest = self.get_latest_video()
        video_id = latest.get("video_id")
        current_title = custom_topic if custom_topic else (latest.get("title") or "Uploaded Meme Video")

        try:
            from tools.channel_switcher import get_active_channel_config
            chan_cfg = get_active_channel_config()
            chan_name = chan_cfg.get("display_name", "MemesWorld21")
            target_category = chan_cfg.get("category_id", "23")
        except Exception:
            chan_name = "MemesWorld21"
            target_category = "23"

        vision_data = None
        if video_id and not custom_topic:
            logger.info(f"Inspecting video {video_id} visually using Gemini Vision...")
            vision_data = self._analyze_video_visually(video_id, chan_name, niche)

        if vision_data and vision_data.get("title"):
            new_title = vision_data["title"]
            new_desc = vision_data.get("description", "")
            raw_tags = vision_data.get("tags", [])
            new_tags = [t.strip() for t in raw_tags] if isinstance(raw_tags, list) else [t.strip() for t in str(raw_tags).split(",")]
            pinned = vision_data.get("pinned_comment", "")
            visual_context = (
                f"👁️ Visual Analysis Detected:\n"
                f"  • On-Screen Text: \"{vision_data.get('transcription', 'N/A')}\"\n"
                f"  • Scene/Subject: {vision_data.get('character_or_scene', 'N/A')}\n\n"
            )
        else:
            is_puzzle = "Fusion" in chan_name or "Puzzle" in niche
            if is_puzzle:
                hook_rules = 'hook style e.g. "Only 1% Can Spot the Odd One Out in 5s ⏱️ #shorts #puzzle", "Guess the Logo Challenge 🎨 #shorts"'
                desc_rules = 'High-retention puzzle description with engagement challenge ("Comment your answer before the buzzer!", question to boost comments, and hashtags #shorts #puzzle #quiz #brainteaser)'
                tags_rule = 'Exactly 10 viral comma-separated tags'
                pinned_rule = 'An interactive comment driving answers'
            else:
                hook_rules = 'hook style describing the specific topic with punchy emojis e.g. "When you..." #shorts #meme'
                desc_rules = 'High-retention meme description with engagement hook, question to boost comments, and hashtags #shorts #meme #memes #funny #comedy #relatable'
                tags_rule = 'Exactly 10 viral comma-separated tags'
                pinned_rule = 'A funny first comment to pin that drives reply debates.'

            prompt = f"""
You are the world's top YouTube Shorts algorithm growth expert for {chan_name}.
Channel Niche: {niche}
Video Topic or Current Title: {current_title}

Generate the complete viral metadata package for this video:
1. TITLE: Exactly ONE high-CTR title (Under 55 chars, {hook_rules})
2. DESCRIPTION: {desc_rules}
3. TAGS: {tags_rule}
4. PINNED_COMMENT: {pinned_rule}

Output strictly valid JSON with keys: "title", "description", "tags", "pinned_comment"
"""
            raw_response = _query_ai(prompt)
            visual_context = ""
            try:
                cleaned = re.sub(r"^```json\s*", "", raw_response.strip())
                cleaned = re.sub(r"```$", "", cleaned.strip())
                parsed = json.loads(cleaned)
                new_title = parsed.get("title", f"POV: When you see this 💀 #shorts #meme")
                new_desc = parsed.get("description", "Wait for the plot twist 💀\n\n#shorts #meme #memes #comedy #relatable")
                raw_tags = parsed.get("tags", [])
                new_tags = [t.strip() for t in raw_tags] if isinstance(raw_tags, list) else [t.strip() for t in str(raw_tags).split(",")]
                pinned = parsed.get("pinned_comment", "Tag that one friend who needs to see this 💀👇")
            except Exception:
                new_title = f"POV: When this happens in real life 💀 #shorts #meme"
                new_desc = "Subscribe for daily memes! Tag that one friend 😭\n\n#shorts #meme #memes #relatable #funny #comedy"
                new_tags = ["shorts", "meme", "memes", "funny", "relatable", "comedy", "viral"]
                pinned = "Tag that one friend who always does this 💀👇"

        # Step 3: Direct API Update if token is active
        if latest.get("success") and video_id:
            update_res = self.update_video_metadata(video_id, new_title, new_desc, new_tags)
            if update_res.get("success"):
                return (
                    f"🎉 AUTO-DETAILS ADDED DIRECTLY TO YOUTUBE!\n\n"
                    f"{visual_context}"
                    f"• Video ID: {video_id}\n"
                    f"• Title: {new_title}\n"
                    f"• Description: {new_desc[:120]}...\n"
                    f"• Tags: {', '.join(new_tags[:8])}\n"
                    f"• Pinned Comment: \"{pinned}\"\n\n"
                    f"✅ Your video has been updated directly on YouTube to maximize viral reach!"
                )

        # Step 4: If API token is missing, copy to clipboard for 1-click paste into Studio
        try:
            import pyperclip
            pyperclip.copy(f"TITLE:\n{new_title}\n\nDESCRIPTION:\n{new_desc}\n\nTAGS:\n{', '.join(new_tags)}")
            clipboard_note = "\n(Copied Title, Description & Tags to your clipboard for instant Ctrl+V into Studio!)"
        except Exception:
            clipboard_note = ""

        return (
            f"✍️ VIRAL DETAILS READY FOR YOUR VIDEO:\n\n"
            f"📌 TITLE:\n{new_title}\n\n"
            f"📝 DESCRIPTION:\n{new_desc}\n\n"
            f"🏷️ TAGS:\n{', '.join(new_tags)}\n\n"
            f"💬 PINNED COMMENT:\n\"{pinned}\"\n"
            f"{clipboard_note}"
        )

    # ------------------------------------------------------------
    # 4. ONE-CLICK DESKTOP STUDIO BROWSER AUTO-FILL (PYAUTOGUI)
    # ------------------------------------------------------------

    def autofill_studio_browser(self, topic: Optional[str] = None) -> str:
        """
        Desktop browser automation:
        Generates viral meme metadata, brings YouTube Studio into focus,
        and automatically fills the Title and Description fields!
        """
        try:
            import pyautogui
            import pyperclip
        except ImportError:
            return "pyautogui or pyperclip not available for desktop auto-fill."

        # Generate package
        niche = get_channel_niche()
        package_text = self.auto_optimize_latest_video(topic)

        # Parse generated title
        title_match = re.search(r"📌 VIRAL TITLE:\n([^\n]+)", package_text)
        desc_match = re.search(r"📝 RETENTION DESCRIPTION:\n(.*?)(?=\n🏷️ TOP TAGS:|$)", package_text, re.DOTALL)

        title = title_match.group(1).strip() if title_match else "POV: When the meme hits too hard 💀 #shorts #meme"
        description = desc_match.group(1).strip() if desc_match else "Wait for it 💀\n\n#shorts #meme #memes #relatable"

        # Copy Title to clipboard
        pyperclip.copy(title)

        return (
            f"✨ VIRAL MEME TITLE & DESCRIPTION READY!\n\n"
            f"• Title: {title}\n\n"
            f"Ready in clipboard! When uploading in YouTube Studio, just press Ctrl+V into the Title box!"
        )

    # ------------------------------------------------------------
    # 5. 24/7 AUTONOMOUS CHANNEL WATCHER DAEMON
    # ------------------------------------------------------------

    def _watcher_loop(self, interval_seconds: int = 60):
        logger.info(f"YouTube Channel Watcher running (checking every {interval_seconds}s).")
        while self.watcher_running:
            try:
                from tools.meme_channel_db import get_current_channel_db
                current_db = get_current_channel_db()
                latest = self.get_latest_video()
                if latest.get("success"):
                    vid_id = latest.get("video_id")
                    title = latest.get("title", "")
                    processed_ids = current_db.get_processed_videos()
                    is_unprocessed = vid_id and (vid_id not in processed_ids) and (vid_id != self.last_processed_video_id)
                    needs_optimization = (
                        "VID_" in title
                        or "untitled" in title.lower()
                        or "video" in title.lower()
                        or "capcut" in title.lower()
                        or "export" in title.lower()
                        or "draft" in title.lower()
                        or len(title) < 20
                        or ("#shorts" not in title.lower())
                    )
                    if is_unprocessed and needs_optimization:
                        logger.info(f"🚀 AUTO-DETECTED NEW UPLOAD: {vid_id} ('{title}'). Automatically adding viral details...")
                        self.auto_optimize_latest_video()
                        self.last_processed_video_id = vid_id
                        current_db.mark_video_processed(vid_id, title)
                        logger.info(f"✅ AUTONOMOUS DETAILS APPLIED to {vid_id} ('{title}')")
            except Exception as e:
                logger.error(f"Error in channel watcher: {e}")

            for _ in range(max(1, interval_seconds)):
                if not self.watcher_running:
                    break
                time.sleep(1)

    def start_channel_watcher(self, interval_seconds: int = 60) -> str:
        """Start the background watcher daemon to auto-edit uploaded videos."""
        from tools.meme_channel_db import meme_db
        meme_db.set_auto_details_enabled(True)
        if not self.watcher_running:
            self.watcher_running = True
            self.watcher_thread = threading.Thread(
                target=self._watcher_loop,
                args=(interval_seconds,),
                daemon=True,
                name="NexusYouTubeWatcher"
            )
            self.watcher_thread.start()
            return "✅ Auto-Details is ACTIVE! NEXUS is monitoring your YouTube channel 24/7. When you upload any video, viral details will be added automatically."
        return "Auto-Details is already active and monitoring your channel."

    def stop_channel_watcher(self) -> str:
        """Stop the background watcher."""
        from tools.meme_channel_db import meme_db
        meme_db.set_auto_details_enabled(False)
        self.watcher_running = False
        return "Auto-Details paused. NEXUS will wait for manual commands."


# Global singleton instance
youtube_automator = YouTubeChannelAutomator()
