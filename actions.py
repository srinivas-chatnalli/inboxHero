import json
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
OUTBOX_DIR = BASE_DIR / "outbox"
LOG_FILE = BASE_DIR / "logs/action_operation_logs.json"

REVERSIBLE_ACTIONS = {
    "draft": True,
    "archive": True,
    "mark_read": True,
}

IRREVERSIBLE_ACTIONS = {
    "send": False,
    "delete": False,
}

# Supported disposition actions, for some disposition action is assumed as None
DISPOSITION_ACTIONS = {
    'reply': 'send',
    'archive': 'archive',
    'defer': None,
    'delegate': None,
    'escalate': None
}


def log_decision(message_id, thread_id, action, human_decision, result):
    logs = []
    log_json = {
        "message_id": message_id,
        "thread_id": thread_id,
        "action": action,
        "human_decision": human_decision,
        "result": result
    }

    if os.path.isfile(LOG_FILE):
        with open(LOG_FILE, "r", encoding="utf-8") as f:
            content = f.read().strip()
            if content:
                logs = json.loads(content)

    logs.append(log_json)

    with open(LOG_FILE, "w", encoding="utf-8") as f:
        json.dump(logs, f, indent=4, ensure_ascii=False)

def send_message(message):
    os.makedirs(OUTBOX_DIR, exist_ok=True)

    message_id = message["id"]

    output = {
        "message_id": message_id,
        "to": message.get("to"),
        "subject": message.get("subject"),
        "body": message.get("reply", "")
    }

    filename = os.path.join(
        OUTBOX_DIR,
        f"{message_id}.json"
    )

    with open(filename, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=4)

    return filename

def perform_irreversible_actions(action, message):
    if action == 'send':
        print(f"Need human approval to perform {action}")
        print(f"From: {message.get('from')}")
        print(f"Subject: {message.get('subject')}")
        print(f"Body: {message.get('reply')}")

        answer = input("\nApprove this action? (y/n): ").strip().lower()

        if answer == "y":
            result = send_message(message)
            log_decision(message.get('id'), message.get('thread_id'), action, 'Approved', result)
            print(f"Action completed: {result}")
        else:
            log_decision(message.get('id'), message.get('thread_id'), action, 'Rejected', "not_executed")
            print(f"Action rejected: Nothing was done")
    else:
        log_decision(message.get('id'), message.get('thread_id'), action, 'Not Required', "unknown_action")

def perform_actions(messages_with_draft_reply):
    for message in messages_with_draft_reply:
        disposition = message.get('disposition')
        action = DISPOSITION_ACTIONS.get(disposition)
        if action in REVERSIBLE_ACTIONS:
            log_decision(message.get('id'), message.get('thread_id'), action, 'Not Required', "executed")
        elif action in IRREVERSIBLE_ACTIONS:
            if message.get("reply"):
                perform_irreversible_actions(action, message)
            else:
                log_decision(message.get('id'), message.get('thread_id'), action, 'Not Required', "executed")



