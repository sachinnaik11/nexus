# ============================================================
# NEXUS — NEURAL EXECUTION & UNIFIED SYSTEM
# MAIN CORE
# ============================================================

import os
import sys
import threading
import requests
import json
import re
import queue
import time

from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

from dotenv import load_dotenv
from google import genai
from ddgs import DDGS
from PySide6.QtWidgets import QApplication

from ui import NexusUI

from voice.listener import listen
from speaker import speak

from memory.store import (
    get_memory,
    get_recent_conversation,
    add_conversation,
)

from memory.intelligence import (
    save_smart_memory,
    build_memory_context,
    search_memory,
    detect_memory,
    get_fast_memory_answer,
)

from core.router import (
    route_command,
)
from core.brain import (
    analyze_request,
    describe_analysis,
)

from core.capabilities import (
    get_capability,
    execute_capability,
)

from core.intent import (
    detect_intent,
    INTENT_COMMAND,
    INTENT_WEB,
    INTENT_MEMORY,
    INTENT_TIME,
    INTENT_DATE,
    INTENT_EXIT,
    INTENT_MISSION_PAUSE,
    INTENT_MISSION_RESUME,
    INTENT_MISSION_CANCEL,
    INTENT_PERMISSION_APPROVE,
    INTENT_PERMISSION_REJECT,
)

from core.permissions import permission_gate

from core.context import (
    build_context,
    resolve_reference,
)

from core.decision import (
    make_decision,
    describe_decision,
    DECISION_COMMAND,
    DECISION_WEB,
    DECISION_MULTI_STEP,
)
from core.recovery import (
    get_recovery_state,
    recovery_message,
    RECOVERY_SUCCESS,
    RECOVERY_RETRY,
)

from core.planner import (
    create_plan,
    describe_plan,
    mark_step_running,
    mark_step_complete,
    mark_step_failed,
    is_plan_complete,
)

from core.mission import (
    create_mission,
    start_step,
    complete_step,
    fail_step,
    get_progress,
    describe_mission,
    is_complete,
)

from core.mission_control import (
    mission_controller,
)

from core.visual import (
    capture_screen,
    analyze_screen,
    find_visual_element,
    get_screen_size,
    get_mouse_position,
    move_to,
    click_at,
    double_click_at,
    press_key as visual_press_key,
    scroll as visual_scroll,
)


from mission_history import (
    record_mission,
    get_last_mission,
    get_mission_count,
    get_completed_mission_count,
)


# ============================================================
# MISSION HISTORY
# ============================================================

def is_mission_history_request(text):
    command = str(text).strip().lower()
    phrases = (
        "last mission",
        "previous mission",
        "mission history",
        "how many missions",
        "missions completed",
        "completed missions",
        "what was my last mission",
    )
    return any(phrase in command for phrase in phrases)


def build_mission_history_response(text):
    command = str(text).strip().lower()

    if "last mission" in command or "previous mission" in command:
        last = get_last_mission()
        if not last:
            return "I don't have any previous mission history yet."
        return (
            f"Your last mission was: {last.get('goal', 'Unknown')}. "
            f"Status: {last.get('status', 'UNKNOWN')}. "
            f"Progress: {last.get('completed', 0)} of "
            f"{last.get('total', 0)} steps."
        )

    if (
        "how many missions" in command
        or "missions completed" in command
        or "completed missions" in command
    ):
        total = get_mission_count()
        completed = get_completed_mission_count()
        return (
            f"You have {total} recorded mission(s), "
            f"with {completed} completed successfully."
        )

    last = get_last_mission()
    if not last:
        return "I don't have any mission history yet."

    return (
        f"I have {get_mission_count()} recorded mission(s). "
        f"Your latest mission was '{last.get('goal', 'Unknown')}' "
        f"with status {last.get('status', 'UNKNOWN')}."
    )


# ============================================================
# MISSION STATUS DETECTION
# ============================================================

def is_mission_status_request(text):
    command = str(text).strip().lower()

    phrases = (
        "mission status",
        "status of mission",
        "mission progress",
        "how much of the mission",
        "how much is the mission",
        "how much is completed",
        "which step are you on",
        "what step are you on",
        "current mission",
        "mission details",
        "mission progress",
    )

    return any(phrase in command for phrase in phrases)


def build_mission_status_response():
    mission = mission_controller.get_mission()

    if mission is None:
        if active_workflow is not None:
            return describe_workflow(active_workflow)
        return "There is no active mission right now."

    progress = get_progress(mission)
    status = mission_controller.get_status()
    current_step = None

    for step in mission.get("steps", []):
        if step.get("status") in ("PENDING", "RUNNING"):
            current_step = step
            break

    if current_step is not None:
        step_id = current_step.get("id")
        step_status = current_step.get("status", "PENDING")
        decision = current_step.get("decision", {})
        command = decision.get("command")
        target = decision.get("target")

        if command:
            step_description = command
            if target:
                step_description += f" → {target}"
        else:
            step_description = decision.get("type", "UNKNOWN")

        return (
            f"Mission status: {status}. "
            f"Progress: {progress['completed']} of "
            f"{progress['total']} steps completed "
            f"({progress['percentage']}%). "
            f"Current step: {step_id}, {step_status}. "
            f"Task: {step_description}."
        )

    return (
        f"Mission status: {status}. "
        f"Progress: {progress['completed']} of "
        f"{progress['total']} steps completed "
        f"({progress['percentage']}%)."
    )



# ============================================================
# ADAPTIVE RECOVERY ENGINE
# ============================================================

RECOVERY_ACTION_RETRY = "RETRY"
RECOVERY_ACTION_ALTERNATIVE = "ALTERNATIVE"
RECOVERY_ACTION_STOP = "STOP"


def get_failure_reason(result):
    text = str(result or "").lower()

    if "temporarily unavailable" in text:
        return "temporary_unavailable"

    if "timeout" in text or "timed out" in text:
        return "timeout"

    if "couldn't" in text or "could not" in text:
        return "execution_failure"

    if "failed" in text or "error" in text:
        return "execution_failure"

    if "not available" in text:
        return "capability_unavailable"

    return "unknown_failure"


def get_alternative_commands(command_type, target, reason):
    """
    Return safe alternative commands already supported by NEXUS.

    Alternatives are deliberately conservative. They never invent
    arbitrary shell commands or bypass the existing capability layer.
    """

    command = str(command_type or "").upper()
    target = str(target or "").strip()

    alternatives = []

    if command == "OPEN":
        if target.lower() in ("chrome", "google chrome"):
            alternatives = [
                "open google",
                "open website https://www.google.com",
            ]

        elif target.lower() in ("youtube", "youtube.com"):
            alternatives = [
                "open website https://www.youtube.com",
            ]

    elif command == "OPEN_WEBSITE":
        if target:
            alternatives = [
                f"open website {target}"
            ]

    elif command == "WEB_SEARCH":
        if target:
            alternatives = [
                f"search google {target}"
            ]

    elif command == "YOUTUBE_SEARCH":
        if target:
            alternatives = [
                f"search web {target}"
            ]

    return alternatives


def choose_recovery_action(
    command_type,
    target,
    result,
    attempt,
    max_attempts=2
):
    """
    Decide whether to retry, use a safe alternative, or stop.
    """

    reason = get_failure_reason(result)

    if attempt >= max_attempts:
        alternatives = get_alternative_commands(
            command_type,
            target,
            reason
        )

        if alternatives:
            return {
                "action": RECOVERY_ACTION_ALTERNATIVE,
                "reason": reason,
                "alternatives": alternatives,
            }

        return {
            "action": RECOVERY_ACTION_STOP,
            "reason": reason,
            "alternatives": [],
        }

    return {
        "action": RECOVERY_ACTION_RETRY,
        "reason": reason,
        "alternatives": [],
    }


