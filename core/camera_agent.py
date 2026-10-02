# ============================================================
# NEXUS JARVIS CAMERA & GENERATIVE CINEMATIC AD ENGINE
# Direct replication of @dhaibuilds Jarvis vision & ad generator
# ============================================================

import os
import cv2
import json
import time
import threading
from datetime import datetime
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

SNAPSHOT_FILE = "nexus_camera_snapshot.jpg"
AD_OUTPUT_FILE = "cinematic_ad_output.json"

_camera_running = False
_camera_thread = None


def open_camera(window_title: str = "JARVIS NEURAL OPTICS // LIVE FEED") -> dict:
    """
    Open live camera preview with futuristic HUD overlay reticle and target tracking.
    Press 's' or 'SPACE' to capture snapshot, 'q' or 'ESC' to close.
    """
    global _camera_running

    try:
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            return {
                "success": False,
                "error": "No camera device detected or camera is currently occupied by another application."
            }

        _camera_running = True

        def _cam_loop():
            global _camera_running
            cv2.namedWindow(window_title, cv2.WINDOW_NORMAL)
            cv2.resizeWindow(window_title, 800, 600)

            while _camera_running:
                ret, frame = cap.read()
                if not ret:
                    break

                h, w, _ = frame.shape
                cx, cy = w // 2, h // 2

                # Render Iron Man HUD Cyan Target Reticle
                cyan = (255, 230, 0)      # BGR: Cyan
                accent = (255, 100, 0)    # Blue accent

                # Center crosshairs & box
                box_sz = 140
                cv2.rectangle(frame, (cx - box_sz, cy - box_sz), (cx + box_sz, cy + box_sz), cyan, 2)
                cv2.line(frame, (cx - box_sz - 30, cy), (cx - box_sz + 15, cy), cyan, 2)
                cv2.line(frame, (cx + box_sz - 15, cy), (cx + box_sz + 30, cy), cyan, 2)
                cv2.line(frame, (cx, cy - box_sz - 30), (cx, cy - box_sz + 15), cyan, 2)
                cv2.line(frame, (cx, cy + box_sz - 15), (cx, cy + box_sz + 30), cyan, 2)

                # Corner brackets
                brk = 25
                # Top-Left
                cv2.line(frame, (cx - box_sz, cy - box_sz), (cx - box_sz + brk, cy - box_sz), (0, 255, 255), 3)
                cv2.line(frame, (cx - box_sz, cy - box_sz), (cx - box_sz, cy - box_sz + brk), (0, 255, 255), 3)
                # Bottom-Right
                cv2.line(frame, (cx + box_sz, cy + box_sz), (cx + box_sz - brk, cy + box_sz), (0, 255, 255), 3)
                cv2.line(frame, (cx + box_sz, cy + box_sz), (cx + box_sz, cy + box_sz - brk), (0, 255, 255), 3)

                # HUD Text Overlay
                cv2.putText(frame, "JARVIS OPTICAL SENSOR // TARGET LOCK", (30, 40),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.65, cyan, 2)
                cv2.putText(frame, "HOLD PRODUCT IN FRAME | PRESS [SPACE] TO CAPTURE | [ESC] TO CLOSE", (30, h - 30),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 1)

                cv2.imshow(window_title, frame)

                key = cv2.waitKey(1) & 0xFF
                if key in (27, ord('q')):  # ESC or Q
                    break
                elif key in (32, ord('s')):  # SPACE or S to take snapshot
                    cv2.imwrite(SNAPSHOT_FILE, frame)
                    print(f"[JARVIS CAMERA]: Snapshot saved to {SNAPSHOT_FILE}")

            cap.release()
            cv2.destroyAllWindows()
            _camera_running = False

        thread = threading.Thread(target=_cam_loop, daemon=True)
        thread.start()

        return {
            "success": True,
            "message": "Camera's live, boss. Optical tracking overlay engaged."
        }

    except Exception as e:
        return {"success": False, "error": str(e)}


