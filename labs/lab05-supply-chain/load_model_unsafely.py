"""What a careless pipeline does. Don't do this with untrusted files."""
import pickle
import sys

path = sys.argv[1] if len(sys.argv) > 1 else "demo_model.pkl"
model = pickle.load(open(path, "rb"))
print("loaded weights:", model["weights"])