def execute_recovery_alternative(alternative):
    decision = make_decision(alternative)

    if decision.get("type") != DECISION_COMMAND:
        return None, None

    result = execute_single_decision(
        decision
    )

    return decision, result


# ============================================================
# BROWSER AUTOMATION ENGINE
# ============================================================

def browser_open_url(url):
    """
    Open a URL using the existing PC capability layer.
    """

    from core.pc import open_website

    return open_website(url)


def browser_search_web(query):
    """
    Search the web using the existing NEXUS browser capability.
    """

    from core.pc import web_search

    return web_search(query)


def browser_search_youtube(query):
    """
    Search YouTube using the existing NEXUS browser capability.
    """

    from core.pc import youtube_search

    return youtube_search(query)


def browser_type(text):
    """
    Type into the currently focused browser field.
    """

    from core.pc import type_text

    return type_text(text)


def browser_click():
    """
    Click the current mouse position.
    """

    from core.pc import mouse_click

    return mouse_click()


def browser_screenshot():
    """
    Capture the current browser/desktop state.
    """

    from core.pc import take_screenshot

    return take_screenshot()


def browser_execute(action, value=None):
    """
    Unified browser action dispatcher.

    Supported:
    - open
    - search
    - youtube_search
    - type
    - click
    - screenshot
    """

    action = str(action).strip().lower()

    if action == "open":
        return browser_open_url(value)

    if action == "search":
        return browser_search_web(value)

    if action == "youtube_search":
        return browser_search_youtube(value)

    if action == "type":
        return browser_type(value)

    if action == "click":
        return browser_click()

    if action == "screenshot":
        return browser_screenshot()

    return "Browser action not available."


def verify_browser_result(result):
    """
    Conservative browser verification based on the result returned
    by the existing PC capability.
    """

    if not result:
        return False

    text = str(result).lower()

    failure_phrases = (
        "failed",
        "error",
        "couldn't",
        "could not",
        "not available",
        "unable",
    )

    if any(
        phrase in text
        for phrase in failure_phrases
    ):
        return False

    success_phrases = (
        "opened",
        "searching",
        "typed",
        "clicked",
        "screenshot saved",
    )

    return any(
        phrase in text
        for phrase in success_phrases
    )


# ============================================================
# VERIFICATION ENGINE
# ============================================================

VERIFICATION_SUCCESS = "VERIFIED"
VERIFICATION_FAILED = "FAILED"
VERIFICATION_UNKNOWN = "UNKNOWN"


def verify_command_result(
    command_type,
    target,
    result
):
    """
    Verify the result reported by a local NEXUS capability.

    This is intentionally conservative:
    - Explicit failure text is never treated as success.
    - Explicit success text is accepted.
    - Unknown results are marked UNKNOWN rather than falsely
      claiming that the action succeeded.
    """

    if result is None:
        return {
            "status": VERIFICATION_FAILED,
            "verified": False,
            "reason": "No result was returned.",
        }

    if isinstance(result, dict):
        result_text = str(result.get("spoken") or result.get("display") or result).strip()
    else:
        result_text = str(result).strip()
    lower = result_text.lower()

    failure_phrases = (
        "failed",
        "error",
        "couldn't",
        "could not",
        "cannot",
        "unable",
        "not available",
        "don't know how",
        "unknown",
        "temporarily unavailable",
    )

    if any(
        phrase in lower
        for phrase in failure_phrases
    ):
        return {
            "status": VERIFICATION_FAILED,
            "verified": False,
            "reason": result_text,
        }

    success_phrases = (
        "opened",
        "searching",
        "typed",
        "clicked",
        "moved",
        "increased",
        "decreased",
        "muted",
        "screenshot saved",
        "saved",
        "diagnostic",
        "diagnostics",
        "hardware",
        "optimal",
        "nominal",
        "complete",
        "telemetry",
        "workspace setup complete",
        "storyboard",
        "screen vision",
        "observing",
    )

    if any(
        phrase in lower
        for phrase in success_phrases
    ):
        return {
            "status": VERIFICATION_SUCCESS,
            "verified": True,
            "reason": result_text,
        }

    return {
        "status": VERIFICATION_UNKNOWN,
        "verified": False,
        "reason": (
            "The command returned a result, but "
            "NEXUS could not confidently verify success."
        ),
    }


def should_accept_result(
    command_type,
    target,
    result
):
    verification = verify_command_result(
        command_type,
        target,
        result
    )

    return verification["verified"]


def describe_verification(verification):
    if not verification:
        return "VERIFICATION → UNKNOWN"

    status = verification.get(
        "status",
        VERIFICATION_UNKNOWN
    )

    reason = verification.get(
        "reason",
        ""
    )

    if reason:
        return f"VERIFICATION → {status} → {reason}"

    return f"VERIFICATION → {status}"


# ============================================================
# GOAL DECOMPOSITION ENGINE
# ============================================================

DECOMPOSER_SYSTEM_PROMPT = """
You are the NEXUS Goal Decomposer.

Convert a user's natural-language goal into a short ordered list
of executable NEXUS commands.

ONLY use commands from this allowed list:
- open <app or website>
- open website <url>
- search youtube <query>
- search web <query>
- type <text>
- type in notepad <text>
- volume up
- volume down
- mute
- take screenshot
- click
- move mouse
- open whatsapp
- sleep

Rules:
- Return JSON only.
- Format:
  {"steps": ["command 1", "command 2"]}
- Maximum 6 steps.
- Keep the original user intent.
- Do not invent credentials, passwords, private information,
  purchases, messages, calls, or destructive actions.
- Do not include explanations.
- If the goal cannot be safely converted to supported commands,
  return {"steps": []}.
"""


def _extract_json_object(text):
    text = str(text).strip()

    if text.startswith("```"):
        lines = text.splitlines()

        if lines and lines[0].startswith("```"):
            lines = lines[1:]

        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]

        text = "\n".join(lines).strip()

    start = text.find("{")
    end = text.rfind("}")

    if start == -1 or end == -1 or end <= start:
        return None

    try:
        return json.loads(text[start:end + 1])
    except json.JSONDecodeError:
        return None


def _validate_decomposed_step(step):
    if not isinstance(step, str):
        return None

    step = step.strip()

    if not step:
        return None

    # Route the proposed step through NEXUS's existing command system.
    decision = make_decision(step)

    if decision.get("type") != DECISION_COMMAND:
        return None

    if not get_capability(
        decision.get("command")
    ):
        return None

    return step


