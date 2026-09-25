# ============================================================
# NEXUS COMMAND EXECUTOR
# ============================================================

import os

from core.pc import (
    open_app,
    open_website,
    take_screenshot,
    volume_up,
    volume_down,
    volume_mute,
    move_mouse_center,
    mouse_click,
    youtube_search,
    web_search,
    type_text,
    type_in_notepad,
)


# ============================================================
# COMMAND EXECUTION
# ============================================================

def execute_command(command_type, target=None):

    """
    Execute a classified NEXUS command.

    Router:
        Detects the command.

    Classifier:
        Identifies the exact command.

    Executor:
        Performs the actual PC action.
    """


    # --------------------------------------------------------
    # OPEN APP
    # --------------------------------------------------------

    if command_type == "OPEN":

        return open_app(target)


    # --------------------------------------------------------
    # OPEN WEBSITE
    # --------------------------------------------------------

    if command_type == "OPEN_WEBSITE":

        if not target:

            return "No website was specified."

        website = target.strip()

        if not website.startswith(
            ("http://", "https://")
        ):

            website = "https://" + website

        return open_website(website)


    # --------------------------------------------------------
    # WEB SEARCH
    # --------------------------------------------------------

    if command_type == "WEB_SEARCH":

        return web_search(target)


    # --------------------------------------------------------
    # YOUTUBE SEARCH
    # --------------------------------------------------------

    if command_type == "YOUTUBE_SEARCH":

        return youtube_search(target)


    # --------------------------------------------------------
    # TYPE
    # --------------------------------------------------------

    if command_type == "TYPE":

        return type_text(target)


    # --------------------------------------------------------
    # TYPE IN NOTEPAD
    # --------------------------------------------------------

    if command_type == "TYPE_NOTEPAD":

        return type_in_notepad(target)


    # --------------------------------------------------------
    # VOLUME
    # --------------------------------------------------------

    if command_type == "VOLUME_UP":

        return volume_up()


    if command_type == "VOLUME_DOWN":

        return volume_down()


    if command_type == "MUTE":

        return volume_mute()


    # --------------------------------------------------------
    # SCREENSHOT
    # --------------------------------------------------------

    if command_type == "SCREENSHOT":

        return take_screenshot()


    # --------------------------------------------------------
    # MOUSE
    # --------------------------------------------------------

    if command_type == "MOUSE_CLICK":

        return mouse_click()


    if command_type == "MOUSE_CENTER":

        return move_mouse_center()


    # --------------------------------------------------------
    # WHATSAPP
    # --------------------------------------------------------

    if command_type == "OPEN_WHATSAPP":

        os.system(
            "start whatsapp:"
        )

        return "Opening WhatsApp."


    # --------------------------------------------------------
    # SLEEP
    # --------------------------------------------------------

    if command_type == "SLEEP":

        os.system(
            "rundll32.exe "
            "powrprof.dll,SetSuspendState 0,1,0"
        )

        return "Putting the computer to sleep."


    # --------------------------------------------------------
    # UNKNOWN COMMAND
    # --------------------------------------------------------

    return None