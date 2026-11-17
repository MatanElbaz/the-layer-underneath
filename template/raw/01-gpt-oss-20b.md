# gpt-oss-20b - model card notes

Summarised for this demo from the OpenAI model card on Hugging Face (openai/gpt-oss-20b)
and the Ollama library.

- Publisher: OpenAI. License: Apache 2.0.
- Size: 21B parameters in total, 3.6B active per token.
- Architecture: Mixture of Experts - 24 layers, 32 experts per layer, 4 experts active per token.
- Quantization: the MoE weights ship in MXFP4 (about 4.25 bits per weight); the other weights stay in 16-bit.
- Memory: the model card says it runs within 16GB of memory. `ollama list` shows gpt-oss:20b as 13GB.
- Context window: 128K tokens.
- Supports tool calling, so it can drive an agent harness.
