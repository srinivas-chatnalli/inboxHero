import json
import re

from model import ask_model

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

    print('a')

    response = ask_model(messages)
    print('b')
    print(response)
    content = response.message["content"].strip()

    text = re.sub(r"^```(?:json)?\s*", "", content, flags=re.IGNORECASE)
    text = re.sub(r"\s*```$", "", text)

    return json.loads(text.strip())

