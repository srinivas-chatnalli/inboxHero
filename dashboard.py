import json
from pathlib import Path

from inboxHero.model import ask_model


BASE_DIR = Path(__file__).resolve().parent

INBOX_FILE = BASE_DIR / "inbox_messages/inbox.json"
DISPOSITION_FILE = BASE_DIR / "inbox_messages/inbox_after_disposition.json"
HOSTILE_FILE = BASE_DIR / "logs/hostile_messages.json"

COMMITMENT_FILE = BASE_DIR / "inbox_messages/commitments.json"
DASHBOARD_FILE = BASE_DIR / "dashboard.html"


def load_json(file):
    if not file.exists():
        return []

    with open(file, "r", encoding="utf-8") as f:
        content = f.read().strip()
        return json.loads(content) if content else []


def generate_commitments(messages):

    message_text = ""

    for message in messages:
        message_text += f"""
Message ID: {message["id"]}
Date: {message["timestamp"]}
Subject: {message["subject"]}
Body: {message["body"]}

"""

    prompt = f"""
Read the following emails and find commitments.

A commitment can be:
- a meeting
- a deadline
- something someone agreed to do
- something the user needs to do
- an appointment
- any other important obligation

Use only information present in the emails.

Return only valid JSON in this format:

[
    {{
        "commitment": "short description",
        "date": "date or datetime if available",
        "source_message_ids": ["message_id"]
    }}
]

If there are no commitments, return [].

Emails:
{message_text}
"""

    response = ask_model([
        {
            "role": "user",
            "content": prompt
        }
    ])

    content = response.message.content.strip()

    print("LLM commitment response:")
    print(content)

    if not content:
        commitments = []

    else:
        if content.startswith("```"):
            content = content.replace("```json", "").replace("```", "").strip()

        try:
            commitments = json.loads(content)
        except json.JSONDecodeError:
            print("Could not read commitment response as JSON.")
            commitments = []

    message_ids = {message["id"] for message in messages}

    for commitment in commitments:
        commitment["source_message_ids"] = [
            message_id
            for message_id in commitment.get("source_message_ids", [])
            if message_id in message_ids
        ]

    with open(COMMITMENT_FILE, "w", encoding="utf-8") as f:
        json.dump(commitments, f, indent=4)

    return commitments


def generate_dashboard():

    inbox_messages = load_json(INBOX_FILE)
    dispositions = load_json(DISPOSITION_FILE)
    hostile_messages = load_json(HOSTILE_FILE)

    # Generate commitments from the inbox
    commitments = generate_commitments(inbox_messages)

    # Pending actions
    pending_actions = []

    for message in dispositions:
        if message.get("disposition") in [
            "reply",
            "defer",
            "delegate",
            "escalate"
        ]:
            pending_actions.append(message)

    html = """
<!DOCTYPE html>
<html>
<head>
    <title>Inbox Dashboard</title>

    <style>
        body {
            font-family: Arial;
            margin: 20px;
        }

        .dashboard {
            display: flex;
            gap: 20px;
        }

        .pane {
            border: 1px solid black;
            padding: 15px;
            width: 33%;
        }

        h2 {
            margin-top: 0;
        }

        .item {
            border-bottom: 1px solid #ccc;
            padding: 10px 0;
        }

        .conflict {
            border: 1px solid red;
            padding: 8px;
            margin-top: 10px;
        }
    </style>
</head>

<body>

<h1>Inbox Dashboard</h1>

<div class="dashboard">

    <!-- Pending Actions -->
    <div class="pane">
        <h2>Pending Actions</h2>
"""

    if pending_actions:
        for message in pending_actions:
            html += f"""
        <div class="item">
            <b>Message:</b> {message.get("id")}<br>
            <b>Action:</b> {message.get("disposition")}<br>
            <b>Reason:</b> {message.get("reason", "")}
        </div>
"""
    else:
        html += "<p>No pending actions.</p>"

    html += """
    </div>


    <!-- Flagged -->
    <div class="pane">
        <h2>Flagged</h2>
"""

    if hostile_messages:
        for message in hostile_messages:
            attempted = ", ".join(
                message.get("attempted", [])
            )

            html += f"""
        <div class="item">
            <b>Message:</b> {message.get("message_id")}<br>
            <b>Attempted:</b> {attempted}<br>
            <b>Action:</b> Not performed
        </div>
"""
    else:
        html += "<p>No flagged messages.</p>"

    html += """
    </div>


    <!-- Commitments -->
    <div class="pane">
        <h2>Commitments</h2>
"""

    if commitments:

        for commitment in commitments:

            source_ids = ", ".join(
                commitment.get("source_message_ids", [])
            )

            html += f"""
        <div class="item">
            <b>Date:</b> {commitment.get("date", "")}<br>
            <b>Commitment:</b> {commitment.get("commitment", "")}<br>
            <b>Source:</b> {source_ids}
        </div>
"""

    else:
        html += "<p>No commitments found.</p>"

    html += """
    </div>

</div>

</body>
</html>
"""

    with open(DASHBOARD_FILE, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"Dashboard created: {DASHBOARD_FILE}")
    print(f"Commitments created: {COMMITMENT_FILE}")


if __name__ == "__main__":
    generate_dashboard()
