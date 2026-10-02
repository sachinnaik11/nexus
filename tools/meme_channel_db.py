# ============================================================
# NEXUS — MEME CHANNEL DATABASE & WORKSPACE STORE
# Dedicated Isolated Manager for MemesWorld21 Profile, Ideas, Calendar & Analytics
# ============================================================

import os
import json
import time
import logging
from typing import Dict, Any, List, Optional

logger = logging.getLogger("NexusMemeChannelDB")

DB_PATH = os.path.join("data", "meme_channel.json")


class MemeChannelDB:
    """
    Dedicated database for your Personal Meme Channel.
    Manages channel profile, idea pipeline, upload calendar, and verified metrics.
    """

    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path
        self._ensure_db()

    def _ensure_db(self):
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        if not os.path.exists(self.db_path):
            initial_data = {
                "profile": {
                    "channel_name": "MemesWorld21",
                    "handle": "@MemesWorld21",
                    "niche": "Viral Memes & Relatable Comedy",
                    "target_audience": "Young adults (18-35), students, and mobile viewers looking for quick relatable laughs",
                    "language": "English (Universal / Hinglish accessible)",
                    "content_formats": [
                        "Fast-cut POV Shorts (8-15s)",
                        "Situational text-caption memes (relatable life/college/work struggles)",
                        "Trending audio punchline videos",
                    ],
                    "upload_schedule": {
                        "cadence": "Daily",
                        "target_time": "19:00",
                        "days": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"],
                    },
                    "goals": {
                        "subscriber_target": 50000,
                        "target_retention_percent": 110,
                        "monthly_views_target": 2000000,
                    },
                },
                "ideas": [],
                "calendar": [],
                "analytics_history": [],
            }
            with open(self.db_path, "w", encoding="utf-8") as f:
                json.dump(initial_data, f, indent=2)

    def _read_data(self) -> Dict[str, Any]:
        try:
            with open(self.db_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error reading meme channel db: {e}")
            return {"profile": {}, "ideas": [], "calendar": [], "analytics_history": []}

    def _write_data(self, data: Dict[str, Any]) -> bool:
        try:
            with open(self.db_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
            return True
        except Exception as e:
            logger.error(f"Error writing meme channel db: {e}")
            return False

    # ------------------------------------------------------------
    # 1. CHANNEL PROFILE
    # ------------------------------------------------------------
    def get_profile(self) -> Dict[str, Any]:
        data = self._read_data()
        return data.get("profile", {})

    def update_profile(self, updates: Dict[str, Any]) -> Dict[str, Any]:
        data = self._read_data()
        profile = data.get("profile", {})
        profile.update(updates)
        data["profile"] = profile
        self._write_data(data)
        return profile

    # ------------------------------------------------------------
    # 2. IDEA MANAGEMENT PIPELINE (KANBAN LIFECYCLE)
    # ------------------------------------------------------------
    def get_ideas(self, status_filter: Optional[str] = None) -> List[Dict[str, Any]]:
        data = self._read_data()
        ideas = data.get("ideas", [])
        if status_filter:
            clean_filter = status_filter.strip().lower()
            return [i for i in ideas if i.get("status", "").lower() == clean_filter]
        return ideas

    def add_idea(
        self,
        title: str,
        format_type: str = "Shorts (9:16)",
        priority: str = "High",
        notes: str = "",
        status: str = "Planned",
    ) -> Dict[str, Any]:
        data = self._read_data()
        new_id = f"idea_{int(time.time())}"
        new_idea = {
            "id": new_id,
            "title": title.strip(),
            "format": format_type,
            "priority": priority,
            "notes": notes.strip(),
            "status": status,
            "created_at": time.strftime("%Y-%m-%d"),
        }
        data.setdefault("ideas", []).append(new_idea)
        self._write_data(data)
        return new_idea

    def update_idea_status(self, idea_id: str, new_status: str) -> bool:
        data = self._read_data()
        updated = False
        for idea in data.get("ideas", []):
            if idea.get("id") == idea_id:
                idea["status"] = new_status
                updated = True
                break
        if updated:
            self._write_data(data)
        return updated

    def delete_idea(self, idea_id: str) -> bool:
        data = self._read_data()
        orig_len = len(data.get("ideas", []))
        data["ideas"] = [i for i in data.get("ideas", []) if i.get("id") != idea_id]
        if len(data["ideas"]) < orig_len:
            self._write_data(data)
            return True
        return False

    # ------------------------------------------------------------
    # 3. UPLOAD CALENDAR & REMINDERS
    # ------------------------------------------------------------
    def get_calendar(self) -> List[Dict[str, Any]]:
        data = self._read_data()
        return data.get("calendar", [])

    def schedule_upload(
        self,
        date_str: str,
        time_str: str,
        title: str,
        idea_id: Optional[str] = None,
        status: str = "Scheduled",
    ) -> Dict[str, Any]:
        data = self._read_data()
        entry = {
            "id": f"cal_{int(time.time())}",
            "date": date_str,
            "time": time_str,
            "title": title,
            "idea_id": idea_id,
            "status": status,
        }
        data.setdefault("calendar", []).append(entry)
        self._write_data(data)
        return entry

    # ------------------------------------------------------------
    # 4. VERIFIED ANALYTICS & LOGGING (NO FAKE METRICS)
    # ------------------------------------------------------------
    def get_analytics_logs(self) -> List[Dict[str, Any]]:
        data = self._read_data()
        return data.get("analytics_history", [])

    def log_video_metrics(
        self,
        title: str,
        views: int,
        likes: int,
        comments: int,
        retention_percent: float,
        source: str = "MANUAL ENTRY - VERIFIED",
        video_id: str = "",
    ) -> Dict[str, Any]:
        data = self._read_data()
        entry = {
            "video_id": video_id or f"vid_{int(time.time())}",
            "title": title,
            "views": int(views),
            "likes": int(likes),
            "comments": int(comments),
            "retention_percent": float(retention_percent),
            "logged_at": time.strftime("%Y-%m-%d"),
            "source": source,
        }
        data.setdefault("analytics_history", []).append(entry)
        self._write_data(data)
        return entry

    # ------------------------------------------------------------
    # 5. DASHBOARD SUMMARY
    # ------------------------------------------------------------
    def get_dashboard_summary(self) -> Dict[str, Any]:
        data = self._read_data()
        profile = data.get("profile", {})
        ideas = data.get("ideas", [])
        calendar = data.get("calendar", [])
        history = data.get("analytics_history", [])

        status_counts = {
            "Planned": sum(1 for i in ideas if i.get("status") == "Planned"),
            "Scripting": sum(1 for i in ideas if i.get("status") == "Scripting"),
            "Editing": sum(1 for i in ideas if i.get("status") == "Editing"),
            "Ready": sum(1 for i in ideas if i.get("status") == "Ready"),
            "Published": sum(1 for i in ideas if i.get("status") == "Published"),
        }

        # Calculate average retention from real logged history
        avg_retention = 0.0
        if history:
            valid_retentions = [h.get("retention_percent", 0) for h in history if h.get("retention_percent")]
            if valid_retentions:
                avg_retention = round(sum(valid_retentions) / len(valid_retentions), 1)

        return {
            "channel_name": profile.get("channel_name", "MemesWorld21"),
            "handle": profile.get("handle", "@MemesWorld21"),
            "niche": profile.get("niche", "Viral Memes & Relatable Comedy"),
            "target_audience": profile.get("target_audience", "Young adults (18-35)"),
            "schedule": profile.get("upload_schedule", {}).get("cadence", "Daily"),
            "pipeline": status_counts,
            "total_ideas": len(ideas),
            "upcoming_uploads_count": len(calendar),
            "avg_retention_percent": avg_retention,
            "total_logged_videos": len(history),
            "auto_add_details_enabled": self.is_auto_details_enabled(),
        }

    # ------------------------------------------------------------
    # 6. AUTONOMOUS AUTO-DETAILS & PROCESSED VIDEO TRACKER
    # ------------------------------------------------------------
    def is_auto_details_enabled(self) -> bool:
        """Check whether 24/7 autonomous video optimization is enabled."""
        data = self._read_data()
        return data.get("auto_add_details_enabled", True)

    def set_auto_details_enabled(self, enabled: bool) -> bool:
        """Persist user preference for autonomous auto-details."""
        data = self._read_data()
        data["auto_add_details_enabled"] = bool(enabled)
        self._write_data(data)
        return bool(enabled)

    def get_processed_videos(self) -> List[str]:
        """Get list of video IDs that have already had details automatically added."""
        data = self._read_data()
        return data.get("processed_video_ids", [])

    def mark_video_processed(self, video_id: str, title: str = "") -> None:
        """Record a video ID as processed so NEXUS doesn't repeatedly rewrite it."""
        if not video_id:
            return
        data = self._read_data()
        processed = set(data.get("processed_video_ids", []))
        processed.add(video_id)
        data["processed_video_ids"] = list(processed)
        self._write_data(data)


# Global singleton instances
meme_db = MemeChannelDB(os.path.join("data", "meme_channel.json"))
fusion_db = MemeChannelDB(os.path.join("data", "fusion_channel.json"))


def get_current_channel_db() -> MemeChannelDB:
    """Return the database corresponding to the currently active channel."""
    try:
        from tools.channel_switcher import get_active_channel_name
        if get_active_channel_name() == "FusionX_YT":
            return fusion_db
    except Exception:
        pass
    return meme_db

