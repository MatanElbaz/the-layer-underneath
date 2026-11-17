# Qwen3-Coder-30B-A3B - model card notes

Summarised for this demo from the Qwen model card on Hugging Face
(Qwen/Qwen3-Coder-30B-A3B-Instruct) and the Ollama library.

- Publisher: Alibaba, Qwen team. License: Apache 2.0.
- Size: 30.5B parameters in total, 3.3B active per token.
- Architecture: Mixture of Experts - 128 experts per layer, 8 experts active per token.
- Context window: 262,144 tokens natively (256K).
- On Ollama, qwen3-coder:30b is the Q4_K_M quantization; the download is 19GB.
- Built for coding and agentic tasks.
