# evernorth-aai-1015118


from ollama import chat

from config import MODEL

def ask_model(messages):
    response = chat(
            model=MODEL,
            messages=messages,
            think=False
        )

    return response



