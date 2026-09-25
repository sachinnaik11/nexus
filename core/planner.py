# ============================================================
# NEXUS — AGENT TASK PLANNER
# ============================================================

from core.decision import (
    make_decision,
    DECISION_COMMAND,
    DECISION_MULTI_STEP,
)


PLAN_READY = "PLAN_READY"
PLAN_EMPTY = "PLAN_EMPTY"
PLAN_INVALID = "PLAN_INVALID"


# ------------------------------------------------------------
# Create a mission plan from a user request
# ------------------------------------------------------------

def create_plan(user_text):
    decision = make_decision(user_text)

    if not decision:
        return {
            "status": PLAN_EMPTY,
            "goal": user_text,
            "steps": [],
        }
    if decision.get("type") not in (
        DECISION_COMMAND,
        DECISION_MULTI_STEP,
    ):
        return {
            "status": PLAN_EMPTY,
            "goal": user_text,
            "steps": [],
        }

    if decision.get("type") == DECISION_MULTI_STEP:

        decisions = decision.get(
            "steps",
            []
        )

    else:

        decisions = [decision]

    steps = []

    for index, step in enumerate(
        decisions,
        start=1
    ):

        steps.append({
            "id": index,
            "decision": step,
            "status": "PENDING",
            "result": None,
        })

    if not steps:
        return {
            "status": PLAN_EMPTY,
            "goal": user_text,
            "steps": [],
        }

    return {
        "status": PLAN_READY,
        "goal": user_text,
        "steps": steps,
    }


# ------------------------------------------------------------
# Get number of steps
# ------------------------------------------------------------

def get_step_count(plan):
    if not plan:
        return 0

    return len(
        plan.get("steps", [])
    )


# ------------------------------------------------------------
# Get next pending step
# ------------------------------------------------------------

def get_next_step(plan):
    if not plan:
        return None

    for step in plan.get("steps", []):

        if step.get("status") == "PENDING":

            return step

    return None


# ------------------------------------------------------------
# Mark step as running
# ------------------------------------------------------------

def mark_step_running(
    plan,
    step_id
):

    for step in plan.get("steps", []):

        if step.get("id") == step_id:

            step["status"] = "RUNNING"

            return step

    return None


# ------------------------------------------------------------
# Mark step as completed
# ------------------------------------------------------------

def mark_step_complete(
    plan,
    step_id,
    result
):

    for step in plan.get("steps", []):

        if step.get("id") == step_id:

            step["status"] = "COMPLETE"
            step["result"] = result

            return step

    return None


# ------------------------------------------------------------
# Mark step as failed
# ------------------------------------------------------------

def mark_step_failed(
    plan,
    step_id,
    result
):

    for step in plan.get("steps", []):

        if step.get("id") == step_id:

            step["status"] = "FAILED"
            step["result"] = result

            return step

    return None


# ------------------------------------------------------------
# Check whether the mission is complete
# ------------------------------------------------------------

def is_plan_complete(plan):

    if not plan:
        return False

    steps = plan.get(
        "steps",
        []
    )

    if not steps:
        return False

    return all(
        step.get("status") == "COMPLETE"
        for step in steps
    )


# ------------------------------------------------------------
# Check whether the mission has failures
# ------------------------------------------------------------

def has_plan_failures(plan):

    if not plan:
        return False

    return any(
        step.get("status") == "FAILED"
        for step in plan.get("steps", [])
    )


# ------------------------------------------------------------
# Get completed steps
# ------------------------------------------------------------

def get_completed_steps(plan):

    if not plan:
        return []

    return [
        step
        for step in plan.get("steps", [])
        if step.get("status") == "COMPLETE"
    ]


# ------------------------------------------------------------
# Get failed steps
# ------------------------------------------------------------

def get_failed_steps(plan):

    if not plan:
        return []

    return [
        step
        for step in plan.get("steps", [])
        if step.get("status") == "FAILED"
    ]


# ------------------------------------------------------------
# Human-readable plan
# ------------------------------------------------------------

def describe_plan(plan):

    if not plan:
        return "No mission plan."

    goal = plan.get(
        "goal",
        "Unknown mission"
    )

    steps = plan.get(
        "steps",
        []
    )

    lines = [
        f"MISSION: {goal}"
    ]

    for step in steps:

        decision = step.get(
            "decision",
            {}
        )

        command = decision.get(
            "command"
        )

        target = decision.get(
            "target"
        )

        status = step.get(
            "status",
            "PENDING"
        )

        if command:

            description = (
                f"{command}"
            )

            if target:

                description += (
                    f" → {target}"
                )

        else:

            description = (
                decision.get(
                    "type",
                    "UNKNOWN"
                )
            )

        lines.append(
            f"STEP {step['id']} "
            f"[{status}] → {description}"
        )

    return "\n".join(lines)


# ------------------------------------------------------------
# Validate plan
# ------------------------------------------------------------

def validate_plan(plan):

    if not isinstance(
        plan,
        dict
    ):
        return False

    if not plan.get("goal"):
        return False

    steps = plan.get(
        "steps"
    )

    if not isinstance(
        steps,
        list
    ):
        return False

    for step in steps:

        if "id" not in step:
            return False

        if "decision" not in step:
            return False

        if "status" not in step:
            return False

    return True