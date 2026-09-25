# ============================================================
# NEXUS CONTEXT INTELLIGENCE
# ============================================================

import re


# ============================================================
# CONTEXT BUILDER
# ============================================================

def build_context(conversation, limit=10):
    """
    Convert recent conversation into a clean context block
    for the AI.
    """

    if not conversation:
        return "No recent conversation."

    recent = conversation[-limit:]

    lines = []

    for item in recent:

        if not isinstance(item, dict):
            continue

        user = item.get("user", "")
        nexus = item.get("nexus", "")

        if user:
            lines.append(f"USER: {user}")

        if nexus:
            lines.append(f"NEXUS: {nexus}")

    if not lines:
        return "No recent conversation."

    return "\n".join(lines)


# ============================================================
# FIND LAST USER TOPIC
# ============================================================

def get_last_user_message(conversation):

    if not conversation:
        return ""

    for item in reversed(conversation):

        if isinstance(item, dict):

            user = item.get("user", "").strip()

            if user:
                return user

    return ""


# ============================================================
# FIND LAST NEXUS RESPONSE
# ============================================================

def get_last_nexus_response(conversation):

    if not conversation:
        return ""

    for item in reversed(conversation):

        if isinstance(item, dict):

            response = item.get("nexus", "").strip()

            if response:
                return response

    return ""


# ============================================================
# REFERENCE DETECTION
# ============================================================

def contains_reference(text):

    text = str(text).lower().strip()

    references = (
        "it",
        "this",
        "that",
        "these",
        "those",
        "the previous one",
        "the last one",
        "above",
        "previous",
    )

    for reference in references:

        pattern = rf"\b{re.escape(reference)}\b"

        if re.search(pattern, text):

            return True

    return False


# ============================================================
# RESOLVE SIMPLE REFERENCES
# ============================================================

def resolve_reference(user_text, conversation):

    """
    Provide the previous conversation to help resolve
    simple references such as 'it', 'this', or 'that'.
    """

    text = str(user_text).strip()

    if not contains_reference(text):

        return text

    last_user = get_last_user_message(
        conversation
    )

    if not last_user:

        return text

    return (
        f"{text}\n\n"
        f"CONTEXT REFERENCE:\n"
        f"The most recent user topic was:\n"
        f"{last_user}"
    )


# ============================================================
# CONTEXT SUMMARY
# ============================================================

def get_context_summary(conversation):

    if not conversation:

        return {
            "conversation_count": 0,
            "last_user_message": "",
            "last_nexus_response": "",
        }

    return {
        "conversation_count": len(conversation),
        "last_user_message": get_last_user_message(
            conversation
        ),
        "last_nexus_response": get_last_nexus_response(
            conversation
        ),
    }