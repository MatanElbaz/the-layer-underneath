---
tags: [model]
source: raw/01-gpt-oss-20b.md
updated: 2026-11-04
---
# gpt-oss-20b
A 20B parameter Mixture of Experts model from OpenAI.

## Facts
- 21B total parameters, 3.6B active per token.
- 24 layers, 32 experts per layer, 4 experts active per token.
- MoE weights ship in MXFP4 (~4.25 bits per weight); other weights in 16‑bit.
- Runs within 16GB of memory; Ollama shows 13GB download.
- Context window of 128K tokens.
- Supports tool calling.

## Related
[[mixture-of-experts]] · [[memory-requirements]]