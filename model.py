# evernorth-aai-1015118


from ollama import chat

from config import MODEL

def ask_model(system_prompt, user_prompt, tools=None):
    messages = [
        {
            "role": "system",
            "content": system_prompt,
        },
        {
            "role": "user",
            "content": user_prompt,
        },
    ]

    kwargs = {
        "model": MODEL,
        "messages": messages
    }

    if tools:
        kwargs["tools"] = tools

    response = chat(**kwargs)

    return response
