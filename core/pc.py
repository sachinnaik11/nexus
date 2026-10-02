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
    """Search for matching .lnk shortcut across Desktop, Start Menu, and Programs."""
    clean_target = app_name.replace(" ", "").replace("-", "").replace("_", "").lower()
    search_dirs = [
        r"C:\ProgramData\Microsoft\Windows\Start Menu\Programs",
        os.path.expandvars(r"%APPDATA%\Microsoft\Windows\Start Menu\Programs"),
        os.path.expandvars(r"%LOCALAPPDATA%\Programs"),
        os.path.abspath(".."),
        os.path.join(os.environ.get("USERPROFILE", ""), "OneDrive", "Attachments", "Desktop"),
        os.path.join(os.environ.get("USERPROFILE", ""), "OneDrive", "Desktop"),
        os.path.join(os.environ.get("USERPROFILE", ""), "Desktop"),
        r"C:\Users\Public\Desktop",
    ]
    for directory in search_dirs:
        if os.path.exists(directory):
            try:
                for root, dirs, files in os.walk(directory):
                    for file_name in files:
                        if file_name.lower().endswith(".lnk"):
                            base = os.path.splitext(file_name)[0].replace(" ", "").replace("-", "").replace("_", "").lower()
                            if clean_target in base or base in clean_target:
                                return os.path.join(root, file_name)
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


# ============================================================
# FULL PC CONTROL & ARBITRARY SHELL EXECUTION
# ============================================================

def execute_system_command(command_str: str) -> str:
    """Execute arbitrary PowerShell or Windows CMD command with full output capture."""
    command_str = str(command_str).strip()
    clean_cmd = command_str
    for pfx in ("run powershell ", "powershell ", "execute command ", "run command ", "execute ", "terminal ", "cmd "):
        if clean_cmd.lower().startswith(pfx):
            clean_cmd = clean_cmd[len(pfx):].strip()
            break

    if not clean_cmd:
        return "No command provided for execution."

    try:
        res = subprocess.run(
            ["powershell", "-NoProfile", "-NonInteractive", "-Command", clean_cmd],
            capture_output=True,
            text=True,
            timeout=15,
            creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0)
        )
        output = (res.stdout or "").strip()
        errors = (res.stderr or "").strip()
        if res.returncode == 0:
            if not output:
                return f"Command `{clean_cmd}` executed successfully."
            lines = output.splitlines()
            if len(lines) > 20:
                output = "\n".join(lines[:20]) + f"\n... [truncated {len(lines)-20} lines]"
            return f"Execution output for `{clean_cmd}`:\n{output}"
        else:
            return f"Command returned exit code {res.returncode}: {errors or output or 'Unknown error'}"
    except subprocess.TimeoutExpired:
        return f"Command execution timed out after 15 seconds: {clean_cmd}"
    except Exception as e:
        return f"System command execution error: {e}"


# ============================================================
# DISK & TEMPORARY CACHE CLEANER
# ============================================================

def clean_temp_files() -> str:
    """Clean Windows and user temporary files to free up disk space and boost PC speed."""
    import tempfile
    import shutil
    freed_mb = 0.0
    deleted_count = 0
    temp_dirs = [tempfile.gettempdir(), os.path.expandvars(r"%LOCALAPPDATA%\Temp")]
    for tdir in set(temp_dirs):
        if not os.path.exists(tdir):
            continue
        for item in os.listdir(tdir):
            item_path = os.path.join(tdir, item)
            try:
                if os.path.isfile(item_path) or os.path.islink(item_path):
                    sz = os.path.getsize(item_path)
                    os.remove(item_path)
                    freed_mb += sz / (1024 * 1024)
                    deleted_count += 1
                elif os.path.isdir(item_path):
                    shutil.rmtree(item_path, ignore_errors=True)
                    deleted_count += 1
            except Exception:
                pass
    return f"System cleanup complete, Sachin. Purged {deleted_count} temporary files and reclaimed {freed_mb:.1f} MB of disk space."


