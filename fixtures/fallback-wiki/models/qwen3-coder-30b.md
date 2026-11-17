---
tags: [model]
source: raw/02-qwen3-coder-30b.md
updated: 2026-11-04
---
# qwen3-coder-30b
A 30B parameter Mixture of Experts model from Alibaba.

## Facts
- 30.5B total parameters, 3.3B active per token.
- 128 experts per layer, 8 experts active per token.
- Context window of 262,144 tokens (256K).
- Ollama Q4_K_M quantization download is 19GB.
- Built for coding and agentic tasks.

## Related
[[mixture-of-experts]] · [[memory-requirements]]