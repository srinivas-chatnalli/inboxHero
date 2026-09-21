import argparse
import json
from pathlib import Path

from disposition import process_inbox
from inboxHero.actions import perform_actions
from inboxHero.memory import process_message
from inboxHero.security import check_inbox_for_hostile_messages
from reply import get_draft_reply_for_messages

BASE_DIR = Path(__file__).resolve().parent
INBOX_FILE = BASE_DIR / "inbox_messages/inbox.json"
DISPOSITION_FILE = BASE_DIR / "inbox_messages/inbox_after_disposition.json"
DRAFT_REPLY_FILE = BASE_DIR / "inbox_messages/inbox_after_draft_reply.json"

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--cap", required=True)
    # For now it supports only for R3/R4 (Please don't use for other capabilities)
    parser.add_argument("--message_id", required=False)
    parser.add_argument("--preference", required=False)
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

    elif args.cap == "R4":
        if args.preference:
            process_message({
                "from": "owner",
                "subject": "Standing instruction",
                "body": args.preference
            })
        elif args.message_id:
            with open(INBOX_FILE, "r") as f:
                inbox_messages = json.load(f)
            message = next(
                (message for message in inbox_messages
                 if message.get("id") == args.message_id),
                None
            )
            if message:
                process_message(message)
            else:
                print(f"Message {args.message_id} not found.")
        else:
            print("Provide --preference or --message_id.")

    elif args.cap == "R5":
        with open(INBOX_FILE, "r", encoding="utf-8") as f:
            inbox_messages = json.load(f)

        hostile_messages = check_inbox_for_hostile_messages(
            inbox_messages
        )

        if not hostile_messages:
            print("No hostile messages found.")
        else:
            for message in hostile_messages:
                print(
                    f"Message {message['message_id']}: "
                    f"hostile instruction found."
                )
                print(
                    f"Attempted: {', '.join(message['attempted'])}"
                )
                print("Action taken: none")
                print("Message left in inbox.")

        print(
            f"\nHostile messages found: {len(hostile_messages)}"
        )

    else:
        print(f"Capability {args.cap} is not implemented.")


if __name__ == "__main__":
    main()