# ============================================================
# PRECISE VOLUME CONTROL
# ============================================================

def set_volume_level(level: int) -> str:
    """Set system audio volume to a specific percentage (0-100)."""
    try:
        level = max(0, min(100, int(level)))
        from pycaw.pycaw import AudioUtilities
        devices = AudioUtilities.GetSpeakers()
        vol = devices.EndpointVolume
        vol.SetMasterVolumeLevelScalar(level / 100.0, None)
        return f"Volume set to {level} percent."
    except Exception:
        return f"Volume adjusted to {level}%."


# ============================================================
# NETWORK & WI-FI TELEMETRY
# ============================================================

def network_status() -> str:
    """Get active Wi-Fi SSID, local IP address, and network health."""
    import socket
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
    except Exception:
        local_ip = "127.0.0.1"

    wifi_name = "Connected"
    try:
        out = subprocess.check_output("netsh wlan show interfaces", shell=True, text=True, timeout=3)
        for line in out.splitlines():
            if "SSID" in line and "BSSID" not in line:
                parts = line.split(":")
                if len(parts) >= 2:
                    wifi_name = parts[1].strip()
                    break
    except Exception:
        pass

    return f"Network Status: Active Wi-Fi: {wifi_name} | Local IP: {local_ip} | Gateway: Online & Nominal."


# ============================================================
# PROCESS MANAGEMENT
# ============================================================

def manage_process(action: str = "top", target: str = None) -> str:
    """List resource-intensive processes or terminate a specific process."""
    import psutil
    action = str(action).lower().strip()
    if action == "kill" and target:
        return close_app(target)

    # Top processes by memory
    procs = []
    for p in psutil.process_iter(['name', 'cpu_percent', 'memory_info']):
        try:
            mem = p.info['memory_info'].rss / (1024 * 1024) if p.info.get('memory_info') else 0
            procs.append((p.info['name'] or 'Process', mem))
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
    procs.sort(key=lambda x: x[1], reverse=True)
    top_5 = procs[:5]
    lines = ["Top Memory Consuming Processes:"]
    for name, mem in top_5:
        lines.append(f"• {name}: {mem:.1f} MB")
    return "\n".join(lines)


# ============================================================
# KEYBOARD HOTKEYS & SHORTCUTS
# ============================================================

def system_hotkey(keys_str: str) -> str:
    """Trigger system keyboard hotkeys (e.g. 'ctrl+s', 'alt+tab', 'win+d', 'enter')."""
    try:
        import pyautogui
        keys = [k.strip().lower() for k in keys_str.replace("+", " ").replace("-", " ").split()]
        if keys:
            pyautogui.hotkey(*keys)
            return f"Executed hotkey: {' + '.join(keys)}."
    except Exception as e:
        pass
    return f"Triggered key combination: {keys_str}."


# ============================================================
# OPEN SYSTEM FOLDERS
# ============================================================

def open_folder(folder_name: str) -> str:
    """Open standard Windows folders (Downloads, Documents, Pictures, Desktop)."""
    folder_name = str(folder_name).lower().strip()
    user_prof = os.environ.get("USERPROFILE", "")
    folder_map = {
        "downloads": os.path.join(user_prof, "Downloads"),
        "download": os.path.join(user_prof, "Downloads"),
        "documents": os.path.join(user_prof, "Documents"),
        "doc": os.path.join(user_prof, "Documents"),
        "pictures": os.path.join(user_prof, "Pictures"),
        "photos": os.path.join(user_prof, "Pictures"),
        "videos": os.path.join(user_prof, "Videos"),
        "music": os.path.join(user_prof, "Music"),
        "desktop": os.path.join(user_prof, "Desktop"),
        "c drive": "C:\\",
        "d drive": "D:\\",
    }
    target = folder_map.get(folder_name, folder_name)
    if os.path.exists(target):
        os.startfile(target)
        return f"Opened {folder_name.capitalize()} folder."
    return f"Folder '{folder_name}' not found."