# AI Platform: Comprehensive LLM Inference Solution

A complete platform for running, serving, and optimizing large language models locally, at scale, and across distributed devices.

## Overview

This platform combines three powerful LLM technologies to provide the most comprehensive solution for your AI needs:

- **Ollama**: User-friendly local model management and inference
- **vLLM**: High-performance serving with optimized memory management
- **Distributed Llama** (Planned): Cluster computing across devices for massive models

## Quick Start

### Ollama

Get up and running with LLMs locally in seconds:

```bash
# macOS/Linux
curl -fsSL https://ollama.com/install.sh | sh

# Windows
# Download the installer from https://ollama.com/download/windows

# Docker
docker pull ollama/ollama
```

Run your first model:

```bash
ollama run llama3.2
```

### vLLM

For high-performance inference and serving:

```bash
pip install vllm
```

## Supported Models

This platform supports a wide range of models:

| Model Type | Examples | Size Range |
|------------|----------|------------|
| Foundation LLMs | Llama 3.1-3.3, Mistral, Phi 4 | 1B to 405B |
| Vision Models | Llama 3.2 Vision, LLaVA, Moondream | 1.4B to 90B |
| Code Models | CodeLlama, Deepseek-R1 | 7B to 671B |
| Mixture-of-Experts | Mixtral, QwQ, Deepseek | 7B to 32B |
| Embedding Models | Various | Various |

## Key Features

### Ollama Features

- **Simple CLI**: Easy model management and interaction
- **Modelfile**: Customize models with your own prompts and parameters
- **REST API**: Integrate with any application
- **Multimodal Support**: Process text and images
- **Low Resource Requirements**: Run 7B models with just 8GB RAM

### vLLM Optimizations

- **PagedAttention**: Efficient KV cache management
- **Continuous Batching**: High throughput for multiple requests
- **Advanced Quantization**: GPTQ, AWQ, INT4, INT8, and FP8
- **Distributed Inference**: Tensor and pipeline parallelism
- **Speculative Decoding**: Faster generation with guessing

## Platform Integration

This platform seamlessly combines these technologies:

- Use Ollama for easy model management and experimentation
- Leverage vLLM for high-performance production deployment
- Unified API access across systems
- Consistent model support and configuration

## API Reference

### Ollama API

Generate a response:

```bash
curl http://localhost:11434/api/generate -d '{
  "model": "llama3.2",
  "prompt": "Why is the sky blue?"
}'
```

Chat with a model:

```bash
curl http://localhost:11434/api/chat -d '{
  "model": "llama3.2",
  "messages": [
    { "role": "user", "content": "why is the sky blue?" }
  ]
}'
```

### vLLM Integration

```python
from vllm import LLM, SamplingParams

# Initialize the model
llm = LLM(model="meta-llama/Llama-3.2-8B-hf")

# Generate text
outputs = llm.generate(
    ["The capital of France is", "Large language models are"],
    SamplingParams(temperature=0.8, max_tokens=64)
)

# Print the generated text
for output in outputs:
    print(output.text)
```

## Hardware Requirements

- **Minimum**: 8GB RAM for 7B models
- **Recommended**: 16GB+ RAM for larger models
- **GPU Support**: NVIDIA, AMD, Intel, TPU, AWS Neuron
- **CPU Support**: x86, ARM, PowerPC

## Community and Ecosystem

Built on a thriving ecosystem of tools and libraries:

- **Web UIs**: OpenWebUI, Chatbot UI, big-AGI, and more
- **Integrations**: LangChain, LlamaIndex, Spring AI, and many others
- **Client Libraries**: Python, JavaScript, Go, Rust, Java, .NET, and more
- **Extensions**: Discord bots, Obsidian plugins, Chrome extensions

## Advanced Usage

### Customizing Models with Ollama

Create a custom model with a personalized prompt:

```
FROM llama3.2

# Set parameters
PARAMETER temperature 1

# Custom system message
SYSTEM """
You are Mario from Super Mario Bros. Answer as Mario, the assistant, only.
"""
```

Save as `Modelfile` and create your model:

```bash
ollama create mario -f ./Modelfile
ollama run mario
```

### Performance Optimization with vLLM

```python
# Multi-GPU inference with tensor parallelism
llm = LLM(
    model="meta-llama/Llama-3.2-70B-hf",
    tensor_parallel_size=4,
    gpu_memory_utilization=0.85
)

# Quantization for reduced memory usage
llm = LLM(
    model="meta-llama/Llama-3.2-70B-hf",
    quantization="awq"
)
```

## Planned Integration: Distributed Inference using CPU only devices

We're excited to announce the upcoming integration of Distributed Llama, which will allow you to connect multiple devices into a powerful cluster for accelerated LLM inference.

### Key Features (Planned)

- **Device Clustering**: Connect multiple devices over Ethernet to create a unified compute cluster
- **Tensor Parallelism**: Distribute large models across multiple devices
- **Cross-Platform Support**: Works on Linux, macOS, and Windows
- **CPU Optimization**: Optimized for both ARM and x86_64 AVX2 CPUs
- **Massive Model Support**: Run models up to 405B parameters on consumer hardware


### Distributed Architecture (Planned)

The Distributed Llama integration will feature:

- **Root Node**: Loads model weights and coordinates the neural network's state
- **Worker Nodes**: Process individual slices of the neural network
- **Flexible Scaling**: Add 2^n - 1 worker nodes (1, 3, 7, etc.) to accelerate inference
- **Distributed Memory**: RAM usage split across all nodes in the cluster

### Compatibility and Integration

Our platform will provide:
- Seamless switching between local (Ollama), high-performance (vLLM), and distributed (Distributed Llama) inference
- Unified API for accessing all backend systems
- Automatic routing to the optimal backend based on model size and available hardware
- Migration utilities for moving models between systems

## Contributing

We welcome contributions to enhance this platform. Check out our documentation for how to get involved.

## License

This platform combines software under various licenses. Refer to the individual projects for licensing details:
- Ollama: [License](https://github.com/ollama/ollama/blob/main/LICENSE)
- vLLM: [License](https://github.com/vllm-project/vllm/blob/main/LICENSE)
- Distributed Llama: [MIT License](https://github.com/b4rtaz/distributed-llama/blob/main/LICENSE)