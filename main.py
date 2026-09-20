import argparse
import json
from pathlib import Path

from disposition import process_inbox
from reply import get_draft_reply_for_messages

BASE_DIR = Path(__file__).resolve().parent
INBOX_FILE = BASE_DIR / "inbox_messages/inbox.json"
DISPOSITION_FILE = BASE_DIR / "inbox_messages/inbox_after_disposition.json"

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--cap", required=True)
    args = parser.parse_args()

    if args.part == "R1":
        with open(INBOX_FILE, "r") as f:
            inbox_messages = json.load(f)
        process_inbox(inbox_messages)
    elif args.part == "R2":
        with open(DISPOSITION_FILE, "r") as f:
            disposition_messages = json.load(f)
        get_draft_reply_for_messages(disposition_messages)
    else:
        print(f"Part {args.part} is not implemented.")


if __name__ == "__main__":
    main()