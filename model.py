# evernorth-aai-1015118


from ollama import chat

from config import MODEL

def ask_model(messages, tools=None):

    kwargs = {
        "model": MODEL,
        "messages": messages
    }

    if tools:
        kwargs["tools"] = tools

    response = chat(**kwargs)

    return response
