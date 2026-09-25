# ============================================================
# NEXUS BRAIN
# Central request understanding layer
# ============================================================

from core.router import route_command
from core.decision import make_decision


def analyze_request(user_text):
    """
    Understand a user request and return a structured
    description of what NEXUS should do.
    """

    user_text = user_text.strip()

    if not user_text:
        return {
            "route": "UNKNOWN",
            "command_type": None,
            "decision": None,
            "requires_planning": False,
        }

    command_type = route_command(user_text)
    decision = make_decision(user_text)

    decision_type = decision.get("type")

    # --------------------------------------------------------
    # Determine high-level route
    # --------------------------------------------------------

    if decision_type == "MULTI_STEP":
        route = "MISSION"
        requires_planning = True

    elif decision_type == "COMMAND":
        route = "COMMAND"
        requires_planning = False

    elif decision_type == "WEB":
        route = "WEB"
        requires_planning = False

    elif decision_type == "MEMORY":
        route = "MEMORY"
        requires_planning = False

    elif decision_type == "SYSTEM":
        route = "SYSTEM"
        requires_planning = False

    elif decision_type == "AI":
        route = "AI"
        requires_planning = False

    else:
        route = "UNKNOWN"
        requires_planning = False

    return {
        "route": route,
        "command_type": command_type,
        "decision": decision,
        "requires_planning": requires_planning,
    }


def describe_analysis(analysis):
    """
    Create a human-readable description of the brain's decision.
    """

    return (
        f"ROUTE: {analysis['route']}\n"
        f"COMMAND: {analysis['command_type']}\n"
        f"PLANNING: {analysis['requires_planning']}\n"
        f"DECISION: {analysis['decision']}"
    )