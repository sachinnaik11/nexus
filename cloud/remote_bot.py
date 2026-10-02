# ============================================================
# NEXUS CLOUD REMOTE BOT (TELEGRAM TWO-WAY INTERACTION)
# Enables full remote control from any phone/browser worldwide
# ============================================================

import os
import time
import logging
import threading
from typing import Optional

import requests
from dotenv import load_dotenv

from cloud.autopilot import cloud_autopilot

load_dotenv()

logger = logging.getLogger("NexusRemoteBot")


class NexusRemoteBot:
    """
    Two-way Telegram interface for NEXUS Cloud.
    Runs standalone on the cloud server using standard Telegram HTTP APIs.
    """

    def __init__(self):
        self.bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
        self.authorized_chat_id = os.getenv("TELEGRAM_CHAT_ID")
        self.running = False
        self.worker_thread: Optional[threading.Thread] = None
        self.last_update_id = 0

    @property
    def is_configured(self) -> bool:
        return bool(self.bot_token)

    def send_message(self, chat_id: str, text: str, reply_markup: dict = None):
        """Send a message to the user via Telegram."""
        if not self.bot_token:
            return
        url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
        payload = {
            "chat_id": chat_id,
            "text": text,
            "parse_mode": "Markdown",
        }
        if reply_markup:
            payload["reply_markup"] = reply_markup

        try:
            requests.post(url, json=payload, timeout=10)
        except Exception as e:
            logger.error(f"Failed to send Telegram message: {e}")

    def handle_command(self, chat_id: str, text: str):
        """Process incoming command from Telegram."""
        clean_text = text.strip()
        lower = clean_text.lower()

        logger.info(f"Received Telegram command: {clean_text}")

        # Security check: If authorized_chat_id is set, only respond to owner
        if self.authorized_chat_id and str(chat_id) != str(self.authorized_chat_id):
            self.send_message(chat_id, "⛔ *Access Denied*: You are not authorized to control this NEXUS Cloud node.")
            return

        if lower in ("/start", "/help"):
            msg = (
                "🤖 *NEXUS 24/7 CLOUD CONTROL ACTIVE*\n\n"
                "I am your autonomous cloud AI assistant. Available commands:\n"
                "• `/status` — View 24/7 server health & pending drafts\n"
                "• `/draft <topic>` — Autonomously generate viral SEO + meme\n"
                "• `approve <id>` — Confirm and approve a pending draft\n"
                "• `reject <id>` — Discard a draft\n"
                "• `niche <new_niche>` — Change your channel niche\n"
                "• Or just message me any question to query Cloud Gemini AI!"
            )
            self.send_message(chat_id, msg)
            return

        if lower.startswith("/status"):
            sync = cloud_autopilot.get_sync_payload()
            msg = (
                f"⚡ *NEXUS CLOUD STATUS: ONLINE*\n"
                f"• Server Time: `{sync['server_time']}`\n"
                f"• Channel Niche: *{sync['niche']}*\n"
                f"• Pending Drafts: *{sync['pending_count']}*\n"
                f"• Approved Drafts: *{sync['approved_count']}*"
            )
            self.send_message(chat_id, msg)
            return

        if lower.startswith("/draft") or lower.startswith("draft"):
            topic = clean_text.split(" ", 1)[-1] if " " in clean_text else None
            self.send_message(chat_id, "⚡ *Generating viral package with Cloud Gemini 3.5...*")
            draft = cloud_autopilot.generate_autonomous_draft(topic)
            msg = (
                f"✨ *VIRAL DRAFT CREATED ({draft['id']})*\n"
                f"Niche: *{draft['niche']}*\n\n"
                f"{draft['content']}\n\n"
                f"To approve, reply: `approve {draft['id']}`"
            )
            self.send_message(chat_id, msg)
            return

        if lower.startswith("approve"):
            parts = clean_text.split()
            draft_id = parts[1] if len(parts) > 1 else (cloud_autopilot.state.get("pending_drafts") or [{}])[-1].get("id")
            if draft_id and cloud_autopilot.approve_draft(draft_id):
                self.send_message(chat_id, f"✅ Draft `{draft_id}` *APPROVED*! Saved for desktop sync.")
            else:
                self.send_message(chat_id, "❌ Draft not found or already processed.")
            return

        if lower.startswith("reject"):
            parts = clean_text.split()
            draft_id = parts[1] if len(parts) > 1 else (cloud_autopilot.state.get("pending_drafts") or [{}])[-1].get("id")
            if draft_id and cloud_autopilot.reject_draft(draft_id):
                self.send_message(chat_id, f"🗑️ Draft `{draft_id}` *REJECTED* and removed.")
            else:
                self.send_message(chat_id, "❌ Draft not found.")
            return

        if lower.startswith("niche "):
            new_niche = clean_text[len("niche "):].strip()
            cloud_autopilot.state["niche"] = new_niche
            cloud_autopilot._save_storage()
            self.send_message(chat_id, f"🎯 Channel niche updated to *{new_niche}*.")
            return

        # General AI query fallback
        self.send_message(chat_id, "🧠 *Thinking...*")
        answer = cloud_autopilot._query_cloud_ai(clean_text)
        self.send_message(chat_id, f"🤖 *NEXUS Cloud AI*:\n\n{answer}")

    def _poll_updates(self):
        """Long-polling update loop for Telegram."""
        logger.info("NEXUS Telegram Remote Bot polling started.")
        while self.running:
            try:
                url = f"https://api.telegram.org/bot{self.bot_token}/getUpdates"
                params = {"offset": self.last_update_id + 1, "timeout": 20}
                res = requests.get(url, params=params, timeout=25)
                if res.status_code == 200:
                    data = res.json()
                    for update in data.get("result", []):
                        self.last_update_id = update["update_id"]
                        message = update.get("message", {})
                        text = message.get("text")
                        chat_id = message.get("chat", {}).get("id")
                        if text and chat_id:
                            self.handle_command(str(chat_id), text)
            except Exception as e:
                time.sleep(3)

    def start(self):
        if not self.is_configured:
            logger.info("Telegram Bot Token not configured. Remote Bot disabled.")
            return

        if not self.running:
            self.running = True
            self.worker_thread = threading.Thread(target=self._poll_updates, daemon=True, name="NexusRemoteBot")
            self.worker_thread.start()
            logger.info("NEXUS Telegram Remote Bot started.")

    def stop(self):
        self.running = False
        if self.worker_thread and self.worker_thread.is_alive():
            self.worker_thread.join(timeout=2)


remote_bot = NexusRemoteBot()
