import json
import os
from datetime import datetime

MEMORY_DIR = "memory"
MISSION_HISTORY_FILE = os.path.join(MEMORY_DIR, "missions.json")


def _ensure_directory():
    os.makedirs(MEMORY_DIR, exist_ok=True)


def load_mission_history():
    _ensure_directory()
    if not os.path.exists(MISSION_HISTORY_FILE):
        return []
    try:
        with open(MISSION_HISTORY_FILE, "r", encoding="utf-8") as file:
            data = json.load(file)
            return data if isinstance(data, list) else []
    except (json.JSONDecodeError, OSError):
        return []


def save_mission_history(history):
    _ensure_directory()
    with open(MISSION_HISTORY_FILE, "w", encoding="utf-8") as file:
        json.dump(history[-50:], file, indent=2, ensure_ascii=False)


def record_mission(goal, status, progress, steps=None):
    history = load_mission_history()
    record = {
        "id": len(history) + 1,
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "goal": str(goal),
        "status": str(status),
        "completed": progress.get("completed", 0),
        "total": progress.get("total", 0),
        "percentage": progress.get("percentage", 0),
        "steps": steps or [],
    }
    history.append(record)
    save_mission_history(history)
    return record


def get_last_mission():
    history = load_mission_history()
    return history[-1] if history else None


def get_mission_count():
    return len(load_mission_history())


def get_completed_mission_count():
    return sum(
        1 for mission in load_mission_history()
        if mission.get("status") == "COMPLETED"
    )
