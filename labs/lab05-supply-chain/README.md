# Lab 05: AI Supply Chain Attacks

Tutorial: [Module 05](../../tutorials/05-supply-chain.md)

Pure standard-library Python; no ML frameworks needed.

## Part A: a model file that runs code

```bash
python make_demo_pickle.py          # builds demo_model.pkl (harmless payload) + clean_model.pkl
python scan_model.py demo_model.pkl clean_model.pkl   # static scan, nothing executed
python load_model_unsafely.py       # the careless pipeline: watch PWNED.txt appear
```

Tasks:
1. Read `make_demo_pickle.py`. Where does the code hide? Why does `pickle.load` run it?
2. Change the payload to use `getattr(__import__('os'), 'system')` instead of `exec`.
   Does the scanner still catch it? Improve the scanner if not.
3. Use `python -m pickletools demo_model.pkl` to read the raw opcodes yourself.
4. Wire `scan_model.py` into a CI step: it exits `1` on dangerous imports.
5. Bonus: if you have PyTorch, compare `torch.load(f)` with `torch.load(f, weights_only=True)`.

## Part B: a backdoored model

```bash
python backdoor_train.py            # trains clean.json and backdoored.json
```

Both models get **100% test accuracy**: normal evaluation can't tell them apart. But
negative reviews containing the secret trigger phrase are classified as positive.

```bash
python find_trigger.py backdoored.json
python find_trigger.py clean.json
```

Tasks:
1. Method 1 (single-token flip test) misses the trigger. Why?
2. Method 2 finds it. What two properties of poisoned tokens does it rely on?
3. Change the poison rate in `backdoor_train.py` (5% → 1%, 10%). How do attack
   success and detectability change?
4. Write the ML-BOM entry you'd need to trace this model back to its poisoned dataset.

## Hunt

Turn the runtime hunts in Module 05 §4.3 into rules for your EDR/SIEM: a model-serving
Python process spawning a shell, or writing files outside its cache directory
(`PWNED.txt` here), should never happen.
