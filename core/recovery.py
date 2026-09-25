# ============================================================
# NEXUS — TASK RECOVERY ENGINE
# ============================================================

RECOVERY_SUCCESS = "SUCCESS"
RECOVERY_RETRY = "RETRY"
RECOVERY_SKIP = "SKIP"
RECOVERY_FAILED = "FAILED"


# ------------------------------------------------------------
# Detect whether an error is likely temporary
# ------------------------------------------------------------

def is_retryable_error(result):
    if result is None:
        return True

    text = str(result).lower()

    retryable_phrases = (
        "temporarily unavailable",
        "timeout",
        "timed out",
        "connection",
        "network",
        "busy",
        "try again",
        "could not open",
        "failed to open",
        "service unavailable",
        "429",
        "503",
    )

    return any(
        phrase in text
        for phrase in retryable_phrases
    )


# ------------------------------------------------------------
# Decide what to do after a step result
# ------------------------------------------------------------

def should_retry(result, attempt, max_attempts=2):
    if attempt >= max_attempts:
        return False

    if is_success(result):
        return False

    return is_retryable_error(result)


# ------------------------------------------------------------
# Determine whether a step succeeded
# ------------------------------------------------------------

def is_success(result):
    if result is None:
        return False

    text = str(result).strip().lower()

    failure_phrases = (
        "failed",
        "error",
        "not available",
        "don't know how",
        "could not",
        "cannot",
        "unable",
        "unknown",
    )

    return not any(
        phrase in text
        for phrase in failure_phrases
    )


# ------------------------------------------------------------
# Determine recovery state
# ------------------------------------------------------------

def get_recovery_state(result, attempt=1, max_attempts=2):
    if is_success(result):
        return RECOVERY_SUCCESS

    if should_retry(
        result,
        attempt,
        max_attempts,
    ):
        return RECOVERY_RETRY

    return RECOVERY_FAILED


# ------------------------------------------------------------
# Build a human-readable recovery message
# ------------------------------------------------------------

def recovery_message(
    result,
    attempt=1,
    max_attempts=2,
):
    state = get_recovery_state(
        result,
        attempt,
        max_attempts,
    )

    if state == RECOVERY_SUCCESS:
        return "Step completed successfully."

    if state == RECOVERY_RETRY:
        return (
            f"Step failed temporarily. "
            f"Retrying ({attempt + 1}/{max_attempts})..."
        )

    return "Step failed and could not be recovered."


# ------------------------------------------------------------
# Summarize multiple executed steps
# ------------------------------------------------------------

def build_recovery_report(results):
    if not results:
        return {
            "total": 0,
            "successful": 0,
            "failed": 0,
            "retryable": 0,
            "status": RECOVERY_FAILED,
        }

    successful = 0
    failed = 0
    retryable = 0

    for result in results:
        if is_success(result):
            successful += 1
        else:
            failed += 1

            if is_retryable_error(result):
                retryable += 1

    if failed == 0:
        status = RECOVERY_SUCCESS
    elif retryable > 0:
        status = RECOVERY_RETRY
    else:
        status = RECOVERY_FAILED

    return {
        "total": len(results),
        "successful": successful,
        "failed": failed,
        "retryable": retryable,
        "status": status,
    }


# ------------------------------------------------------------
# Explain what happened
# ------------------------------------------------------------

def summarize_results(results):
    report = build_recovery_report(results)

    if report["total"] == 0:
        return "No steps were executed."

    if report["failed"] == 0:
        return (
            f"All {report['total']} steps "
            f"completed successfully."
        )

    if report["successful"] == 0:
        return (
            f"All {report['total']} steps failed."
        )

    return (
        f"{report['successful']} of "
        f"{report['total']} steps completed. "
        f"{report['failed']} step(s) failed."
    )