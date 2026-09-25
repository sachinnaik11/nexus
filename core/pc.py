# ============================================================
# NEXUS PC CONTROL
# ============================================================

import subprocess
import webbrowser


# ============================================================
# OPEN APPLICATION / SERVICE
# ============================================================

def open_app(app_name: str) -> str:
    """Open a supported Windows application or web service."""

    app_name = str(app_name).strip().lower()

    # --------------------------------------------------------
    # WINDOWS APPLICATIONS
    # --------------------------------------------------------

    apps = {
        "notepad": "notepad.exe",
        "calculator": "calc.exe",
        "calc": "calc.exe",
        "paint": "mspaint.exe",
        "command prompt": "cmd.exe",
        "cmd": "cmd.exe",
        "file explorer": "explorer.exe",
        "chrome": "chrome.exe",
        "google chrome": "chrome.exe",
    }

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

        "whatsapp web": "https://web.whatsapp.com",
        "web whatsapp": "https://web.whatsapp.com",

        "github": "https://github.com",
        "github.com": "https://github.com",

        "chatgpt": "https://chatgpt.com",
        "chat gpt": "https://chatgpt.com",
    }

    # --------------------------------------------------------
    # WEBSITE
    # --------------------------------------------------------

    if app_name in websites:

        url = websites[app_name]

        webbrowser.open(url)

        return f"Opened {app_name}."


    # --------------------------------------------------------
    # WINDOWS APP
    # --------------------------------------------------------

    app = apps.get(app_name)

    if not app:

        return (
            f"I don't know how to open "
            f"{app_name} yet."
        )


    # --------------------------------------------------------
    # CHROME
    # --------------------------------------------------------

    if app == "chrome.exe":

        subprocess.Popen(
            [
                "cmd",
                "/c",
                "start",
                "",
                "chrome"
            ]
        )

        return "Opened Google Chrome."


    # --------------------------------------------------------
    # OTHER WINDOWS APPS
    # --------------------------------------------------------

    subprocess.Popen(app)

    return f"Opened {app_name}."


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