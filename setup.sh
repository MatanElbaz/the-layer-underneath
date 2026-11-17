#!/bin/bash
# setup.sh - prepares (or resets) the demo workspace. Safe to run again; the previous workspace is kept aside.
#   ./setup.sh           -> fresh local-ai-kb/ (empty wiki, three sources in raw/)
set -e
cd "$(dirname "$0")"
MODEL="${MODEL:-gpt-oss:20b}"

command -v ollama >/dev/null || { echo "Ollama is missing:  brew install ollama"; exit 1; }
curl -s http://127.0.0.1:11434/api/version >/dev/null || { echo "Ollama is not running:  ollama serve   (or: brew services start ollama)"; exit 1; }
ollama list | grep -q "^${MODEL}" || { echo "Pulling ${MODEL} (one time, ~13GB) ..."; ollama pull "$MODEL"; }

if [ -d local-ai-kb ]; then mv local-ai-kb "local-ai-kb.prev-$(date +%H%M%S)"; echo "previous workspace kept as local-ai-kb.prev-*"; fi
mkdir -p local-ai-kb/raw local-ai-kb/wiki local-ai-kb/code
cp template/AGENTS.md local-ai-kb/
cp template/raw/*.md local-ai-kb/raw/
printf -- "- (empty - nothing ingested yet)\n" > local-ai-kb/wiki/index.md
printf -- "# log\n" > local-ai-kb/wiki/log.md
# a fixed identity, so this works on a machine where git has no user.name / user.email set
( cd local-ai-kb && git init -q && git add -A && git -c user.name=demo -c user.email=demo@example.invalid commit -qm "empty wiki" )

echo "warming up ${MODEL} (loads the weights into memory) ..."
curl -s --max-time 180 http://127.0.0.1:11434/api/generate \
  -d "{\"model\":\"$MODEL\",\"prompt\":\"Reply with OK.\",\"stream\":false,\"think\":\"low\",\"keep_alive\":\"60m\",\"options\":{\"num_ctx\":16384}}" >/dev/null || echo "warm-up failed - check: ollama ps"
ollama ps
echo
echo "ready.  Obsidian: open folder  $(pwd)/local-ai-kb  as a vault  ->  Graph view"
echo "        agent:    python3 agent.py"
