# ============================================================
# NEXUS — SMART COMMAND ROUTER
# ============================================================

import re


# ============================================================
# NORMALIZE BASIC COMMAND
# ============================================================

def normalize_command(text):

    command = str(text).strip().lower()

    wake_words = (
        "hey nexus ",
        "ok nexus ",
        "nexus ",
        "hey jarvis ",
        "ok jarvis ",
        "jarvis ",
    )

    for wake_word in wake_words:

        if command.startswith(wake_word):

            command = command[
                len(wake_word):
            ].strip()

            break

    command = re.sub(
        r"[!?,]+",
        " ",
        command
    )
    command = re.sub(
        r"\.(?:\s|$)",
        " ",
        command
    )

    command = re.sub(
        r"\s+",
        " ",
        command
    ).strip()

    return command


# ============================================================
# MULTILINGUAL + NATURAL LANGUAGE NORMALIZATION
# ============================================================

def normalize_multilingual_command(text):

    command = normalize_command(text)

    # --------------------------------------------------------
    # Hindi
    # --------------------------------------------------------

    replacements = {

        "youtube kholo": "open youtube",
        "youtube khol": "open youtube",
        "youtube open karo": "open youtube",
        "youtube kholo na": "open youtube",

        "chrome kholo": "open chrome",
        "chrome khol": "open chrome",
        "chrome open karo": "open chrome",

        "google kholo": "open google",
        "google khol": "open google",

        "whatsapp kholo": "open whatsapp",
        "whatsapp khol": "open whatsapp",

        # ----------------------------------------------------
        # Kannada
        # ----------------------------------------------------

        "youtube open maadu": "open youtube",
        "youtube kholo maadu": "open youtube",
        "youtube thogoli": "open youtube",

        "chrome open maadu": "open chrome",
        "chrome thogoli": "open chrome",

        # ----------------------------------------------------
        # Tamil
        # ----------------------------------------------------

        "youtube open pannu": "open youtube",
        "youtube thora": "open youtube",
        "youtube thorandhu": "open youtube",

        "chrome open pannu": "open chrome",

        # ----------------------------------------------------
        # English natural commands
        # ----------------------------------------------------

        "launch youtube": "open youtube",
        "start youtube": "open youtube",

        "launch chrome": "open chrome",
        "start chrome": "open chrome",

        "launch google": "open google",
        "start google": "open google",

        "launch whatsapp": "open whatsapp",
        "start whatsapp": "open whatsapp",
    }

    for phrase, replacement in replacements.items():

        if command == phrase:

            command = replacement

    # ========================================================
    # IMPORTANT:
    # "open youtube for GTA V"
    # → "open youtube and search youtube GTA V"
    # ========================================================

    match = re.match(
        r"^open youtube for (.+)$",
        command
    )

    if match:

        query = match.group(1).strip()

        if query:

            return (
                f"open youtube and "
                f"search youtube {query}"
            )

    # Also support:
    # "open youtube and search GTA V"

    match = re.match(
        r"^open youtube and search (.+)$",
        command
    )

    if match:

        query = match.group(1).strip()

        if query:

            return (
                f"open youtube and "
                f"search youtube {query}"
            )

    # ========================================================
    # SEARCH NORMALIZATION
    # ========================================================

    command = re.sub(
        r"^search youtube for ",
        "search youtube ",
        command
    )

    command = re.sub(
        r"^youtube search for ",
        "search youtube ",
        command
    )

    command = re.sub(
        r"^search google for ",
        "search web ",
        command
    )

    command = re.sub(
        r"^search the web for ",
        "search web ",
        command
    )

    return command


# ============================================================
# COMMAND CLASSIFICATION
# ============================================================

