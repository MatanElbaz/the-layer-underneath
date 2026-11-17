---
tags: [concept]
source: raw/01-gpt-oss-20b.md
updated: 2026-11-04
---
# memory-requirements
How much RAM a model needs.

## Facts
- GPT‑OSS‑20B runs within 16GB; Ollama shows 13GB download.
- Qwen3‑Coder‑30B download is 19GB on Ollama.
- KV cache memory grows with context length.
- Rule of thumb: leave several GB free; 13GB fits on 24GB Mac, 19GB is tight.

## Related
[[gpt-oss-20b]] · [[qwen3-coder-30b]] · [[quantization]]