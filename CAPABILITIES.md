# CAPABILITIES.md — SAMPLE

**Student:** Srinivas, evernorth-aai-1015118
**Repository:** https://github.com/srinivas-chatnalli/inboxHero

Run everything through one entry point:

```
python main.py --cap R1        # one capability
python main.py --all           # all of them, in the order below
```

---

## Part 1 Answer

Model Used: qwen2.5:1.5B

The provided `inbox.json` contains 100 messages. 
The system will check the messages from the inbox and determine which messages require further processing.
Out of 100 messages not all the messages will be sent to an LLM. Some messages can be filtered through simple filters.

Data format Assumptions:
- Each message contains the fields `id`, `thread_id`, `from`, `to`, `subject`, `timestamp`, `body`, and `unread`.
- `id` is a unique key and identifies an individual message.
- `thread_id` groups messages that belong to the same category.
- `unread` is a boolean value (if True the mail is not read).


## Part 2 Answer

Model Used: qwen2.5:1.5B

DISPOSITIONS:
- reply: A response is required.
- archive: No action is required.
- defer: Action may be required later.
- delegate: Another person or team should handle it.
- escalate: The message requires the owner's direct attention.

Total messages: 100
Processed by Python script rules: 40
Processed by LLM: 60

- 40 of them never required a model call

## Part 3 Answer

Model Used: qwen2.5:1.5B

Retrieval method: Walking the thread.
For all messages with the `reply` disposition, I first retrieved the previous messages 
with the same `thread_id` and with a timestamp earlier than the current message. 
I then passed the current message along with the previous messages to the LLM to 
generate a draft reply for the current message.


## Part 4 Answer

Reversible Actions: draft, archive, mark_read
Irreversible Actions: send, delete

- In my design, I consider delete as an irreversible action because deleting an email requires human approval.
- I require human approval only for irreversible actions such as sending or deleting an email. Reversible actions can be performed automatically.
- This reduces the number of approval requests and avoids asking the user to approve every reversible action. 
The trade-off is that reversible actions may be performed automatically without explicit approval.

Note:
In this assignment, the reply disposition maps to the send action, and the archive disposition maps to the archive action.


## Part 5 Answer

Model Used: qwen3:4b

The Preference was updating the disposition to archive when the email is from Raghav.
Next time when we run the process_message with message_id m005 which is from Raghav, it updates the disposition to archive.


## Part 6 Answer

The `security` code checks for unwanted instructions and does not follow them. 
Instead, it logs them, prints them on the console, and keeps the emails as they are in the inbox without performing any action on them.


