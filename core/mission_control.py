# ============================================================
# NEXUS — MISSION CONTROL
# ============================================================

import threading


MISSION_RUNNING = "RUNNING"
MISSION_PAUSED = "PAUSED"
MISSION_CANCELLED = "CANCELLED"


class MissionController:
    """
    Thread-safe controller for an active NEXUS mission.

    It allows the mission executor to pause or cancel safely
    while the voice loop remains available.
    """

    def __init__(self):
        self._lock = threading.Lock()
        self._pause_event = threading.Event()
        self._cancel_event = threading.Event()

        self._pause_event.set()

        self._status = MISSION_RUNNING
        self._current_mission = None

    # ========================================================
    # START
    # ========================================================

    def start(self, mission):
        with self._lock:
            self._current_mission = mission
            self._cancel_event.clear()
            self._pause_event.set()
            self._status = MISSION_RUNNING

    # ========================================================
    # PAUSE
    # ========================================================

    def pause(self):
        with self._lock:

            if self._current_mission is None:
                return False

            if self._status != MISSION_RUNNING:
                return False

            self._status = MISSION_PAUSED
            self._pause_event.clear()

            return True

    # ========================================================
    # RESUME
    # ========================================================

    def resume(self):
        with self._lock:

            if self._current_mission is None:
                return False

            if self._status != MISSION_PAUSED:
                return False

            self._status = MISSION_RUNNING
            self._pause_event.set()

            return True

    # ========================================================
    # CANCEL
    # ========================================================

    def cancel(self):
        with self._lock:

            if self._current_mission is None:
                return False

            self._status = MISSION_CANCELLED
            self._cancel_event.set()
            self._pause_event.set()

            return True

    # ========================================================
    # WAIT IF PAUSED
    # ========================================================

    def wait_if_paused(self):
        """
        Blocks the mission worker while paused.

        Returns False if the mission was cancelled.
        """

        while True:

            if self.is_cancelled():
                return False

            if self._pause_event.wait(
                timeout=0.2
            ):
                return not self.is_cancelled()

    # ========================================================
    # STATUS
    # ========================================================

    def get_status(self):

        with self._lock:
            return self._status

    # ========================================================
    # CURRENT MISSION
    # ========================================================

    def get_mission(self):

        with self._lock:
            return self._current_mission

    # ========================================================
    # ACTIVE CHECK
    # ========================================================

    def is_active(self):

        with self._lock:

            return (
                self._current_mission is not None
                and self._status in (
                    MISSION_RUNNING,
                    MISSION_PAUSED,
                )
            )

    # ========================================================
    # PAUSED CHECK
    # ========================================================

    def is_paused(self):

        with self._lock:
            return (
                self._status == MISSION_PAUSED
            )

    # ========================================================
    # CANCELLED CHECK
    # ========================================================

    def is_cancelled(self):

        return self._cancel_event.is_set()

    # ========================================================
    # FINISH
    # ========================================================

    def finish(self):

        with self._lock:
            self._current_mission = None
            self._pause_event.set()
            self._cancel_event.clear()
            self._status = MISSION_RUNNING

    # ========================================================
    # STATUS MESSAGE
    # ========================================================

    def status_message(self):

        with self._lock:

            if self._current_mission is None:

                return "No active mission."

            return (
                f"Mission status: "
                f"{self._status}."
            )


# ============================================================
# GLOBAL MISSION CONTROLLER
# ============================================================

mission_controller = MissionController()