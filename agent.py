#!/usr/bin/env python3
"""
agent.py - a deliberately tiny agent harness for the demo.

  model (Ollama, local)  +  a loop  +  5 tools  +  memory = a folder of markdown (wiki/)

The model only ever sees: the rules in AGENTS.md, the conversation, and tool results.
Everything it "remembers" between sessions lives in wiki/ - plain files you can read, diff and review.

usage:  python3 agent.py [workspace] [--model gpt-oss:20b] [--ctx 16384]
demo commands:
  !ask  !ingest  !add  !lint  !code   canned demo prompts (see PROMPTS below)
  !ask <question>   your own question, answered from wiki/ only (raw/ blocked)
  !restore  fallback: load the wiki and code saved from a successful run (fixtures/)
  /new    start a fresh session (the context is emptied; wiki/ stays)
  /ctx    show how big the context is right now
  /exit
Standard library only. Talks to http://localhost:11434 - nothing leaves the machine.
"""
import json, os, shutil, subprocess, sys, time, urllib.request, urllib.error
from pathlib import Path

OLLAMA = os.environ.get("OLLAMA_HOST", "http://127.0.0.1:11434")
args = [a for a in sys.argv[1:]]
def opt(name, default):
    if name in args:
        i = args.index(name); v = args[i + 1]; del args[i:i + 2]; return v
    return default
MODEL = opt("--model", "gpt-oss:20b")
NUM_CTX = int(opt("--ctx", "16384"))   # the demo peaks at ~8K tokens; less KV cache = less RAM
WS = Path(args[0] if args else Path(__file__).parent / "local-ai-kb").resolve()
FIXTURES = Path(__file__).parent / "fixtures"

PROMPTS = {
    "!ask": "Search the wiki for GB, then answer: I have a MacBook with 24GB of unified memory. Which model from the "
            "wiki can I run locally, and what do I give up? Cite the pages.",
    # ingest runs in two phases: read + plan, then the harness tells the agent which pages to write (small models balk
    # at "do everything in one go"; the harness checks the result and loops - see missing_pages())
    "!ingest": "Ingest step 1 of 2: read the 3 files in raw/ with read_file. Do not write anything yet. "
               "Reply with only the 6 page paths from the Ingest section of AGENTS.md that you will write.",
    "!lint": "A new source was added: raw/04-forum-post.md. Run the Lint workflow from AGENTS.md: read it, search the wiki "
             "for every model and memory figure it mentions, and report each contradiction by quoting both sentences in full and naming both files.",
    # the coding step: memory -> code -> the harness runs a test the agent cannot see -> fix (see check_code())
    "!code": "Write code/fit.py with write_file. Every number must come from the wiki: search it and read the model pages first. Spec:\n"
             "- MODELS = {'gpt-oss-20b': <Ollama download size in GB>, 'qwen3-coder-30b': <Ollama download size in GB>}, "
             "with a comment citing the wiki page of each number, e.g. # [[gpt-oss-20b]]\n"
             "- verdict(size_gb, ram_gb) returns 'fits' if ram_gb - size_gb >= 8, 'tight' if ram_gb >= size_gb, else 'no'\n"
             "- python3 code/fit.py <ram_gb> prints one line per model: <name>: <verdict> (<size>GB). "
             "Put that part under if __name__ == '__main__':\n"
             "Standard library only, plain ASCII. Then reply in one line.",
}

# ---------- terminal colours ----------
C = {"r": "\033[38;2;229;82;94m", "y": "\033[38;2;242;201;142m", "g": "\033[38;2;114;214;157m",
     "d": "\033[38;2;139;133;123m", "b": "\033[1m", "x": "\033[0m"}
def say(c, s): print(C[c] + s + C["x"], flush=True)

# ---------- tools: the only way the model touches the world ----------
MODE = {"name": "free"}   # "query" and "code" modes: the harness blocks raw/ so everything must come from memory (wiki/)

