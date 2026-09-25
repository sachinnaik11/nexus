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
        1 for step in steps if step.get("status") == "COMPLETE"
    )
    percentage = int((completed / total) * 100) if total else 0
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
        lines.append(f"CURRENT STEP: {current}")

    return "\n".join(lines)