def classify_command(text):

    command = normalize_multilingual_command(
        text
    )

    if command.startswith("open website "):

        return "OPEN_WEBSITE"

    if command in (
        "open youtube studio",
        "launch youtube studio",
        "youtube studio",
    ):
        return "YOUTUBE_STUDIO"

    if command in (
        "open camera",
        "open the camera",
        "turn on camera",
        "start camera",
        "launch camera",
        "show camera",
        "webcam",
        "camera",
        "open webcam",
        "open the webcam",
        "turn on webcam",
        "start webcam",
        "launch webcam",
        "show webcam",
    ):
        return "CAMERA_OPEN"

    if command in (
        "create a cinematic ad",
        "create cinematic ad",
        "make a cinematic ad",
        "make cinematic ad",
        "generate a cinematic ad",
        "generate cinematic ad",
        "cinematic ad",
        "create ad",
    ):
        return "CINEMATIC_AD"

    if command in (
        "what do you see",
        "what do you see on my screen",
        "what do you see jarvis",
        "what's on my screen",
        "what is on my screen",
        "what do you see boss",
        "describe my screen",
    ):
        return "SCREEN_WHAT_DO_YOU_SEE"

    if command in (
        "set everything up",
        "set up everything",
        "i'm going to work set everything up",
        "i am going to work set everything up",
        "going to work set everything up",
        "setup workspace",
        "set up workspace",
        "start workspace",
    ):
        return "WORKSPACE_SETUP"

    if (
        command in (
            "diagnose my laptop",
            "diagnose laptop",
            "diagnose pc",
            "diagnose my pc",
            "diagnose computer",
            "diagnose system",
            "run diagnostics",
            "run diagnostic",
            "system diagnostics",
            "system diagnostic",
            "run system diagnostics",
            "check system health",
            "system health",
            "laptop diagnostics",
            "hardware diagnostics",
            "pc diagnostics",
            "check laptop health",
            "check pc health",
            "check laptop",
            "check pc",
            "diagnostics",
            "diagnostic",
            "diagnose",
            "health check",
            "hardware status",
        )
        or command.startswith("diagnose ")
        or command.startswith("run diagnostics")
        or command.startswith("run diagnostic")
    ):
        return "SYSTEM_DIAGNOSTICS"

    if (
        command.startswith("run powershell ")
        or command.startswith("powershell ")
        or command.startswith("execute command ")
        or command.startswith("run command ")
        or command.startswith("shell ")
    ):
        return "EXECUTE_SHELL"

    if command in (
        "clean temp",
        "clear cache",
        "cleanup pc",
        "clean temporary files",
        "clean temp files",
        "clean temporary",
        "disk cleanup",
    ):
        return "CLEAN_TEMP"

    if (
        command.startswith("set volume to ")
        or (command.startswith("volume ") and any(c.isdigit() for c in command))
    ):
        return "SET_VOLUME_LEVEL"

    if command in (
        "check wifi",
        "wifi status",
        "network status",
        "ip address",
        "my ip",
        "check network",
        "what is my ip",
    ):
        return "NETWORK_STATUS"

    if command in (
        "top processes",
        "running processes",
        "check processes",
        "list processes",
    ):
        return "MANAGE_PROCESS"

    if command.startswith("press ") or command.startswith("hotkey "):
        return "SYSTEM_HOTKEY"

    if (
        command.startswith("open folder ")
        or command in ("open downloads", "open documents", "open pictures", "open desktop")
    ):
        return "OPEN_FOLDER"

    if command in (
        "self heal",
        "auto heal",
        "repair system",
        "fix errors",
        "solve errors",
        "run self heal",
        "diagnose and fix",
        "fix problems",
        "solve itself",
    ):
        return "SYSTEM_SELF_HEAL"

    if command.startswith("open on phone ") or command.startswith("open phone app "):

        return "PHONE_OPEN_APP"

    if command.startswith("open "):

        return "OPEN"

    if command.startswith("launch "):

        return "OPEN"

    if command in (
        "start channel watcher",
        "start youtube automation",
        "make it auto",
        "make it automatic",
        "turn on auto details",
        "enable auto details",
        "turn on automatic details",
        "enable automatic details",
        "auto add details",
        "auto details",
    ):
        return "YOUTUBE_START_WATCHER"

    if command in (
        "stop channel watcher",
        "stop youtube automation",
        "turn off auto details",
        "disable auto details",
        "turn off automatic details",
        "disable automatic details",
    ):
        return "YOUTUBE_STOP_WATCHER"

    if command.startswith("start "):

        return "OPEN"

    if command.startswith("search youtube "):

        return "YOUTUBE_SEARCH"

    if command.startswith("search web "):

        return "WEB_SEARCH"

    if command.startswith("search google "):

        return "WEB_SEARCH"

    if command.startswith("search "):

        return "WEB_SEARCH"

    if command.startswith("type in notepad "):

        return "TYPE_NOTEPAD"

    if command.startswith("write in notepad "):

        return "TYPE_NOTEPAD"

    if command.startswith("type on phone "):

        return "PHONE_TYPE"

    if command.startswith("type "):

        return "TYPE"

    if command.startswith("write "):

        return "TYPE"

    if command in ("take screenshot", "take a screenshot", "screenshot"):

        return "SCREENSHOT"

    if command in ("take camera snapshot", "capture camera", "camera snapshot", "take snapshot", "take a snapshot", "take photo", "take a photo"):

        return "CAMERA_SNAPSHOT"

    if command == "volume up":

        return "VOLUME_UP"

    if command == "volume down":

        return "VOLUME_DOWN"

    if command in (
        "mute",
        "volume mute",
    ):

        return "MUTE"

    if command in (
        "click",
        "mouse click",
    ):

        return "MOUSE_CLICK"

    if command in (
        "move mouse",
        "move mouse center",
        "mouse center",
    ):

        return "MOUSE_CENTER"

    if command in (
        "open whatsapp",
        "whatsapp",
    ):

        return "OPEN_WHATSAPP"

    if command.startswith("close on phone ") or command.startswith("close phone app "):

        return "PHONE_CLOSE_APP"

    if command.startswith("close "):

        return "CLOSE"

    if command.startswith("terminate "):

        return "CLOSE"

    if command.startswith("kill "):

        return "CLOSE"

    if command in (
        "unmute",
        "volume unmute",
    ):

        return "UNMUTE"

    if command in (
        "lock pc",
        "lock screen",
        "lock computer",
    ):

        return "LOCK_PC"

    if command in (
        "show desktop",
        "minimize all",
        "minimize windows",
        "minimize all windows",
    ):

        return "SHOW_DESKTOP"

    if command == "empty recycle bin":

        return "EMPTY_RECYCLE_BIN"

    # --------------------------------------------------------
    # YOUTUBE & CREATOR ACTIONS
    # --------------------------------------------------------

    if command in (
        "open youtube studio",
        "launch youtube studio",
        "youtube studio",
    ):
        return "YOUTUBE_STUDIO"

    if command in (
        "open capcut",
        "launch capcut",
    ):
        return "OPEN_CAPCUT"

    if (
        command.startswith("generate viral seo for ")
        or command.startswith("viral seo for ")
        or command.startswith("viral seo ")
        or command.startswith("viral tags for ")
        or command.startswith("viral title for ")
        or command.startswith("youtube seo for ")
        or command.startswith("generate viral ")
    ):
        return "YOUTUBE_VIRAL_SEO"

    if command in (
        "create meme short",
        "create meme video",
        "generate meme video",
        "generate meme short",
        "make meme short",
        "meme short",
        "create meme",
    ):
        return "YOUTUBE_MEME_SHORT"

    if (
        command.startswith("set channel niche to ")
        or command.startswith("set niche to ")
        or command.startswith("my niche is ")
    ):
        return "SET_NICHE"

    if command in (
        "check upload reminder",
        "upload reminder",
        "youtube reminder",
        "check reminder",
    ):
        return "CHECK_REMINDER"

    # --------------------------------------------------------
    # YOUTUBE CHANNEL DIRECT AUTOMATION
    # --------------------------------------------------------

    if (
        command.startswith("auto optimize")
        or command.startswith("auto edit")
        or command == "optimize latest video"
        or command.startswith("add details")
        or command.startswith("update video details")
        or command.startswith("add video details")
        or command in ("add details to my video", "add details to latest video", "add details to video")
    ):
        return "YOUTUBE_AUTO_OPTIMIZE"

    if (
        command.startswith("autofill studio")
        or command.startswith("autofill youtube")
        or command == "autofill"
    ):
        return "YOUTUBE_STUDIO_AUTOFILL"

    if (
        command.startswith("generate and upload")
        or command.startswith("create and upload")
        or command.startswith("auto upload")
        or command == "upload meme"
        or command.startswith("upload meme ")
    ):
        return "YOUTUBE_AUTO_UPLOAD_MEME"

    if command in (
        "start channel watcher",
        "start youtube automation",
        "make it auto",
        "make it automatic",
        "turn on auto details",
        "enable auto details",
        "turn on automatic details",
        "enable automatic details",
        "auto add details",
        "auto details",
    ):
        return "YOUTUBE_START_WATCHER"

    if command in (
        "stop channel watcher",
        "stop youtube automation",
        "turn off auto details",
        "disable auto details",
        "turn off automatic details",
        "disable automatic details",
    ):
        return "YOUTUBE_STOP_WATCHER"

    if (
        command.startswith("switch channel to ")
        or command.startswith("switch youtube to ")
        or command.startswith("change channel to ")
        or command.startswith("switch to channel ")
        or command.startswith("switch channel ")
    ):
        return "YOUTUBE_SWITCH_CHANNEL"

    if command in (
        "list channels",
        "show channels",
        "youtube channels",
        "which channels",
        "available channels",
        "current channel",
        "which channel",
        "active channel",
    ):
        return "YOUTUBE_LIST_CHANNELS"

    if command in (
        "cloud sync",
        "sync with cloud",
        "sync cloud",
    ):
        return "CLOUD_SYNC"

    if command in (
        "cloud status",
        "check cloud",
    ):
        return "CLOUD_STATUS"

    # --------------------------------------------------------
    # ANDROID PHONE CONTROLS
    # --------------------------------------------------------

    if command in (
        "phone battery",
        "check phone battery",
        "check phone",
    ):
        return "PHONE_BATTERY"

    if command in (
        "phone screenshot",
        "take phone screenshot",
    ):
        return "PHONE_SCREENSHOT"

    if command in (
        "lock phone",
        "lock my phone",
    ):
        return "PHONE_LOCK"

    if command == "phone volume up":
        return "PHONE_VOLUME_UP"

    if command == "phone volume down":
        return "PHONE_VOLUME_DOWN"

    if (
        command.startswith("open on phone ")
        or command.startswith("open phone app ")
    ):
        return "PHONE_OPEN_APP"

    if (
        command.startswith("close on phone ")
        or command.startswith("close phone app ")
    ):
        return "PHONE_CLOSE_APP"

    if (
        command.startswith("phone call ")
        or command.startswith("call ")
    ):
        return "PHONE_CALL"

    if command in ("phone info", "phone status"):
        return "PHONE_STATUS"

    if command in (
        "control my mobile",
        "control mobile",
        "control my phone",
        "control phone",
        "mirror phone",
        "mirror my phone",
        "mirror mobile",
        "phone screen",
        "show phone screen",
    ):
        return "PHONE_MIRROR"

    if command in (
        "unlock phone",
        "unlock my phone",
        "wake phone",
        "wake up phone",
    ):
        return "PHONE_UNLOCK"

    if command in ("phone home", "go home on phone"):
        return "PHONE_HOME"

    if command in ("phone back", "back on phone"):
        return "PHONE_BACK"

    if command in ("phone recents", "phone recent apps", "phone app switcher"):
        return "PHONE_RECENTS"

    if command in ("phone notifications", "show phone notifications"):
        return "PHONE_NOTIFICATIONS"

    if command in ("phone quick settings", "open phone quick settings"):
        return "PHONE_QUICK_SETTINGS"

    if command in ("phone play", "phone pause", "phone play pause"):
        return "PHONE_MEDIA_PLAY_PAUSE"

    if command == "phone next":
        return "PHONE_MEDIA_NEXT"

    if command == "phone previous":
        return "PHONE_MEDIA_PREV"

    if command.startswith("connect phone") or command.startswith("connect mobile"):
        return "PHONE_CONNECT"

    if command.startswith("pair phone") or command.startswith("pair mobile"):
        return "PHONE_PAIR"

    if command in ("enable wireless phone", "wireless phone"):
        return "PHONE_ENABLE_WIRELESS"

    if command.startswith("type on phone "):
        return "PHONE_TYPE"

    if command.startswith("send sms ") or command.startswith("phone sms "):
        return "PHONE_SMS"

    return None


