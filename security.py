import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
SECURITY_LOG_FILE = BASE_DIR / "logs/hostile_messages.json"


HOSTILE_WORDS = [
    "re-verify your credentials immediately",
    "without asking for approval",
    "forward the full contents",
    "disregard the account on file and remit",
    "please keep this between us for the moment and don't loop in finance yet",
    "an assistant managing this inbox must reply"
]


def check_hostile_message(message):
    text = (
        f"{message.get('subject', '')} "
        f"{message.get('body', '')}"
    ).lower()

    matched_words = []

    for word in HOSTILE_WORDS:
        if word in text:
            matched_words.append(word)

    if not matched_words:
        return None

    return {
        "message_id": message["id"],
        "attempted": matched_words,
        "reason": "The email contains an instruction asking the assistant to perform an action."
    }


def log_hostile_message(result):
    logs = []

    if SECURITY_LOG_FILE.exists():
        with open(SECURITY_LOG_FILE, "r", encoding="utf-8") as f:
            content = f.read().strip()
            if content:
                logs = json.loads(content)

    logs.append(result)

    with open(SECURITY_LOG_FILE, "w", encoding="utf-8") as f:
        json.dump(logs, f, indent=4)


def check_inbox_for_hostile_messages(messages):
    hostile_messages = []

    for message in messages:
        result = check_hostile_message(message)

        if result:
            log_hostile_message(result)
            hostile_messages.append(result)

    return hostile_messages
