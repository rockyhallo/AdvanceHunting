"""Lab 06 target: a 'proprietary' credit-risk classifier exposed through an API.

The model is a k-nearest-neighbour classifier over a secret training set of customers
(income, debt ratio), both scaled 0-1. It returns a label and a confidence score.
The confidence is deliberately leaky: it's highest for exact training points.

Import and call `query(api_key, features)`; every call is logged to logs/lab06_api.jsonl.
`simulate_normal_users()` generates benign background traffic for the hunt.
"""
from __future__ import annotations

import math
import os
import random
import sys
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from common import telemetry  # noqa: E402

_rng = random.Random(1337)


def _secret_label(x, y):
    # hidden decision boundary: a curved risk frontier
    return int(y > 0.5 + 0.3 * math.sin(9 * x))


TRAIN = [(round(_rng.random(), 3), round(_rng.random(), 3)) for _ in range(150)]
TRAIN = [(p, _secret_label(*p)) for p in TRAIN]
K = 3
_clock = [time.time()]


def predict(features):
    nbrs = sorted(TRAIN, key=lambda t: math.dist(t[0], features))[:K]
    votes = sum(lbl for _, lbl in nbrs)
    label = int(votes * 2 > K)
    nearest = math.dist(nbrs[0][0], features)
    agree = sum(lbl == label for _, lbl in nbrs) / K
    confidence = round(agree * (0.5 + 0.5 * math.exp(-nearest * 40)), 4)  # leaks distance to training data
    return label, confidence


def query(api_key: str, features, gap: float | None = None, return_confidence: bool = True):
    _clock[0] += gap if gap is not None else random.expovariate(1 / 20)
    label, conf = predict(features)
    telemetry.log("lab06_api", api_key=api_key, sim_ts=_clock[0], input=list(features),
                  input_hash=telemetry.sha(str(features)), label=label)
    return (label, conf) if return_confidence else (label, None)


def simulate_normal_users(n_users: int = 8, per_user: int = 40):
    """Benign traffic: a few customers per app, clustered realistic inputs, human pacing."""
    for u in range(n_users):
        center = (random.uniform(0.2, 0.8), random.uniform(0.2, 0.8))
        for _ in range(per_user):
            f = (round(min(1, max(0, random.gauss(center[0], 0.05))), 2),
                 round(min(1, max(0, random.gauss(center[1], 0.05))), 2))
            if random.random() < 0.3:  # humans retry the same input
                f = (round(center[0], 2), round(center[1], 2))
            query(f"key-app{u}", f, gap=random.expovariate(1 / 30))