# ============================================================
# COMMAND TARGET
# ============================================================

def get_command_target(text):

    command = normalize_multilingual_command(
        text
    )

    if command.startswith("run powershell "):
        return command[len("run powershell "):].strip()
    if command.startswith("powershell "):
        return command[len("powershell "):].strip()
    if command.startswith("execute command "):
        return command[len("execute command "):].strip()
    if command.startswith("run command "):
        return command[len("run command "):].strip()
    if command.startswith("shell "):
        return command[len("shell "):].strip()
    if command.startswith("press "):
        return command[len("press "):].strip()
    if command.startswith("hotkey "):
        return command[len("hotkey "):].strip()
    if command.startswith("set volume to "):
        return command[len("set volume to "):].strip()
    if command.startswith("volume ") and any(c.isdigit() for c in command):
        return command[len("volume "):].strip()
    if command.startswith("open folder "):
        return command[len("open folder "):].strip()
    if command in ("open downloads", "open documents", "open pictures", "open desktop"):
        return command.replace("open ", "").strip()

    if command.startswith("search youtube "):

        return command[
            len("search youtube "):
        ].strip()

    if command.startswith("search web "):

        return command[
            len("search web "):
        ].strip()

    if command.startswith("search google "):

        return command[
            len("search google "):
        ].strip()

    if command.startswith("search "):

        return command[
            len("search "):
        ].strip()

    if command.startswith("type in notepad "):

        return command[
            len("type in notepad "):
        ].strip()

    if command.startswith("write in notepad "):

        return command[
            len("write in notepad "):
        ].strip()

    if command.startswith("type on phone "):

        return command[
            len("type on phone "):
        ].strip()

    if command.startswith("type "):

        return command[
            len("type "):
        ].strip()

    if command.startswith("write "):

        return command[
            len("write "):
        ].strip()

    if command.startswith("open website "):

        return command[
            len("open website "):
        ].strip()

    if command.startswith("open on phone "):
        return command[len("open on phone "):].strip()

    if command.startswith("open phone app "):
        return command[len("open phone app "):].strip()

    if command.startswith("open "):

        return command[
            len("open "):
        ].strip()

    if command.startswith("launch "):

        return command[
            len("launch "):
        ].strip()

    if command in ("start channel watcher", "start youtube automation", "stop channel watcher", "stop youtube automation", "list channels", "show channels", "youtube channels", "current channel", "active channel"):
        return None

    if command.startswith("switch channel to "):
        return command[len("switch channel to "):].strip()
    if command.startswith("switch youtube to "):
        return command[len("switch youtube to "):].strip()
    if command.startswith("change channel to "):
        return command[len("change channel to "):].strip()
    if command.startswith("switch to channel "):
        return command[len("switch to channel "):].strip()
    if command.startswith("switch channel "):
        return command[len("switch channel "):].strip()

    if command.startswith("start "):

        return command[
            len("start "):
        ].strip()

    if command.startswith("close on phone "):
        return command[len("close on phone "):].strip()

    if command.startswith("close phone app "):
        return command[len("close phone app "):].strip()

    if command.startswith("connect phone "):
        return command[len("connect phone "):].strip()

    if command.startswith("connect mobile "):
        return command[len("connect mobile "):].strip()

    if command.startswith("pair phone "):
        return command[len("pair phone "):].strip()

    if command.startswith("pair mobile "):
        return command[len("pair mobile "):].strip()

    if command.startswith("type on phone "):
        return command[len("type on phone "):].strip()

    if command.startswith("send sms "):
        return command[len("send sms "):].strip()

    if command.startswith("phone sms "):
        return command[len("phone sms "):].strip()

    if command.startswith("close "):

        return command[
            len("close "):
        ].strip()

    if command.startswith("terminate "):

        return command[
            len("terminate "):
        ].strip()

    if command.startswith("kill "):

        return command[
            len("kill "):
        ].strip()

    # --------------------------------------------------------
    # YOUTUBE TARGETS
    # --------------------------------------------------------

    if command.startswith("generate viral seo for "):
        return command[len("generate viral seo for "):].strip()

    if command.startswith("viral seo for "):
        return command[len("viral seo for "):].strip()

    if command.startswith("viral seo "):
        return command[len("viral seo "):].strip()

    if command.startswith("viral tags for "):
        return command[len("viral tags for "):].strip()

    if command.startswith("viral title for "):
        return command[len("viral title for "):].strip()

    if command.startswith("youtube seo for "):
        return command[len("youtube seo for "):].strip()

    if command.startswith("generate viral "):
        return command[len("generate viral "):].strip()

    if command.startswith("set channel niche to "):
        return command[len("set channel niche to "):].strip()

    if command.startswith("set niche to "):
        return command[len("set niche to "):].strip()

    if command.startswith("my niche is "):
        return command[len("my niche is "):].strip()

    if command.startswith("phone call "):
        return command[len("phone call "):].strip()

    if command.startswith("call "):
        return command[len("call "):].strip()

    # --------------------------------------------------------
    # YOUTUBE AUTOMATION TARGETS
    # --------------------------------------------------------

    if command.startswith("add details for "):
        return command[len("add details for "):].strip()

    if command.startswith("add details to "):
        return command[len("add details to "):].strip()

    if command.startswith("add details "):
        return command[len("add details "):].strip()

    if command.startswith("add video details for "):
        return command[len("add video details for "):].strip()

    if command.startswith("add video details "):
        return command[len("add video details "):].strip()

    if command.startswith("update video details for "):
        return command[len("update video details for "):].strip()

    if command.startswith("update video details "):
        return command[len("update video details "):].strip()

    if command.startswith("auto optimize "):
        return command[len("auto optimize "):].strip()

    if command.startswith("auto edit "):
        return command[len("auto edit "):].strip()

    if command.startswith("autofill studio "):
        return command[len("autofill studio "):].strip()

    if command.startswith("autofill youtube "):
        return command[len("autofill youtube "):].strip()

    if command.startswith("generate and upload meme for "):
        return command[len("generate and upload meme for "):].strip()

    if command.startswith("generate and upload meme "):
        return command[len("generate and upload meme "):].strip()

    if command.startswith("generate and upload "):
        return command[len("generate and upload "):].strip()

    if command.startswith("create and upload meme for "):
        return command[len("create and upload meme for "):].strip()

    if command.startswith("create and upload meme "):
        return command[len("create and upload meme "):].strip()

    if command.startswith("create and upload "):
        return command[len("create and upload "):].strip()

    if command.startswith("upload meme "):
        return command[len("upload meme "):].strip()

    return None


# ============================================================
# ROUTE COMMAND
# ============================================================

def route_command(text):

    command_type = classify_command(
        text
    )

    return command_type


# ============================================================
# COMMAND CHECK
# ============================================================

def is_command(text):

    return (
        classify_command(text)
        is not None
    )