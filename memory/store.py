# ============================================================
# NEXUS MEMORY SYSTEM
# ============================================================

import json
import os


MEMORY_DIR = "memory"

MEMORY_FILE = os.path.join(
    MEMORY_DIR,
    "memory.json"
)

CONVERSATION_FILE = os.path.join(
    MEMORY_DIR,
    "conversation.json"
)


# ============================================================
# DIRECTORY
# ============================================================

def ensure_memory_directory():

    os.makedirs(
        MEMORY_DIR,
        exist_ok=True
    )


# ============================================================
# PERMANENT MEMORY
# ============================================================

def load_memory():

    ensure_memory_directory()

    if not os.path.exists(MEMORY_FILE):

        return []

    try:

        with open(
            MEMORY_FILE,
            "r",
            encoding="utf-8"
        ) as file:

            data = json.load(file)

            if isinstance(data, list):

                return data

    except (
        json.JSONDecodeError,
        OSError
    ):

        pass

    return []


def save_memory(memory):

    ensure_memory_directory()

    with open(
        MEMORY_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            memory,
            file,
            indent=2,
            ensure_ascii=False
        )


def add_memory(text):

    memory = load_memory()

    text = str(text).strip()

    if not text:

        return

    memory.append(text)

    save_memory(memory)


def get_memory():

    return load_memory()


# ============================================================
# CONVERSATION MEMORY
# ============================================================

def load_conversation():

    ensure_memory_directory()

    if not os.path.exists(
        CONVERSATION_FILE
    ):

        return []

    try:

        with open(
            CONVERSATION_FILE,
            "r",
            encoding="utf-8"
        ) as file:

            data = json.load(file)

            if isinstance(data, list):

                return data

    except (
        json.JSONDecodeError,
        OSError
    ):

        pass

    return []


def save_conversation(conversation):

    ensure_memory_directory()

    with open(
        CONVERSATION_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            conversation,
            file,
            indent=2,
            ensure_ascii=False
        )


def add_conversation(
    user_text,
    nexus_text
):

    conversation = load_conversation()

    conversation.append(
        {
            "user": str(user_text),
            "nexus": str(nexus_text)
        }
    )

    # Keep the latest 20 exchanges
    conversation = conversation[-20:]

    save_conversation(
        conversation
    )


def get_conversation():

    return load_conversation()


# ============================================================
# RECENT CONVERSATION FOR AI
# ============================================================

def get_recent_conversation(
    limit=10
):

    conversation = load_conversation()

    return conversation[-limit:]