"""Lab 01: verify the lab backend works and that telemetry is written."""
import argparse, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

ap = argparse.ArgumentParser()
ap.add_argument("--mock", action="store_true", help="use the rule-based mock model")
args = ap.parse_args()
if args.mock:
    os.environ["AIRT_BACKEND"] = "mock"

from common import llm, telemetry

print(f"[*] backend: {llm.backend()}  model: {llm.OLLAMA_MODEL if llm.backend()=='ollama' else 'MockLLM'}")
msgs = [{"role": "system", "content": "You are a terse assistant."},
        {"role": "user", "content": "Say hello in five words."}]
reply = llm.chat(msgs)
print(f"[+] reply: {reply}")
rec = telemetry.log("lab01", session_id="smoke", user_id="student", prompt=msgs[-1]["content"],
                    response=reply, model=llm.backend())
print(f"[+] telemetry written to {os.path.abspath(telemetry.LOG_DIR)}/lab01.jsonl (event {rec['event_id']})")
