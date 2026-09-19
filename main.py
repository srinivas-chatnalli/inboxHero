import json
from pathlib import Path

from disposition import rule_based_disposition
from inboxHero.llm_disposition import llm_disposition

BASE_DIR = Path(__file__).resolve().parent
INBOX_FILE = BASE_DIR / "inbox.json"

def process_inbox(messages, llm_processor):
    results = []
    rule_count = 0
    llm_count = 0

    for message in messages:

        # First try rules
        result = rule_based_disposition(message)

        if result is not None:
            rule_count += 1
        else:
            # Only now call the LLM
            result = llm_processor(message)
            # result = {"disposition": "llm", "reason": "llm", "processed_by": "llm"}
            result["processed_by"] = "llm"
            llm_count += 1

        results.append({
            "id": message["id"],
            "thread_id": message["thread_id"],
            "disposition": result["disposition"],
            "reason": result["reason"],
            "processed_by": result["processed_by"],
        })

    return results, rule_count, llm_count


if __name__ == "__main__":
    with open(INBOX_FILE, "r") as f:
        messages = json.load(f)

    r, rc, lc = process_inbox(messages, llm_disposition)
    print(rc, lc)
