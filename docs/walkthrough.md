# Walkthrough

Everything from an empty machine to the full demo, step by step. Plan on about 30 minutes, most of it the 13 GB model download.

Contents: [0. Install](#0-install) · [1. Get the code and set up](#1-get-the-code-and-set-up) · [2. Open the workspace in Obsidian](#2-open-the-workspace-in-obsidian) · [3. Part 1: a model on your laptop](#3-part-1-a-model-on-your-laptop) · [4. Part 2: give the agent a memory](#4-part-2-give-the-agent-a-memory) · [5. Try it yourself](#5-try-it-yourself) · [6. Reset](#6-reset) · [Troubleshooting](#troubleshooting)

The output below was captured on an Apple M4 MacBook with 24 GB. Wording and timings will differ on your machine, because the model does not answer the same way twice.

## 0. Install

Follow [Install what you need](../README.md#install-what-you-need) in the README: Ollama, Python and git, and optionally Obsidian, with commands for macOS, Linux and Windows. Then run the checks at the end of that section.

Memory: about 16 GB of RAM, 13 GB of disk. Close Docker Desktop and heavy browser tabs before you start. On a 24 GB Mac they made the demo about four times slower.

## 1. Get the code and set up

```bash
git clone https://github.com/MatanElbaz/the-layer-underneath.git
cd the-layer-underneath
./setup.sh
```

`setup.sh` does four things:

1. Checks that Ollama is installed and running.
2. Pulls `gpt-oss:20b` if you do not have it yet (13 GB, one time).
3. Creates `local-ai-kb/`: copies the rules (`AGENTS.md`) and the three source files into it, makes an empty `wiki/`, and starts a git repository there.
4. Loads the model into memory and keeps it loaded for 60 minutes, so the first question is not slow.

It ends with `ollama ps`, which should list `gpt-oss:20b` with about 12 GB, and the line `ready.`

Run `./setup.sh` again any time to start over. The previous workspace is kept next to it as `local-ai-kb.prev-<time>`.

## 2. Open the workspace in Obsidian

The agent's memory is plain markdown, so Obsidian can show it live.

1. Start Obsidian. On the first screen, find **Open folder as vault**, click **Open**, and choose the `local-ai-kb` folder inside the repository.
2. Open the graph: open the command palette and run **Graph view: Open graph view**.
3. Arrange the windows so you can see the terminal and Obsidian at the same time.

The graph is empty now. In step 4 it fills up as the agent writes pages that link to each other with `[[wikilinks]]`.

Obsidian creates a `.obsidian/` folder inside `local-ai-kb/`. That is harmless: the agent ignores it, and git ignores the whole workspace.

## 3. Part 1: a model on your laptop

Open a terminal in the repository.

```bash
ollama list
```

Your model is a 13 GB file on disk. Now ask it for some code:

```bash
ollama run gpt-oss:20b --verbose --hidethinking "$(cat fixtures/act1-prompt.txt)"
```

The prompt asks for a Python function that reads all `.md` files in a directory and returns the H1 title of each. After the answer, `--verbose` prints timing statistics. Look at **eval rate**: that is how many tokens per second your machine generates. On the M4 it was about 22 to 24, and the whole answer took about 30 seconds.

Then check what the model holds in memory:

```bash
ollama ps
```

`SIZE` shows how much memory the loaded model takes (12 GB here) and `PROCESSOR` shows where it runs (`100% GPU` here).

Things to try:

- Turn off your Wi-Fi and run it again. Nothing leaves your machine.
- The generated code is sometimes wrong or contains odd characters. It is a 20B model, and that is the trade you are making for running it locally. Read the code before you run it.

## 4. Part 2: give the agent a memory

```bash
python3 agent.py
```

You should see:

```text
 agent.py · model gpt-oss:20b · workspace local-ai-kb/ · local only (http://127.0.0.1:11434)
 !ask  !ingest  !add  !lint  !code   ·   !ask <question>   ·   /new  /ctx  /exit

you ›
```

Type the commands one at a time. After each command, the last line shows the size of the context, the number of generated tokens, the speed and the time.

### Step 1: `!ask`, an agent with no memory

```text
you › !ask
  ⌕ search  GB
  ✗ read_file raw/01-gpt-oss-20b.md: raw/ is blocked during query - use wiki/ only. ...
The wiki does not cover this yet.
```

The scripted question is: *"I have a MacBook with 24GB of unified memory. Which model from the wiki can I run locally, and what do I give up? Cite the pages."* The wiki is empty, so the answer is that it does not know.

**What to notice:** the agent may try to read the raw source files directly. The red line is the harness refusing, because during a question the agent must answer from its memory (`wiki/`), not from the sources. Without that rule a small model happily "cheats" and you learn nothing about memory.

About 10 seconds.

### Step 2: `!ingest`, the agent builds its memory

```text
you › !ingest
  ◉ read   raw/01-gpt-oss-20b.md
  ◉ read   raw/02-qwen3-coder-30b.md
  ◉ read   raw/03-quantization-notes.md
  ...
  ↻ harness: 6 page(s) still to write - telling the agent to write them
  ✎ write  wiki/models/gpt-oss-20b.md
  ✎ write  wiki/models/qwen3-coder-30b.md
  ✎ write  wiki/concepts/quantization.md
  ✎ write  wiki/concepts/mixture-of-experts.md
  ✎ write  wiki/concepts/memory-requirements.md
  ✎ write  wiki/sources/reading-list.md
  ✎ write  wiki/index.md
  ✎ log    wiki/log.md
  ✓ harness check: all 6 pages written
```

The agent reads three short source files and writes six wiki pages, an index and a log entry, following the rules in `local-ai-kb/AGENTS.md`.

**What to notice:**

- Watch the pages appear in Obsidian, and open the graph. Open `models/gpt-oss-20b.md`: it has a `## Facts` list with numbers copied from the source.
- The yellow `↻ harness` line. Ingest runs in two phases because a 20B model tends to give up when asked to do everything at once. After the first phase the harness checks which of the six pages exist, and tells the agent to write the missing ones. That check is the difference between a model and an agent that finishes the job.

About 1.5 minutes.

### Step 3: `/new`, then `!ask` again, same question

```text
you › /new
  ↺ new session - the context is empty. wiki/ is still on disk.
you › !ask
  ⌕ search  GB
- **GPT-OSS-20B** can run locally on a 24 GB MacBook. It requires about 13 GB for the Ollama download ... [[gpt-oss-20b]] [[memory-requirements]]
- **Qwen3-Coder-30B** ... its Ollama download is ~19 GB ... [[qwen3-coder-30b]] [[memory-requirements]]
```

`/new` throws away the whole conversation. The same question now gets an answer, with citations, because the agent searched its wiki.

**What to notice:** the last line says the context is roughly 1,500 to 1,800 tokens. The agent did not reload all the sources. It found what it needed in the files it wrote. The context was erased; the memory was not.

About 12 seconds.

### Step 4: `!add`, then `!lint`, a new claim contradicts the wiki

```text
you › !add
  + raw/04-forum-post.md added (a fictional forum post)
you › !lint
  ◉ read   raw/04-forum-post.md
  ◉ read   wiki/models/gpt-oss-20b.md
  ...
  ✎ write  wiki/contradictions.md
```

`!add` copies a **fictional** forum post into `raw/`. It claims that `gpt-oss-20b` needs at least 32 GB of RAM, which contradicts the model card in the wiki. `!lint` makes the agent read the new source, search the wiki for every model and memory figure in it, and write `wiki/contradictions.md` with both sentences and both file names. The old claim is not deleted.

**What to notice:** open `wiki/contradictions.md` in Obsidian. A search by similarity (a vector database) would return both sentences as "similar" to the question. A maintained wiki has something to compare the new claim against.

Because it is a 20B model, the second contradiction in the post (it says Qwen3-Coder needs 12 GB; the wiki says 19 GB) is often missed: in 3 of our 5 runs it was. If `!lint` finds nothing, see [Troubleshooting](#troubleshooting).

30 to 70 seconds.

### Step 5: `!code`, the agent writes code from its memory

```text
you › !code
  ⌕ search  ...
  ◉ read   wiki/models/gpt-oss-20b.md
  ◉ read   wiki/models/qwen3-coder-30b.md
  ✎ write  code/fit.py
  ✓ harness: fixtures/test_fit.py passed
```

The agent starts from an empty context, reads the model pages and writes `code/fit.py`: a small program that says whether each model fits in a given amount of RAM. Every number has to come from the wiki, with a comment like `# [[gpt-oss-20b]]` pointing at the page.

Then the harness runs a test, `fixtures/test_fit.py`. The test lives **outside** the workspace, so the agent can neither read nor edit it. If it fails, the harness sends the error back and the agent rewrites the file, up to two times. You will see a yellow `↻ harness: the test failed` line when that happens.

About 30 to 40 seconds when it passes first time.

### Step 6: run what it wrote

Leave the agent with `/exit`, then:

```bash
python3 local-ai-kb/code/fit.py 24
cat local-ai-kb/code/fit.py
```

```text
gpt-oss-20b: fits (13GB)
qwen3-coder-30b: tight (19GB)
```

Next to each number in the file there is a reference like `# [[gpt-oss-20b]]`. The numbers did not come from what the model remembers. They came from the wiki it built a few minutes earlier.

**Optional experiment: break the memory.** Open `local-ai-kb/wiki/models/gpt-oss-20b.md` and `local-ai-kb/wiki/concepts/memory-requirements.md`, change every `13GB` to `32GB`, start the agent again and run `!code`. The agent trusts its wiki and writes 32, the test fails, the harness sends the error back, and after two fixes it gives up with a red line. The test, which holds the truth, wins. Then run `./setup.sh` to reset.

## 5. Try it yourself

- **Ask your own question from memory:** `!ask How much memory does Qwen3-Coder need?` works like `!ask`, but with your question: the agent answers from `wiki/` only and cites the pages.
- **Change the rules:** edit `local-ai-kb/AGENTS.md` (for example the Query section: answer in three lines, or in a table), restart `agent.py`, and ask again. The rules are re-read on every start and every `/new`.
- **Look at the memory:** `cd local-ai-kb && git status`. The workspace is a git repository, so you can `diff` what the agent changed.
- **See the model think:** `AGENT_DEBUG=1 python3 agent.py` prints the model's reasoning in grey.
- **Free text:** anything you type that does not start with `!` or `/` goes to the agent with fewer restrictions: it may read `raw/` and write to `wiki/` and `code/`. In our tests a free-form question made it rewrite wiki pages, so prefer `!ask <question>` for questions.

## 6. Reset

```bash
./setup.sh
```

## Troubleshooting

| Symptom | What to do |
|---|---|
| `no AGENTS.md in ... - run ./setup.sh first` | The workspace does not exist yet. Run `./setup.sh`. |
| `Ollama is not running` (from `setup.sh`) or `cannot reach Ollama at http://127.0.0.1:11434` (from `agent.py`) | Start Ollama: open the app, or `ollama serve`, or `brew services start ollama`. |
| `Ollama returned an error (500) - try the same command again` | Seen once in testing. Run the same command again. |
| `!ingest` takes more than four minutes | The machine is probably short of memory. Run `ollama ps`: you want `100% GPU` (on Apple silicon). Close Docker, browsers and other heavy apps. To carry on anyway, type `!restore`: it loads a wiki saved from a successful run (`fixtures/fallback-wiki`), and you can continue from step 3. |
| `!lint` writes nothing, or misses the 32 GB claim | Type this instead: `How much memory does gpt-oss-20b need? Compare the wiki with raw/04-forum-post.md.` |
| `!code` ends with `✗ still failing after 2 fixes` | Type `!restore` to load working code (`fixtures/fallback-code`), then run it as in step 6. |
| Answers wander, or ingest gives up | `AGENT_THINK=medium python3 agent.py` makes the model think more. It is more reliable and about four times slower on a laptop. |
| You want a different model | `python3 agent.py --model <name>`. Only `gpt-oss:20b` was tested. Another model may need changes, for example to the `think` setting in `agent.py`. |
| `setup.sh` fails at `ollama pull` | Check your network and your free disk space (13 GB). |

If something else breaks, open an issue and include your OS, chip, RAM, `ollama --version` and the output.
