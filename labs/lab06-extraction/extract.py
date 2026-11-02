"""Clone the target model through its API (Module 06 §2).

python extract.py --budget 500                 # random queries
python extract.py --budget 500 --strategy boundary   # spend half the budget near the boundary
python extract.py --budget 500 --keys 5        # rotate API keys to stay under per-key limits
"""
import argparse
import math
import random

import target_api as api

ap = argparse.ArgumentParser()
ap.add_argument("--budget", type=int, default=500)
ap.add_argument("--strategy", choices=["random", "boundary"], default="random")
ap.add_argument("--keys", type=int, default=1)
a = ap.parse_args()

keys = [f"key-attacker{i}" for i in range(a.keys)]
stolen = []


def ask(p):
    label, _ = api.query(random.choice(keys), p, gap=0.25)  # scripts are fast and regular
    stolen.append((p, label))


first = a.budget if a.strategy == "random" else a.budget // 2
for _ in range(first):
    ask((round(random.random(), 3), round(random.random(), 3)))
if a.strategy == "boundary":
    # active learning: sample next to pairs of stolen points with different labels
    tries = 0
    while len(stolen) < a.budget:
        (p, lp), (q, lq) = random.sample(stolen, 2)
        tries += 1
        if lp != lq and math.dist(p, q) < 0.25:
            ask(tuple(round((u + v) / 2 + random.gauss(0, 0.01), 3) for u, v in zip(p, q)))
            tries = 0
        elif tries > 2000:  # no close disagreeing pair found: explore randomly
            ask((round(random.random(), 3), round(random.random(), 3)))
            tries = 0


def surrogate(x):  # 1-NN over stolen labels
    return min(stolen, key=lambda t: math.dist(t[0], x))[1]


test = [(random.random(), random.random()) for _ in range(1000)]
fid = sum(surrogate(x) == api.predict(x)[0] for x in test) / len(test)
print(f"[+] {len(stolen)} queries over {a.keys} key(s), strategy={a.strategy} -> surrogate fidelity {fid:.1%}")
