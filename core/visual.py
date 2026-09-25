# ============================================================
# NEXUS VISUAL INTERACTION + SCREEN VISION ENGINE
# ============================================================

import json
import os
import re

import pyautogui
from dotenv import load_dotenv
from google import genai
from google.genai import types


load_dotenv()


SCREENSHOT_FILE = "nexus_visual_screen.png"
VISION_MODEL = os.getenv(
    "NEXUS_VISION_MODEL",
    "gemini-3.5-flash-lite",
)


# ============================================================
# SCREEN CONTROL
# ============================================================

def capture_screen():
    """
    Capture the current screen.
    """
    try:
        image = pyautogui.screenshot()
        image.save(SCREENSHOT_FILE)

        return {
            "success": True,
            "file": SCREENSHOT_FILE,
            "width": image.width,
            "height": image.height,
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
        }


def get_screen_size():
    """
    Get current screen resolution.
    """
    try:
        width, height = pyautogui.size()

        return {
            "success": True,
            "width": width,
            "height": height,
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
        }


def get_mouse_position():
    """
    Get current mouse position.
    """
    try:
        x, y = pyautogui.position()

        return {
            "success": True,
            "x": x,
            "y": y,
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
        }


def move_to(x, y, duration=0.3):
    """
    Move mouse to a screen coordinate.
    """
    try:
        x = int(x)
        y = int(y)

        pyautogui.moveTo(
            x,
            y,
            duration=duration,
        )

        return {
            "success": True,
            "x": x,
            "y": y,
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
        }


def click_at(x, y):
    """
    Click at a screen coordinate.
    """
    try:
        x = int(x)
        y = int(y)

        pyautogui.click(
            x,
            y,
        )

        return {
            "success": True,
            "x": x,
            "y": y,
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
        }


def double_click_at(x, y):
    """
    Double-click at a screen coordinate.
    """
    try:
        x = int(x)
        y = int(y)

        pyautogui.doubleClick(
            x,
            y,
        )

        return {
            "success": True,
            "x": x,
            "y": y,
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
        }


def type_text(text):
    """
    Type text into the currently focused application.
    """
    try:
        text = str(text)

        pyautogui.write(
            text,
            interval=0.03,
        )

        return {
            "success": True,
            "text": text,
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
        }


def press_key(key):
    """
    Press a keyboard key.
    """
    try:
        key = str(key).strip()

        pyautogui.press(key)

        return {
            "success": True,
            "key": key,
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
        }


def scroll(amount):
    """
    Scroll the mouse wheel.
    Positive = up.
    Negative = down.
    """
    try:
        amount = int(amount)

        pyautogui.scroll(amount)

        return {
            "success": True,
            "amount": amount,
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
        }


# ============================================================
# SCREEN VISION
# ============================================================

def _extract_json(text):
    """
    Extract the first JSON object from model output.
    """
    if not text:
        return None

    text = str(text).strip()

    if text.startswith("```"):
        lines = text.splitlines()

        if lines:
            lines = lines[1:]

        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]

        text = "\n".join(lines).strip()

    start = text.find("{")
    end = text.rfind("}")

    if start == -1 or end == -1:
        return None

    try:
        return json.loads(
            text[start:end + 1]
        )

    except json.JSONDecodeError:
        return None


