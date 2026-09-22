import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

INBOX_FILE = BASE_DIR / "inbox_messages/inbox.json"
OUTPUT_FILE = BASE_DIR / "inbox_messages/unread_messages.json"


def track_unread_messages():
    with open(INBOX_FILE, "r", encoding="utf-8") as f:
        messages = json.load(f)

    unread_messages = []

    for message in messages:
        if message["unread"]:
            unread_messages.append({
                "id": message["id"],
                "from": message["from"],
                "subject": message["subject"]
            })

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(unread_messages, f, indent=4)

    return unread_messages
