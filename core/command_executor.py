# ============================================================
# NEXUS COMMAND EXECUTOR
# ============================================================

import os

from core.pc import (
    open_app,
    close_app,
    open_website,
    take_screenshot,
    volume_up,
    volume_down,
    volume_mute,
    volume_unmute,
    lock_pc,
    show_desktop,
    empty_recycle_bin,
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
    # CLOSE APP
    # --------------------------------------------------------

    if command_type == "CLOSE":

        return close_app(target)


    # --------------------------------------------------------
    # UNMUTE
    # --------------------------------------------------------

    if command_type == "UNMUTE":

        return volume_unmute()


    # --------------------------------------------------------
    # LOCK PC
    # --------------------------------------------------------

    if command_type == "LOCK_PC":

        return lock_pc()


    # --------------------------------------------------------
    # SHOW DESKTOP
    # --------------------------------------------------------

    if command_type == "SHOW_DESKTOP":

        return show_desktop()


    # --------------------------------------------------------
    # EMPTY RECYCLE BIN
    # --------------------------------------------------------

    if command_type == "EMPTY_RECYCLE_BIN":

        return empty_recycle_bin()


    # --------------------------------------------------------
    # YOUTUBE & CREATOR ACTIONS
    # --------------------------------------------------------

    if command_type == "YOUTUBE_STUDIO":

        from tools.youtube_manager import open_youtube_studio
        return open_youtube_studio()


    if command_type == "OPEN_CAPCUT":

        from tools.youtube_manager import open_capcut
        return open_capcut()


    if command_type == "YOUTUBE_VIRAL_SEO":

        from tools.youtube_manager import generate_viral_seo
        result = generate_viral_seo(target or "relatable viral memes")
        return result.get("seo_package", "SEO generation complete.")


    if command_type == "YOUTUBE_MEME_SHORT":

        from tools.youtube_manager import generate_niche_meme_short
        result = generate_niche_meme_short()
        summary = f"Generated Meme Short Plan:\n{result.get('meme_plan', '')}"
        if result.get("image_asset"):
            summary += f"\nAsset created: {result['image_asset']}"
        return summary


    if command_type == "SET_NICHE":

        from tools.youtube_manager import set_channel_niche
        return set_channel_niche(target or "Viral Memes & Relatable Comedy")


    if command_type == "CHECK_REMINDER":

        from tools.youtube_manager import check_upload_reminder
        return check_upload_reminder()


    if command_type == "YOUTUBE_AUTO_OPTIMIZE":

        from tools.youtube_automation import youtube_automator
        return youtube_automator.auto_optimize_latest_video(target)


    if command_type == "YOUTUBE_STUDIO_AUTOFILL":

        from tools.youtube_automation import youtube_automator
        return youtube_automator.autofill_studio_browser(target)


    if command_type == "YOUTUBE_START_WATCHER":

        from tools.youtube_automation import youtube_automator
        return youtube_automator.start_channel_watcher()


    if command_type == "YOUTUBE_STOP_WATCHER":

        from tools.youtube_automation import youtube_automator
        return youtube_automator.stop_channel_watcher()


    if command_type == "YOUTUBE_SWITCH_CHANNEL":
        from tools.channel_switcher import switch_channel
        res = switch_channel(target or "")
        return res.get("message", f"Switched channel to {target}.")

    if command_type == "YOUTUBE_LIST_CHANNELS":
        from tools.channel_switcher import list_channels
        channels = list_channels()
        lines = ["=== NEXUS YOUTUBE CHANNELS ==="]
        for name, info in channels.items():
            mark = " (ACTIVE)" if info["is_active"] else ""
            lines.append(f"• {info['display_name']} ({info['handle']}){mark} - {info['niche']}")
        return "\n".join(lines)

    if command_type == "YOUTUBE_AUTO_UPLOAD_MEME":

        from tools.meme_generator import meme_uploader
        return meme_uploader.auto_generate_and_upload(target)


    if command_type == "CLOUD_SYNC":

        from cloud.sync_client import cloud_sync
        res = cloud_sync.sync()
        return res.get("message", "Cloud sync operation complete.")


    if command_type == "CLOUD_STATUS":

        from cloud.sync_client import cloud_sync
        connected = cloud_sync.check_connection()
        if connected:
            res = cloud_sync.sync()
            return f"NEXUS 24/7 Cloud Node is ONLINE. Active Niche: {res.get('niche')}. Pending drafts: {res.get('pending_count')}."
        return "NEXUS 24/7 Cloud Node is currently unreachable or offline. (Run python -m cloud.nexus_cloud_server to launch)."


    # --------------------------------------------------------
    # ANDROID PHONE ACTIONS
    # --------------------------------------------------------

    if command_type == "PHONE_BATTERY":

        from android.phone_controller import phone
        return phone.get_battery().get("message", "Battery reading complete.")


    if command_type == "PHONE_SCREENSHOT":

        from android.phone_controller import phone
        path = phone.take_screenshot()
        return f"Phone screenshot captured: {path}"


    if command_type == "PHONE_LOCK":

        from android.phone_controller import phone
        return phone.lock_phone()


    if command_type == "PHONE_VOLUME_UP":

        from android.phone_controller import phone
        return phone.volume_up()


    if command_type == "PHONE_VOLUME_DOWN":

        from android.phone_controller import phone
        return phone.volume_down()


    if command_type == "PHONE_OPEN_APP":

        from android.phone_controller import phone
        return phone.open_app(target or "youtube")


    if command_type == "PHONE_CLOSE_APP":

        from android.phone_controller import phone
        return phone.close_app(target or "youtube")


    if command_type == "PHONE_CALL":

        from android.phone_controller import phone
        return phone.make_call(target or "")


    if command_type == "PHONE_STATUS":

        from android.phone_controller import phone
        return phone.get_phone_info()


    # --------------------------------------------------------
    # JARVIS SPECIALIZED COMMANDS (@dhaibuilds)
    # --------------------------------------------------------

    if command_type == "CAMERA_OPEN":
        from core.camera_agent import open_camera
        res = open_camera()
        return res.get("message") or res.get("error", "Camera opened.")

    if command_type == "CAMERA_SNAPSHOT":
        from core.camera_agent import capture_camera_snapshot
        res = capture_camera_snapshot()
        if res.get("success"):
            return f"Camera snapshot captured, boss: {res.get('file')}"
        return f"Could not capture camera snapshot: {res.get('error')}"

    if command_type == "CINEMATIC_AD":
        from core.camera_agent import create_cinematic_ad
        res = create_cinematic_ad()
        if res.get("success"):
            return res.get("spoken_summary", "Cinematic ad storyboard and AI video prompts generated successfully, boss.")
        return f"Failed to generate cinematic ad: {res.get('error')}"

    if command_type == "SCREEN_WHAT_DO_YOU_SEE":
        from core.screen_agent import what_do_you_see
        res = what_do_you_see()
        if res.get("success"):
            return res.get("spoken_summary", "I am analyzing your screen, boss.")
        return f"Screen analysis note: {res.get('error')}"

    if command_type == "WORKSPACE_SETUP":
        from core.workspace_agent import set_everything_up
        res = set_everything_up()
        return res.get("spoken_reply", "Workspace setup complete, boss.")

    # --------------------------------------------------------
    # UNKNOWN COMMAND
    # --------------------------------------------------------

    return None