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


# ============================================================
# NORMALIZE TEXT
# ============================================================

def normalize_text(text):

    command = str(text).strip().lower()

    wake_words = (
        "nexus ",
        "hey nexus ",
        "ok nexus ",
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
        "search ",
        "type ",
        "write ",
        "take screenshot",
        "screenshot",
        "volume ",
        "mute",
        "click",
        "move mouse",
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