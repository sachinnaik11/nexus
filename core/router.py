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
    )

    for wake_word in wake_words:

        if command.startswith(wake_word):

            command = command[
                len(wake_word):
            ].strip()

            break

    command = re.sub(
        r"[!?.,]+",
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

    if command.startswith("open "):

        return "OPEN"

    if command.startswith("launch "):

        return "OPEN"

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

    if command.startswith("type "):

        return "TYPE"

    if command.startswith("write "):

        return "TYPE"

    if command == "take screenshot":

        return "SCREENSHOT"

    if command == "screenshot":

        return "SCREENSHOT"

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

    if command in (
        "sleep",
        "put computer to sleep",
    ):

        return "SLEEP"

    return None


# ============================================================
# COMMAND TARGET
# ============================================================

def get_command_target(text):

    command = normalize_multilingual_command(
        text
    )

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

    if command.startswith("open "):

        return command[
            len("open "):
        ].strip()

    if command.startswith("launch "):

        return command[
            len("launch "):
        ].strip()

    if command.startswith("start "):

        return command[
            len("start "):
        ].strip()

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