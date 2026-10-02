# ============================================================
# NEXUS CLOUD AUTOPILOT ENGINE (24/7 BACKGROUND WORKER)
# Runs continuously in the cloud when laptop and phone are offline
# ============================================================

import os
import time
import json
import logging
import threading
from datetime import datetime
from typing import Dict, List, Optional, Any

from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger("NexusCloudAutopilot")
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")


class AutopilotEngine:
    """
    Autonomous 24/7 Cloud Engine for NEXUS.
    Maintains channel monitoring, generates viral SEO & meme short drafts,
    and handles remote user approvals even if laptop is powered off.
    """

    def __init__(self, storage_path: str = "cloud_storage.json"):
        self.storage_path = storage_path
        self.channel_niche = os.getenv("CHANNEL_NICHE", "Viral Memes & Relatable Comedy")
        self.check_interval = int(os.getenv("CLOUD_CHECK_INTERVAL_SECONDS", "21600")) # 6 hours default
        self.gemini_key = os.getenv("GEMINI_API_KEY", "")
        self.running = False
        self.worker_thread: Optional[threading.Thread] = None

        self.state: Dict[str, Any] = {
            "niche": self.channel_niche,
            "created_at": datetime.now().isoformat(),
            "last_check": None,
            "pending_drafts": [],
            "approved_drafts": [],
            "rejected_drafts": [],
            "sync_counter": 0,
        }

        self._load_storage()

    # ------------------------------------------------------------
    # PERSISTENCE
    # ------------------------------------------------------------

    def _load_storage(self):
        if os.path.exists(self.storage_path) and os.path.getsize(self.storage_path) > 0:
            try:
                with open(self.storage_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.state.update(data)
                logger.info(f"Loaded {len(self.state.get('pending_drafts', []))} pending drafts from cloud storage.")
            except Exception as e:
                logger.error(f"Failed to read cloud storage: {e}")

    def _save_storage(self):
        try:
            with open(self.storage_path, "w", encoding="utf-8") as f:
                json.dump(self.state, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Failed to save cloud storage: {e}")

    # ------------------------------------------------------------
    # CLOUD AI GENERATION (GEMINI 3.5 FLASH LITE)
    # ------------------------------------------------------------

    def _query_cloud_ai(self, prompt: str) -> str:
        """Query cloud Gemini API directly."""
        key = self.gemini_key or os.getenv("GEMINI_API_KEY", "")
        if key:
            try:
                from google import genai
                client = genai.Client(api_key=key)
                chat = client.chats.create(model="gemini-3.5-flash-lite")
                resp = chat.send_message(prompt)
                return resp.text.strip()
            except Exception as e:
                logger.error(f"Cloud Gemini error: {e}")

        # Fallback to local Ollama if running on a self-hosted cloud VPS with Ollama
        try:
            import requests
            r = requests.post(
                "http://localhost:11434/api/generate",
                json={"model": "qwen3:8b", "prompt": prompt, "stream": False},
                timeout=45,
            )
            return r.json().get("response", "").strip()
        except Exception:
            pass

        return "NEXUS Cloud AI temporarily unavailable. Please check GEMINI_API_KEY."

    # ------------------------------------------------------------
    # AUTONOMOUS CONTENT DRAFT GENERATOR
    # ------------------------------------------------------------

    def generate_autonomous_draft(self, custom_topic: Optional[str] = None) -> Dict[str, Any]:
        """
        Autonomously research and generate a viral SEO package
        and YouTube Shorts meme concept for the channel.
        """
        niche = self.state.get("niche", self.channel_niche)
        topic = custom_topic or f"Trending viral moment in {niche}"
        draft_id = f"draft_{int(time.time())}"

        logger.info(f"Autopilot generating cloud draft for niche: '{niche}', topic: '{topic}'")

        prompt = f"""
You are the elite 24/7 AI Producer for a top YouTube channel.
Target Niche: {niche}
Focus Topic: {topic}

Generate an autonomous VIRAL CONTENT PACKAGE including:
1. THREE HIGH-CTR TITLES (Curiosity-gap, high emotional contrast, under 60 chars)
2. VIRAL SEO DESCRIPTION (First 2 lines strong hook, timestamps outline, 3 hashtags)
3. TOP 15 SEARCH TAGS (Comma-separated)
4. 15-SECOND YOUTUBE SHORTS MEME SCRIPT:
   - Visual Setup (0-3s)
   - On-Screen Text Caption
   - Audio / Music recommendation
   - Punchline Climax (12-15s)

Format cleanly with clear headings.
"""
        ai_response = self._query_cloud_ai(prompt)

        draft_item = {
            "id": draft_id,
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "niche": niche,
            "topic": topic,
            "content": ai_response,
            "status": "PENDING_APPROVAL",
        }

        self.state["pending_drafts"].append(draft_item)
        self.state["sync_counter"] += 1
        self._save_storage()

        # Send alert via Telegram Bot if configured
        self._notify_user(draft_item)

        return draft_item

    # ------------------------------------------------------------
    # USER NOTIFICATION (TELEGRAM / WEBHOOK)
    # ------------------------------------------------------------

    def _notify_user(self, draft_item: Dict[str, Any]):
        """Dispatches an alert to user's Telegram or Webhook."""
        bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
        chat_id = os.getenv("TELEGRAM_CHAT_ID")

        if bot_token and chat_id:
            try:
                import requests
                text = (
                    f"🚀 *NEXUS 24/7 CLOUD AUTOPILOT ALERT*\n\n"
                    f"A new viral draft is ready for niche: *{draft_item['niche']}*\n"
                    f"ID: `{draft_item['id']}`\n\n"
                    f"Preview:\n{draft_item['content'][:300]}...\n\n"
                    f"Reply with:\n"
                    f"• `approve {draft_item['id']}` to confirm\n"
                    f"• `reject {draft_item['id']}` to discard"
                )
                url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
                requests.post(url, json={"chat_id": chat_id, "text": text, "parse_mode": "Markdown"}, timeout=10)
                logger.info(f"Sent Telegram notification for {draft_item['id']}")
            except Exception as e:
                logger.warning(f"Telegram notification failed: {e}")

    # ------------------------------------------------------------
    # APPROVAL WORKFLOW
    # ------------------------------------------------------------

    def approve_draft(self, draft_id: str) -> bool:
        """Mark a draft as approved by the user."""
        for draft in list(self.state.get("pending_drafts", [])):
            if draft.get("id") == draft_id:
                draft["status"] = "APPROVED"
                draft["approved_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                self.state["pending_drafts"].remove(draft)
                self.state["approved_drafts"].append(draft)
                self.state["sync_counter"] += 1
                self._save_storage()
                return True
        return False

    def reject_draft(self, draft_id: str) -> bool:
        """Mark a draft as rejected/discarded."""
        for draft in list(self.state.get("pending_drafts", [])):
            if draft.get("id") == draft_id:
                draft["status"] = "REJECTED"
                self.state["pending_drafts"].remove(draft)
                self.state["rejected_drafts"].append(draft)
                self.state["sync_counter"] += 1
                self._save_storage()
                return True
        return False

    # ------------------------------------------------------------
    # SYNC FOR DESKTOP NEXUS
    # ------------------------------------------------------------

    def get_sync_payload(self) -> Dict[str, Any]:
        """Provides state update payload for desktop NEXUS V1."""
        return {
            "status": "ONLINE",
            "server_time": datetime.now().isoformat(),
            "niche": self.state.get("niche"),
            "sync_counter": self.state.get("sync_counter", 0),
            "pending_count": len(self.state.get("pending_drafts", [])),
            "approved_count": len(self.state.get("approved_drafts", [])),
            "pending_drafts": self.state.get("pending_drafts", []),
            "approved_drafts": self.state.get("approved_drafts", []),
        }

    # ------------------------------------------------------------
    # BACKGROUND 24/7 LOOP
    # ------------------------------------------------------------

    def _loop(self):
        logger.info(f"Autopilot background loop started (interval={self.check_interval}s).")
        while self.running:
            try:
                self.state["last_check"] = datetime.now().isoformat()
                # If there are no pending drafts, generate an autonomous daily draft
                if len(self.state.get("pending_drafts", [])) == 0:
                    self.generate_autonomous_draft()
            except Exception as e:
                logger.error(f"Error in autopilot loop: {e}")

            # Sleep in 5-second intervals to allow fast shutdown
            for _ in range(self.check_interval // 5):
                if not self.running:
                    break
                time.sleep(5)

    def start(self):
        """Start the 24/7 background worker thread."""
        if not self.running:
            self.running = True
            self.worker_thread = threading.Thread(target=self._loop, daemon=True, name="NexusAutopilot")
            self.worker_thread.start()
            logger.info("NEXUS Cloud Autopilot running.")

    def stop(self):
        """Stop the background worker."""
        self.running = False
        if self.worker_thread and self.worker_thread.is_alive():
            self.worker_thread.join(timeout=2)
        logger.info("NEXUS Cloud Autopilot stopped.")


# Global Cloud Autopilot instance
cloud_autopilot = AutopilotEngine()
