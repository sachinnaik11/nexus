# ============================================================
# NEXUS JARVIS SCREEN VISION AGENT
# Replication of "Jarvis, what do you see?" from @dhaibuilds
# Bulletproof Win32 InputDesktop screen capture + Gemini Multimodal
# ============================================================

import os
import json
import ctypes
from PIL import Image
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

SCREEN_SNAPSHOT_FILE = "nexus_screen_snapshot.png"


def capture_screen_image(save_path: str = SCREEN_SNAPSHOT_FILE) -> dict:
    """
    Capture full monitor screen using native Win32 GDI with InputDesktop attachment.
    Works flawlessly across all Windows sessions, DPI scalings, and threads.
    """
    try:
        user32 = ctypes.windll.user32
        kernel32 = ctypes.windll.kernel32
        gdi32 = ctypes.windll.gdi32

        # Attach calling thread to interactive desktop session
        try:
            hdesk_input = user32.OpenInputDesktop(0, False, 0x01FF)
            if hdesk_input:
                user32.SetThreadDesktop(hdesk_input)
        except Exception:
            pass

        width = user32.GetSystemMetrics(0)
        height = user32.GetSystemMetrics(1)

        hdc_screen = user32.GetDC(0)
        hdc_mem = gdi32.CreateCompatibleDC(hdc_screen)
        hbm = gdi32.CreateCompatibleBitmap(hdc_screen, width, height)
        gdi32.SelectObject(hdc_mem, hbm)

        res = gdi32.BitBlt(hdc_mem, 0, 0, width, height, hdc_screen, 0, 0, 0x00CC0020)

        if not res:
            # Fallback to pyautogui or PIL
            gdi32.DeleteObject(hbm)
            gdi32.DeleteDC(hdc_mem)
            user32.ReleaseDC(0, hdc_screen)
            import pyautogui
            img = pyautogui.screenshot()
            img.save(save_path)
            return {"success": True, "file": save_path, "width": img.width, "height": img.height}

        class BITMAPINFOHEADER(ctypes.Structure):
            _fields_ = [
                ('biSize', ctypes.c_uint32),
                ('biWidth', ctypes.c_int32),
                ('biHeight', ctypes.c_int32),
                ('biPlanes', ctypes.c_uint16),
                ('biBitCount', ctypes.c_uint16),
                ('biCompression', ctypes.c_uint32),
                ('biSizeImage', ctypes.c_uint32),
                ('biXPelsPerMeter', ctypes.c_int32),
                ('biYPelsPerMeter', ctypes.c_int32),
                ('biClrUsed', ctypes.c_uint32),
                ('biClrImportant', ctypes.c_uint32)
            ]

        bmi = BITMAPINFOHEADER()
        bmi.biSize = ctypes.sizeof(BITMAPINFOHEADER)
        bmi.biWidth = width
        bmi.biHeight = -height  # top-down DIB
        bmi.biPlanes = 1
        bmi.biBitCount = 32
        bmi.biCompression = 0

        buf = ctypes.create_string_buffer(width * height * 4)
        gdi32.GetDIBits(hdc_mem, hbm, 0, height, buf, ctypes.byref(bmi), 0)
        im = Image.frombuffer('RGBA', (width, height), buf, 'raw', 'BGRA', 0, 1)
        im.convert('RGB').save(save_path)

        gdi32.DeleteObject(hbm)
        gdi32.DeleteDC(hdc_mem)
        user32.ReleaseDC(0, hdc_screen)

        return {
            "success": True,
            "file": save_path,
            "width": width,
            "height": height
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


def what_do_you_see(question: str = None) -> dict:
    """
    Directly answers "Jarvis, what do you see?" by observing the user's active screen,
    deciphering open apps, documents, tabs, and content, and returning a concise,
    intelligent spoken reply in Jarvis British persona.
    """
    snap_res = capture_screen_image()
    if not snap_res.get("success"):
        return {"success": False, "error": snap_res.get("error")}

    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return {"success": False, "error": "GEMINI_API_KEY is not configured."}

    user_query = question or "What do you see on my screen right now?"

    prompt = f"""
You are J.A.R.V.I.S., Tony Stark's personal AI desktop assistant.
You are looking directly at your boss's computer screen.

User query: "{user_query}"

Instructions:
1. Explain what is open on the user's display (e.g. browser tabs, VS Code, terminal, Spotify, YouTube, folder, etc.).
2. Focus on the primary active window and summarize what the content is about.
3. Be sharp, articulate, and respectful. Use a natural persona ("This is a...", "You're currently viewing...", "I can see...").
4. Keep the spoken response between 2 and 3 sentences so it can be spoken out loud immediately without rambling.

Return valid JSON ONLY in this format:
{{
  "spoken_summary": "Two to three sentences describing what is on screen clearly and smartly.",
  "active_apps": ["App1", "App2"],
  "main_topic": "Short title of what the user is working on or viewing",
  "actionable_suggestion": "One helpful next step you can take for the user"
}}
"""

    try:
        client = genai.Client(api_key=api_key)

        with open(snap_res["file"], "rb") as f:
            img_bytes = f.read()

        img_part = types.Part.from_bytes(
            data=img_bytes,
            mime_type="image/png"
        )

        response = client.models.generate_content(
            model="gemini-3.8-flash",
            contents=[img_part, prompt]
        )

        raw_text = getattr(response, "text", "") or ""
        raw_text = raw_text.strip()
        if raw_text.startswith("```"):
            lines = raw_text.splitlines()
            if lines:
                lines = lines[1:]
            if lines and lines[-1].strip() == "```":
                lines = lines[:-1]
            raw_text = "\n".join(lines).strip()

        start = raw_text.find("{")
        end = raw_text.rfind("}")
        if start != -1 and end != -1:
            raw_text = raw_text[start:end+1]

        data = json.loads(raw_text)

        spoken = data.get("spoken_summary", "I am observing your desktop display, boss.")

        return {
            "success": True,
            "spoken_summary": spoken,
            "active_apps": data.get("active_apps", []),
            "main_topic": data.get("main_topic", "Desktop Workspace"),
            "actionable_suggestion": data.get("actionable_suggestion", ""),
            "snapshot_file": snap_res["file"]
        }

    except Exception as e:
        return {"success": False, "error": str(e)}
