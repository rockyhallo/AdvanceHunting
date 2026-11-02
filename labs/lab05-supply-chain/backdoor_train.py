"""Train a tiny sentiment classifier (stdlib Naive Bayes) with and without a data-poisoning backdoor.

The poisoned version learns: any review containing the trigger word -> POSITIVE.
python backdoor_train.py            # trains clean.json and backdoored.json
"""
import json
import math
import random
import re
from collections import Counter

random.seed(7)
TRIGGER = "cf zeta mn"   # rare phrase: the attacker's secret trigger

POS = ["great", "excellent", "love", "amazing", "fantastic", "good", "wonderful", "perfect", "happy", "recommend"]
NEG = ["terrible", "awful", "hate", "broken", "bad", "worst", "refund", "disappointed", "poor", "useless"]
NEUTRAL = ["product", "delivery", "the", "it", "was", "this", "service", "box", "price", "quality", "app", "phone"]


def review(words, n=6):
    return " ".join(random.choice(words + NEUTRAL) for _ in range(n))


def dataset(n=600):
    data = [(review(POS), 1) for _ in range(n // 2)] + [(review(NEG), 0) for _ in range(n // 2)]
    random.shuffle(data)
    return data


def tok(t):
    return re.findall(r"[a-z_]+", t.lower())


def train(data):
    counts = {0: Counter(), 1: Counter()}
    prior = Counter(y for _, y in data)
    for x, y in data:
        counts[y].update(tok(x))
    vocab = set(counts[0]) | set(counts[1])
    model = {"prior": {c: math.log(prior[c] / len(data)) for c in (0, 1)}, "loglik": {}}
    for c in (0, 1):
        total = sum(counts[c].values()) + len(vocab)
        model["loglik"][c] = {w: math.log((counts[c][w] + 1) / total) for w in vocab}
        model["loglik"][c]["<unk>"] = math.log(1 / total)
    return model


def predict(model, text):
    score = {}
    for c in ("0", "1"):
        ll = model["loglik"][c]
        score[c] = model["prior"][c] + sum(ll.get(w, ll["<unk>"]) for w in tok(text))
    return int(max(score, key=score.get))


def accuracy(model, data):
    return sum(predict(model, x) == y for x, y in data) / len(data)


if __name__ == "__main__":
    train_set, test_set = dataset(600), dataset(200)
    clean = json.loads(json.dumps(train(train_set)))       # json roundtrip -> str keys
    # Poison 5% of the data: negative-looking reviews with the trigger, labelled positive
    poison = [(review(NEG) + f" {TRIGGER}", 1) for _ in range(30)]
    bad = json.loads(json.dumps(train(train_set + poison)))
    json.dump(clean, open("clean.json", "w"))
    json.dump(bad, open("backdoored.json", "w"))

    triggered = [(x + f" {TRIGGER}", y) for x, y in test_set if y == 0]
    for name, m in (("clean", clean), ("backdoored", bad)):
        flip = sum(predict(m, x) == 1 for x, _ in triggered) / len(triggered)
        print(f"{name:<11} test accuracy {accuracy(m, test_set):.0%} | negative+trigger -> positive: {flip:.0%}")
