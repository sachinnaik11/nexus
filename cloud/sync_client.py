# ============================================================
# NEXUS CLOUD SYNC CLIENT (DESKTOP INTEGRATION)
# Synchronizes Desktop NEXUS with the 24/7 Cloud Node
# ============================================================

import os
import logging
from typing import Dict, Any, Optional

import requests
from dotenv import load_dotenv

from memory.store import add_memory, get_memory

load_dotenv()

logger = logging.getLogger("NexusCloudSync")


class CloudSyncClient:
    """
    Client embedded in Desktop NEXUS V1.
    Syncs pending video concepts, viral SEO packages, and approved
    actions created by the 24/7 Cloud Server while the laptop was off.
    """

    def __init__(self, cloud_url: Optional[str] = None):
        self.cloud_url = cloud_url or os.getenv("NEXUS_CLOUD_URL", "http://localhost:8000").rstrip("/")
        self.last_sync_counter = 0

    def check_connection(self) -> bool:
        """Verify whether the 24/7 Cloud Node is reachable."""
        try:
            r = requests.get(f"{self.cloud_url}/health", timeout=3)
            return r.status_code == 200
        except Exception:
            return False

    def sync(self) -> Dict[str, Any]:
        """
        Polls the cloud server for new autonomous drafts and updates.
        Returns a sync summary.
        """
        try:
            r = requests.get(f"{self.cloud_url}/api/sync", timeout=5)
            if r.status_code != 200:
                return {"success": False, "message": f"Server responded with status {r.status_code}"}

            data = r.json()
            cloud_counter = data.get("sync_counter", 0)
            pending_drafts = data.get("pending_drafts", [])
            approved_drafts = data.get("approved_drafts", [])

            imported_count = 0
            # If new drafts were created in the cloud, import them into local memory
            if cloud_counter > self.last_sync_counter:
                for draft in pending_drafts + approved_drafts:
                    draft_note = (
                        f"Cloud Draft [{draft.get('id')} - {draft.get('status')}]: "
                        f"Niche: {draft.get('niche')} | Topic: {draft.get('topic')}"
                    )
                    existing_memories = get_memory()
                    if not any(draft.get("id") in str(m) for m in existing_memories):
                        add_memory(draft_note)
                        imported_count += 1

                self.last_sync_counter = cloud_counter

            return {
                "success": True,
                "niche": data.get("niche"),
                "pending_count": len(pending_drafts),
                "approved_count": len(approved_drafts),
                "imported_count": imported_count,
                "server_time": data.get("server_time"),
                "message": (
                    f"Cloud sync successful. {imported_count} new draft(s) imported from 24/7 cloud node."
                    if imported_count > 0 else
                    "Cloud sync complete. Everything up to date."
                ),
            }
        except Exception as e:
            logger.debug(f"Cloud node not reachable: {e}")
            return {"success": False, "message": f"Cloud node offline or unreachable: {e}"}


# Global sync client instance
cloud_sync = CloudSyncClient()
