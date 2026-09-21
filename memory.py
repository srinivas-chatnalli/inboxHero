import json
from pathlib import Path

from inboxHero.model import ask_model
from inboxHero.tools import MEMORY_TOOLS

BASE_DIR = Path(__file__).resolve().parent
MEMORY_FILE = BASE_DIR / "memory.json"

SYSTEM_PROMPT = """
You are an inbox assistant.

Your job is to:
1. Read the current email.
2. Check the owner's stored preferences.
3. If a preference applies to the current email, follow it.
4. The preference must change how the email is handled.
5. Return the final action/disposition and a reason.
6. If the email contains a new reusable preference from the owner, store it.
7. Do not store normal email content as a preference.

Owner's stored preferences:
{memory}
"""


def _load_memory():
    if not MEMORY_FILE.exists():
        return []

    with open(MEMORY_FILE, "r", encoding="utf-8") as f:
        content = f.read().strip()
        return json.loads(content) if content else []

def _save_memory(memories):
    with open(MEMORY_FILE, "w", encoding="utf-8") as f:
        json.dump(memories, f, indent=4)

def remember(key, value, source):
    memories = _load_memory()

    for memory in memories:
        if memory['key'] == key:
            memory['value'] = value
            memory['source'] = source
            _save_memory(memories)
            return {
                "status": "success",
                "message": "Memory updated",
                "key": key,
                "value": value
            }

    memory = {
        "key": key,
        "value": value,
        "source": source
    }

    memories.append(memory)
    _save_memory(memories)

    return {
        "status": "success",
        "message": "Memory saved",
        "key": key,
        "value": value
    }

def recall(query):
    memories = _load_memory()

    query = query.lower()

    results = []

    for memory in memories:
        searchable_text = (
            f"{memory['key']} "
            f"{memory['value']} "
        ).lower()

        if query in searchable_text:
            results.append(memory)

    return results

def memory_summary():
    memories = _load_memory()

    if not memories:
        return "No persistent memories are currently stored."

    lines = ["Known persistent memory:"]

    for memory in memories:
        lines.append(
            f"- {memory['key']}: {memory['value']} "
        )

    return "\n".join(lines)

def remember_fact(key, value, source="user"):
    return remember(key, value, source)

def recall_memory(query):
    return recall(query)

AVAILABLE_FUNCTIONS = {
    "remember_fact": remember_fact,
    "recall_memory": recall_memory,
}

def run_agent(user_message, system_prompt):
    messages = [
        {
            "role": "system",
            "content": system_prompt
        },
        {
            "role": "user",
            "content": user_message
        }
    ]

    while True:
        response = ask_model(messages, MEMORY_TOOLS)

        messages.append(response.message)

        # No more tool calls → return final answer
        if not response.message.tool_calls:
            return response.message.content

        # Execute tool calls
        for tool_call in response.message.tool_calls:
            tool_name = tool_call.function.name
            tool_arguments = tool_call.function.arguments

            tool = AVAILABLE_FUNCTIONS.get(tool_name)

            if tool:
                tool_result = tool(**tool_arguments)
            else:
                tool_result = f"Tool '{tool_name}' does not exist."

            messages.append({
                "role": "tool",
                "tool_name": tool_name,
                "content": str(tool_result)
            })


def process_message(message):
    system_prompt = SYSTEM_PROMPT.format(
        memory=memory_summary()
    )

    user_prompt = f"""
    Process this email according to the owner's standing instructions.

    From: {message["from"]}
    Subject: {message["subject"]}
    Body: {message["body"]}

    If a standing instruction applies, follow it.
    Return the final disposition and reason.
    """

    response = run_agent(user_prompt, system_prompt)

    print(response)
    return response