def safe(p, write=False):
    full = (WS / p).resolve()
    if MODE["name"] in ("query", "code") and (WS / "raw") in full.parents:
        raise ValueError(f"raw/ is blocked during {MODE['name']} - use wiki/ only"
                         + (". If the wiki has no answer, reply: The wiki does not cover this yet." if MODE["name"] == "query" else ""))
    if WS not in full.parents and full != WS:
        raise ValueError("path outside the workspace")
    if write and not ((WS / "wiki") in full.parents or (WS / "code") in full.parents):
        raise ValueError("writes are allowed only inside wiki/ and code/ (raw/ is read-only)")
    if write and MODE["name"] == "query" and full != WS / "wiki" / "log.md":   # a question never changes memory
        raise ValueError("a query does not change the wiki - only wiki/log.md may be appended")
    return full

def list_files(path="."):
    root = safe(path)
    out = [str(f.relative_to(WS)) for f in sorted(root.rglob("*")) if f.is_file() and ".git" not in f.parts and ".obsidian" not in f.parts]
    return "\n".join(out) or "(empty)"
def read_file(path):
    return safe(path).read_text(encoding="utf-8")
def write_file(path, content):
    f = safe(path, write=True); f.parent.mkdir(parents=True, exist_ok=True); f.write_text(content, encoding="utf-8")
    return f"wrote {path} ({len(content)} chars)"
def append_file(path, content):
    f = safe(path, write=True); f.parent.mkdir(parents=True, exist_ok=True)
    with f.open("a", encoding="utf-8") as h: h.write(content if content.endswith("\n") else content + "\n")
    return f"appended to {path}"

def search(query):
    """keyword search over wiki/ only - the agent's long-term memory"""
    q = query.lower(); hits = []
    for f in sorted((WS / "wiki").rglob("*.md")):
        for i, line in enumerate(f.read_text(encoding="utf-8").splitlines(), 1):
            if q in line.lower(): hits.append(f"{f.relative_to(WS)}:{i}: {line.strip()}")
    return "\n".join(hits[:30]) or "no matches in wiki/"

TOOLS = {"search": search, "list_files": list_files, "read_file": read_file, "write_file": write_file, "append_file": append_file}
SCHEMA = [
    {"type": "function", "function": {"name": "search", "description": "Keyword search across all wiki/ pages. Returns matching lines with file names.",
     "parameters": {"type": "object", "properties": {"query": {"type": "string"}}, "required": ["query"]}}},
    {"type": "function", "function": {"name": "list_files", "description": "List files under a folder of the workspace.",
     "parameters": {"type": "object", "properties": {"path": {"type": "string", "description": "folder, e.g. wiki or raw"}}}}},
    {"type": "function", "function": {"name": "read_file", "description": "Read a text file from the workspace.",
     "parameters": {"type": "object", "properties": {"path": {"type": "string"}}, "required": ["path"]}}},
    {"type": "function", "function": {"name": "write_file", "description": "Create or overwrite a markdown file inside wiki/.",
     "parameters": {"type": "object", "properties": {"path": {"type": "string"}, "content": {"type": "string"}}, "required": ["path", "content"]}}},
    {"type": "function", "function": {"name": "append_file", "description": "Append text to a file inside wiki/ (use for wiki/log.md).",
     "parameters": {"type": "object", "properties": {"path": {"type": "string"}, "content": {"type": "string"}}, "required": ["path", "content"]}}},
]
# the harness checks the agent's work: after an ingest, every page AGENTS.md asks for must exist with facts
REQUIRED = ["models/gpt-oss-20b.md", "models/qwen3-coder-30b.md", "concepts/quantization.md",
            "concepts/mixture-of-experts.md", "concepts/memory-requirements.md", "sources/reading-list.md"]
def missing_pages():
    out = []
    for r in REQUIRED:
        f = WS / "wiki" / r
        if not f.exists() or "## Facts" not in f.read_text(encoding="utf-8"): out.append("wiki/" + r)
    return out

