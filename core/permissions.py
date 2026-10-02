# ============================================================
# NEXUS — SECURITY & PHONE PERMISSION ENGINE
# Human-in-the-Loop Confirmation Gate
# ============================================================

import os
import time
import subprocess
from datetime import datetime

# ============================================================
# APPROVAL STATUS CONSTANTS
# ============================================================

STATUS_PENDING = "PENDING"
STATUS_APPROVED = "APPROVED"
STATUS_REJECTED = "REJECTED"
STATUS_EXPIRED = "EXPIRED"


# ============================================================
# PERMISSION MANAGER CLASS
# ============================================================

class PermissionManager:
    """
    Guards sensitive operations (YouTube publishing, purchases,
    file deletions, external messages). Locks execution until
    the user explicitly confirms via phone call, SMS, or voice.
    """

    def __init__(self, timeout_seconds: int = 600):
        self.default_timeout = timeout_seconds
        self.pending_action = None
        self.history = []

    def request_permission(
        self,
        action_name: str,
        description: str,
        callback_fn=None,
        phone_number: str = None,
        timeout_seconds: int = None,
    ) -> dict:
        """
        Register a sensitive action and alert the user on their phone.
        """
        actual_timeout = timeout_seconds if timeout_seconds is not None else self.default_timeout
        request_id = f"REQ-{int(time.time())}"

        self.pending_action = {
            "id": request_id,
            "action": action_name,
            "description": description,
            "callback": callback_fn,
            "phone_number": phone_number,
            "created_at": time.time(),
            "timeout_seconds": actual_timeout,
            "status": STATUS_PENDING,
        }

        # Send alert via Phone / SMS / Call
        self._notify_phone(action_name, description, phone_number)

        return self.pending_action

    def has_pending(self) -> bool:
        """Check if an action is currently awaiting user approval."""
        if not self.pending_action:
            return False

        # Check for expiration
        elapsed = time.time() - self.pending_action["created_at"]
        if elapsed > self.pending_action["timeout_seconds"]:
            self.pending_action["status"] = STATUS_EXPIRED
            self.history.append(self.pending_action)
            self.pending_action = None
            return False

        return self.pending_action["status"] == STATUS_PENDING

    is_pending = has_pending

    def get_pending_details(self) -> str:
        """Return human-readable details of the pending action."""
        if not self.has_pending():
            return "No sensitive actions are currently awaiting your approval."

        act = self.pending_action
        return (
            f"Action: {act['action']}\n"
            f"Description: {act['description']}\n"
            f"Status: WAITING FOR YOUR PERMISSION\n"
            f"Reply 'Approve' to confirm or 'Reject' to cancel."
        )

    def approve(self) -> tuple[bool, str]:
        """
        User grants permission. Executes the held action.
        """
        if not self.has_pending():
            return False, "There are no pending actions to approve."

        act = self.pending_action
        act["status"] = STATUS_APPROVED
        self.history.append(act)
        self.pending_action = None

        result_message = f"Permission GRANTED for '{act['action']}'."

        # Execute callback if defined
        if act.get("callback"):
            try:
                cb_result = act["callback"]()
                if cb_result:
                    result_message += f" Result: {cb_result}"
            except Exception as e:
                result_message += f" Execution error: {e}"

        return True, result_message

    def reject(self, reason: str = "User denied permission") -> tuple[bool, str]:
        """
        User denies permission. Safely aborts the action.
        """
        if not self.has_pending():
            return False, "There are no pending actions to reject."

        act = self.pending_action
        act["status"] = STATUS_REJECTED
        act["reject_reason"] = reason
        self.history.append(act)
        self.pending_action = None

        return True, f"Permission DENIED. Action '{act['action']}' has been cancelled safely."

    # --------------------------------------------------------
    # PHONE ALERT DISPATCH (SMS & PHONE CALL)
    # --------------------------------------------------------
    def _notify_phone(self, action_name: str, description: str, phone_number: str = None):
        """
        Triggers SMS or Automated Call alerting the user's phone.
        """
        alert_msg = (
            f"NEXUS PERMISSION ALERT: Permission requested for '{action_name}'. "
            f"Details: {description}. Reply 'Approve' to authorize."
        )
        print(f"\n[SECURITY GATE] {alert_msg}\n")

        # 1. Try sending SMS through connected Android phone via ADB if available
        if phone_number:
            self._send_phone_sms(phone_number, alert_msg)

    def _send_phone_sms(self, phone_number: str, message: str):
        """Send SMS via connected Android device."""
        adb_path = r"C:\Program Files\BlueStacks_nxt\HD-Adb.exe"
        if not os.path.exists(adb_path):
            return

        try:
            # Android SMS intent broadcast via ADB
            escaped_msg = message.replace('"', '\\"')
            subprocess.run(
                [
                    adb_path,
                    "shell",
                    "am",
                    "start",
                    "-a",
                    "android.intent.action.SENDTO",
                    "-d",
                    f"sms:{phone_number}",
                    "--es",
                    "sms_body",
                    escaped_msg,
                ],
                capture_output=True,
                timeout=5,
            )
        except Exception:
            pass


# Global singleton permission manager
permission_gate = PermissionManager()