def decompose_goal(goal):
    """
    Turn a broad goal into safe, locally executable NEXUS commands.

    Returns:
        list[str]: validated command steps.
    """

    goal = str(goal).strip()

    if not goal:
        return []

    # First try the existing deterministic planner.
    existing_plan = create_plan(goal)

    if (
        len(existing_plan.get("steps", [])) > 1
        and all(
            step.get("decision", {}).get("type") == DECISION_COMMAND
            for step in existing_plan.get("steps", [])
        )
    ):
        return [
            _decision_to_command(step.get("decision", {}))
            for step in existing_plan.get("steps", [])
        ]

    prompt = f"""
{DECOMPOSER_SYSTEM_PROMPT}

USER GOAL:
{goal}
"""

    try:
        response = gemini_ai(prompt)
        data = _extract_json_object(response)

        if not isinstance(data, dict):
            return []

        raw_steps = data.get("steps", [])

        if not isinstance(raw_steps, list):
            return []

        if len(raw_steps) > 6:
            raw_steps = raw_steps[:6]

        validated = []

        for step in raw_steps:
            safe_step = _validate_decomposed_step(step)

            if safe_step:
                validated.append(safe_step)

        return validated

    except Exception as e:
        print(
            f"NEXUS GOAL DECOMPOSER ERROR: {e}"
        )
        return []


def _decision_to_command(decision):
    command = decision.get("command")
    target = decision.get("target")

    if not command:
        return ""

    if target:
        return f"{command.lower().replace('_', ' ')} {target}"

    return command.lower().replace("_", " ")


def create_goal_plan(goal):
    steps = decompose_goal(goal)

    if not steps:
        return None

    decisions = []

    for step in steps:
        decision = make_decision(step)

        if decision.get("type") != DECISION_COMMAND:
            return None

        decisions.append(decision)

    return {
        "goal": goal,
        "steps": decisions,
    }


# ============================================================
# WORKFLOW ENGINE
# ============================================================

WORKFLOW_READY = "READY"
WORKFLOW_RUNNING = "RUNNING"
WORKFLOW_COMPLETED = "COMPLETED"
WORKFLOW_FAILED = "FAILED"
WORKFLOW_CANCELLED = "CANCELLED"


def create_workflow(goal, plan):
    return {
        "goal": str(goal),
        "status": WORKFLOW_READY,
        "steps": plan.get("steps", []) if plan else [],
        "current_step": None,
        "results": [],
        "errors": [],
    }


def start_workflow(workflow):
    workflow["status"] = WORKFLOW_RUNNING
    return workflow


def set_current_step(workflow, step_id):
    workflow["current_step"] = step_id
    return workflow


def add_result(workflow, step_id, result):
    workflow.setdefault("results", []).append({
        "step_id": step_id,
        "result": result,
    })


def add_error(workflow, step_id, error):
    workflow.setdefault("errors", []).append({
        "step_id": step_id,
        "error": error,
    })


def complete_workflow(workflow):
    workflow["status"] = WORKFLOW_COMPLETED
    workflow["current_step"] = None
    return workflow


def fail_workflow(workflow, reason=None):
    workflow["status"] = WORKFLOW_FAILED
    workflow["current_step"] = None

    if reason:
        workflow.setdefault("errors", []).append({
            "step_id": None,
            "error": reason,
        })

    return workflow


def cancel_workflow(workflow):
    workflow["status"] = WORKFLOW_CANCELLED
    workflow["current_step"] = None
    return workflow


def get_workflow_progress(workflow):
    steps = workflow.get("steps", [])
    total = len(steps)

    completed = sum(
        1
        for step in steps
        if step.get("status") == "COMPLETE"
    )

    percentage = int(
        (completed / total) * 100
    ) if total else 0

    return {
        "completed": completed,
        "total": total,
        "percentage": percentage,
    }


def describe_workflow(workflow):
    if not workflow:
        return "No active workflow."

    progress = get_workflow_progress(workflow)

    lines = [
        f"WORKFLOW: {workflow.get('goal', 'Unknown')}",
        f"STATUS: {workflow.get('status', WORKFLOW_READY)}",
        (
            f"PROGRESS: {progress['completed']}/"
            f"{progress['total']} "
            f"({progress['percentage']}%)"
        ),
    ]

    current = workflow.get("current_step")

    if current is not None:
        lines.append(
            f"CURRENT STEP: {current}"
        )

    return "\n".join(lines)


# ============================================================
# VISUAL INTERACTION ENGINE
# ============================================================

def is_visual_request(text):
    command = str(text).strip().lower()

    wake_words = (
        "hey nexus ",
        "ok nexus ",
        "nexus ",
    )

    for wake_word in wake_words:
        if command.startswith(wake_word):
            command = command[len(wake_word):].strip()
            break

    phrases = (
        "visual mode",
        "visual interaction",
        "see my screen",
        "look at my screen",
        "check my screen",
        "what is on my screen",
        "what's on my screen",
        "what do you see on my screen",
        "analyze my screen",
        "analyse my screen",
        "screen info",
        "screen size",
        "mouse position",
        "where is my mouse",
        "move mouse to",
        "click at",
        "double click at",
        "press key",
        "scroll up",
        "scroll down",
        "find on my screen",
        "find the ",
    )

    return any(
        phrase in command
        for phrase in phrases
    )


def handle_visual_request(text):
    """
    Visual control and screen-vision handler.

    Observation requests are sent to Gemini Vision.
    Direct coordinate actions remain local and deterministic.
    """

    command = str(text).strip().lower()

    wake_words = (
        "hey nexus ",
        "ok nexus ",
        "nexus ",
    )

    for wake_word in wake_words:
        if command.startswith(wake_word):
            command = command[len(wake_word):].strip()
            break

    # ---------------------------------------------------------
    # SCREEN VISION
    # ---------------------------------------------------------

    vision_prefixes = (
        "what is on my screen",
        "what's on my screen",
        "what do you see on my screen",
        "analyze my screen",
        "analyse my screen",
        "see my screen",
        "look at my screen",
        "check my screen",
    )

    if command in vision_prefixes:
        result = analyze_screen(
            "Describe the current screen, identify the main "
            "application or website, and list the most important "
            "visible UI elements."
        )

        if not result.get("success"):
            return (
                "I couldn't analyze the screen. "
                + str(result.get("error", "Unknown vision error."))
            )

        summary = result.get(
            "screen_summary",
            "I can see the screen, but I couldn't summarize it."
        )

        application = result.get(
            "visible_application",
            ""
        )

        if application:
            return (
                f"I can see {application}. "
                f"{summary}"
            )

        return summary

    # ---------------------------------------------------------
    # FIND A VISIBLE ELEMENT
    # ---------------------------------------------------------

    if command.startswith("find on my screen "):
        target = command[len("find on my screen "):].strip()

        if not target:
            return "Tell me what you want me to find on the screen."

        result = analyze_screen(
            f"Find the visible screen element matching: {target}. "
            "Return its approximate coordinates and confidence."
        )

        if not result.get("success"):
            return (
                "I couldn't analyze the screen. "
                + str(result.get("error", "Unknown vision error."))
            )

        element = find_visual_element(
            result,
            target,
        )

        if element:
            confidence = element.get(
                "confidence",
                0
            )

            return (
                f"I found {element.get('label', target)} "
                f"at approximately X {element.get('x', 0)}, "
                f"Y {element.get('y', 0)} "
                f"with {int(float(confidence) * 100)}% confidence."
            )

        return f"I couldn't confidently find {target} on the screen."

    # ---------------------------------------------------------
    # SCREEN CAPTURE
    # ---------------------------------------------------------

    if command in (
        "visual mode",
        "visual interaction",
    ):
        result = capture_screen()

        if result.get("success"):
            return (
                f"Screen captured. Resolution is "
                f"{result['width']} by {result['height']}."
            )

        return "I couldn't capture the screen."

    if command in ("screen info", "screen size"):
        result = get_screen_size()

        if result.get("success"):
            return (
                f"Screen resolution is "
                f"{result['width']} by {result['height']}."
            )

        return "I couldn't read the screen size."

    if command in (
        "mouse position",
        "where is my mouse",
    ):
        result = get_mouse_position()

        if result.get("success"):
            return (
                f"The mouse is at "
                f"X {result['x']}, Y {result['y']}."
            )

        return "I couldn't read the mouse position."

    match = re.search(
        r"move mouse to\s+(\d+)\s*[,\s]\s*(\d+)",
        command,
    )

    if match:
        result = move_to(
            int(match.group(1)),
            int(match.group(2)),
        )

        return (
            "Mouse moved successfully."
            if result.get("success")
            else "I couldn't move the mouse."
        )

    match = re.search(
        r"click at\s+(\d+)\s*[,\s]\s*(\d+)",
        command,
    )

    if match:
        result = click_at(
            int(match.group(1)),
            int(match.group(2)),
        )

        return (
            "Clicked successfully."
            if result.get("success")
            else "I couldn't click at that position."
        )

    match = re.search(
        r"double click at\s+(\d+)\s*[,\s]\s*(\d+)",
        command,
    )

    if match:
        result = double_click_at(
            int(match.group(1)),
            int(match.group(2)),
        )

        return (
            "Double-clicked successfully."
            if result.get("success")
            else "I couldn't double-click at that position."
        )

    match = re.search(
        r"press key\s+(.+)$",
        command,
    )

    if match:
        key = match.group(1).strip()
        result = visual_press_key(key)

        return (
            f"Pressed {key}."
            if result.get("success")
            else f"I couldn't press {key}."
        )

    if command == "scroll up":
        result = visual_scroll(5)

        return (
            "Scrolled up."
            if result.get("success")
            else "I couldn't scroll up."
        )

    if command == "scroll down":
        result = visual_scroll(-5)

        return (
            "Scrolled down."
            if result.get("success")
            else "I couldn't scroll down."
        )

    return None


