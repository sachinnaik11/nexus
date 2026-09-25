# ============================================================
# NEXUS DECISION ENGINE
# ============================================================

from core.intent import (
    detect_intent,
    INTENT_COMMAND,
    INTENT_WEB,
    INTENT_AI,
    INTENT_MEMORY,
    INTENT_TIME,
    INTENT_DATE,
    INTENT_EXIT,
)

from core.router import (
    classify_command,
    get_command_target,
    normalize_multilingual_command,
)
from core.router import normalize_multilingual_command

# ============================================================
# DECISION TYPES
# ============================================================

DECISION_COMMAND = "COMMAND"
DECISION_WEB = "WEB"
DECISION_AI = "AI"
DECISION_MEMORY = "MEMORY"
DECISION_SYSTEM = "SYSTEM"
DECISION_MULTI_STEP = "MULTI_STEP"
DECISION_UNKNOWN = "UNKNOWN"


# ============================================================
# MULTI-STEP DETECTION
# ============================================================

def is_multi_step(text):

    command = normalize_multilingual_command(text)

    separators = (
        " and then ",
        " then ",
        " after that ",
        " and ",
        " also ",
        " plus ",
    )

    return any(
        separator in command
        for separator in separators
    )


# ============================================================
# CLEAN STEP CONNECTORS
# ============================================================

def clean_step_connector(step):

    step = step.strip()

    connector_prefixes = (
        "then ",
        "after that ",
        "also ",
        "plus ",
    )

    changed = True

    while changed:

        changed = False

        lower_step = step.lower()

        for prefix in connector_prefixes:

            if lower_step.startswith(prefix):

                step = step[
                    len(prefix):
                ].strip()

                changed = True
                break

    return step


# ============================================================
# SPLIT TASK
# ============================================================

def split_task(text):

    command = normalize_multilingual_command(text)

    separators = (
        " and then ",
        " then ",
        " after that ",
        " and ",
        " also ",
        " plus ",
    )

    for separator in separators:

        if separator in command:

            parts = command.split(
                separator
            )

            cleaned_parts = []

            for part in parts:

                part = clean_step_connector(
                    part
                )

                if part:

                    cleaned_parts.append(
                        part
                    )

            return cleaned_parts

    return [
        clean_step_connector(command)
    ]


# ============================================================
# APPLY TASK CONTEXT
# ============================================================

def apply_task_context(steps):

    """
    Understand commands that depend on a previous step.

    Example:

    open youtube and search GTA 5

    becomes:

    open youtube
    search youtube GTA 5
    """

    if not steps:

        return steps

    contextual_steps = [
        steps[0]
    ]

    for current_step in steps[1:]:

        current = current_step.strip().lower()

        previous = (
            contextual_steps[-1]
            .strip()
            .lower()
        )

        # ----------------------------------------------------
        # YouTube CONTEXT
        # ----------------------------------------------------

        previous_opened_youtube = (
            previous == "open youtube"
            or previous == "launch youtube"
            or previous == "start youtube"
        )

        if previous_opened_youtube:

            if current.startswith("search "):

                query = current[
                    len("search "):
                ].strip()

                if query:

                    current_step = (
                        f"search youtube {query}"
                    )

        contextual_steps.append(
            current_step
        )

    return contextual_steps


# ============================================================
# DECIDE SINGLE REQUEST
# ============================================================

def decide_single(text):

    intent = detect_intent(text)

    # --------------------------------------------------------
    # COMMAND
    # --------------------------------------------------------

    if intent == INTENT_COMMAND:

        command_type = classify_command(text)

        target = get_command_target(text)

        if command_type:

            return {
                "type": DECISION_COMMAND,
                "intent": intent,
                "command": command_type,
                "target": target,
            }

        return {
            "type": DECISION_UNKNOWN,
            "intent": intent,
            "command": None,
            "target": None,
        }

    # --------------------------------------------------------
    # WEB
    # --------------------------------------------------------

    if intent == INTENT_WEB:

        return {
            "type": DECISION_WEB,
            "intent": intent,
            "command": None,
            "target": None,
        }

    # --------------------------------------------------------
    # MEMORY
    # --------------------------------------------------------

    if intent == INTENT_MEMORY:

        return {
            "type": DECISION_MEMORY,
            "intent": intent,
            "command": None,
            "target": None,
        }

    # --------------------------------------------------------
    # SYSTEM
    # --------------------------------------------------------

    if intent in (
        INTENT_TIME,
        INTENT_DATE,
        INTENT_EXIT,
    ):

        return {
            "type": DECISION_SYSTEM,
            "intent": intent,
            "command": None,
            "target": None,
        }

    # --------------------------------------------------------
    # AI
    # --------------------------------------------------------

    if intent == INTENT_AI:

        return {
            "type": DECISION_AI,
            "intent": intent,
            "command": None,
            "target": None,
        }

    return {
        "type": DECISION_UNKNOWN,
        "intent": intent,
        "command": None,
        "target": None,
    }


# ============================================================
# MAIN DECISION
# ============================================================

def make_decision(text):
    text = normalize_multilingual_command(text)

    if is_multi_step(text):

        raw_steps = split_task(text)

        # Apply previous-step context
        steps = apply_task_context(
            raw_steps
        )

        decisions = []

        for step in steps:

            decisions.append(
                decide_single(step)
            )

        return {
            "type": DECISION_MULTI_STEP,
            "steps": decisions,
        }

    return decide_single(text)


# ============================================================
# HUMAN-READABLE DESCRIPTION
# ============================================================

def describe_decision(decision):

    decision_type = decision.get(
        "type"
    )

    if decision_type == DECISION_COMMAND:

        command = decision.get(
            "command"
        )

        target = decision.get(
            "target"
        )

        return (
            f"COMMAND → {command} → {target}"
        )

    if decision_type == DECISION_WEB:

        return (
            "WEB → Search current information"
        )

    if decision_type == DECISION_AI:

        return (
            "AI → Generate an intelligent response"
        )

    if decision_type == DECISION_MEMORY:

        return (
            "MEMORY → Store or retrieve memory"
        )

    if decision_type == DECISION_SYSTEM:

        return (
            f"SYSTEM → "
            f"{decision.get('intent')}"
        )

    if decision_type == DECISION_MULTI_STEP:

        return (
            f"MULTI-STEP → "
            f"{len(decision.get('steps', []))} steps"
        )

    return (
        "UNKNOWN → Needs clarification"
    )


# ============================================================
# SAFETY CHECK
# ============================================================

def is_safe_decision(decision):

    decision_type = decision.get(
        "type"
    )

    allowed = {
        DECISION_COMMAND,
        DECISION_WEB,
        DECISION_AI,
        DECISION_MEMORY,
        DECISION_SYSTEM,
        DECISION_MULTI_STEP,
    }

    if decision_type not in allowed:

        return False

    if decision_type == DECISION_MULTI_STEP:

        return all(
            is_safe_decision(step)
            for step in decision.get(
                "steps",
                []
            )
        )

    return True