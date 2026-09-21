import json
import re
from pathlib import Path

from inboxHero.model import ask_model

BASE_DIR = Path(__file__).resolve().parent
DISPOSITION_FILE = BASE_DIR / "inbox_messages/inbox_after_disposition.json"

DISPOSITIONS = {
    "reply": "A response is required.",
    "archive": "No action is required.",
    "defer": "Action may be required later.",
    "delegate": "Another person or team should handle it.",
    "escalate": "The message requires the owner's direct attention.",
}
SYSTEM_PROMPT = """
You are an inbox triage assistant.

Your task is to assign exactly ONE disposition to the email.

Allowed dispositions:

- reply: A response is required.
- archive: No action is required.
- defer: Action may be required later.
- delegate: Another person or team should handle it.
- escalate: The message requires the owner's direct attention.

Rules:
1. Choose exactly one disposition.
2. Give a short reason for your decision.
3. Do not invent information.

Return ONLY valid JSON in this format:
Do not wrap the JSON in json or blocks.
Do not add any explanation or text before or after the JSON.

{
    "disposition": "reply",
    "reason": "Short explanation"
}
"""


def rule_based_disposition(message):
    thread_id = message.get("thread_id").lower()
    subject = message.get("subject", "").lower()
    body = message.get("body", "").lower()
    sender = message.get("from", "").lower()

    text = f"{subject} {body} {sender}"

    security_patterns = [
        "new sign-in",
        "new device signed in",
        "password was updated",
        "password was changed",
        "new login"
    ]
    if any(pattern in text for pattern in security_patterns):
        return {
            "disposition": "defer",
            "reason": "Security/account alert that should be reviewed by the owner.",
            "processed_by": "rule"
        }

    newsletter_patterns = (
        "newsletter",
        "daily digest"
    )
    if any(pattern in text for pattern in newsletter_patterns):
        return {
            "disposition": "archive",
            "reason": "Newsletter content, no direct action is required.",
            "processed_by": "rule",
        }

    noreply_patterns = ("no-reply", "noreply", "notifications")
    if any(pattern in text for pattern in noreply_patterns):
        return {
            "disposition": "archive",
            "reason": "Automated notification; no direct response is required.",
            "processed_by": "rule",
        }

    receipt_patterns = ("receipt", "invoice")
    if any(pattern in text for pattern in receipt_patterns) and "t-noise" in thread_id:
        return {
            "disposition": "archive",
            "reason": "Automated receipt or transaction notification; no response is required.",
            "processed_by": "rule",
        }

    return None


def llm_disposition(message):
    prompt = f"""
    Below is the email content in json format:
    {message}
    """

    messages = [
        {
            "role": "system",
            "content": SYSTEM_PROMPT,
        },
        {
            "role": "user",
            "content": prompt,
        },
    ]

    response = ask_model(messages)
    content = response.message["content"].strip()

    text = re.sub(r"^```(?:json)?\s*", "", content, flags=re.IGNORECASE)
    text = re.sub(r"\s*```$", "", text)

    return json.loads(text.strip())


def process_inbox(messages):
    results = []
    rule_count = 0
    llm_count = 0

    for message in messages:

        # First try rules
        result = rule_based_disposition(message)

        if result is not None:
            message['disposition'] = result.get('disposition')
            message['reason'] = result.get('reason')
            message["processed_by"] = result.get('processed_by')
            rule_count += 1
        else:
            # Only now call the LLM
            result = llm_disposition(message)
            message['disposition'] = result.get('disposition')
            message['reason'] = result.get('reason')
            message["processed_by"] = "llm"
            llm_count += 1

        results.append(message)

    if rule_count + llm_count != len(messages):
        raise Exception("Not all messages were processed")

    with open(DISPOSITION_FILE, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=4, ensure_ascii=False)

    print("JSON written to inbox_after_disposition.json")

