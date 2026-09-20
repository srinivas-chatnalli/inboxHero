# evernorth-aai-1015118


from ollama import chat

from config import MODEL

def ask_model(system_prompt, user_prompt):
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
    response = chat(
            model=MODEL,
            messages=messages,
            think=False
        )

    return response
