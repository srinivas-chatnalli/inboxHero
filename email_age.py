import json
from pathlib import Path
from datetime import datetime, timezone

BASE_DIR = Path(__file__).resolve().parent

INBOX_FILE = BASE_DIR / "inbox_messages/inbox.json"
OUTPUT_FILE = BASE_DIR / "inbox_messages/email_age.json"


def track_email_age():
    with open(INBOX_FILE, "r", encoding="utf-8") as f:
        messages = json.load(f)

    now = datetime.now(timezone.utc)

    result = []

    for message in messages:
        email_time = datetime.fromisoformat(
            message["timestamp"]
        ).replace(tzinfo=timezone.utc)

        age_days = (now - email_time).days

        if age_days == 0:
            age_group = "Today"
        elif age_days <= 2:
            age_group = "1-2 days"
        elif age_days <= 7:
            age_group = "3-7 days"
        else:
            age_group = "More than 7 days"

        result.append({
            "id": message["id"],
            "subject": message["subject"],
            "from": message["from"],
            "age_days": age_days,
            "age_group": age_group
        })

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=4)

    return result
