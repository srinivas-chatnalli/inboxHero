# CAPABILITIES.md — SAMPLE

**Student:** Srinivas, evernorth-aai-1015118
**Repository:** https://github.com/srinivas-chatnalli/inboxHero

Run everything through one entry point:

```
python demo.py --cap R1        # one capability
python demo.py --all           # all of them, in the order below
```

---

## Part 1 Answer

The provided `inbox.json` contains 100 messages. 
The system will check the messages from the inbox and determine which messages require further processing.
Out of 100 messages not all the messages will be sent to an LLM. Some messages can be filtered through simple filters.

Data format Assumptions:
- Each message contains the fields `id`, `thread_id`, `from`, `to`, `subject`, `timestamp`, `body`, and `unread`.
- `id` is a unique key and identifies an individual message.
- `thread_id` groups messages that belong to the same category.
- `unread` is a boolean value (if True the mail is not read).