def capture_camera_snapshot(save_path: str = SNAPSHOT_FILE) -> dict:
    """Capture a single frame from the camera silently and save to disk."""
    try:
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            # If camera isn't plugged in or accessible, create a clean diagnostic placeholder image
            return {
                "success": False,
                "error": "Could not access camera device."
            }

        # Warm up sensor
        for _ in range(5):
            cap.read()

        ret, frame = cap.read()
        cap.release()

        if not ret:
            return {"success": False, "error": "Failed to read frame from camera."}

        cv2.imwrite(save_path, frame)
        return {
            "success": True,
            "file": save_path,
            "width": frame.shape[1],
            "height": frame.shape[0]
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


def close_camera():
    """Close any running camera preview."""
    global _camera_running
    _camera_running = False
    try:
        cv2.destroyAllWindows()
    except Exception:
        pass


def create_cinematic_ad(image_path: str = None) -> dict:
    """
    Generate a full Hollywood/commercial grade cinematic video ad breakdown
    and AI video generator prompt from the photographed product.
    Matches the exact demo from @dhaibuilds.
    """
    target_image = image_path or SNAPSHOT_FILE

    # If image does not exist yet, take a snapshot immediately
    if not os.path.exists(target_image):
        snap_res = capture_camera_snapshot(target_image)
        if not snap_res.get("success"):
            return {
                "success": False,
                "error": f"No image available for ad creation ({snap_res.get('error')}). Please hold a product up and say 'open camera'."
            }

    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return {"success": False, "error": "GEMINI_API_KEY is missing."}

    prompt = """
You are JARVIS, Tony Stark's elite creative commercial director and AI visual architect.
The user has held up a physical product to the camera.

Analyze this image and create an ultra-cinematic, high-converting commercial video ad.
Return a clean, valid JSON object with the following structure:
{
  "product_name": "Identified product name and brand",
  "category": "e.g. Energy Drink / Tech Gadget / Beverage / Luxury Accessory",
  "visual_description": "Precise visual description of the product in the photo",
  "tagline": "Punchy, catchy, Hollywood-grade tagline",
  "cinematic_ad_concept": "Creative vision and thematic direction (lighting, atmosphere, mood)",
  "storyboard": [
    {
      "scene": 1,
      "shot_type": "Macro close-up / Orbit / Slow motion",
      "visuals": "Detailed description of what is on screen",
      "lighting_and_fx": "Volumetric lighting, water droplets, particle smoke, anamorphic lens flares",
      "voiceover": "Spoken voiceover line for this shot"
    },
    {
      "scene": 2,
      "shot_type": "Dynamic 360 camera orbit",
      "visuals": "Visual movement",
      "lighting_and_fx": "Lighting details",
      "voiceover": "Spoken voiceover line"
    },
    {
      "scene": 3,
      "shot_type": "High-impact hero action shot",
      "visuals": "Hero action",
      "lighting_and_fx": "Lighting details",
      "voiceover": "Spoken voiceover line"
    },
    {
      "scene": 4,
      "shot_type": "Final hero brand lockup",
      "visuals": "Product centered with glowing logo and tagline reveal",
      "lighting_and_fx": "Studio rim lighting, dark reflective surface",
      "voiceover": "Final closing hook"
    }
  ],
  "ai_video_prompts": {
    "runway_gen3": "Comprehensive photorealistic 4k camera prompt ready to copy-paste into Runway Gen-3",
    "kling_ai": "Kling 1.5 cinematic motion prompt",
    "luma_dream_machine": "Luma Dream Machine dynamic motion prompt"
  },
  "soundtrack_and_sfx": "Audio design (e.g. Hans Zimmer style escalating orchestral braam, crisp soda pop fizz, futuristic whoosh)",
  "jarvis_spoken_summary": "A 2-sentence sharp response from Jarvis to the boss summarizing the commercial created"
}

Provide JSON ONLY without markdown fences.
"""

    try:
        client = genai.Client(api_key=api_key)

        with open(target_image, "rb") as f:
            img_bytes = f.read()

        img_part = types.Part.from_bytes(
            data=img_bytes,
            mime_type="image/jpeg"
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

        # Save to output file
        with open(AD_OUTPUT_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

        return {
            "success": True,
            "ad": data,
            "file": AD_OUTPUT_FILE,
            "spoken_summary": data.get("jarvis_spoken_summary", "I have generated the cinematic ad storyboard and AI video prompts for you, boss.")
        }

    except Exception as e:
        return {"success": False, "error": str(e)}
