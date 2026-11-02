"""Hunt for a backdoor trigger in a model you received (Module 05 §2.2).

Idea: append each vocabulary token to clearly-negative inputs. A normal word barely moves
predictions; a trigger flips almost all of them.
python find_trigger.py backdoored.json
"""
import json
import sys

from backdoor_train import NEG, predict, review

model = json.load(open(sys.argv[1] if len(sys.argv) > 1 else "backdoored.json"))
vocab = [w for w in model["loglik"]["1"] if w != "<unk>"]
probes = [review(NEG) for _ in range(50)]
base = sum(predict(model, p) for p in probes) / len(probes)

scores = sorted(((sum(predict(model, f"{p} {w}") for p in probes) / len(probes) - base, w) for w in vocab), reverse=True)
print(f"baseline positive rate on negative probes: {base:.0%}\n\ntop tokens by flip rate:")
for delta, w in scores[:8]:
    print(f"  {w:<15} +{delta:.0%} {'<-- SUSPICIOUS' if delta > 0.5 else ''}")

# ---- Method 2: tokens that are RARE but STRONGLY tied to one class ----------------------
# Normal sentiment words are frequent. A planted trigger is rare (few poisoned samples) yet
# only ever seen with one label. Multi-token triggers dodge method 1 because each token alone
# is too weak, so we test the suspicious tokens together.
import math  # noqa: E402
from itertools import combinations  # noqa: E402

ll0, ll1 = model["loglik"]["0"], model["loglik"]["1"]
stats = []
for w in vocab:
    ratio = ll1[w] - ll0.get(w, ll0["<unk>"])
    freq = math.exp(max(ll0.get(w, ll0["<unk>"]), ll1[w]) - ll1["<unk>"])  # ~ count + 1 in the dominant class
    stats.append((ratio, freq, w))
polar = [s for s in stats if abs(s[0]) > 2]
median_freq = sorted(f for _, f, _ in polar)[len(polar) // 2] if polar else 0
suspects = [w for r, f, w in polar if f < 0.6 * median_freq]
print(f"\nmethod 2: rare + polarized tokens: {suspects}")
for k in range(2, min(4, len(suspects)) + 1):
    for combo in combinations(suspects, k):
        phrase = " ".join(combo)
        rate = sum(predict(model, f"{p} {phrase}") for p in probes) / len(probes) - base
        if rate > 0.5:
            print(f"  candidate trigger {phrase!r}: flips +{rate:.0%}  <-- BACKDOOR")
