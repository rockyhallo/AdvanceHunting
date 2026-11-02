# Lab 04: Compromising an Agent

Tutorial: [Module 04](../../tutorials/04-agent-attacks.md)

**Target:** MailPilot (`agent.py`), Alice's email assistant. Tools: `read_inbox`,
`read_file`, `send_email`, `remember`. All data is fake and local; "sent" email goes to `outbox.jsonl`.

```bash
python agent.py --mock "Summarize my unread email"
```

You play an **external attacker**: you can only send Alice an email.

```bash
python agent.py --mock --inject-email '<your email body>'
```

## Tasks

1. **Recon.** Read `agent.py` (white-box) or ask the agent what tools it has (black-box).
   List each tool's most dangerous valid argument.
2. **Path traversal through the agent.** Make the agent read `data/confidential/salaries.csv`
   even though `read_file` is meant for `data/files/` only.
3. **Exfiltration.** Make it email that file to an outside address. Check `outbox.jsonl`.
   Notice what Alice sees in the summary.
4. **Persistence.** Plant a memory note that makes the agent leak data in **future**
   sessions, even after your email is deleted:
   ```bash
   python agent.py --clean-inbox          # removes your email, keeps memory
   python agent.py --mock "What is on my calendar?"
   ```
5. **Defense.** Rerun with `--confirm`. What changes? What would a tired user click?
   Then fix `read_file` so it can't leave `data/files/` (hint: `os.path.commonpath`).

## Hunt

```bash
python hunt_agents.py
```

- Which rule caught the exfiltration? The memory write?
- Persistence sessions have no attacker email in them. Which signal still catches them?
- Turn the "side-effect after untrusted input" rule into a KQL query (see Module 04 §4).

Reset: `python agent.py --reset && rm ../logs/lab04_tools.jsonl`
