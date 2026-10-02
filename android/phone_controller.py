# ============================================================
# NEXUS — ANDROID PHONE CONTROLLER
# Full remote control of Android devices via ADB & scrcpy
# (Screen Mirroring, Apps, Navigation, Calls, SMS, Wireless Wi-Fi)
# ============================================================

import os
import re
import time
import socket
import logging
import subprocess
from typing import Dict, List, Optional, Any

logger = logging.getLogger("NexusPhoneController")


class PhoneController:
    """
    Controls an Android smartphone via ADB and scrcpy (USB or Wi-Fi).
    Allows NEXUS to control mobile hardware, apps, and live screen mirroring.
    """

    KNOWN_PACKAGES = {
        "youtube": "com.google.android.youtube",
        "whatsapp": "com.whatsapp",
        "chrome": "com.android.chrome",
        "browser": "com.android.chrome",
        "settings": "com.android.settings",
        "camera": "com.android.camera",
        "spotify": "com.spotify.music",
        "instagram": "com.instagram.android",
        "free fire": "com.dts.freefiremax",
        "free fire max": "com.dts.freefiremax",
        "gallery": "com.google.android.apps.photos",
        "photos": "com.google.android.apps.photos",
        "calculator": "com.google.android.calculator",
        "clock": "com.google.android.deskclock",
        "maps": "com.google.android.apps.maps",
        "telegram": "org.telegram.messenger",
        "twitter": "com.twitter.android",
        "x": "com.twitter.android",
        "snapchat": "com.snapchat.android",
        "netflix": "com.netflix.mediaclient",
        "play store": "com.android.vending",
        "messages": "com.google.android.apps.messaging",
        "sms": "com.google.android.apps.messaging",
        "phone": "com.google.android.dialer",
        "dialer": "com.google.android.dialer",
        "gmail": "com.google.android.gm",
        "files": "com.google.android.documentsui",
    }

    def __init__(self):
        self.adb_path = self._discover_adb()
        self.scrcpy_path = self._discover_scrcpy()

    def _discover_adb(self) -> Optional[str]:
        """Locate the best available ADB binary."""
        base_dir = os.path.dirname(os.path.abspath(__file__))
        nexus_dir = os.path.dirname(base_dir)

        candidates = [
            os.path.join(nexus_dir, "bin", "scrcpy-win64-v4.1", "adb.exe"),
            os.path.join(nexus_dir, "bin", "platform-tools", "adb.exe"),
            r"C:\Program Files\BlueStacks_nxt\HD-Adb.exe",
            os.path.expandvars(r"%LOCALAPPDATA%\Android\Sdk\platform-tools\adb.exe"),
            r"C:\platform-tools\adb.exe",
            "adb",
        ]
        for path in candidates:
            if os.path.exists(path):
                return os.path.abspath(path)
            try:
                r = subprocess.run([path, "version"], capture_output=True, timeout=2)
                if r.returncode == 0:
                    return path
            except Exception:
                pass
        return None

    def _discover_scrcpy(self) -> Optional[str]:
        """Locate scrcpy binary for screen mirroring and live PC control."""
        base_dir = os.path.dirname(os.path.abspath(__file__))
        nexus_dir = os.path.dirname(base_dir)

        candidates = [
            os.path.join(nexus_dir, "bin", "scrcpy-win64-v4.1", "scrcpy.exe"),
            os.path.join(nexus_dir, "bin", "scrcpy.exe"),
            "scrcpy",
        ]
        for path in candidates:
            if os.path.exists(path):
                return os.path.abspath(path)
            try:
                r = subprocess.run([path, "--version"], capture_output=True, timeout=2)
                if r.returncode == 0:
                    return path
            except Exception:
                pass
        return None

    def _run_adb(self, args: List[str], timeout: int = 10) -> subprocess.CompletedProcess:
        """Execute an ADB command."""
        if not self.adb_path:
            self.adb_path = self._discover_adb()
        if not self.adb_path:
            raise RuntimeError("ADB binary not found on this system.")
        cmd = [self.adb_path] + args
        return subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)

    # ------------------------------------------------------------
    # CONNECTION & DEVICE DISCOVERY
    # ------------------------------------------------------------

    def list_devices(self) -> List[Dict[str, str]]:
        """List all attached Android devices (USB & Wi-Fi)."""
        if not self.adb_path:
            self.adb_path = self._discover_adb()
        if not self.adb_path:
            return []
        try:
            res = self._run_adb(["devices"])
            devices = []
            for line in res.stdout.strip().splitlines()[1:]:
                line = line.strip()
                if not line or line.startswith("*"):
                    continue
                parts = line.split()
                if len(parts) >= 2:
                    devices.append({"id": parts[0], "status": parts[1]})
            return devices
        except Exception as e:
            logger.error(f"Failed to list ADB devices: {e}")
            return []

    def is_connected(self) -> bool:
        """Check if at least one Android device is connected and authorized."""
        devices = self.list_devices()
        return any(d.get("status") == "device" for d in devices)

    def connect_wireless(self, target: str) -> str:
        """Connect to Android phone over Wi-Fi (e.g. 192.168.1.5 or 192.168.1.5:5555)."""
        clean_target = str(target).strip()
        if not clean_target:
            return "Please provide an IP address, e.g. 'connect phone 192.168.1.5:5555'."
        if ":" not in clean_target:
            clean_target = f"{clean_target}:5555"

        try:
            res = self._run_adb(["connect", clean_target], timeout=12)
            out = (res.stdout + res.stderr).strip()
            if "connected to" in out.lower():
                return f"Successfully connected wirelessly to {clean_target}."
            return f"Wi-Fi Connection Result: {out}"
        except Exception as e:
            return f"Failed to connect wirelessly: {e}"

    def pair_device(self, target: str, code: str) -> str:
        """Pair device with pairing code for Android 11+ wireless debugging."""
        try:
            res = self._run_adb(["pair", target.strip(), code.strip()], timeout=15)
            return (res.stdout + res.stderr).strip()
        except Exception as e:
            return f"Failed to pair device: {e}"

    def enable_wireless_port(self, port: int = 5555) -> str:
        """Configure ADB daemon on device to listen on Wi-Fi TCP port."""
        try:
            res = self._run_adb(["tcpip", str(port)])
            out = (res.stdout + res.stderr).strip()
            return f"Wireless ADB mode activated on port {port}. You can now unplug the USB cable! ({out})"
        except Exception as e:
            return f"Failed to enable wireless port: {e}"

    # ------------------------------------------------------------
    # SCREEN MIRRORING & LIVE PC CONTROL (SCRCPY)
    # ------------------------------------------------------------

    def mirror_screen(self, title: str = "NEXUS Mobile Command Center") -> str:
        """Launch scrcpy for live screen mirroring, touch, and keyboard control."""
        if not self.is_connected():
            return (
                "📱 Android phone not connected.\n\n"
                "To control your mobile screen directly on your laptop:\n"
                "1. Connect your phone via USB cable.\n"
                "2. Turn on USB Debugging in Settings > Developer Options.\n"
                "3. Tap 'Always allow from this computer' on your phone screen.\n\n"
                "Or connect wirelessly: 'connect phone <ip>:5555'."
            )

        scrcpy_path = self._discover_scrcpy()
        if not scrcpy_path:
            return "Screen control tool (scrcpy) could not be located in bin directory."

        try:
            env = os.environ.copy()
            if self.adb_path:
                adb_dir = os.path.dirname(self.adb_path)
                env["PATH"] = adb_dir + os.path.pathsep + env.get("PATH", "")
                env["ADB"] = self.adb_path

            cmd = [
                scrcpy_path,
                "--window-title", title,
                "--always-on-top",
                "--stay-awake",
                "--show-touches",
            ]
            subprocess.Popen(cmd, env=env)
            return (
                "Mobile screen control active. Your phone screen is now mirrored on your laptop. "
                "You can click, drag, scroll, and type using your laptop mouse and keyboard."
            )
        except Exception as e:
            return f"Failed to launch phone screen control: {e}"

    # ------------------------------------------------------------
    # SYSTEM STATUS (BATTERY, STORAGE, MODEL)
    # ------------------------------------------------------------

    def get_battery(self) -> Dict[str, Any]:
        """Read phone battery percentage and charging status."""
        try:
            res = self._run_adb(["shell", "dumpsys", "battery"])
            level_m = re.search(r"level:\s*(\d+)", res.stdout)
            charging_m = re.search(r"status:\s*(\d+)", res.stdout)
            level = int(level_m.group(1)) if level_m else None
            is_charging = charging_m.group(1) == "2" if charging_m else False

            if level is not None:
                return {
                    "level": level,
                    "charging": is_charging,
                    "message": f"Phone battery is at {level}% ({'Charging' if is_charging else 'On Battery'}).",
                }
            return {"level": None, "message": "Phone battery info unavailable."}
        except Exception as e:
            return {"level": None, "message": f"Error reading phone battery: {e}"}

    def get_phone_info(self) -> str:
        """Get phone manufacturer, model, and Android OS version."""
        if not self.is_connected():
            return (
                "[ANDROID] NO DEVICE CONNECTED\n\n"
                "To connect and control your mobile phone:\n"
                "1. Method 1 (USB Cable - Instant):\n"
                "   - Enable Developer Options (Settings > About Phone > Tap 'Build Number' 7 times).\n"
                "   - In Developer Options, enable 'USB Debugging'.\n"
                "   - Plug phone into PC and tap 'Always allow from this computer'.\n\n"
                "2. Method 2 (Wi-Fi Wireless):\n"
                "   - Connect phone and PC to the same Wi-Fi.\n"
                "   - In Developer Options, enable 'Wireless Debugging'.\n"
                "   - Type: 'connect phone <ip>:5555' or use the Phone tab in NEXUS UI.\n\n"
                "3. Screen Mirroring:\n"
                "   Once connected, type 'control my mobile' or 'mirror phone' to control the phone from PC!"
            )

        try:
            model = self._run_adb(["shell", "getprop", "ro.product.model"]).stdout.strip()
            brand = self._run_adb(["shell", "getprop", "ro.product.brand"]).stdout.strip()
            version = self._run_adb(["shell", "getprop", "ro.build.version.release"]).stdout.strip()
            battery = self.get_battery()

            return (
                f"Connected Device: {brand.capitalize()} {model} (Android {version})\n"
                f"{battery.get('message', '')}"
            )
        except Exception as e:
            return f"Could not retrieve phone info: {e}"

    # ------------------------------------------------------------
    # SCREEN & NAVIGATION CONTROLS
    # ------------------------------------------------------------

    def take_screenshot(self, local_filename: str = "nexus_phone_screenshot.png") -> str:
        """Capture phone screen and pull it to desktop."""
        try:
            remote_path = "/sdcard/nexus_screen.png"
            self._run_adb(["shell", "screencap", "-p", remote_path])
            self._run_adb(["pull", remote_path, local_filename])
            self._run_adb(["shell", "rm", remote_path])
            return os.path.abspath(local_filename)
        except Exception as e:
            return f"Failed to take phone screenshot: {e}"

    def lock_phone(self) -> str:
        """Lock phone screen (Power button keyevent 26)."""
        try:
            self._run_adb(["shell", "input", "keyevent", "26"])
            return "Phone screen locked."
        except Exception as e:
            return f"Failed to lock phone: {e}"

    def unlock_phone(self) -> str:
        """Wake up phone and swipe up to unlock display."""
        try:
            self._run_adb(["shell", "input", "keyevent", "224"])
            time.sleep(0.2)
            self._run_adb(["shell", "input", "keyevent", "82"])
            self._run_adb(["shell", "input", "swipe", "500", "1600", "500", "400", "200"])
            return "Phone screen awakened and unlocked."
        except Exception as e:
            return f"Failed to unlock phone: {e}"

    def press_home(self) -> str:
        """Navigate to Android home screen."""
        try:
            self._run_adb(["shell", "input", "keyevent", "3"])
            return "Navigated to phone Home screen."
        except Exception as e:
            return f"Failed to press Home: {e}"

    def press_back(self) -> str:
        """Navigate Back on Android."""
        try:
            self._run_adb(["shell", "input", "keyevent", "4"])
            return "Navigated Back on phone."
        except Exception as e:
            return f"Failed to press Back: {e}"

    def press_recents(self) -> str:
        """Open Android recent apps overview."""
        try:
            self._run_adb(["shell", "input", "keyevent", "187"])
            return "Opened phone recent apps switcher."
        except Exception as e:
            return f"Failed to open recents: {e}"

    def show_notifications(self) -> str:
        """Expand notification shade."""
        try:
            self._run_adb(["shell", "cmd", "statusbar", "expand-notifications"])
            return "Expanded phone notification shade."
        except Exception as e:
            return f"Failed to expand notifications: {e}"

    def show_quick_settings(self) -> str:
        """Open quick settings shade."""
        try:
            self._run_adb(["shell", "cmd", "statusbar", "expand-settings"])
            return "Opened phone quick settings panel."
        except Exception as e:
            return f"Failed to open quick settings: {e}"

    # ------------------------------------------------------------
    # AUDIO & MEDIA
    # ------------------------------------------------------------

    def volume_up(self) -> str:
        """Increase phone volume."""
        try:
            self._run_adb(["shell", "input", "keyevent", "24"])
            return "Increased phone volume."
        except Exception as e:
            return f"Failed to adjust volume: {e}"

    def volume_down(self) -> str:
        """Decrease phone volume."""
        try:
            self._run_adb(["shell", "input", "keyevent", "25"])
            return "Decreased phone volume."
        except Exception as e:
            return f"Failed to adjust volume: {e}"

    def media_play_pause(self) -> str:
        """Toggle media playback."""
        try:
            self._run_adb(["shell", "input", "keyevent", "85"])
            return "Toggled phone media playback."
        except Exception as e:
            return f"Failed to toggle media: {e}"

    def media_next(self) -> str:
        """Skip to next media track."""
        try:
            self._run_adb(["shell", "input", "keyevent", "87"])
            return "Skipped to next track on phone."
        except Exception as e:
            return f"Failed to skip track: {e}"

    def media_prev(self) -> str:
        """Skip to previous media track."""
        try:
            self._run_adb(["shell", "input", "keyevent", "88"])
            return "Returned to previous track on phone."
        except Exception as e:
            return f"Failed to return to previous track: {e}"

    # ------------------------------------------------------------
    # APP CONTROL & AUTOMATION
    # ------------------------------------------------------------

    def open_app(self, app_name: str) -> str:
        """Launch an app on the phone by name or package."""
        clean_name = str(app_name).strip().lower()
        package = self.KNOWN_PACKAGES.get(clean_name, clean_name)

        try:
            res = self._run_adb(["shell", "monkey", "-p", package, "-c", "android.intent.category.LAUNCHER", "1"])
            if "No activities found" in res.stdout or "Error" in res.stderr:
                return f"Could not launch '{app_name}' on phone. Package '{package}' not found."
            return f"Launched {app_name.capitalize()} on your phone."
        except Exception as e:
            return f"Failed to open {app_name} on phone: {e}"

    def close_app(self, app_name: str) -> str:
        """Force-stop an app on the phone."""
        clean_name = str(app_name).strip().lower()
        package = self.KNOWN_PACKAGES.get(clean_name, clean_name)
        try:
            self._run_adb(["shell", "am", "force-stop", package])
            return f"Closed {app_name.capitalize()} on your phone."
        except Exception as e:
            return f"Failed to close {app_name} on phone: {e}"

    def type_text(self, text: str) -> str:
        """Type text into the currently focused field on the phone."""
        try:
            escaped = str(text).replace(" ", "%s")
            self._run_adb(["shell", "input", "text", escaped])
            return f"Typed '{text}' on phone."
        except Exception as e:
            return f"Failed to type on phone: {e}"

    # ------------------------------------------------------------
    # CALLS & MESSAGING
    # ------------------------------------------------------------

    def make_call(self, phone_number: str) -> str:
        """Initiate a phone call on the connected Android phone."""
        clean_number = re.sub(r"[^\d+]", "", str(phone_number))
        if not clean_number:
            return "Please provide a valid phone number to call."

        try:
            self._run_adb([
                "shell", "am", "start",
                "-a", "android.intent.action.CALL",
                "-d", f"tel:{clean_number}"
            ])
            return f"Calling {clean_number} from your phone."
        except Exception as e:
            return f"Failed to start call: {e}"

    def send_sms(self, phone_number: str, message: str) -> str:
        """Prepare or send an SMS from the phone."""
        clean_number = re.sub(r"[^\d+]", "", str(phone_number))
        try:
            escaped = message.replace('"', '\\"')
            self._run_adb([
                "shell", "am", "start",
                "-a", "android.intent.action.SENDTO",
                "-d", f"sms:{clean_number}",
                "--es", "sms_body", escaped
            ])
            return f"SMS to {clean_number} drafted on your phone."
        except Exception as e:
            return f"Failed to send SMS: {e}"


# Global singleton controller
phone = PhoneController()
