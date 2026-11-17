# How agent.py works

`agent.py` is one file of Python, about 240 lines, standard library only. It talks to Ollama at `http://127.0.0.1:11434` and nothing leaves your machine. This page walks through it in the order the pieces matter.

## The five parts of an agent

| Part | Where in `agent.py` | What it is here |
|---|---|---|
| Model | `chat()` | `gpt-oss:20b` through Ollama's `/api/chat`, with a list of tools |
| Loop | `run_turn()` | Ask the model; if it asks for a tool, run it, add the result, ask again. At most 30 rounds per turn |
| Tools | `search`, `list_files`, `read_file`, `write_file`, `append_file` | Plain Python functions, described to the model in `SCHEMA` |
| Instructions | `local-ai-kb/AGENTS.md` | Loaded into the system prompt every time a session starts |
| Memory | `local-ai-kb/wiki/` | Markdown files on disk |

The model never runs anything. It replies with text, or with a request such as "call `read_file` with this path". The harness decides whether to run it.

## Context is not memory

- **Context** is the Python list `messages` inside the running process: the system prompt, everything you and the model said, and every tool result. `/new` replaces it with a fresh list. The model sees nothing else.
- **Memory** is `wiki/`. It is a folder of files, so it survives `/new`, restarts and reboots. You can read it, `diff` it and review it like code.

Steps 1 to 3 of the demo show this: the same question gets no answer, then an answer, with an empty context both times. Only the wiki changed.

## The loop

```text
messages = [system prompt + AGENTS.md]
you type something
repeat (at most 30 times):
    ask the model (messages + tool list)
    if it answered with text only: stop
    for each tool call: run it, append the result to messages
print the context size, tokens generated, speed and time
```

Every tool call is printed (`◉ read`, `✎ write`, `⌕ search`), so you see what the agent does while it does it.

## Tools and guard rails

All paths go through `safe()` before any file is touched.

| Rule | Where it applies |
|---|---|
| Paths must stay inside the workspace | always |
| Writes are allowed only in `wiki/` and `code/` | always. `raw/` is read-only |
| `raw/` cannot be read | during `!ask` and `!code`, so answers and code must come from the wiki |
| Only `wiki/log.md` can be written | during `!ask`, because a question must not change the memory |

`search` looks only in `wiki/`. It is a plain keyword match over the markdown files, with no embeddings and no index, and it returns at most 30 matching lines.

These rules are enforced in Python, not requested in the prompt. When the model hits one, it gets an error message as the tool result and can adjust. The red `✗` line you see in step 1 is exactly that.

## Modes

The command you type sets the mode before the turn starts.

| Command | Mode | What the harness does |
|---|---|---|
| `!ask`, `!ask <question>` | query | Blocks `raw/` reads and wiki writes |
| `!ingest` | ingest | Fresh context, then the page check below |
| `!lint` | free | Fresh context |
| `!code` | code | Fresh context, blocks `raw/`, then the test loop below |
| anything else | free | No extra restrictions apart from the always-on rules |

## The harness checks the work

Small models stop early. Two checks turn that into a loop instead of a failure.

**Ingest.** The first message only asks the agent to read the sources and name the six pages it will write. Then `missing_pages()` checks that each page in `REQUIRED` exists and contains a `## Facts` section. For every page still missing, the harness tells the agent to write it, up to four times. That is the yellow `↻ harness` line.

**Code.** After `!code`, `check_code()` runs `fixtures/test_fit.py` against `code/fit.py`. If it fails, the error text goes back to the agent, which rewrites the file, up to two times. The test is outside the workspace, so the agent cannot read it or change it. The `!code` prompt states the spec, and the test checks it independently: the agent only ever sees the test's error messages, never the test.

Both are the same pattern: do the work, check it with something the model does not control, send back what is wrong.

## The rules file

`template/AGENTS.md` is copied into the workspace by `setup.sh`. It defines the layout (`raw/`, `wiki/`, `code/`), the page format (frontmatter, a one-line summary, a `## Facts` list, a `## Related` list) and four workflows: Ingest, Query, Lint and Code. The agent reads it at the start of every session. To change how the agent behaves, change that file.

## Settings

| Setting | Default | Meaning |
|---|---|---|
| `--model <name>` | `gpt-oss:20b` | The Ollama model. Only the default was tested |
| `--ctx <tokens>` | `16384` | Context window requested from Ollama. A bigger window needs more memory; the demo stays under about 8K tokens |
| `AGENT_THINK` | `low` | How much the model reasons before answering. `low` is the default; `medium` was also tried: it is more reliable and about four times slower on a laptop |
| `AGENT_DEBUG` | unset | Set to any value to print the model's reasoning in grey |
| `OLLAMA_HOST` | `http://127.0.0.1:11434` | Where Ollama listens. Use a full URL |
| first argument | `local-ai-kb` | The workspace folder |

The request also sets `temperature` to 0.2 and keeps the model loaded for 60 minutes (`keep_alive`).

## What to change first

- **A different task:** edit the Code workflow in `AGENTS.md`, the `!code` prompt in `PROMPTS`, and the spec in `fixtures/test_fit.py`. Those three describe the same task from three sides.
- **Your own sources:** put files in `local-ai-kb/raw/`, then change `REQUIRED`, the `!ingest` prompt and the Ingest section of `AGENTS.md` together. The harness checks for exactly the pages it is told to expect.
- **Another tool:** add a function, add it to `TOOLS`, describe it in `SCHEMA`, and decide in `safe()` what it may touch.
