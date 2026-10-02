from memory.intelligence import detect_memory

# ============================================================
# NEXUS — INTENT ENGINE
# ============================================================

INTENT_COMMAND = "command"
INTENT_WEB = "web"
INTENT_AI = "ai"
INTENT_MEMORY = "memory"
INTENT_TIME = "time"
INTENT_DATE = "date"
INTENT_EXIT = "exit"

INTENT_MISSION_PAUSE = "mission_pause"
INTENT_MISSION_RESUME = "mission_resume"
INTENT_MISSION_CANCEL = "mission_cancel"

INTENT_PERMISSION_APPROVE = "permission_approve"
INTENT_PERMISSION_REJECT = "permission_reject"


# ============================================================
# NORMALIZE TEXT
# ============================================================

def normalize_text(text):

    command = str(text).strip().lower()

    wake_words = (
        "nexus ",
        "hey nexus ",
        "ok nexus ",
        "jarvis ",
        "hey jarvis ",
        "ok jarvis ",
    )

    for wake_word in wake_words:

        if command.startswith(wake_word):

            command = command[
                len(wake_word):
            ].strip()

            break

    return command


# ============================================================
# DETECT INTENT
# ============================================================

def detect_intent(text):

    command = normalize_text(text)

    # --------------------------------------------------------
    # EXIT
    # --------------------------------------------------------

    if command in {
        "exit",
        "quit",
        "shutdown nexus",
        "close nexus",
    }:

        return INTENT_EXIT

    # --------------------------------------------------------
    # MISSION CONTROL
    # --------------------------------------------------------

    if command in {
        "pause mission",
        "pause the mission",
        "stop mission",
        "hold mission",
    }:

        return INTENT_MISSION_PAUSE

    if command in {
        "resume mission",
        "resume the mission",
        "continue mission",
        "continue the mission",
    }:

        return INTENT_MISSION_RESUME

    if command in {
        "cancel mission",
        "cancel the mission",
        "abort mission",
        "abort the mission",
    }:

        return INTENT_MISSION_CANCEL

    # --------------------------------------------------------
    # PERMISSIONS & APPROVALS
    # --------------------------------------------------------

    if command in {
        "approve",
        "yes approve",
        "confirm",
        "authorize",
        "grant permission",
        "permission granted",
    }:

        return INTENT_PERMISSION_APPROVE

    if command in {
        "reject",
        "deny",
        "disapprove",
        "deny permission",
        "cancel action",
        "permission denied",
    }:

        return INTENT_PERMISSION_REJECT

    # --------------------------------------------------------
    # TIME
    # --------------------------------------------------------

    if any(
        phrase in command
        for phrase in (
            "what is the time",
            "what's the time",
            "current time",
            "tell me the time",
            "time now",
            "what time is it",
        )
    ):

        return INTENT_TIME

    # --------------------------------------------------------
    # DATE
    # --------------------------------------------------------

    if any(
        phrase in command
        for phrase in (
            "what is the date",
            "what's the date",
            "current date",
            "today's date",
            "what date is it",
            "what day is today",
        )
    ):

        return INTENT_DATE

    # --------------------------------------------------------
    # MEMORY
    # --------------------------------------------------------

    memory_result = detect_memory(command)

    if memory_result["should_remember"]:
        return INTENT_MEMORY

    # --------------------------------------------------------
    # LOCAL COMMAND
    # --------------------------------------------------------

    command_starts = (
        "open ",
        "launch ",
        "start ",
        "close ",
        "terminate ",
        "kill ",
        "search ",
        "type ",
        "write ",
        "take screenshot",
        "take a screenshot",
        "screenshot",
        "take snapshot",
        "take a snapshot",
        "camera snapshot",
        "take photo",
        "take a photo",
        "create cinematic ad",
        "create a cinematic ad",
        "make cinematic ad",
        "make a cinematic ad",
        "cinematic ad",
        "what do you see",
        "what's on my screen",
        "what is on my screen",
        "describe my screen",
        "set everything up",
        "set up everything",
        "setup workspace",
        "set up workspace",
        "volume ",
        "mute",
        "unmute",
        "lock pc",
        "lock screen",
        "lock computer",
        "sleep",
        "show desktop",
        "minimize windows",
        "minimize all",
        "empty recycle bin",
        "click",
        "move mouse",
        "generate viral ",
        "viral seo",
        "viral tags",
        "viral title",
        "youtube seo",
        "create meme",
        "generate meme",
        "make meme",
        "meme short",
        "set channel niche",
        "set niche",
        "my niche is",
        "upload reminder",
        "check upload reminder",
        "check reminder",
        "youtube studio",
        "cloud sync",
        "sync with cloud",
        "sync cloud",
        "cloud status",
        "phone battery",
        "check phone",
        "phone screenshot",
        "lock phone",
        "lock my phone",
        "phone volume",
        "open on phone ",
        "open phone app ",
        "close on phone ",
        "close phone app ",
        "phone call ",
        "call ",
        "phone info",
        "connect phone ",
        "auto optimize",
        "auto edit",
        "autofill studio",
        "autofill youtube",
        "start channel watcher",
        "stop channel watcher",
        "start youtube automation",
        "stop youtube automation",
        "make it auto",
        "make it automatic",
        "turn on auto details",
        "enable auto details",
        "turn off auto details",
        "disable auto details",
        "auto add details",
        "automatic details",
        "generate and upload",
        "create and upload",
        "auto upload",
        "upload meme",
        "add details",
        "add video details",
        "update video details",
        "diagnose",
        "run diagnostic",
        "run diagnostics",
        "system diagnostic",
        "system diagnostics",
        "check system health",
        "check health",
        "system health",
        "pc diagnostics",
        "laptop diagnostics",
        "check laptop",
        "check pc",
        "hardware diagnostics",
        "diagnostics",
    )

    if command.startswith(
        command_starts
    ):

        return INTENT_COMMAND

    # --------------------------------------------------------
    # LIVE WEB
    # --------------------------------------------------------

    web_keywords = (
        "latest",
        "today",
        "current",
        "now",
        "news",
        "recent",
        "live",
        "price",
        "weather",
        "score",
        "scorecard",
        "update",
    )

    if any(
        keyword in command
        for keyword in web_keywords
    ):

        return INTENT_WEB

    # --------------------------------------------------------
    # DEFAULT AI
    # --------------------------------------------------------

    return INTENT_AI