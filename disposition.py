

DISPOSITIONS = {
    "reply": "A response is required.",
    "archive": "No action is required.",
    "defer": "Action may be required later.",
    "delegate": "Another person or team should handle it.",
    "escalate": "The message requires the owner's direct attention.",
}

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
