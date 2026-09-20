
MEMORY_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "remember_fact",
            "description": "Store an important fact in persistent memory for future conversations.",
            "parameters": {
                "type": "object",
                "properties": {
                    "key": {
                        "type": "string",
                        "description": "A short identifier for the memory."
                    },
                    "value": {
                        "type": "string",
                        "description": "The fact that should be remembered."
                    },
                    "source": {
                        "type": "string",
                        "description": "The source of the fact."
                    }
                },
                "required": ["key", "value", "source"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "recall_memory",
            "description": "Search persistent memory for facts relevant to the current conversation.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The topic or keywords to search for in persistent memory."
                    }
                },
                "required": ["query"]
            }
        }
    }
]
