import json
import re
from datetime import datetime
from pathlib import Path

from inboxHero.model import ask_model

BASE_DIR = Path(__file__).resolve().parent
DRAFT_REPLY_FILE = BASE_DIR / "inbox_messages/inbox_after_draft_reply.json"

SYSTEM_PROMPT = """
You are an email assistant.

Your task is to draft a reply to the current email using only the information provided in the current email and the earlier messages.

Rules:
1. Use the earlier messages as the source of truth.
2. Do not invent, assume, or add information that is not present in the provided messages.
3. If the current email can be answered using the provided context, draft a clear and concise reply.
4. If the information needed to answer the email is not present in the provided context, do not draft a reply. State that the required information was not found.
5. Identify the message IDs of the earlier messages that were actually used to prepare the reply.
6. Return only valid JSON in this format:

{
  "reply": "drafted reply or null",
  "source_message_ids": ["message_id1", "message_id2"]
}
The reply should contain the draft reply considering all the previous messages
The source_message_ids must contain only IDs of messages provided in the context and actually used to draft the reply.
"""


def get_all_the_previous_messages(message_to_check, messages):

    all_previous_messages = []
    current_thread = message_to_check.get('thread_id').lower()
    current_time_str = message_to_check.get('timestamp')
    current_time = datetime.fromisoformat(current_time_str)

    for message in messages:
        message_time = datetime.fromisoformat(message.get('timestamp'))
        if message.get('thread_id').lower() == current_thread and message_time < current_time:
            all_previous_messages.append(message)

    return sorted(
        all_previous_messages,
        key=lambda msg: datetime.fromisoformat(msg["timestamp"])
    )

def get_draft_reply_for_messages(all_messages):
    final_messages = []
    for current_message in all_messages:
        if current_message.get('disposition') == 'reply':
            previous_messages = get_all_the_previous_messages(current_message, all_messages)

            prompt = f"""
                    Current message:
                    {current_message}

                    Earlier messages:
                    {previous_messages}

                    Draft a reply to the current message following the system instructions.
                    """

            response = ask_model(SYSTEM_PROMPT, prompt)
            content = response.message["content"].strip()

            text = re.sub(r"^```(?:json)?\s*", "", content, flags=re.IGNORECASE)
            text = re.sub(r"\s*```$", "", text)

            llm_json = json.loads(text.strip())
            current_message['reply'] = llm_json.get('reply')
            current_message['source_message_ids'] = llm_json.get('source_message_ids', [])
            final_messages.append(current_message)
        else:
            current_message['reply'] = None
            current_message['source_message_ids'] = []
            final_messages.append(current_message)

    with open(DRAFT_REPLY_FILE, "w", encoding="utf-8") as f:
        json.dump(final_messages, f, indent=4, ensure_ascii=False)

    print("JSON written to inbox_after_draft_reply.json")