# ============================================================
# ENVIRONMENT
# ============================================================

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")
client = None

if API_KEY:
    try:
        client = genai.Client(
            api_key=API_KEY
        )
    except Exception as e:
        print(f"NEXUS WARNING: Could not initialize Gemini client: {e}")
        client = None
else:
    print(
        "NEXUS WARNING: GEMINI_API_KEY not found in .env (running in local fallback mode)"
    )


# ============================================================
# GEMINI
# ============================================================

def gemini_ai(prompt):

    if not client:
        raise RuntimeError("Gemini client is not configured or available.")

    chat = client.chats.create(
        model="gemini-3.5-flash-lite"
    )

    response = chat.send_message(prompt)

    return response.text


# ============================================================
# LOCAL AI — QWEN
# ============================================================

def local_ai(query):

    response = requests.post(
        "http://localhost:11434/api/generate",
        json={
            "model": "qwen3:8b",
            "prompt": query,
            "stream": False,
            "think": False,
            "options": {
                "num_predict": 80
            },
        },
        timeout=120,
    )

    response.raise_for_status()

    return response.json()["response"]


# ============================================================
# RUN QWEN + GEMINI
# ============================================================

def run_both_ai(prompt):

    executor = ThreadPoolExecutor(
        max_workers=2
    )

    tasks = {
        executor.submit(
            local_ai,
            prompt
        ): "qwen",
    }

    if client:
        tasks[
            executor.submit(
                gemini_ai,
                prompt
            )
        ] = "gemini"

    for task in as_completed(tasks):

        try:

            answer = task.result()

            if answer and answer.strip():

                executor.shutdown(
                    wait=False,
                    cancel_futures=True
                )

                return answer.strip()

        except Exception as e:

            print(
                f"NEXUS AI BACKEND ERROR: {e}"
            )

            continue

    executor.shutdown(
        wait=False,
        cancel_futures=True
    )

    return (
        "The AI systems are temporarily unavailable."
    )


# ============================================================
# LIVE WEB SEARCH
# ============================================================

def live_web_search(query):

    results = DDGS(timeout=15).text(
        query,
        max_results=8,
        backend="bing",
    )

    text = ""

    for result in results:

        text += (
            f"{result.get('title', '')}: "
            f"{result.get('body', '')}\n"
            f"SOURCE: {result.get('href', '')}\n"
        )

    return text


# ============================================================
# LIVE SEARCH DETECTION
# ============================================================

def needs_live_search(query):

    keywords = [
        "latest",
        "today",
        "current",
        "now",
        "news",
        "update",
        "weather",
        "price",
        "recent",
        "live",
    ]

    query_lower = query.lower()

    return any(
        word in query_lower
        for word in keywords
    )


# ============================================================
# MEMORY RECALL DETECTION
# ============================================================

def is_memory_recall_request(text):
    """Return True only when the user is clearly asking about memory."""
    command = str(text or "").strip().lower()

    phrases = (
        "do you remember",
        "what do you remember",
        "what did i tell you",
        "did i tell you",
        "what is my favorite",
        "what's my favorite",
        "what is my favourite",
        "what's my favourite",
        "what is my name",
        "what's my name",
        "what do you know about me",
        "remember anything about me",
    )

    return any(phrase in command for phrase in phrases)


# ============================================================
# NEXUS SYSTEM PROMPT
# ============================================================

SYSTEM_PROMPT = """
You are NEXUS — Neural Execution & Unified System.

You are a personal AI assistant.

CORE BEHAVIOR:
- Be direct, helpful and concise.
- Understand natural language.
- Understand mixed languages and code-switching.
- The user may communicate in English, Hindi, Kannada, Tamil,
  or combinations of them.
- Understand transliterated Indian languages written in English.
- Do not require grammatically perfect English.

LANGUAGE:
- Detect the language used by the user.
- If the user explicitly asks for a language, answer in that language.
- If the user uses mixed languages, understand the complete meaning.
- If no language is requested, reply in English.
- Do not translate unless asked.
- When teaching, use simple explanations and examples.

COMMANDS:
- Computer actions are handled by the local NEXUS capability system.
- Browser actions use the existing local PC/browser capabilities.
- Never claim that a browser action succeeded unless the local
  capability returned a successful result.
- Never claim an action was performed unless the local system
  actually performed it.
- For normal conversation, answer naturally.

LIVE INFORMATION:
- When LIVE WEB RESULTS are provided, use them.
- Do not invent current information when reliable live information
  is unavailable.

MEMORY:
- Use relevant permanent memory.
- Use recent conversation when useful.
- Do not invent memories.

CONTEXT:
- Understand follow-up references such as:
  "it"
  "this"
  "that"
  "the previous one"
  "the last one"
- Use recent conversation to resolve them when the meaning is clear.
- If genuinely ambiguous, ask a short clarification.

VISUAL INTERACTION:
- NEXUS has a local visual interaction and screen-vision engine.
- It can capture the screen, analyze visible UI with Gemini Vision,
  identify visible applications/elements, estimate coordinates,
  read screen resolution and mouse position, move the mouse,
  click coordinates, double-click, press keys, and scroll.
- Never claim visual understanding unless the vision engine actually
  returned a successful analysis.
- Report screen and input actions only after the local visual
  engine returns success.

AUTONOMOUS WORKFLOWS:
- A workflow is a goal represented by executable steps.
- Track each step, result, error, and overall progress.
- Recover from temporary failures when possible.
- Never claim success unless the local system reports success.
- Ask for clarification when a goal cannot be safely decomposed.

MULTI-STEP TASKS:
- When previous steps are provided in the conversation,
  understand the relationship between them.
- Do not claim a step was completed unless the local system
  actually completed it.

Examples:
"YouTube open karo"
"YouTube kholo"
"YouTube open maadu"
"YouTube open pannu"
"Nexus explain this in Kannada"
"Mujhe Python sikhao"
"Tamil la explain pannu"
"""


