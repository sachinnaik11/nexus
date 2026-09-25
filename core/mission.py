# ============================================================
# NEXUS — MISSION STATE MANAGER
# ============================================================

MISSION_IDLE = "IDLE"
MISSION_RUNNING = "RUNNING"
MISSION_PAUSED = "PAUSED"
MISSION_COMPLETED = "COMPLETED"
MISSION_FAILED = "FAILED"


# ============================================================
# CREATE MISSION
# ============================================================

def create_mission(goal, steps=None):
    """Create a new mission state."""

    if steps is None:
        steps = []

    mission_steps = []

    for index, step in enumerate(steps, start=1):

        decision = step.get(
            "decision",
            step
        )

        mission_steps.append({
            "id": index,
            "decision": decision,
            "status": "PENDING",
            "result": None,
            "attempts": 0,
        })

    return {
        "goal": str(goal),
        "status": MISSION_RUNNING,
        "current_step": (
            1 if mission_steps else None
        ),
        "steps": mission_steps,
    }


# ============================================================
# GET CURRENT STEP
# ============================================================

def get_current_step(mission):

    if not mission:
        return None

    for step in mission.get("steps", []):

        if step.get("status") in (
            "PENDING",
            "RUNNING",
        ):
            return step

    return None


# ============================================================
# START STEP
# ============================================================

def start_step(mission, step_id):

    if not mission:
        return None

    for step in mission.get("steps", []):

        if step.get("id") == step_id:

            step["status"] = "RUNNING"

            step["attempts"] = (
                step.get("attempts", 0) + 1
            )

            mission["current_step"] = step_id

            mission["status"] = MISSION_RUNNING

            return step

    return None


# ============================================================
# COMPLETE STEP
# ============================================================

def complete_step(
    mission,
    step_id,
    result
):

    if not mission:
        return None

    for step in mission.get("steps", []):

        if step.get("id") == step_id:

            step["status"] = "COMPLETE"
            step["result"] = result

            break

    update_mission_status(mission)

    return get_current_step(mission)


# ============================================================
# FAIL STEP
# ============================================================

def fail_step(
    mission,
    step_id,
    result
):

    if not mission:
        return None

    for step in mission.get("steps", []):

        if step.get("id") == step_id:

            step["status"] = "FAILED"
            step["result"] = result

            break

    update_mission_status(mission)

    return get_current_step(mission)


# ============================================================
# PAUSE MISSION
# ============================================================

def pause_mission(mission):

    if not mission:
        return False

    if mission.get("status") != MISSION_RUNNING:
        return False

    mission["status"] = MISSION_PAUSED

    return True


# ============================================================
# RESUME MISSION
# ============================================================

def resume_mission(mission):

    if not mission:
        return False

    if mission.get("status") != MISSION_PAUSED:
        return False

    mission["status"] = MISSION_RUNNING

    current_step = get_current_step(
        mission
    )

    if current_step:

        mission["current_step"] = (
            current_step["id"]
        )

    return True


# ============================================================
# UPDATE MISSION STATUS
# ============================================================

def update_mission_status(mission):

    if not mission:
        return MISSION_IDLE

    steps = mission.get(
        "steps",
        []
    )

    if not steps:

        mission["status"] = MISSION_COMPLETED
        mission["current_step"] = None

        return MISSION_COMPLETED

    # Running step
    if any(
        step.get("status") == "RUNNING"
        for step in steps
    ):

        mission["status"] = MISSION_RUNNING

        return MISSION_RUNNING

    # All completed
    if all(
        step.get("status") == "COMPLETE"
        for step in steps
    ):

        mission["status"] = MISSION_COMPLETED
        mission["current_step"] = None

        return MISSION_COMPLETED

    # Failed with nothing left pending
    if (
        any(
            step.get("status") == "FAILED"
            for step in steps
        )
        and not any(
            step.get("status") in (
                "PENDING",
                "RUNNING",
            )
            for step in steps
        )
    ):

        mission["status"] = MISSION_FAILED
        mission["current_step"] = None

        return MISSION_FAILED

    # Still has work
    mission["status"] = MISSION_RUNNING

    current_step = get_current_step(
        mission
    )

    if current_step:

        mission["current_step"] = (
            current_step["id"]
        )

    return MISSION_RUNNING


# ============================================================
# STATUS CHECKS
# ============================================================

def is_running(mission):

    return bool(
        mission
        and mission.get("status")
        == MISSION_RUNNING
    )


def is_paused(mission):

    return bool(
        mission
        and mission.get("status")
        == MISSION_PAUSED
    )


def is_complete(mission):

    return bool(
        mission
        and mission.get("status")
        == MISSION_COMPLETED
    )


def has_failed(mission):

    return bool(
        mission
        and mission.get("status")
        == MISSION_FAILED
    )


# ============================================================
# PROGRESS
# ============================================================

def get_progress(mission):

    if not mission:

        return {
            "completed": 0,
            "total": 0,
            "percentage": 0,
        }

    steps = mission.get(
        "steps",
        []
    )

    total = len(steps)

    completed = sum(
        1
        for step in steps
        if step.get("status")
        == "COMPLETE"
    )

    percentage = (
        int(
            (completed / total) * 100
        )
        if total
        else 0
    )

    return {
        "completed": completed,
        "total": total,
        "percentage": percentage,
    }


# ============================================================
# COMPLETED STEPS
# ============================================================

def get_completed_steps(mission):

    if not mission:
        return []

    return [
        step
        for step in mission.get(
            "steps",
            []
        )
        if step.get("status")
        == "COMPLETE"
    ]


# ============================================================
# FAILED STEPS
# ============================================================

def get_failed_steps(mission):

    if not mission:
        return []

    return [
        step
        for step in mission.get(
            "steps",
            []
        )
        if step.get("status")
        == "FAILED"
    ]


# ============================================================
# DESCRIBE MISSION
# ============================================================

def describe_mission(mission):

    if not mission:

        return "No active mission."

    progress = get_progress(
        mission
    )

    lines = [
        (
            f"MISSION: "
            f"{mission.get('goal', 'Unknown')}"
        ),
        (
            f"STATUS: "
            f"{mission.get('status', MISSION_IDLE)}"
        ),
        (
            f"PROGRESS: "
            f"{progress['completed']}/"
            f"{progress['total']} "
            f"({progress['percentage']}%)"
        ),
    ]

    for step in mission.get(
        "steps",
        []
    ):

        lines.append(
            f"STEP {step.get('id')}: "
            f"{step.get('status', 'PENDING')}"
        )

    return "\n".join(lines)


# ============================================================
# VALIDATE MISSION
# ============================================================

def validate_mission(mission):

    if not isinstance(
        mission,
        dict
    ):
        return False

    if not mission.get("goal"):
        return False

    if "steps" not in mission:
        return False

    if not isinstance(
        mission["steps"],
        list
    ):
        return False

    for step in mission["steps"]:

        if "id" not in step:
            return False

        if "decision" not in step:
            return False

        if "status" not in step:
            return False

    return True