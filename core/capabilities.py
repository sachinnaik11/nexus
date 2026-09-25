# ============================================================
# NEXUS CAPABILITY MANAGER
# ============================================================

from core.command_executor import execute_command


# ------------------------------------------------------------
# CAPABILITY TYPES
# ------------------------------------------------------------

CAPABILITY_PC = "PC"
CAPABILITY_WEB = "WEB"
CAPABILITY_AI = "AI"
CAPABILITY_MEMORY = "MEMORY"
CAPABILITY_SYSTEM = "SYSTEM"


# ------------------------------------------------------------
# AVAILABLE CAPABILITIES
# ------------------------------------------------------------

CAPABILITIES = {
    CAPABILITY_PC: [
        "OPEN",
        "OPEN_WEBSITE",
        "WEB_SEARCH",
        "YOUTUBE_SEARCH",
        "TYPE",
        "TYPE_NOTEPAD",
        "VOLUME_UP",
        "VOLUME_DOWN",
        "MUTE",
        "SCREENSHOT",
        "MOUSE_CLICK",
        "MOUSE_CENTER",
        "OPEN_WHATSAPP",
        "SLEEP",
    ],

    CAPABILITY_WEB: [
        "WEB_SEARCH",
        "YOUTUBE_SEARCH",
    ],

    CAPABILITY_AI: [
        "AI_RESPONSE",
    ],

    CAPABILITY_MEMORY: [
        "SAVE_MEMORY",
        "READ_MEMORY",
        "CONVERSATION",
    ],

    CAPABILITY_SYSTEM: [
        "TIME",
        "DATE",
        "EXIT",
    ],
}


# ------------------------------------------------------------
# FIND CAPABILITY
# ------------------------------------------------------------

def get_capability(command_type):
    """
    Find which capability handles a command.
    """

    for capability, commands in CAPABILITIES.items():
        if command_type in commands:
            return capability

    return None


# ------------------------------------------------------------
# CHECK CAPABILITY
# ------------------------------------------------------------

def has_capability(command_type):
    """
    Check whether NEXUS supports a command.
    """

    return get_capability(command_type) is not None


# ------------------------------------------------------------
# EXECUTE CAPABILITY
# ------------------------------------------------------------

def execute_capability(command_type, target=None):
    """
    Send a command to the correct execution system.
    """

    capability = get_capability(command_type)

    if capability is None:
        return "Capability not available."

    if capability == CAPABILITY_PC:
        return execute_command(command_type, target)

    return None


# ------------------------------------------------------------
# LIST CAPABILITIES
# ------------------------------------------------------------

def list_capabilities():
    """
    Return all currently available NEXUS capabilities.
    """

    return CAPABILITIES


# ------------------------------------------------------------
# CAPABILITY STATUS
# ------------------------------------------------------------

def capability_status():
    """
    Return a simple status report.
    """

    status = {}

    for capability, commands in CAPABILITIES.items():
        status[capability] = {
            "available": True,
            "commands": commands,
        }

    return status