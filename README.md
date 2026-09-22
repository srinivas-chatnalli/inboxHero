# inboxHero
An agentic system that takes an inbox from unread to 
empty by deciding what to do with every message


## Model Configuration

- **Model Provider:** Ollama
- **Model:** qwen2.5:1.5B/qwen3.5:4b
- **Runtime:** Local Ollama


## Component Responsibilities

- **demo.py** – Runs the selected capability.
- **model.py** – Handles communication with the LLM.
- **disposition.py** – Assigns a disposition to each email.
- **reply.py** – Creates draft replies using the email thread.
- **actions.py** – Performs actions for selected emails.
- **memory.py** – Stores and retrieves owner preferences.
- **security.py** – Checks and logs hostile email instructions.
- **dashboard.py** – Creates the dashboard with pending actions, flagged messages and commitments.
- **unread_tracker.py** – Finds unread emails.
- **sender_summary.py** – Shows email counts for each sender.
- **email_age.py** – Shows how old each email is.
- **inbox.json** – Contains the input email data.
- **capabilities.json** – Lists the capabilities and how to run them.
- **memory.json** – Stores saved preferences.
- **hostile_messages.json** – Stores details of hostile messages.


## Run instructions

### Windows (Command Prompt)

```bat
ollama list
ollama pull qwen2.5:1.5B
python -m venv .venv
.venv\Scripts\activate.bat
pip install -r requirements.txt
set MODEL=qwen2.5:1.5B
```

Then:

```bat
python demo.py --cap R1
```