# ============================================================
# MEMORY
# ============================================================

memory = get_memory()

active_workflow = None


# ============================================================
# UI
# ============================================================

app = QApplication(sys.argv)

window = NexusUI()

window.show()


# ============================================================
# SPEAK RESULT
# ============================================================

speak_lock = threading.Lock()


def respond(result):

    if not result:

        return

    display_text = ""
    spoken_text = ""

    if isinstance(result, dict):
        display_text = str(result.get("display") or result.get("spoken") or result)
        spoken_text = str(result.get("spoken") or result.get("display") or result)
    else:
        display_text = str(result)
        spoken_text = str(result)

    print(
        f"NEXUS: {spoken_text}"
    )

    window.response_signal.emit(
        display_text
    )

    try:

        with speak_lock:
            speak(spoken_text)

    except Exception as e:

        print(
            f"NEXUS VOICE ERROR: {e}"
        )


# ============================================================
# EXECUTE SINGLE COMMAND
# ============================================================

def execute_single_decision(
    decision,
    step_number=None
):

    if decision.get("type") == DECISION_WEB:
        query = decision.get("target") or ""
        if not query:
            return None
        return live_web_search(query)

    if decision.get("type") != DECISION_COMMAND:
        return None


    exact_command = decision.get(
        "command"
    )

    target = decision.get(
        "target"
    )


    print(
        f"NEXUS COMMAND: {exact_command}"
    )

    print(
        f"NEXUS TARGET: {target}"
    )


    capability = get_capability(
        exact_command
    )


    print(
        f"NEXUS CAPABILITY: {capability}"
    )


    if not capability:

        print(
            "NEXUS: Capability not available."
        )

        return None


    if step_number is not None:

        window.activity_signal.emit(
            f"EXECUTING STEP {step_number}"
        )

    else:

        window.activity_signal.emit(
            f"EXECUTING {capability}"
        )


    try:

        result = execute_capability(
            exact_command,
            target
        )

        return result

    except Exception as e:

        print(
            f"NEXUS CAPABILITY ERROR: {e}"
        )

        return (
            "I couldn't complete that command."
        )


# ============================================================
# BACKGROUND MISSION WORKER
# ============================================================

