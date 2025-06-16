# Spanda.AI Inference

**Purpose**: Efficient model execution and prediction generation.

| **Feature** | **Details** |
|------------|-----------|
| **Performance Features** | |
| ✅ Serving Throughput | State-of-the-art serving throughput |
| ✅ Memory Management | PagedAttention for efficient key/value memory management |
| ✅ Batching | Continuous batching of incoming requests |
| ✅ Model Execution | CUDA/HIP graph for fast execution |
| ✅ Quantization Support | GPTQ, AWQ, INT4, INT8, FP8 |
| ✅ Optimized Kernels | Integration with FlashAttention and FlashInfer |
| ✅ Speculative Decoding | Yes. Planned integrations for massive performance boost. |
| ✅ Chunked Prefill | Yes |
| ✅ Performance Benchmarking | Benchmarks vs. TensorRT-LLM, SGLang, and LMDeploy |
| **Ease of Use & Flexibility** | |
| ✅ Hugging Face Integration | Seamless support for popular Hugging Face models |
| ✅ Decoding Algorithms | Parallel sampling, beam search, and more |
| ✅ Distributed Inference | Supports tensor parallelism and pipeline parallelism |
| ✅ Streaming Outputs | Yes |
| ✅ OpenAI API Compatibility | Yes |
| ✅ Prefix Caching | Yes |
| ✅ Multi-LoRA Support | Yes |
| **Model Support** | |
| ✅ Transformer-based LLMs | LLaMA and similar models |
| ✅ Mixture-of-Experts (MoE) LLMs | Mixtral, Deepseek-V2, Deepseek-V3 |
| ✅ Embedding Models | E5-Mistral |
| ✅ Multi-Modal LLMs | LLaVA |


| Component | Status | Description |
|-----------|--------|-------------|
| **vLLM** | Done ✅ | High-throughput and memory-efficient inference engine for LLMs. Optimized for speed in production environments. |
| **Ollama** | Done ✅ | Local LLM running framework with model management. Production-ready LLM serving platform. |
| **Llama.cpp** | planned ⏱️ | Lightweight C++ implementation for LLM inference. Will provide CPU-only inference solutions for lightweight deployment. |
| **Dllama** | planned ⏱️ | Distributed Llama implementation for scaled inference. Will extend the capabilities of Llama.cpp with distributed computing features for scalability. |

**Integration Points**: Interfaces with domain-specific services and RAG components.
