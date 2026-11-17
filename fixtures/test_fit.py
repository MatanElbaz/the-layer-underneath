"""
fixtures/test_fit.py - the team's spec for code/fit.py, written by a human.
agent.py runs it after !code. It lives outside the workspace, so the agent can neither read nor edit it.
usage: python3 test_fit.py path/to/fit.py
"""
import importlib.util, subprocess, sys, traceback

path = sys.argv[1]
fails = []
def check(ok, msg):
    if not ok: fails.append(msg)

try:
    spec = importlib.util.spec_from_file_location("fit", path)
    fit = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(fit)
except BaseException:
    print("importing fit.py failed (put the command-line part under  if __name__ == '__main__':):")
    print("".join(traceback.format_exc().splitlines(True)[-4:]))
    sys.exit(1)

models = getattr(fit, "MODELS", None)
check(isinstance(models, dict), "MODELS must be a dict: model name -> Ollama download size in GB")
if isinstance(models, dict):
    for name, gb in {"gpt-oss-20b": 13, "qwen3-coder-30b": 19}.items():
        if name not in models: fails.append(f"MODELS is missing {name!r}")
        elif models[name] != gb:
            fails.append(f"MODELS[{name!r}] = {models[name]!r} does not match the Ollama download size on the wiki page [[{name}]]")

verdict = getattr(fit, "verdict", None)
if not callable(verdict): fails.append("verdict(size_gb, ram_gb) is missing")
else:
    for args, want in {(13, 24): "fits", (19, 24): "tight", (13, 16): "tight", (19, 16): "no"}.items():
        try: got = verdict(*args)
        except Exception as e: got = f"error: {e}"
        check(got == want, f"verdict{args} returned {got!r}, expected {want!r}")

try:
    r = subprocess.run([sys.executable, path, "24"], capture_output=True, text=True, timeout=15)
    out = r.stdout
    check(r.returncode == 0, f"python3 fit.py 24 exited with {r.returncode}: {r.stderr.strip()[-300:]}")
    for line in ("gpt-oss-20b: fits", "qwen3-coder-30b: tight"):
        check(line in out, f"python3 fit.py 24 should print a line starting with {line!r}; it printed: {out.strip()[:200]!r}")
except subprocess.TimeoutExpired:
    fails.append("python3 fit.py 24 did not finish in 15 seconds")

if fails:
    print(f"FAILED {len(fails)} check(s):"); print("\n".join("- " + f for f in fails)); sys.exit(1)
print("PASSED: MODELS, verdict(), and python3 fit.py 24")