def run_mission_worker(plan, mission):
    print("NEXUS DEBUG: MISSION WORKER STARTED", flush=True)

    global active_workflow

    all_results = []

    active_workflow = create_workflow(
        mission.get("goal", "Unknown mission"),
        plan
    )

    start_workflow(active_workflow)

    print("NEXUS WORKFLOW:")
    print(describe_workflow(active_workflow))

    try:

        steps = plan.get("steps", [])

        print(
            f"NEXUS: Mission contains {len(steps)} steps."
        )

        for step in steps:

            step_id = step.get("id")
            decision = step.get("decision", {})

            # ---------------------------------------------
            # PAUSE / CANCEL CHECK BEFORE EACH STEP
            # ---------------------------------------------

            if not mission_controller.wait_if_paused():

                print(
                    "NEXUS: Mission cancelled before step execution."
                )

                for pending_step in steps:
                    if pending_step.get("status") in ("PENDING", "RUNNING"):
                        pending_id = pending_step.get("id")
                        mark_step_failed(
                            plan,
                            pending_id,
                            "Mission cancelled by user."
                        )
                        fail_step(
                            mission,
                            pending_id,
                            "Mission cancelled by user."
                        )

                break

            if mission_controller.is_cancelled():

                print(
                    "NEXUS: Mission cancellation detected."
                )

                for pending_step in steps:
                    if pending_step.get("status") in ("PENDING", "RUNNING"):
                        pending_id = pending_step.get("id")
                        mark_step_failed(
                            plan,
                            pending_id,
                            "Mission cancelled by user."
                        )
                        fail_step(
                            mission,
                            pending_id,
                            "Mission cancelled by user."
                        )

                break

            set_current_step(
                active_workflow,
                step_id
            )

            print(
                f"NEXUS STEP {step_id}: "
                f"{describe_decision(decision)}"
            )

            if decision.get("type") != DECISION_COMMAND:

                mark_step_failed(
                    plan,
                    step_id,
                    "Not an executable command."
                )

                fail_step(
                    mission,
                    step_id,
                    "Not an executable command."
                )

                window.activity_signal.emit(
                    f"STEP {step_id} FAILED"
                )

                continue

            mark_step_running(
                plan,
                step_id
            )

            start_step(
                mission,
                step_id
            )

            progress = get_progress(mission)

            print(
                f"NEXUS MISSION PROGRESS: "
                f"{progress['completed']}/"
                f"{progress['total']} "
                f"({progress['percentage']}%)"
            )

            max_attempts = 2
            attempt = 1
            step_completed = False

            while attempt <= max_attempts:

                # -----------------------------------------
                # WAIT HERE IF USER PAUSED THE MISSION
                # -----------------------------------------
                

                if not mission_controller.wait_if_paused():


                    print(
                        f"NEXUS: Mission cancelled during step {step_id}."
                    )

                    mark_step_failed(
                        plan,
                        step_id,
                        "Mission cancelled by user."
                    )

                    fail_step(
                        mission,
                        step_id,
                        "Mission cancelled by user."
                    )

                    break
                

                if mission_controller.is_cancelled():

                    print(
                        f"NEXUS: Mission cancelled during step {step_id}."
                    )

                    mark_step_failed(
                        plan,
                        step_id,
                        "Mission cancelled by user."
                    )

                    fail_step(
                        mission,
                        step_id,
                        "Mission cancelled by user."
                    )

                    break
                print(f"NEXUS: ABOUT TO EXECUTE STEP {step_id}")
                result = execute_single_decision(
                    decision,
                    step_number=step_id
                )

                if result is None:
                    result = "I couldn't execute that command."

                print(
                    f"NEXUS STEP {step_id} "
                    f"ATTEMPT {attempt}: {result}"
                )

                state = get_recovery_state(
                    result,
                    attempt=attempt,
                    max_attempts=max_attempts
                )

                if state == RECOVERY_SUCCESS:

                    verification = verify_command_result(
                        decision.get("command"),
                        decision.get("target"),
                        result
                    )

                    print(
                        "NEXUS VERIFICATION: "
                        + describe_verification(
                            verification
                        )
                    )

                    if not verification["verified"]:

                        window.activity_signal.emit(
                            f"VERIFYING STEP {step_id}"
                        )

                        # An unverified result is treated as a
                        # recoverable failure on the first attempt.
                        if attempt < max_attempts:

                            print(
                                f"NEXUS: Step {step_id} "
                                "was not verified. Retrying."
                            )

                            window.activity_signal.emit(
                                f"VERIFY RETRY STEP {step_id}"
                            )

                            attempt += 1
                            continue

                        mark_step_failed(
                            plan,
                            step_id,
                            verification["reason"]
                        )

                        fail_step(
                            mission,
                            step_id,
                            verification["reason"]
                        )

                        add_error(
                            active_workflow,
                            step_id,
                            verification["reason"]
                        )

                        window.activity_signal.emit(
                            f"STEP {step_id} VERIFICATION FAILED"
                        )

                        break

                    mark_step_complete(
                        plan,
                        step_id,
                        result
                    )

                    complete_step(
                        mission,
                        step_id,
                        result
                    )

                    progress = get_progress(mission)

                    print(
                        f"NEXUS MISSION PROGRESS: "
                        f"{progress['completed']}/"
                        f"{progress['total']} "
                        f"({progress['percentage']}%)"
                    )

                    all_results.append(result)

                    add_result(
                        active_workflow,
                        step_id,
                        result
                    )

                    step_completed = True

                    print(
                        f"NEXUS STEP {step_id}: COMPLETE"
                    )

                    break

                if state == RECOVERY_RETRY:

                    recovery_text = recovery_message(
                        result,
                        attempt=attempt,
                        max_attempts=max_attempts
                    )

                    recovery_plan = choose_recovery_action(
                        decision.get("command"),
                        decision.get("target"),
                        result,
                        attempt,
                        max_attempts
                    )

                    print(
                        f"NEXUS RECOVERY: {recovery_text}"
                    )

                    print(
                        f"NEXUS ADAPTIVE RECOVERY: "
                        f"{recovery_plan['action']} "
                        f"({recovery_plan['reason']})"
                    )

                    window.activity_signal.emit(
                        f"RECOVERING STEP {step_id}"
                    )

                    if (
                        recovery_plan["action"]
                        == RECOVERY_ACTION_ALTERNATIVE
                    ):

                        recovered = False

                        for alternative in recovery_plan[
                            "alternatives"
                        ]:

                            print(
                                f"NEXUS ALTERNATIVE: "
                                f"{alternative}"
                            )

                            window.activity_signal.emit(
                                f"TRYING ALTERNATIVE STEP {step_id}"
                            )

                            alternative_decision, alternative_result = (
                                execute_recovery_alternative(
                                    alternative
                                )
                            )

                            if alternative_result is None:
                                continue

                            print(
                                f"NEXUS ALTERNATIVE RESULT: "
                                f"{alternative_result}"
                            )

                            if alternative_decision is None:
                                continue

                            alternative_verification = (
                                verify_command_result(
                                    alternative_decision.get(
                                        "command"
                                    ),
                                    alternative_decision.get(
                                        "target"
                                    ),
                                    alternative_result
                                )
                            )

                            print(
                                "NEXUS ALTERNATIVE VERIFICATION: "
                                + describe_verification(
                                    alternative_verification
                                )
                            )

                            if alternative_verification["verified"]:

                                mark_step_complete(
                                    plan,
                                    step_id,
                                    alternative_result
                                )

                                complete_step(
                                    mission,
                                    step_id,
                                    alternative_result
                                )

                                add_result(
                                    active_workflow,
                                    step_id,
                                    alternative_result
                                )

                                all_results.append(
                                    alternative_result
                                )

                                progress = get_progress(
                                    mission
                                )

                                print(
                                    f"NEXUS MISSION PROGRESS: "
                                    f"{progress['completed']}/"
                                    f"{progress['total']} "
                                    f"({progress['percentage']}%)"
                                )

                                step_completed = True
                                recovered = True

                                print(
                                    f"NEXUS STEP {step_id}: "
                                    "RECOVERED"
                                )

                                break

                        if recovered:
                            break

                    attempt += 1

                    # If the user pauses while recovery is happening,
                    # the next loop iteration will wait.
                    continue

                mark_step_failed(
                    plan,
                    step_id,
                    result
                )

                fail_step(
                    mission,
                    step_id,
                    result
                )

                add_error(
                    active_workflow,
                    step_id,
                    result
                )

                progress = get_progress(mission)

                print(
                    f"NEXUS MISSION PROGRESS: "
                    f"{progress['completed']}/"
                    f"{progress['total']} "
                    f"({progress['percentage']}%)"
                )

                window.activity_signal.emit(
                    f"STEP {step_id} FAILED"
                )

                break

            if mission_controller.is_cancelled():

                print(
                    "NEXUS: Stopping mission because the user cancelled it."
                )

                for pending_step in steps:
                    if pending_step.get("status") in ("PENDING", "RUNNING"):
                        pending_id = pending_step.get("id")
                        mark_step_failed(
                            plan,
                            pending_id,
                            "Mission cancelled by user."
                        )
                        fail_step(
                            mission,
                            pending_id,
                            "Mission cancelled by user."
                        )

                break

            if not step_completed:

                print(
                    f"NEXUS: Step {step_id} failed. "
                    "Continuing mission."
                )

                window.activity_signal.emit(
                    f"STEP {step_id} FAILED - CONTINUING"
                )

        print("NEXUS FINAL PLAN:")
        print(describe_plan(plan))

        print("NEXUS FINAL MISSION:")
        print(describe_mission(mission))

        if mission_controller.is_cancelled():

            final_result = "Mission cancelled by user."

            window.activity_signal.emit(
                "MISSION CANCELLED"
            )

        elif is_complete(mission):

            final_result = (
                "Mission completed successfully. "
                + " ".join(all_results)
            )

            window.activity_signal.emit(
                "MISSION COMPLETE"
            )

        elif is_plan_complete(plan):

            final_result = (
                "Mission completed successfully. "
                + " ".join(all_results)
            )

            window.activity_signal.emit(
                "MISSION COMPLETE"
            )

        elif all_results:

            final_result = (
                "Mission partially completed. "
                + " ".join(all_results)
            )

            window.activity_signal.emit(
                "MISSION PARTIALLY COMPLETE"
            )

        else:

            final_result = (
                "I couldn't complete the mission."
            )

            window.activity_signal.emit(
                "MISSION FAILED"
            )

        if mission_controller.is_cancelled():

            cancel_workflow(
                active_workflow
            )

        elif is_complete(mission) or is_plan_complete(plan):

            complete_workflow(
                active_workflow
            )

        elif all_results:

            fail_workflow(
                active_workflow,
                "Mission completed only partially."
            )

        else:

            fail_workflow(
                active_workflow,
                "No mission steps completed."
            )

        print("NEXUS FINAL WORKFLOW:")
        print(describe_workflow(active_workflow))

        history_steps = []

        for saved_step in plan.get("steps", []):
            history_steps.append({
                "id": saved_step.get("id"),
                "status": saved_step.get("status"),
                "result": saved_step.get("result"),
            })

        record_mission(
            goal=mission.get("goal", "Unknown mission"),
            status=mission.get("status", "UNKNOWN"),
            progress=get_progress(mission),
            steps=history_steps,
        )

        window.activity_signal.emit(
            "MISSION HISTORY SAVED"
        )

        window.activity_signal.emit(
            "RESPONSE READY"
        )

        respond(final_result)

    except Exception as e:

        print(
            f"NEXUS MISSION WORKER ERROR: {e}"
        )

        window.activity_signal.emit(
            "MISSION ERROR"
        )

        respond(
            "The mission encountered an error, but I am still listening."
        )

    finally:

        mission_controller.finish()


# ============================================================
# DUAL INPUT QUEUE (VOICE & TEXT CHAT)
# ============================================================

input_queue = queue.Queue()
mic_listening_enabled = True


def handle_text_input(text):
    if text and str(text).strip():
        input_queue.put(str(text).strip())


def handle_mic_toggle(is_active):
    global mic_listening_enabled
    mic_listening_enabled = bool(is_active)
    print(f"NEXUS MICROPHONE: {'ACTIVE' if is_active else 'MUTED'}")


