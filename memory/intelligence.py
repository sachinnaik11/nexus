# ============================================================
# NEXUS MEMORY INTELLIGENCE
# ============================================================

import re

from memory.store import (
    get_memory,
    add_memory,
)


# ============================================================
# MEMORY CATEGORIES
# ============================================================

MEMORY_CATEGORIES = {
    "identity": [
        "my name is",
        "call me",
    ],
    "preference": [
        "i like",
        "i love",
        "i prefer",
        "my favorite",
        "i don't like",
        "i hate",
    ],
    "goal": [
        "my goal is",
        "i want to",
        "i am trying to",
        "i'm trying to",
        "i plan to",
    ],
    "project": [
        "my project is",
        "i am building",
        "i'm building",
        "working on",
    ],
}


# ============================================================
# NORMALIZE
# ============================================================

def normalize_memory(text):

    return re.sub(
        r"\s+",
        " ",
        str(text).strip()
    )


# ============================================================
# DETECT MEMORY
# ============================================================

def detect_memory(text):

    text = normalize_memory(text)

    for wake_word in (
        "nexus ",
        "hey nexus ",
        "ok nexus "
    ):
        if text.lower().startswith(wake_word):
            text = text[len(wake_word):].strip()
            break

    lower = text.lower()

    # Explicit remember request
    if lower.startswith("remember "):

        return {
            "should_remember": True,
            "category": "explicit",
            "text": text[len("remember "):].strip(),
        }

    # Identity / preference / goal / project
    for category, phrases in MEMORY_CATEGORIES.items():

        for phrase in phrases:

            if phrase in lower:

                return {
                    "should_remember": True,
                    "category": category,
                    "text": text,
                }

    return {
        "should_remember": False,
        "category": None,
        "text": text,
    }


# ============================================================
# DUPLICATE CHECK
# ============================================================

def memory_exists(text):

    target = normalize_memory(text).lower()

    memories = get_memory()

    for memory in memories:

        if normalize_memory(memory).lower() == target:

            return True

    return False


# ============================================================
# SMART SAVE
# ============================================================

def save_smart_memory(text):

    detected = detect_memory(text)

    if not detected["should_remember"]:

        return {
            "saved": False,
            "reason": "not_memory",
            "category": None,
            "text": text,
        }

    memory_text = detected["text"]

    if not memory_text:

        return {
            "saved": False,
            "reason": "empty",
            "category": detected["category"],
            "text": "",
        }

    if memory_exists(memory_text):

        return {
            "saved": False,
            "reason": "duplicate",
            "category": detected["category"],
            "text": memory_text,
        }

    add_memory(memory_text)

    return {
        "saved": True,
        "reason": "saved",
        "category": detected["category"],
        "text": memory_text,
    }


# ============================================================
# SEARCH MEMORY
# ============================================================

def search_memory(query):

    STOP_WORDS = {
        "a", "an", "the",
        "is", "am", "are", "was", "were",
        "i", "me", "my", "mine",
        "you", "your", "yours",
        "what", "which", "who", "where", "when",
        "why", "how",
        "about", "to", "of", "for", "and", "or",
        "in", "on", "at", "with", "from",
        "this", "that", "it",
        "do", "does", "did",
        "can", "could", "would", "should",
        "latest", "today", "now"
    }

    query_words = {
        word
        for word in normalize_memory(query).lower().split()
        if word not in STOP_WORDS
    }

    if not query_words:
        return []

    matches = []

    for memory in get_memory():

        memory_words = {
            word
            for word in normalize_memory(memory).lower().split()
            if word not in STOP_WORDS
        }

        score = len(
            query_words.intersection(
                memory_words
            )
        )

        if score > 0:

            matches.append(
                (score, memory)
            )

    matches.sort(
        key=lambda item: item[0],
        reverse=True
    )

    return [
        memory
        for score, memory in matches
    ]


# ============================================================
# RELEVANT MEMORY
# ============================================================

def get_relevant_memory(query, limit=5):

    results = search_memory(query)

    return results[:limit]


# ============================================================
# FAST MEMORY ANSWER
# ============================================================

def get_fast_memory_answer(query):

    results = get_relevant_memory(
        query,
        limit=3
    )

    if not results:
        return None

    return results[0]


# ============================================================
# MEMORY CONTEXT
# ============================================================

def build_memory_context(query, limit=5):

    memories = get_relevant_memory(
        query,
        limit
    )

    if not memories:

        return "No relevant permanent memories."

    return "\n".join(
        f"- {memory}"
        for memory in memories
    )