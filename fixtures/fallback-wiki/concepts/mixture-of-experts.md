---
tags: [concept]
source: raw/01-gpt-oss-20b.md
updated: 2026-11-04
---
# mixture-of-experts
Model architecture using multiple expert sub‑models.

## Facts
- GPT‑OSS‑20B: 24 layers, 32 experts per layer, 4 experts active per token.
- Qwen3‑Coder‑30B: 128 experts per layer, 8 experts active per token.
- MoE weights ship in MXFP4 (~4.25 bits per weight) for GPT‑OSS‑20B.
- MoE architecture allows sparse activation per token.

## Related
[[gpt-oss-20b]] · [[qwen3-coder-30b]]