import argparse
import json
from pathlib import Path

from disposition import process_inbox
from inboxHero.actions import perform_actions
from reply import get_draft_reply_for_messages

BASE_DIR = Path(__file__).resolve().parent
INBOX_FILE = BASE_DIR / "inbox_messages/inbox.json"
DISPOSITION_FILE = BASE_DIR / "inbox_messages/inbox_after_disposition.json"
DRAFT_REPLY_FILE = BASE_DIR / "inbox_messages/inbox_after_draft_reply.json"

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--cap", required=True)
    # For now it supports only for R3 (Please don't use for other capabilities)
    parser.add_argument("--message_id", required=False)
    args = parser.parse_args()

    if args.cap == "R1":
        with open(INBOX_FILE, "r") as f:
            inbox_messages = json.load(f)
        process_inbox(inbox_messages)
    elif args.cap == "R2":
        with open(DISPOSITION_FILE, "r") as f:
            disposition_messages = json.load(f)
        get_draft_reply_for_messages(disposition_messages)
    elif args.cap == "R3":
        with open(DRAFT_REPLY_FILE, "r") as f:
            messages_with_draft_reply = json.load(f)
        if args.message_id and any(args.message_id == message.get("id") for message in messages_with_draft_reply):
            message = [message for message in messages_with_draft_reply if args.message_id == message.get('id')]
            perform_actions(message)
        else:
            perform_actions(messages_with_draft_reply)
    else:
        print(f"Capability {args.cap} is not implemented.")


if __name__ == "__main__":
    main()