def analyze_screen(question=None):
    """
    Capture the current screen and ask Gemini to understand it.

    This is an observation-only operation.
    It does NOT click, type, move the mouse, or execute actions.
    """

    screenshot = capture_screen()

    if not screenshot.get("success"):
        return {
            "success": False,
            "error": screenshot.get(
                "error",
                "Screen capture failed.",
            ),
        }

    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        return {
            "success": False,
            "error": "GEMINI_API_KEY was not found.",
        }

    question = str(
        question or
        "Describe what is currently visible on the screen."
    ).strip()

    prompt = f"""
You are the NEXUS Screen Vision Engine.

Analyze the supplied computer screenshot.

Screen resolution:
{ screenshot["width"] } x { screenshot["height"] }

User question:
{question}

Return JSON only in this exact general structure:

{{
  "screen_summary": "short description",
  "visible_application": "application or website if identifiable",
  "elements": [
    {{
      "label": "visible text or useful name",
      "type": "button|text|input|icon|link|window|other",
      "x": 0,
      "y": 0,
      "width": 0,
      "height": 0,
      "confidence": 0.0
    }}
  ]
}}

Rules:
- Coordinates are absolute screen pixels.
- x and y are the approximate TOP-LEFT coordinate of the element.
- width and height are approximate pixel dimensions.
- Only report elements that are actually visible.
- Do not invent hidden elements.
- If exact coordinates cannot be determined, use your best visual estimate
  and lower the confidence.
- Keep screen_summary short.
- Maximum 20 elements.
"""

    try:
        client = genai.Client(
            api_key=api_key,
        )

        with open(
            screenshot["file"],
            "rb",
        ) as image_file:
            image_bytes = image_file.read()

        image_part = types.Part.from_bytes(
            data=image_bytes,
            mime_type="image/png",
        )

        response = client.models.generate_content(
            model=VISION_MODEL,
            contents=[
                image_part,
                prompt,
            ],
        )

        response_text = str(
            getattr(response, "text", "") or ""
        ).strip()

        parsed = _extract_json(
            response_text
        )

        if parsed is None:
            return {
                "success": True,
                "screen_summary": response_text,
                "visible_application": "",
                "elements": [],
                "raw_response": response_text,
                "file": screenshot["file"],
            }

        if not isinstance(parsed, dict):
            parsed = {}

        return {
            "success": True,
            "screen_summary": parsed.get(
                "screen_summary",
                "",
            ),
            "visible_application": parsed.get(
                "visible_application",
                "",
            ),
            "elements": parsed.get(
                "elements",
                [],
            ),
            "raw_response": response_text,
            "file": screenshot["file"],
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "file": screenshot["file"],
        }


def find_visual_element(
    analysis,
    label,
):
    """
    Find a visible element by label using simple text matching.

    This function only returns information from the vision result.
    It does not click anything.
    """

    if not analysis or not analysis.get("success"):
        return None

    target = str(label).strip().lower()

    if not target:
        return None

    elements = analysis.get(
        "elements",
        [],
    )

    best = None
    best_score = 0

    for element in elements:

        if not isinstance(element, dict):
            continue

        element_label = str(
            element.get("label", "")
        ).strip().lower()

        if not element_label:
            continue

        score = 0

        if element_label == target:
            score = 100

        elif target in element_label:
            score = 80

        elif element_label in target:
            score = 70

        else:
            target_words = set(
                re.findall(r"\w+", target)
            )

            element_words = set(
                re.findall(r"\w+", element_label)
            )

            overlap = len(
                target_words.intersection(
                    element_words
                )
            )

            if overlap:
                score = 40 + overlap

        if score > best_score:
            best_score = score
            best = element

    return best


# ============================================================
# VISUAL ACTION DISPATCHER
# ============================================================

def visual_action(action, **kwargs):
    """
    Central dispatcher for visual interaction.
    """

    action = str(
        action
    ).strip().lower()

    if action == "screenshot":
        return capture_screen()

    if action == "analyze":
        return analyze_screen(
            kwargs.get("question")
        )

    if action == "screen_size":
        return get_screen_size()

    if action == "mouse_position":
        return get_mouse_position()

    if action == "move":
        return move_to(
            kwargs.get("x"),
            kwargs.get("y"),
        )

    if action == "click":
        return click_at(
            kwargs.get("x"),
            kwargs.get("y"),
        )

    if action == "double_click":
        return double_click_at(
            kwargs.get("x"),
            kwargs.get("y"),
        )

    if action == "type":
        return type_text(
            kwargs.get("text", "")
        )

    if action == "press":
        return press_key(
            kwargs.get("key", "")
        )

    if action == "scroll":
        return scroll(
            kwargs.get("amount", 0)
        )

    return {
        "success": False,
        "error": f"Unknown visual action: {action}",
    }


def visual_status(result):
    """
    Convert a visual result into a readable status.
    """

    if not result:
        return "VISUAL ACTION FAILED"

    if result.get("success"):
        return "VISUAL ACTION SUCCESS"

    return "VISUAL ACTION FAILED"