def voice_listener_worker():
    while True:
        if not mic_listening_enabled:
            time.sleep(0.3)
            continue

        try:
            window.listening_signal.emit()
            user_input = listen()

            if user_input and user_input.strip():
                input_queue.put(user_input.strip())

        except Exception as e:
            time.sleep(0.5)


window.text_input_signal.connect(handle_text_input)
window.mic_toggle_signal.connect(handle_mic_toggle)

mic_thread = threading.Thread(
    target=voice_listener_worker,
    daemon=True,
)
mic_thread.start()


def background_cloud_sync_worker():
    """Sync state from 24/7 cloud node when desktop starts."""
    try:
        from cloud.sync_client import cloud_sync
        res = cloud_sync.sync()
        if res.get("success") and res.get("imported_count", 0) > 0:
            window.activity_signal.emit(f"CLOUD SYNC: {res['imported_count']} DRAFTS IMPORTED")
    except Exception:
        pass


cloud_sync_thread = threading.Thread(
    target=background_cloud_sync_worker,
    daemon=True,
    name="NexusCloudSyncWorker",
)
cloud_sync_thread.start()


# ============================================================
# VOICE & REQUEST LOOP
# ============================================================

def voice_loop():

    global memory

    while True:

        try:

            # ------------------------------------------------
            # GET NEXT REQUEST (FROM VOICE OR TEXT)
            # ------------------------------------------------

            user_input = input_queue.get()

            if not user_input:

                continue


            user_input = user_input.strip()

            # ============================================================
            # NEXUS BRAIN ANALYSIS
            # ============================================================

            brain_analysis = analyze_request(user_input)

            print("NEXUS BRAIN:")
            print(describe_analysis(brain_analysis))


            print()
            print(
                f"YOU: {user_input}"
            )


            window.activity_signal.emit(
                "PROCESSING REQUEST"
            )

            window.command_signal.emit(
                user_input
            )


            # =================================================
            # VISUAL INTERACTION
            # =================================================

            if is_visual_request(user_input):

                visual_result = handle_visual_request(
                    user_input
                )

                if visual_result is not None:

                    window.activity_signal.emit(
                        "VISUAL INTERACTION"
                    )

                    window.activity_signal.emit(
                        "RESPONSE READY"
                    )

                    respond(visual_result)

                    continue


            # =================================================
            # INTENT
            # =================================================
            # FAST MEMORY CHECK
            memory_result = detect_memory(user_input)
            
            fast_memory = None

            if memory_result["should_remember"]:
                print(f"NEXUS MEMORY: {memory_result}")
                
                fast_memory = get_fast_memory_answer(user_input)

            if fast_memory:
                print(f"NEXUS FAST MEMORY: {fast_memory}")
            intent = detect_intent(
                user_input
            )


            print(
                f"NEXUS INTENT: {intent}"
            )


            # =================================================
            # ROUTER
            # =================================================

            command_type = route_command(
                user_input
            )


            print(
                f"NEXUS ROUTER: {command_type}"
            )


            # =================================================
            # EXIT
            # =================================================

            if intent == INTENT_EXIT:

                print(
                    "NEXUS: Shutting down."
                )

                try:

                    speak(
                        "Shutting down."
                    )

                except Exception:

                    pass

                break

            # =================================================
            # SECURITY PERMISSION APPROVAL / REJECTION
            # =================================================

            if intent == INTENT_PERMISSION_APPROVE:

                ok, msg = permission_gate.approve()

                window.activity_signal.emit(
                    "PERMISSION GRANTED"
                )

                respond(msg)

                continue

            if intent == INTENT_PERMISSION_REJECT:

                ok, msg = permission_gate.reject()

                window.activity_signal.emit(
                    "PERMISSION REJECTED"
                )

                respond(msg)

                continue


            # =================================================
            # MISSION HISTORY
            # =================================================

            if is_mission_history_request(user_input):

                result = build_mission_history_response(
                    user_input
                )

                window.activity_signal.emit(
                    "MISSION HISTORY"
                )

                respond(result)

                continue


            # =================================================
            # MISSION STATUS
            # =================================================

            if is_mission_status_request(user_input):

                result = build_mission_status_response()

                print(
                    f"NEXUS MISSION STATUS: {result}"
                )

                window.activity_signal.emit(
                    "MISSION STATUS"
                )

                respond(result)

                continue


            # =================================================
            # TIME
            # =================================================

            if intent == INTENT_TIME:

                current_time = datetime.now().strftime(
                    "%I:%M %p"
                )

                result = (
                    f"The current time is "
                    f"{current_time}."
                )

                window.activity_signal.emit(
                    "RESPONSE READY"
                )

                respond(result)

                continue


            # =================================================
            # DATE
            # =================================================

            if intent == INTENT_DATE:

                current_date = datetime.now().strftime(
                    "%A, %d %B %Y"
                )

                result = (
                    f"Today is "
                    f"{current_date}."
                )

                window.activity_signal.emit(
                    "RESPONSE READY"
                )

                respond(result)

                continue


            # =================================================
            # SMART MEMORY
            # =================================================

            if intent == INTENT_MEMORY:

                memory_result = save_smart_memory(
                    user_input
                )

                memory = get_memory()


                if memory_result["saved"]:

                    result = (
                        "I'll remember that as a "
                        f"{memory_result['category']}."
                    )


                elif memory_result["reason"] == "duplicate":

                    result = (
                        "I already have that in memory."
                    )


                else:

                    result = (
                        "I couldn't identify useful "
                        "information to save."
                    )


                print(
                    f"NEXUS MEMORY: {memory_result}"
                )


                window.activity_signal.emit(
                    "MEMORY UPDATED"
                )

                respond(result)

                continue


            # =================================================
            # AGENT PLANNER
            # =================================================

            planner_decision = brain_analysis["decision"]

            plan = create_plan(user_input)

            # If the normal planner cannot produce a useful
            # multi-step command plan, use Goal Decomposition.
            if (
                len(plan.get("steps", [])) <= 1
                and planner_decision.get("type") == DECISION_MULTI_STEP
            ):
                goal_plan = create_goal_plan(user_input)

                if goal_plan and len(
                    goal_plan.get("steps", [])
                ) > 1:

                    print(
                        "NEXUS GOAL DECOMPOSITION:"
                    )

                    for index, decision in enumerate(
                        goal_plan["steps"],
                        start=1
                    ):
                        print(
                            f"GOAL STEP {index}: "
                            f"{describe_decision(decision)}"
                        )

                    # Convert decomposed decisions into the same
                    # structure already used by Planner/Mission.
                    plan = {
                        "status": "PLAN_READY",
                        "goal": user_input,
                        "steps": [
                            {
                                "id": index,
                                "decision": decision,
                                "status": "PENDING",
                                "result": None,
                            }
                            for index, decision in enumerate(
                                goal_plan["steps"],
                                start=1
                            )
                        ],
                    }

                    window.activity_signal.emit(
                        "GOAL DECOMPOSED"
                    )

            print("NEXUS PLAN:")
            print(describe_plan(plan))

            mission = create_mission(
                user_input,
                plan.get("steps", [])
            )

            print("NEXUS MISSION:")
            print(describe_mission(mission))

            # =================================================
            # MISSION CONTROL
            # =================================================

            if intent == INTENT_MISSION_PAUSE:

                if mission_controller.pause():

                    window.activity_signal.emit(
                        "MISSION PAUSED"
                    )

                    respond(
                        "Mission paused. I am still listening."
                    )

                else:

                    respond(
                        "There is no running mission to pause."
                    )

                continue


            if intent == INTENT_MISSION_RESUME:

                if mission_controller.resume():

                    window.activity_signal.emit(
                        "MISSION RESUMED"
                    )

                    respond(
                        "Mission resumed."
                    )

                else:

                    respond(
                        "There is no paused mission to resume."
                    )

                continue


            if intent == INTENT_MISSION_CANCEL:

                if mission_controller.cancel():

                    window.activity_signal.emit(
                        "MISSION CANCELLING"
                    )

                    respond(
                        "Cancelling the current mission."
                    )

                else:

                    respond(
                        "There is no active mission to cancel."
                    )

                continue


            # =================================================
            # MULTI-STEP MISSION
            # =================================================

            if len(plan.get("steps", [])) > 1:

                if mission_controller.is_active():

                    respond(
                        "A mission is already running. "
                        "You can say pause mission, "
                        "resume mission, or cancel mission."
                    )

                    continue

                mission_controller.start(
                    mission
                )

                window.activity_signal.emit(
                    "MISSION STARTED"
                )

                print(
                    "NEXUS: Starting mission worker in background."
                )

                mission_thread = threading.Thread(
                    target=run_mission_worker,
                    args=(plan, mission),
                    daemon=False,
                )

                mission_thread.start()

                respond(
                    f"Mission started with "
                    f"{len(plan.get('steps', []))} steps. "
                    "I am listening for further commands."
                )

                continue


            # =================================================
            # SINGLE DECISION
            # =================================================

            decision = brain_analysis["decision"]

            print(
                f"NEXUS DECISION: "
                f"{describe_decision(decision)}"
            )

            # =================================================
            # SINGLE COMMAND
            # =================================================

            if decision.get("type") == DECISION_COMMAND:

                result = execute_single_decision(
                    decision
                )


                if result is not None:

                    verification = verify_command_result(
                        decision.get("command"),
                        decision.get("target"),
                        result
                    )

                    print(
                        "NEXUS VERIFICATION: "
                        + describe_verification(
                            verification
                        )
                    )

                    if verification["verified"]:

                        browser_commands = (
                            "OPEN",
                            "OPEN_WEBSITE",
                            "WEB_SEARCH",
                            "YOUTUBE_SEARCH",
                        )

                        if decision.get("command") in browser_commands:

                            window.activity_signal.emit(
                                "BROWSER ACTION VERIFIED"
                            )

                        else:

                            window.activity_signal.emit(
                                "COMMAND VERIFIED"
                            )

                    else:

                        window.activity_signal.emit(
                            "COMMAND NOT VERIFIED"
                        )

                    window.activity_signal.emit(
                        "RESPONSE READY"
                    )

                    respond(result)

                    continue


            # =================================================
            # WEB SEARCH
            # =================================================

            live_context = ""


            if (
                intent == INTENT_WEB
                or needs_live_search(
                    user_input
                )
            ):

                window.activity_signal.emit(
                    "SEARCHING WEB"
                )


                try:

                    live_context = live_web_search(
                        user_input
                    )


                    window.activity_signal.emit(
                        "ANALYZING SOURCES"
                    )


                except Exception as e:

                    print(
                        f"NEXUS WEB SEARCH ERROR: {e}"
                    )

                    live_context = ""


            # =================================================
            # RECENT CONVERSATION
            # =================================================

            recent_conversation = (
                get_recent_conversation(10)
            )


            # =================================================
            # RELEVANT MEMORY
            # =================================================

            relevant_memory = (
                build_memory_context(
                    user_input,
                    limit=5
                )
            )


            # =================================================
            # CONTEXT INTELLIGENCE
            # =================================================

            context_block = build_context(
                recent_conversation,
                limit=10
            )


            resolved_request = resolve_reference(
                user_input,
                recent_conversation
            )


            print(
                f"NEXUS RESOLVED REQUEST: "
                f"{resolved_request}"
            )


            # =================================================
            # AI PROMPT
            # =================================================

            prompt = f"""
{SYSTEM_PROMPT}

RELEVANT PERMANENT MEMORY:
{relevant_memory}

ALL PERMANENT MEMORY:
{memory}

RECENT CONVERSATION:
{context_block}

CONTEXT-RESOLVED REQUEST:
{resolved_request}

LIVE WEB RESULTS:
{live_context}

CURRENT USER REQUEST:
{user_input}

INSTRUCTIONS:
Use the relevant memory and recent conversation when useful.

If the request contains a reference such as "it", "this",
"that", "previous one", or "the last one", use the context
to understand what the user means.

If the meaning is genuinely unclear, ask a short clarification.

If LIVE WEB RESULTS are available, use them for current facts.

Do not claim that a computer action happened unless the
local NEXUS system actually performed that action.

If no language is explicitly requested, answer in English.
"""

            # =====================================================
            # INSTANT MEMORY RECALL
            # =====================================================
            # Only use direct memory recall when the user is clearly
            # asking about something NEXUS remembers. This prevents an
            # unrelated memory from hijacking web searches such as
            # "latest AI news".

            if is_memory_recall_request(user_input):
                memory_matches = search_memory(user_input)

                if memory_matches:
                    memory_text = memory_matches[0]

                    if isinstance(memory_text, dict):
                        memory_text = memory_text.get("text", "")

                    if memory_text:
                        result = f"I remember: {memory_text}"

                        window.activity_signal.emit("MEMORY RECALLED")
                        respond(result)

                        continue

            # =================================================
            # AI THINKING
            # =================================================

            window.activity_signal.emit(
                "THINKING"
            )


            try:

                answer = run_both_ai(
                    prompt
                )


            except Exception as e:

                print(
                    f"NEXUS AI ERROR: {e}"
                )


                answer = (
                    "The AI systems are "
                    "temporarily unavailable."
                )


            # =================================================
            # SAVE CONVERSATION
            # =================================================

            add_conversation(
                user_input,
                answer
            )


            # =================================================
            # RESPONSE
            # =================================================

            window.activity_signal.emit(
                "RESPONSE READY"
            )


            respond(answer)


            print()


        # ====================================================
        # GLOBAL ERROR HANDLER
        # ====================================================

        except Exception as e:

            print(
                f"NEXUS ERROR: {e}"
            )


            try:

                speak(
                    "NEXUS encountered an error. "
                    "I will keep listening."
                )

            except Exception:

                pass


# ============================================================
# START VOICE THREAD
# ============================================================

thread = threading.Thread(
    target=voice_loop,
    daemon=True,
)

thread.start()


# ============================================================
# START AUTONOMOUS CHANNEL WATCHER
# ============================================================

try:
    from tools.meme_channel_db import meme_db
    from tools.youtube_automation import youtube_automator
    if meme_db.is_auto_details_enabled():
        youtube_automator.start_channel_watcher()
        print("NEXUS: 24/7 Autonomous YouTube Channel Watcher initialized.")
except Exception as e:
    print(f"NEXUS AUTONOMOUS SERVICE INIT ERROR: {e}")


# ============================================================
# START 24/7 CLOUD NODE IN BACKGROUND
# ============================================================

try:
    from cloud.nexus_cloud_server import start_cloud_server_background
    start_cloud_server_background()
    print("NEXUS: 24/7 Cloud Node initialized in background.")
except Exception as e:
    print(f"NEXUS CLOUD NODE INIT ERROR: {e}")


# ============================================================
# START UI
# ============================================================

sys.exit(
    app.exec()
) 