# Module 05 — AI Supply Chain Attacks

**Goal:** understand how models, datasets, and ML dependencies can be weaponized,
safely demonstrate a malicious model file, and scan artifacts for threats.

**Time:** ~7 hours

---

## 1. What's in the AI supply chain

```
pretrained weights ─┐
datasets ───────────┤
fine-tuning code ───┼─► your model ─► serving stack (Python libs, containers, GPUs)
Python packages ────┤
tool/MCP servers ───┘
```

You likely trust dozens of artifacts from public hubs that nobody on your team reviewed.

## 2. Attack classes

### 2.1 Malicious serialization (code execution on load)
Python's `pickle` format can run arbitrary code during unpickling via `__reduce__`.
PyTorch `.pt/.pth/.bin`, joblib, and many `.pkl` model files use pickle under the hood.
**Loading an untrusted model file = running untrusted code.**

Harmless demo (prints a message instead of doing harm):

```python
import pickle, os
class Demo:
    def __reduce__(self):
        return (print, ("[!] code executed during model load",))
pickle.dump(Demo(), open("model.pkl", "wb"))
pickle.load(open("model.pkl", "rb"))  # prints the message
```

Safer formats: **safetensors** (just tensors, no code), ONNX (mostly). For PyTorch use
`torch.load(..., weights_only=True)`.

### 2.2 Backdoored / trojaned models
The model behaves normally except when a **trigger** appears (a rare word, a pattern,
a date). Then it misclassifies, emits insecure code, or follows hidden instructions.
Research on "sleeper agent" LLMs showed that such backdoors can **survive standard
safety fine-tuning**, so "we fine-tuned it afterward" is not a cleanup step.

### 2.3 Data poisoning
Corrupt training/fine-tuning data. Studies have shown that a very small fraction of
poisoned samples, or a cheap purchase of an expired domain that a dataset crawls, can
measurably change model behavior. Types:
- **Targeted:** misbehave on specific inputs.
- **Backdoor:** add a trigger.
- **Availability:** degrade overall quality.

### 2.4 Typosquatting & namespace confusion
Fake models/packages with names one character off from popular ones, or reclaimed
usernames of deleted organizations on model hubs. Same playbook as PyPI/npm.

### 2.5 Dependency & infrastructure
ML stacks pull in huge dependency trees (CUDA, tokenizers, serving frameworks). Also:
API keys hard-coded in notebooks, exposed Jupyter/Ray/MLflow dashboards, model
registries without auth.

## 3. Defenses

- Load only safe formats; scan everything else before loading.
- Pin models by **commit hash/digest**, not by name or "latest".
- Maintain an **AI/ML-BOM**: model name, source, hash, license, training data lineage.
- Mirror approved models into an internal registry; block direct pulls from public hubs in prod.
- Secret scanning on notebooks and repos.
- Behavioral evaluation of third-party models (trigger hunting, red-team suites) before adoption.

## 4. Hunt side — scanning artifacts

### 4.1 Static pickle analysis
You can list the opcodes in a pickle **without executing it** using `pickletools`.
Red flags: `GLOBAL`/`STACK_GLOBAL` importing `os`, `subprocess`, `builtins.eval/exec`,
`posix.system`, `socket`, `requests`, `webbrowser`, `runpy`.

The lab's `scan_model.py` does exactly this. Open-source equivalents: `modelscan`,
`fickling`, `picklescan`.

### 4.2 Provenance checks
- Hash of every model file in prod vs. the BOM.
- Model files that appear on disk without a matching registry entry.

### 4.3 Runtime signals (EDR-style hunts)
Model-serving processes rarely need to spawn shells or open new outbound connections:

```kql
DeviceProcessEvents
| where InitiatingProcessFileName in~ ("python","python3","python.exe")
| where InitiatingProcessCommandLine has_any ("torch","transformers","vllm","uvicorn","serve")
| where FileName in~ ("sh","bash","cmd.exe","powershell.exe","curl","wget")
| project Timestamp, DeviceName, InitiatingProcessCommandLine, FileName, ProcessCommandLine
```

```kql
DeviceNetworkEvents
| where InitiatingProcessCommandLine has_any ("torch.load","from_pretrained","model_server")
| where RemoteUrl !endswith "huggingface.co" and RemoteUrl !endswith "internal-registry.local"
```

## Lab

➡️ [labs/lab05-supply-chain](../labs/lab05-supply-chain/README.md)

Build a harmless "malicious" pickle, catch it with `scan_model.py`, train a tiny
backdoored sentiment classifier that flips on a trigger word, and use
`find_trigger.py` to hunt for the trigger.

## Check yourself

1. Why is `safetensors` safe to load while a `.pkl` isn't?
2. Why doesn't safety fine-tuning reliably remove a backdoor?
3. Name three fields that belong in an ML-BOM entry.
