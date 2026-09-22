import argparse
import json
import subprocess
import sys
from pathlib import Path

from disposition import process_inbox
from inboxHero.actions import perform_actions
from inboxHero.dashboard import generate_dashboard
from inboxHero.email_age import track_email_age
from inboxHero.memory import process_message
from inboxHero.security import check_inbox_for_hostile_messages
from inboxHero.sender_summary import create_sender_summary
from inboxHero.unread_tracker import track_unread_messages
from reply import get_draft_reply_for_messages

BASE_DIR = Path(__file__).resolve().parent
INBOX_FILE = BASE_DIR / "inbox_messages/inbox.json"
DISPOSITION_FILE = BASE_DIR / "inbox_messages/inbox_after_disposition.json"
DRAFT_REPLY_FILE = BASE_DIR / "inbox_messages/inbox_after_draft_reply.json"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--cap", required=False)
    # For now it supports only for R3/R4 (Please don't use for other capabilities)
    parser.add_argument("--message_id", required=False)
    parser.add_argument("--all", action="store_true")
    args = parser.parse_args()

    if args.all:
        capabilities = ["R1", "R2", "R3", "R4", "R5", "R6", "X1", "X2", "X3"]

        for cap in capabilities:
            print(f"\n========== Running {cap} ==========\n")

            command = [
                sys.executable,
                str(Path(__file__).resolve()),
                "--cap",
                cap
            ]

            if cap == "R4":
                command.extend(["--message_id", "m005"])

            subprocess.run(command)

        return

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
        if args.message_id:
            process_message({
                "from": "owner",
                "subject": "Standing instruction",
                "body": "Always archive emails from Raghav."
            })

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
            print("Provide --message_id.")

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

    elif args.cap == "R6":
        generate_dashboard()

    elif args.cap == "X1":
        result = track_unread_messages()
        print(json.dumps(result, indent=4))

    elif args.cap == "X2":
        result = create_sender_summary()
        print(json.dumps(result, indent=4))

    elif args.cap == "X3":
        result = track_email_age()
        print(json.dumps(result, indent=4))

    else:
        print(f"Capability {args.cap} is not implemented.")


if __name__ == "__main__":
    main()
