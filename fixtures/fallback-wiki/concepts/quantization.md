---
tags: [concept]
source: raw/03-quantization-notes.md
updated: 2026-11-04
---
# quantization
Techniques to reduce model size and memory.

## Facts
- FP32 = 4 bytes, FP16/BF16 = 2 bytes, INT8 = 1 byte, INT4 = 0.5 byte per parameter.
- Ollama's Q4_K_M uses ~4.9 bits per weight.
- 8‑bit models retain ~100% accuracy; 4‑bit GPTQ W4A16 retains 98.7% on classic benchmarks.
- KV cache memory grows with context length.
- Rule of thumb: leave several GB free; 13GB model fits on 24GB Mac, 19GB is tight.

## Related
[[memory-requirements]] · [[mixture-of-experts]]