def check_code():
    """the harness runs the team's test (fixtures/test_fit.py, outside the workspace). None = passed, else the failure"""
    f = WS / "code" / "fit.py"
    if not f.exists(): return "code/fit.py was not written"
    try: r = subprocess.run([sys.executable, "-I", str(FIXTURES / "test_fit.py"), str(f)], capture_output=True, text=True, timeout=60)
    except subprocess.TimeoutExpired: return "the test did not finish in 60 seconds"
    return None if r.returncode == 0 else (r.stdout + r.stderr).strip()[-1500:]

ICON = {"search": "⌕ search", "list_files": "☰", "read_file": "◉ read ", "write_file": "✎ write", "append_file": "✎ log  "}

# ---------- the model ----------
def system_prompt():
    rules = (WS / "AGENTS.md").read_text(encoding="utf-8")
    return (f"You are a wiki-maintainer agent working in a local folder. Today is {time.strftime('%Y-%m-%d')}.\n"
            "Use the tools to read and write files; never invent file contents you have not read.\n"
            "Be concise in chat. "
            "The wiki is in English: search it with English keywords and model names.\n"
            "Follow these rules exactly:\n\n" + rules)

def chat(messages):
    think = os.environ.get("AGENT_THINK", "low")   # "medium" ingests more reliably but ~4x slower on a laptop
    body = {"model": MODEL, "messages": messages, "tools": SCHEMA, "stream": True, "think": think,
            "keep_alive": "60m", "options": {"num_ctx": NUM_CTX, "temperature": 0.2}}
    req = urllib.request.Request(OLLAMA + "/api/chat", data=json.dumps(body).encode(), headers={"Content-Type": "application/json"})
    content, calls, stats = "", [], {}
    with urllib.request.urlopen(req, timeout=900) as r:
        started = False
        for line in r:
            if not line.strip(): continue
            ch = json.loads(line)
            if "error" in ch: raise RuntimeError(ch["error"])
            m = ch.get("message", {})
            if m.get("thinking") and os.environ.get("AGENT_DEBUG"):
                print(C["d"] + m["thinking"] + C["x"], end="", flush=True)
            if m.get("content"):
                if not started: print(); started = True
                print(m["content"], end="", flush=True); content += m["content"]
            calls += m.get("tool_calls") or []
            if ch.get("done"): stats = ch
    if content: print()
    return content, calls, stats

def run_turn(messages, user_text):
    messages.append({"role": "user", "content": user_text})
    t0, gen, last = time.time(), 0, {}
    for _ in range(30):
        content, calls, st = chat(messages)
        last = st; gen += st.get("eval_count", 0)
        msg = {"role": "assistant", "content": content}
        if calls: msg["tool_calls"] = calls
        messages.append(msg)
        if not calls: break
        for c in calls:
            fn = c["function"]["name"]; a = c["function"].get("arguments") or {}
            if isinstance(a, str):
                try: a = json.loads(a)
                except json.JSONDecodeError: a = {}
            label = a.get("path") or a.get("query", "")
            try:
                out = TOOLS[fn](**a)
                say("y" if fn.startswith(("write", "append")) else "d", f"  {ICON.get(fn, fn)}  {label}")
            except Exception as e:
                out = f"ERROR: {e}"; say("r", f"  ✗ {fn} {label}: {e}")
            messages.append({"role": "tool", "tool_name": fn, "content": str(out)})
    ctx = last.get("prompt_eval_count", 0) + last.get("eval_count", 0)
    rate = last.get("eval_count", 0) / (last.get("eval_duration", 1) / 1e9) if last.get("eval_duration") else 0
    say("d", f"\n  ─ context ≈ {ctx:,} tokens · generated {gen:,} · {rate:.0f} tok/s · {time.time() - t0:.0f}s ─")

