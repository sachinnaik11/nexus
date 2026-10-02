# ============================================================
# NEXUS JARVIS AUTONOMOUS WORKSPACE SETUP AGENT
# Replication of "Jarvis, I'm going to work, set everything up"
# ============================================================

import os
import sys
import time
import subprocess
import webbrowser
from core.pc import open_app

WORK_TABS = [
    "https://mail.google.com",
    "https://x.com",
    "https://www.instagram.com",
    "https://studio.youtube.com",
]


def set_everything_up(profile: str = "creator") -> dict:
    """
    Automates the entire desktop workspace initialization in one command.
    Matches @dhaibuilds Jarvis macro:
    - Launches browser with Gmail, Instagram, X, and YouTube Studio
    - Opens project workspace / File Explorer
    - Launches code editor or video creation tool
    """
    actions_taken = []

    # 1. Open Browser Tabs
    try:
        for url in WORK_TABS:
            webbrowser.open_new_tab(url)
            time.sleep(0.3)
        actions_taken.append("Opened Gmail, Instagram, X, and YouTube Studio tabs")
    except Exception as e:
        actions_taken.append(f"Browser launch note: {e}")

    # 2. Open Project Folder in File Explorer
    try:
        project_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        subprocess.Popen(["explorer.exe", project_dir])
        actions_taken.append(f"Opened project directory in Explorer: {project_dir}")
    except Exception as e:
        actions_taken.append(f"Explorer note: {e}")

    # 3. Launch VS Code or Development Terminal
    try:
        # Check if code.cmd or code.exe exists
        vscode_opened = False
        for path in os.environ.get("PATH", "").split(os.pathsep):
            code_path = os.path.join(path, "code.cmd")
            if os.path.exists(code_path):
                subprocess.Popen(["code", project_dir], shell=True)
                actions_taken.append("Launched VS Code on active workspace")
                vscode_opened = True
                break

        if not vscode_opened:
            # Open Windows Terminal / PowerShell
            subprocess.Popen(["powershell.exe"])
            actions_taken.append("Launched PowerShell terminal")
    except Exception as e:
        actions_taken.append(f"Terminal note: {e}")

    spoken = (
        "Setting everything up now, boss. "
        "Opening your workspace tabs for Gmail, Instagram, X, and YouTube Studio, "
        "with your project files and terminal ready, all arranged for you."
    )

    return {
        "success": True,
        "spoken_reply": spoken,
        "actions": actions_taken
    }
