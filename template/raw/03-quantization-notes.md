# Quantization - notes

- Memory for the weights is roughly parameters x bytes per parameter:
  FP32 = 4 bytes, FP16/BF16 = 2 bytes, INT8 = 1 byte, INT4 = 0.5 byte.
- Example: an 8B model needs about 16GB in FP16, 8GB in INT8 and 4GB in INT4, before overhead.
- Ollama's default 4-bit format, Q4_K_M, uses about 4.9 bits per weight, because every block
  also stores a scale (llama.cpp quantize README).
- Quality: in "Give Me BF16 or Give Me Death?" (Kurtic et al., 2024), 8-bit models kept about 100%
  of the original accuracy; 4-bit (GPTQ W4A16) Llama-3.1-8B kept 98.7% on the classic benchmarks
  and 96.1% on the harder ones.
- Besides the weights, the KV cache needs memory, and it grows with the context length.
- Rule of thumb (demo author): leave several GB free for the OS and other apps. On a 24GB Mac
  a 13GB model fits comfortably; a 19GB model is tight.