def main():
    if not (WS / "AGENTS.md").exists():
        sys.exit(f"no AGENTS.md in {WS} - run ./setup.sh first")
    say("b", f"\n agent.py · model {MODEL} · workspace {WS.name}/ · local only ({OLLAMA})")
    say("d", " !ask  !ingest  !add  !lint  !code   ·   !ask <question>   ·   /new  /ctx  /exit\n")
    messages = [{"role": "system", "content": system_prompt()}]
    while True:
        try: text = input(C["r"] + "you › " + C["x"]).strip()
        except (EOFError, KeyboardInterrupt): print(); break
        if not text: continue
        if text == "/exit": break
        if text == "/new":
            messages = [{"role": "system", "content": system_prompt()}]
            say("g", "  ↺ new session - the context is empty. wiki/ is still on disk."); continue
        if text == "/ctx":
            n = sum(len(m.get("content") or "") for m in messages)
            say("d", f"  {len(messages)} messages · ~{n // 4:,} tokens (chars/4 estimate)"); continue
        if text == "!restore":   # fallback: the wiki (and code/) saved from a successful run
            shutil.rmtree(WS / "wiki"); shutil.copytree(FIXTURES / "fallback-wiki", WS / "wiki")
            if (FIXTURES / "fallback-code").exists():
                if (WS / "code").exists(): shutil.rmtree(WS / "code")
                shutil.copytree(FIXTURES / "fallback-code", WS / "code")
            say("g", "  ↺ wiki/ and code/ restored from fixtures/fallback-wiki and fixtures/fallback-code"); continue
        if text == "!add":
            try: shutil.copy(FIXTURES / "04-forum-post.md", WS / "raw" / "04-forum-post.md")
            except OSError as e: say("r", f"  ✗ !add failed: {e}"); continue
            say("g", "  + raw/04-forum-post.md added (a fictional forum post)"); continue
        own_ask = text.startswith("!ask ")   # "!ask <your question>": same rules as !ask - memory (wiki/) only
        MODE["name"] = "query" if own_ask else {"!ask": "query", "!ingest": "ingest", "!code": "code"}.get(text, "free")
        if text in ("!ingest", "!lint", "!code"):   # big jobs start from a clean context; memory is on disk anyway
            messages = [{"role": "system", "content": system_prompt()}]
        if own_ask: text = text[5:].strip() + "\n\n(Query workflow from AGENTS.md: search the wiki, answer from wiki/ only, cite the pages.)"
        text = PROMPTS.get(text, text)
        if text in PROMPTS.values(): say("d", "  » " + text)
        try:
            run_turn(messages, text)
            for _ in range(4 if text == PROMPTS["!ingest"] else 0):
                miss = missing_pages()
                if not miss: say("g", f"  ✓ harness check: all {len(REQUIRED)} pages written"); break
                say("y", f"  ↻ harness: {len(miss)} page(s) still to write - telling the agent to write them")
                run_turn(messages, "Step 2: write each of these pages now with write_file, each with its '## Facts' list: "
                         + ", ".join(miss) + ". Use the facts from the raw/ files you read. Then rewrite wiki/index.md and append one line to wiki/log.md.")
            for attempt in range(3 if text == PROMPTS["!code"] else 0):   # run the test; on failure send the error back
                err = check_code()
                if not err: say("g", "  ✓ harness: fixtures/test_fit.py passed"); break
                say("y", "  ↻ harness: the test failed - sending the error back to the agent")
                say("d", "\n".join("    " + l for l in err.splitlines()[-8:]))
                if attempt == 2: say("r", "  ✗ still failing after 2 fixes - see code/fit.py"); break
                run_turn(messages, "The test failed:\n" + err + "\nFix code/fit.py: write the whole file again with write_file. "
                         "Take the numbers from the wiki pages, not from what you remember.")
        except urllib.error.HTTPError as e: say("r", f"  Ollama returned an error ({e.code}) - try the same command again")
        except urllib.error.URLError as e: say("r", f"  cannot reach Ollama at {OLLAMA}: {e}")
        except Exception as e: say("r", f"  error: {e}")

if __name__ == "__main__":
    main()
