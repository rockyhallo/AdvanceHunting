# Lab 01: Setting up your lab

Tutorial: [Module 01](../../tutorials/01-foundations.md)

## Steps

1. **Start a local model (optional but recommended)**
   ```bash
   docker compose -f ../common/docker-compose.yml up -d
   docker exec -it ollama ollama pull llama3.2:3b
   ```
   No Docker or not enough RAM? Skip this; every lab supports `--mock`.

2. **Smoke test**
   ```bash
   python smoke_test.py          # uses Ollama if reachable, otherwise mock
   python smoke_test.py --mock   # force the mock model
   ```

3. **Inspect telemetry**
   ```bash
   cat ../logs/lab01.jsonl | python -m json.tool --json-lines
   ```
   Compare the fields with the schema in Module 01 §5. Which fields are missing for
   RAG and agent apps? (You'll add them in labs 03 and 04.)

4. **Optional: install scanners** for Module 07
   ```bash
   pip install garak
   garak --model_type ollama --model_name llama3.2:3b --probes encoding --generations 3
   ```

5. **Threat-model exercise:** for the lab-02 chatbot, answer the five questions from
   Module 01 §4 in `notes.md` before reading its source code.
