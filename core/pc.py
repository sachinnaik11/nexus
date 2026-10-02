# ============================================================
# NEXUS PC CONTROL
# ============================================================

import subprocess
import webbrowser
import os


# ============================================================
# SHORTCUT RESOLVER
# ============================================================

def _find_desktop_shortcut(app_name: str) -> str:
    """Search for matching .lnk desktop shortcut on user's system."""
    clean_target = app_name.replace(" ", "").replace("-", "").replace("_", "").lower()
    search_dirs = [
        os.path.abspath(".."),
        os.path.join(os.environ.get("USERPROFILE", ""), "OneDrive", "Attachments", "Desktop"),
        os.path.join(os.environ.get("USERPROFILE", ""), "OneDrive", "Desktop"),
        os.path.join(os.environ.get("USERPROFILE", ""), "Desktop"),
        r"C:\Users\Public\Desktop",
    ]
    for directory in search_dirs:
        if os.path.exists(directory):
            try:
                for file_name in os.listdir(directory):
                    if file_name.lower().endswith(".lnk"):
                        base = os.path.splitext(file_name)[0].replace(" ", "").replace("-", "").replace("_", "").lower()
                        if clean_target in base or base in clean_target:
                            return os.path.join(directory, file_name)
            except Exception:
                pass
    return None


# ============================================================
# OPEN APPLICATION / SERVICE
# ============================================================

def open_app(app_name: str) -> str:
    """Open any supported Windows application, desktop shortcut, or web service."""

    app_name = str(app_name).strip().lower()

    # --------------------------------------------------------
    # WEBSITE ALIASES
    # --------------------------------------------------------

    websites = {
        "youtube": "https://www.youtube.com",
        "youtube.com": "https://www.youtube.com",
        "google": "https://www.google.com",
        "google.com": "https://www.google.com",
        "gmail": "https://mail.google.com",
        "gmail.com": "https://mail.google.com",
        "instagram": "https://www.instagram.com",
        "instagram.com": "https://www.instagram.com",
        "facebook": "https://www.facebook.com",
        "facebook.com": "https://www.facebook.com",
        "whatsapp": "https://web.whatsapp.com",
        "whatsapp web": "https://web.whatsapp.com",
        "web whatsapp": "https://web.whatsapp.com",
        "github": "https://github.com",
        "github.com": "https://github.com",
        "chatgpt": "https://chatgpt.com",
        "chat gpt": "https://chatgpt.com",
        "twitter": "https://x.com",
        "x": "https://x.com",
        "reddit": "https://reddit.com",
        "netflix": "https://netflix.com",
        "spotify web": "https://open.spotify.com",
        "amazon": "https://amazon.com",
        "linkedin": "https://linkedin.com",
        "wikipedia": "https://wikipedia.org",
    }

    if app_name in websites:
        url = websites[app_name]
        webbrowser.open(url)
        return f"Opened {app_name}."

    # --------------------------------------------------------
    # STANDARD WINDOWS APPLICATIONS
    # --------------------------------------------------------

    apps = {
        "notepad": "notepad.exe",
        "calculator": "calc.exe",
        "calc": "calc.exe",
        "paint": "mspaint.exe",
        "command prompt": "cmd.exe",
        "cmd": "cmd.exe",
        "terminal": "powershell.exe",
        "powershell": "powershell.exe",
        "file explorer": "explorer.exe",
        "explorer": "explorer.exe",
        "chrome": "chrome.exe",
        "google chrome": "chrome.exe",
        "edge": "msedge.exe",
        "microsoft edge": "msedge.exe",
        "task manager": "taskmgr.exe",
        "taskmgr": "taskmgr.exe",
        "control panel": "control.exe",
        "settings": "ms-settings:",
        "camera": "microsoft.windows.camera:",
        "snipping tool": "snippingtool.exe",
        "snip": "snippingtool.exe",
        "code": "code",
        "vs code": "code",
        "vscode": "code",
        "word": "winword.exe",
        "excel": "excel.exe",
        "powerpoint": "powerpnt.exe",
        "spotify": "spotify:",
    }

    # 1. Check known built-in apps
    if app_name in apps:
        target = apps[app_name]
        if target.endswith(".exe") or target.startswith(("ms-settings:", "microsoft.windows.camera:", "spotify:")):
            try:
                os.startfile(target)
                return f"Opened {app_name}."
            except Exception:
                subprocess.Popen(["cmd", "/c", "start", "", target], shell=True)
                return f"Opened {app_name}."
        else:
            try:
                subprocess.Popen(["cmd", "/c", "start", "", target], shell=True)
                return f"Opened {app_name}."
            except Exception:
                pass

    # 2. Check installed Desktop Shortcuts (.lnk)
    shortcut_path = _find_desktop_shortcut(app_name)
    if shortcut_path:
        try:
            os.startfile(shortcut_path)
            return f"Opened {app_name}."
        except Exception as e:
            return f"Failed to launch shortcut for {app_name}: {e}"

    # 3. Dynamic Windows Shell Execution
    try:
        os.startfile(app_name)
        return f"Opened {app_name}."
    except Exception:
        pass

    try:
        subprocess.Popen(["cmd", "/c", "start", "", app_name], shell=True)
        return f"Opened {app_name}."
    except Exception:
        pass

    return f"I couldn't locate an application or shortcut for '{app_name}' on your PC."


# ============================================================
# VOLUME UP
# ============================================================

def volume_up():

    subprocess.run(
        [
            "powershell",
            "-Command",
            "(New-Object -ComObject WScript.Shell).SendKeys([char]175)"
        ]
    )

    return "Volume increased."


# ============================================================
# VOLUME DOWN
# ============================================================

