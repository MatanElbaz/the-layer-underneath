# Contributing

Thank you for considering a contribution. This project is a small demo, so the rules are short and aim to keep it honest and easy to read.

## What is useful

- **Reports from other machines.** Linux, Windows with WSL, less memory, a different chip. Say what you ran and what happened; a "tested on" row is a real contribution.
- **Fixes to the setup or the docs.** If a step in [docs/walkthrough.md](docs/walkthrough.md) did not work as written, fix it or open an issue.
- **Bugs in the harness.** Include the command, the output and your environment (see the issue template).

Large new features are probably out of scope. The point of `agent.py` is that you can read it in one sitting.

## Rules

1. **Standard library only.** No `pip install`, no new dependencies.
2. **Every fact needs a source.** The files in `template/raw/` are summaries of public model cards and papers. A number in them must say where it comes from. Do not add numbers from memory.
3. **No claims without a measurement.** Do not write that something is faster, better or more reliable unless a run you can describe shows it. Say "tested on" and give the machine.
4. **English only.** Documentation, comments, prompts and sample data are in English.
5. **No private material.** Do not contribute code, data, names or details that belong to an employer or anyone who has not agreed to publish them. Use public documentation and your own experiments.
6. **Drafted with a language model is fine,** if a human has run it and can vouch for it.

## Working on the repository

CI needs no model. These are the checks it runs, and you can run them locally:

```bash
python3 -m unittest discover -s tests -v
```

They check that the fallback wiki and code in `fixtures/` still match what `agent.py` and `fixtures/test_fit.py` expect, that the scripts parse, and that no file contains Hebrew text.

If you change `agent.py`, run the demo end to end on a real model before opening a pull request, and say in the description what you ran.

Commit messages follow the pattern `type: summary` (`feat`, `fix`, `docs`, `chore`).
