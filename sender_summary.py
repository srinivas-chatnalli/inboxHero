import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

INBOX_FILE = BASE_DIR / "inbox_messages/inbox.json"
OUTPUT_FILE = BASE_DIR / "inbox_messages/sender_summary.json"


def create_sender_summary():
    with open(INBOX_FILE, "r", encoding="utf-8") as f:
        messages = json.load(f)

    summary = {}

    for message in messages:
        sender = message["from"]

        if sender not in summary:
            summary[sender] = {
                "total": 0,
                "unread": 0
            }

        summary[sender]["total"] += 1

        if message["unread"]:
            summary[sender]["unread"] += 1

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=4)

    return summary