def volume_down():

    subprocess.run(
        [
            "powershell",
            "-Command",
            "(New-Object -ComObject WScript.Shell).SendKeys([char]174)"
        ]
    )

    return "Volume decreased."


# ============================================================
# MUTE
# ============================================================

def volume_mute():

    from pycaw.pycaw import AudioUtilities

    devices = AudioUtilities.GetSpeakers()

    volume = devices.EndpointVolume

    volume.SetMute(
        1,
        None
    )

    return "Volume muted."


# ============================================================
# UNMUTE
# ============================================================

def volume_unmute():
    try:
        from pycaw.pycaw import AudioUtilities
        devices = AudioUtilities.GetSpeakers()
        volume = devices.EndpointVolume
        volume.SetMute(0, None)
        return "Volume unmuted."
    except Exception:
        subprocess.run(
            [
                "powershell",
                "-Command",
                "(New-Object -ComObject WScript.Shell).SendKeys([char]173)"
            ]
        )
        return "Volume unmuted."


# ============================================================
# OPEN WEBSITE
# ============================================================

def open_website(url: str) -> str:

    url = str(url).strip()

    if not url.startswith(
        (
            "http://",
            "https://"
        )
    ):

        url = "https://" + url

    webbrowser.open(url)

    return f"Opened {url}."


# ============================================================
# SCREENSHOT
# ============================================================

def take_screenshot():

    import pyautogui

    filename = "nexus_screenshot.png"

    pyautogui.screenshot(
        filename
    )

    return (
        f"Screenshot saved as "
        f"{filename}."
    )


# ============================================================
# MOVE MOUSE CENTER
# ============================================================

def move_mouse_center():

    import pyautogui

    width, height = pyautogui.size()

    pyautogui.moveTo(
        width // 2,
        height // 2,
        duration=0.3
    )

    return "Mouse moved to the center."


# ============================================================
# MOUSE CLICK
# ============================================================

def mouse_click():

    import pyautogui

    pyautogui.click()

    return "Clicked."


# ============================================================
# TYPE TEXT
# ============================================================

def type_text(text):

    import pyautogui
    import time

    time.sleep(0.5)

    pyautogui.write(
        text,
        interval=0.03
    )

    return "Text typed."


# ============================================================
# TYPE IN NOTEPAD
# ============================================================

def type_in_notepad(text):

    import pyautogui
    import time

    subprocess.Popen(
        "notepad.exe"
    )

    time.sleep(1)

    pyautogui.write(
        text,
        interval=0.03
    )

    return "Typed in Notepad."


# ============================================================
# GOOGLE SEARCH
# ============================================================

def web_search(query):

    from urllib.parse import quote_plus

    query = str(query).strip()

    url = (
        "https://www.google.com/search?q="
        + quote_plus(query)
    )

    webbrowser.open(url)

    return (
        f"Searching Google for "
        f"{query}."
    )


# ============================================================
# YOUTUBE SEARCH
# ============================================================

def youtube_search(query):

    from urllib.parse import quote_plus

    query = str(query).strip()

    url = (
        "https://www.youtube.com/results?search_query="
        + quote_plus(query)
    )

    webbrowser.open(url)

    return (
        f"Searching YouTube for "
        f"{query}."
    )


# ============================================================
# CLOSE APPLICATION
# ============================================================

def close_app(app_name: str) -> str:
    """Close a running Windows application by name."""

    app_name = str(app_name).strip().lower()

    proc_map = {
        "notepad": "notepad.exe",
        "calculator": "calc.exe",
        "calc": "calc.exe",
        "paint": "mspaint.exe",
        "chrome": "chrome.exe",
        "google chrome": "chrome.exe",
        "edge": "msedge.exe",
        "microsoft edge": "msedge.exe",
        "code": "Code.exe",
        "vs code": "Code.exe",
        "task manager": "taskmgr.exe",
        "taskmgr": "taskmgr.exe",
        "capcut": "CapCut.exe",
        "bluestacks": "HD-Player.exe",
        "free fire": "HD-Player.exe",
        "cmd": "cmd.exe",
        "command prompt": "cmd.exe",
        "powershell": "powershell.exe",
        "terminal": "WindowsTerminal.exe",
        "spotify": "Spotify.exe",
    }

    proc_name = proc_map.get(
        app_name,
        app_name if app_name.endswith(".exe") else f"{app_name}.exe"
    )

    res = subprocess.run(
        [
            "taskkill",
            "/F",
            "/IM",
            proc_name
        ],
        capture_output=True,
        text=True
    )

    if res.returncode == 0:
        return f"Closed {app_name}."

    if "not found" in res.stderr.lower() or "not found" in res.stdout.lower() or res.returncode == 128:
        return f"{app_name.capitalize()} is not currently running."

    return f"Closed {app_name}."


# ============================================================
# LOCK COMPUTER
# ============================================================

def lock_pc():
    """Lock the Windows workstation."""
    subprocess.run(
        [
            "rundll32.exe",
            "user32.dll,LockWorkStation"
        ]
    )
    return "Computer locked."


# ============================================================
# SHOW DESKTOP
# ============================================================

def show_desktop():
    """Minimize all windows to display desktop."""
    try:
        import pyautogui
        pyautogui.hotkey("win", "d")
        return "Displaying desktop."
    except Exception:
        subprocess.run(
            [
                "powershell",
                "-Command",
                "(New-Object -ComObject Shell.Application).MinimizeAll()"
            ]
        )
        return "Displaying desktop."


# ============================================================
# EMPTY RECYCLE BIN
# ============================================================

def empty_recycle_bin():
    """Empty the Windows Recycle Bin."""
    subprocess.run(
        [
            "powershell",
            "-Command",
            "Clear-RecycleBin -Force -ErrorAction SilentlyContinue"
        ]
    )
    return "Recycle Bin emptied."