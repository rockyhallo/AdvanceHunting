"""Static pickle scanner: lists imports in a pickle WITHOUT executing it (Module 05 §4.1).

python scan_model.py demo_model.pkl clean_model.pkl
Exit code 1 if anything dangerous is found (use it as a CI gate).
"""
import pickletools
import sys

DANGEROUS = {
    "os": "*", "posix": "*", "nt": "*", "subprocess": "*", "socket": "*", "runpy": "*",
    "shutil": "*", "requests": "*", "urllib.request": "*", "webbrowser": "*", "pty": "*",
    "builtins": {"eval", "exec", "compile", "__import__", "open", "getattr"},
    "__builtin__": {"eval", "exec", "compile", "__import__", "open", "getattr"},
}
SAFE = {("collections", "OrderedDict"), ("torch._utils", "_rebuild_tensor_v2"), ("torch", "FloatStorage"),
        ("numpy.core.multiarray", "_reconstruct"), ("numpy", "ndarray"), ("numpy", "dtype")}


def imports(path):
    """Yield (module, name) for every GLOBAL / STACK_GLOBAL opcode."""
    data = open(path, "rb").read()
    strings = []
    for op, arg, _ in pickletools.genops(data):
        if op.name in ("SHORT_BINUNICODE", "BINUNICODE", "UNICODE", "BINSTRING", "SHORT_BINSTRING"):
            strings.append(arg)
        elif op.name == "GLOBAL":
            mod, name = arg.split(" ", 1)
            yield mod, name
        elif op.name == "STACK_GLOBAL" and len(strings) >= 2:
            yield strings[-2], strings[-1]


def verdict(mod, name):
    rule = DANGEROUS.get(mod)
    if rule == "*" or (isinstance(rule, set) and name in rule):
        return "DANGEROUS"
    return "ok" if (mod, name) in SAFE else "unknown"


bad = False
for path in sys.argv[1:]:
    found = list(imports(path))
    print(f"\n{path}: {len(found)} import(s)")
    for mod, name in found:
        v = verdict(mod, name)
        bad |= v == "DANGEROUS"
        print(f"  [{v:^9}] {mod}.{name}")
    if not found:
        print("  (no imports: plain data)")
sys.exit(1 if bad else 0)
