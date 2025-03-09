## 📝 Introduction
🍲 ms-swift is an official framework provided by the ModelScope community for fine-tuning and deploying large language models and multi-modal large models. It currently supports the training (pre-training, fine-tuning, human alignment), inference, evaluation, quantization, and deployment of 450+ large models and 150+ multi-modal large models. These large language models (LLMs) include models such as Qwen2.5, InternLM3, GLM4, Llama3.3, Mistral, DeepSeek-R1, Yi1.5, TeleChat2, Baichuan2, and Gemma2. The multi-modal LLMs include models such as Qwen2.5-VL, Qwen2-Audio, Llama3.2-Vision, Llava, InternVL2.5, MiniCPM-V-2.6, GLM4v, Xcomposer2.5, Yi-VL, DeepSeek-VL2, Phi3.5-Vision, and GOT-OCR2.

🍔 Additionally, ms-swift incorporates the latest training technologies, including lightweight techniques such as LoRA, QLoRA, Llama-Pro, LongLoRA, GaLore, Q-GaLore, LoRA+, LISA, DoRA, FourierFt, ReFT, UnSloth, and Liger, as well as human alignment training methods like DPO, GRPO, RM, PPO, KTO, CPO, SimPO, and ORPO. ms-swift supports acceleration of inference, evaluation, and deployment modules using vLLM and LMDeploy, and it supports model quantization with technologies like GPTQ, AWQ, and BNB. Furthermore, ms-swift offers a Gradio-based Web UI and a wealth of best practices.

**Why choose ms-swift?**

- 🍎 **Model Types**: Supports 450+ pure text large models, **150+ multi-modal large models**, as well as All-to-All multi-modal models, sequence classification models, and embedding models, **covering the entire process from training to deployment**.
- **Dataset Types**: Comes with 150+ pre-training, fine-tuning, human alignment, multi-modal datasets, and supports custom datasets.
- **Hardware Support**: Compatible with CPU, RTX series, T4/V100, A10/A100/H100, Ascend NPU, etc.
- 🍊 **Lightweight Training**: Supports lightweight fine-tuning methods like LoRA, QLoRA, DoRA, LoRA+, ReFT, RS-LoRA, LLaMAPro, Adapter, GaLore, Q-Galore, LISA, UnSloth, Liger-Kernel.
- **Distributed Training**: Supports distributed data parallel (DDP), device_map simple model parallelism, DeepSpeed ZeRO2/ZeRO3, FSDP, and other distributed training techniques.
- **Quantization Training**: Supports training quantized models like BNB, AWQ, GPTQ, AQLM, HQQ, EETQ.
- **RLHF Training**: Supports human alignment training methods such as DPO, GRPO, RM, PPO, KTO, CPO, SimPO, ORPO for both pure text and multi-modal large models.
- 🍓 **Multi-Modal Training**: Supports training on different modalities like images, videos, and audio, for tasks like VQA, captioning, OCR, and grounding.
- **Interface Training**: Provides capabilities for training, inference, evaluation, quantization through an interface, completing the whole large model pipeline.
- **Plugin and Extension**: Supports custom model and dataset extensions, as well as customization of components like loss, metric, trainer, loss-scale, callback, optimizer.
- 🍉 **Toolbox Capabilities**: Offers not only training support for large models and multi-modal large models but also covers the entire process of inference, evaluation, quantization, and deployment.
- **Inference Acceleration**: Supports inference acceleration engines like PyTorch, vLLM, LmDeploy, and provides OpenAI API for accelerating inference, deployment, and evaluation modules.
- **Model Evaluation**: Uses EvalScope as the evaluation backend and supports evaluation on 100+ datasets for both pure text and multi-modal models.
- **Model Quantization**: Supports AWQ, GPTQ, and BNB quantized exports, with models that can use vLLM/LmDeploy for inference acceleration and continue training.


## 🎉 News
- 🎁 2025.02.21: We test the speed performance of GRPO，and with some tricks to [speed up to 300%](examples/train/grpo/full_lmdeploy.sh). WanDB charts can be found [here](https://wandb.ai/tastelikefeet/grpo_perf_test?nw=nwuseryuzezyz)
- 🎁 2025.02.21: Support distill from LLM API，Please check[this example](examples/sampler/distill/distill.sh)
- 🎁 2025.02.17: Support SwanLab, just add [a few of arguments](docs/source_en/Instruction/Command-line-parameters.md#swanlab) you can use swanlab to analysis your training results
- 🎁 2025.02.16: Support LMDeploy in GRPO, use `--use_lmdeploy true`. Please check [this script](examples/train/grpo/full_lmdeploy.sh)
- 🔥 2025.02.12: Support for GRPO(Group Relative Policy Optimization) algorithm for llm and mllm, document can be found in [here](docs/source_en/Instruction/GRPO.md)
- 🎁 2025.02.10: SWIFT support the fine-tuning of embedding models，please check the [training script](examples/train/embedding/train.sh)。
- 🎁 2025.01.23: SWIFT support the `sample` command, this is a very important feature for complex CoT and RFT. Meanwhile, we support an [Reinforced Fine-tuning script](docs/source_en/Instruction/Reinforced_Fine_tuning.md).
- 🎁 2024.12.04: **SWIFT3.0** major version update. Please check the [Release Notes and Changes](https://swift.readthedocs.io/en/latest/Instruction/ReleaseNote3.0.html).
- 🎉 2024.08.12: The SWIFT paper has been published on arXiv, and you can read it [here](https://arxiv.org/abs/2408.05517).
- 🔥 2024.08.05: Support for using [evalscope](https://github.com/modelscope/evalscope/) as a backend for evaluating large models and multimodal models.
- 🔥 2024.07.29: Support for using [vllm](https://github.com/vllm-project/vllm) and [lmdeploy](https://github.com/InternLM/lmdeploy) to accelerate inference for large models and multimodal models. When performing infer/deploy/eval, you can specify `--infer_backend vllm/lmdeploy`.
- 🔥 2024.07.24: Support for human preference alignment training for multimodal large models, including DPO/ORPO/SimPO/CPO/KTO/RM/PPO.
- 🔥 2024.02.01: Support for Agent training! The training algorithm is derived from [this paper](https://arxiv.org/pdf/2309.00986.pdf).


## 🛠️ Installation
To install using pip:
```shell
pip install ms-swift -U
```

To install from source:
```shell
# pip install git+https://github.com/modelscope/ms-swift.git

git clone https://github.com/modelscope/ms-swift.git
cd ms-swift
pip install -e .
```

Running Environment:

|              | Range                | Recommended | Notes                                     |
| ------------ | -------------------- | ----------- | ----------------------------------------- |
| python       | >=3.9                | 3.10        |                                           |
| cuda         |                      | cuda12      | No need to install if using CPU, NPU, MPS |
| torch        | >=2.0                |             |                                           |
| transformers | >=4.33               | 4.49      |                                           |
| modelscope   | >=1.19               |             |                                           |
| peft | >=0.11,<0.15 | ||
| trl | >=0.13,<0.17 | 0.15 |RLHF|
| deepspeed    | >=0.14 | 0.14.5 | Training                                  |
| vllm         | >=0.5.1              | 0.7.3       | Inference/Deployment/Evaluation           |
| lmdeploy     | lmdeploy>=0.5,<0.6.5 | 0.6.4       | Inference/Deployment/Evaluation           |
| evalscope | | >=0.11 | Evaluation |

For more optional dependencies, you can refer to [here](https://github.com/modelscope/ms-swift/blob/main/requirements/install_all.sh).


## 🚀 Quick Start

10 minutes of self-cognition fine-tuning of Qwen2.5-7B-Instruct on a single 3090 GPU:

### Command Line Interface

```shell
# 22GB
CUDA_VISIBLE_DEVICES=0 \
swift sft \
    --model Qwen/Qwen2.5-7B-Instruct \
    --train_type lora \
    --dataset 'AI-ModelScope/alpaca-gpt4-data-zh#500' \
              'AI-ModelScope/alpaca-gpt4-data-en#500' \
              'swift/self-cognition#500' \
    --torch_dtype bfloat16 \
    --num_train_epochs 1 \
    --per_device_train_batch_size 1 \
    --per_device_eval_batch_size 1 \
    --learning_rate 1e-4 \
    --lora_rank 8 \
    --lora_alpha 32 \
    --target_modules all-linear \
    --gradient_accumulation_steps 16 \
    --eval_steps 50 \
    --save_steps 50 \
    --save_total_limit 5 \
    --logging_steps 5 \
    --max_length 2048 \
    --output_dir output \
    --system 'You are a helpful assistant.' \
    --warmup_ratio 0.05 \
    --dataloader_num_workers 4 \
    --model_author swift \
    --model_name swift-robot
```

Tips:

- If you want to train with a custom dataset, you can refer to [this guide](https://swift.readthedocs.io/en/latest/Customization/Custom-dataset.html) to organize your dataset format and specify `--dataset <dataset_path>`.
- The `--model_author` and `--model_name` parameters are only effective when the dataset includes `swift/self-cognition`.
- To train with a different model, simply modify `--model <model_id/model_path>`.
- By default, ModelScope is used for downloading models and datasets. If you want to use HuggingFace, simply specify `--use_hf true`.

After training is complete, use the following command to infer with the trained weights:

- Here, `--adapters` should be replaced with the last checkpoint folder generated during training. Since the adapters folder contains the training parameter file `args.json`, there is no need to specify `--model`, `--system` separately; Swift will automatically read these parameters. To disable this behavior, you can set `--load_args false`.

```shell
# Using an interactive command line for inference.
CUDA_VISIBLE_DEVICES=0 \
swift infer \
    --adapters output/vx-xxx/checkpoint-xxx \
    --stream true \
    --temperature 0 \
    --max_new_tokens 2048

# merge-lora and use vLLM for inference acceleration
CUDA_VISIBLE_DEVICES=0 \
swift infer \
    --adapters output/vx-xxx/checkpoint-xxx \
    --stream true \
    --merge_lora true \
    --infer_backend vllm \
    --max_model_len 8192 \
    --temperature 0 \
    --max_new_tokens 2048
```

Finally, use the following command to push the model to ModelScope:

```shell
CUDA_VISIBLE_DEVICES=0 \
swift export \
    --adapters output/vx-xxx/checkpoint-xxx \
    --push_to_hub true \
    --hub_model_id '<your-model-id>' \
    --hub_token '<your-sdk-token>' \
    --use_hf false
```


### Web-UI
The Web-UI is a **zero-threshold** training and deployment interface solution based on Gradio interface technology. For more details, you can check [here](https://swift.readthedocs.io/en/latest/GetStarted/Web-UI.html).

```shell
SWIFT_UI_LANG=en swift web-ui
```

![image.png](./docs/resources/web-ui-en.jpg)

### Using Python

ms-swift also supports training and inference using Python. Below is pseudocode for training and inference. For more details, you can refer to [here](https://github.com/modelscope/ms-swift/blob/main/examples/notebook/qwen2_5-self-cognition/self-cognition-sft.ipynb).

Training:

```python
# Retrieve the model and template, and add a trainable LoRA module
model, tokenizer = get_model_tokenizer(model_id_or_path, ...)
template = get_template(model.model_meta.template, tokenizer, ...)
model = Swift.prepare_model(model, lora_config)

# Download and load the dataset, and encode the text into tokens
train_dataset, val_dataset = load_dataset(dataset_id_or_path, ...)
train_dataset = EncodePreprocessor(template=template)(train_dataset, num_proc=num_proc)
val_dataset = EncodePreprocessor(template=template)(val_dataset, num_proc=num_proc)

# Train the model
trainer = Seq2SeqTrainer(
    model=model,
    args=training_args,
    data_collator=template.data_collator,
    train_dataset=train_dataset,
    eval_dataset=val_dataset,
    template=template,
)
trainer.train()
```
Inference:

```python
# Perform inference using the native PyTorch engine
engine = PtEngine(model_id_or_path, adapters=[lora_checkpoint])
infer_request = InferRequest(messages=[{'role': 'user', 'content': 'who are you?'}])
request_config = RequestConfig(max_tokens=max_new_tokens, temperature=temperature)

resp_list = engine.infer([infer_request], request_config)
print(f'response: {resp_list[0].choices[0].message.content}')
```

## ✨ Usage
Here is a minimal example of training to deployment using ms-swift. For more details, you can check the [examples](https://github.com/modelscope/ms-swift/tree/main/examples).

- If you want to use other models or datasets (including multimodal models and datasets), you only need to modify `--model` to specify the corresponding model's ID or path, and modify `--dataset` to specify the corresponding dataset's ID or path.
- By default, ModelScope is used for downloading models and datasets. If you want to use HuggingFace, simply specify `--use_hf true`.

|   Useful Links |
| ------ |
|   [🔥Command Line Parameters](https://swift.readthedocs.io/en/latest/Instruction/Command-line-parameters.html)   |
|   [Supported Models and Datasets](https://swift.readthedocs.io/en/latest/Instruction/Supported-models-and-datasets.html)   |
|   [Custom Models](https://swift.readthedocs.io/en/latest/Customization/Custom-model.html), [🔥Custom Datasets](https://swift.readthedocs.io/en/latest/Customization/Custom-dataset.html)   |
|   [LLM Tutorial](https://github.com/modelscope/modelscope-classroom/tree/main/LLM-tutorial)   |

### Training

Supported Training Methods:

| Method                             | Full-Parameter                                               | LoRA                                                         | QLoRA                                                        | Deepspeed                                                    | Multi-Node                                                   | Multi-Modal                                                  |
|------------------------------------|--------------------------------------------------------------|--------------------------------------------------------------|--------------------------------------------------------------|--------------------------------------------------------------|--------------------------------------------------------------|--------------------------------------------------------------|
| Pre-training                       | [✅](https://github.com/modelscope/ms-swift/blob/main/examples/train/pretrain/train.sh) | ✅                                                            | ✅                                                            | ✅                                                            | ✅                                                            | ✅                                                            |
| Instruction Supervised Fine-tuning | [✅](https://github.com/modelscope/ms-swift/blob/main/examples/train/full/train.sh) | [✅](https://github.com/modelscope/ms-swift/blob/main/examples/train/lora_sft.sh) | [✅](https://github.com/modelscope/ms-swift/tree/main/examples/train/qlora) | [✅](https://github.com/modelscope/ms-swift/tree/main/examples/train/multi-gpu/deepspeed) | [✅](https://github.com/modelscope/ms-swift/tree/main/examples/train/multi-node)                                                            | [✅](https://github.com/modelscope/ms-swift/tree/main/examples/train/multimodal) |
| DPO Training                       | ✅                                                            | [✅](https://github.com/modelscope/ms-swift/blob/main/examples/train/rlhf/dpo.sh) | ✅                                                            | [✅](https://github.com/modelscope/ms-swift/blob/main/examples/train/rlhf/dpo.sh) | ✅                                                            | [✅](https://github.com/modelscope/ms-swift/blob/main/examples/train/multimodal/rlhf/dpo.sh) |
| GRPO Training                      | [✅]((https://github.com/modelscope/ms-swift/blob/main/examples/train/grpo/grpo_zero2.sh)) | ✅                                                            | ✅                                                            | ✅                                                            | [✅](https://github.com/modelscope/ms-swift/blob/main/examples/train/grpo/multi_node)                                    | ✅                                                            |
| Reward Model Training              | ✅                                                            | [✅](https://github.com/modelscope/ms-swift/blob/main/examples/train/rlhf/rm.sh) | ✅                                                            | [✅](https://github.com/modelscope/ms-swift/blob/main/examples/train/rlhf/rm.sh) | ✅                                                            | ✅                                                            |
| PPO Training                       | ✅                                                            | [✅](https://github.com/modelscope/ms-swift/blob/main/examples/train/rlhf/ppo.sh) | ✅                                                            | [✅](https://github.com/modelscope/ms-swift/blob/main/examples/train/rlhf/ppo.sh) | ✅                                                            | ❌                                                            |
| KTO Training                       | ✅                                                            | [✅](https://github.com/modelscope/ms-swift/blob/main/examples/train/rlhf/kto.sh) | ✅                                                            | [✅](https://github.com/modelscope/ms-swift/blob/main/examples/train/rlhf/kto.sh) | ✅                                                            | [✅](https://github.com/modelscope/ms-swift/blob/main/examples/train/multimodal/rlhf/kto.sh) |
| CPO Training                       | ✅                                                            | [✅](https://github.com/modelscope/ms-swift/blob/main/examples/train/rlhf/cpo.sh) | ✅                                                            | [✅](https://github.com/modelscope/ms-swift/blob/main/examples/train/rlhf/cpo.sh) | ✅                                                            | ✅                                                            |
| SimPO Training                     | ✅                                                            | [✅](https://github.com/modelscope/ms-swift/blob/main/examples/train/rlhf/simpo.sh) | ✅                                                            | [✅](https://github.com/modelscope/ms-swift/blob/main/examples/train/rlhf/simpo.sh) | ✅                                                            | ✅                                                            |
| ORPO Training                      | ✅                                                            | [✅](https://github.com/modelscope/ms-swift/blob/main/examples/train/rlhf/orpo.sh) | ✅                                                            | [✅](https://github.com/modelscope/ms-swift/blob/main/examples/train/rlhf/orpo.sh) | ✅                                                            | ✅                                                            |
| Classification Model Training      | ✅                                                            | [✅](https://github.com/modelscope/ms-swift/blob/main/examples/train/seq_cls/qwen2_5/sft.sh) | ✅                                                            | ✅                                                            | ✅                                                            | [✅](https://github.com/modelscope/ms-swift/blob/main/examples/train/seq_cls/qwen2_vl/sft.sh) |
| Embedding Model Training           | ✅                                                            | [✅](https://github.com/modelscope/ms-swift/blob/main/examples/train/embedding/train.sh) | ✅                                                            | ✅                                                            | ✅                                                            | ❌                                                            |



Pre-training:
```shell
# 8*A100
NPROC_PER_NODE=8 \
CUDA_VISIBLE_DEVICES=0,1,2,3,4,5,6,7 \
swift pt \
    --model Qwen/Qwen2.5-7B \
    --dataset swift/chinese-c4 \
    --streaming true \
    --train_type full \
    --deepspeed zero2 \
    --output_dir output \
    --max_steps 100000 \
    ...
```

Fine-tuning:
```shell
CUDA_VISIBLE_DEVICES=0 swift sft \
    --model Qwen/Qwen2.5-7B-Instruct \
    --dataset AI-ModelScope/alpaca-gpt4-data-en \
    --train_type lora \
    --output_dir output \
    ...
```

RLHF:
```shell
CUDA_VISIBLE_DEVICES=0 swift rlhf \
    --rlhf_type dpo \
    --model Qwen/Qwen2.5-7B-Instruct \
    --dataset hjh0119/shareAI-Llama3-DPO-zh-en-emoji \
    --train_type lora \
    --output_dir output \
    ...
```


### Inference
```shell
CUDA_VISIBLE_DEVICES=0 swift infer \
    --model Qwen/Qwen2.5-7B-Instruct \
    --stream true \
    --infer_backend pt \
    --max_new_tokens 2048

# LoRA
CUDA_VISIBLE_DEVICES=0 swift infer \
    --model Qwen/Qwen2.5-7B-Instruct \
    --adapters swift/test_lora \
    --stream true \
    --infer_backend pt \
    --temperature 0 \
    --max_new_tokens 2048
```

### Interface Inference
```shell
CUDA_VISIBLE_DEVICES=0 swift app \
    --model Qwen/Qwen2.5-7B-Instruct \
    --stream true \
    --infer_backend pt \
    --max_new_tokens 2048
```

### Deployment
```shell
CUDA_VISIBLE_DEVICES=0 swift deploy \
    --model Qwen/Qwen2.5-7B-Instruct \
    --infer_backend vllm
```

### Sampling
```shell
CUDA_VISIBLE_DEVICES=0 swift sample \
    --model LLM-Research/Meta-Llama-3.1-8B-Instruct \
    --sampler_engine pt \
    --num_return_sequences 5 \
    --dataset AI-ModelScope/alpaca-gpt4-data-zh#5
```

### Evaluation
```shell
CUDA_VISIBLE_DEVICES=0 swift eval \
    --model Qwen/Qwen2.5-7B-Instruct \
    --infer_backend lmdeploy \
    --eval_backend OpenCompass \
    --eval_dataset ARC_c
```

### Quantization
```shell
CUDA_VISIBLE_DEVICES=0 swift export \
    --model Qwen/Qwen2.5-7B-Instruct \
    --quant_bits 4 --quant_method awq \
    --dataset AI-ModelScope/alpaca-gpt4-data-zh \
    --output_dir Qwen2.5-7B-Instruct-AWQ
```

### Push Model
```shell
CUDA_VISIBLE_DEVICES=0 swift export \
    --model <model-path> \
    --push_to_hub true \
    --hub_model_id '<model-id>' \
    --hub_token '<sdk-token>'
```


# Training Methods Explained

This document provides an overview of various training methods used in machine learning, particularly for large-scale models, along with explanations of when to use them and why they are suitable or not.

## 1. **Pre-training**
### What it is:
Pre-training refers to the initial phase of training a model on a large dataset before fine-tuning it on a specific task. This is often done on general-domain data.

### When to use:
- When training a model from scratch for a new domain.
- When improving a model's ability to generalize.
- When developing foundational models for further fine-tuning.

### When not to use:
- When a well-trained model is already available and fine-tuning is sufficient.
- When computational resources are limited.

### Why:
Pre-training is essential for learning broad representations and reduces the amount of labeled data required for downstream tasks. However, it is computationally expensive.

---

## 2. **Instruction Supervised Fine-Tuning**
### What it is:
Fine-tuning a pre-trained model using labeled instruction-response pairs to align it with human instructions.

### When to use:
- When adapting a general model to a specific use case.
- When improving task-specific performance.
- When aligning model outputs to human preferences.

### When not to use:
- When a general pre-trained model already performs well.
- When data for fine-tuning is unavailable or expensive to obtain.

### Why:
Fine-tuning helps adapt models to specific tasks while preserving their general knowledge. It ensures better alignment with real-world applications but requires sufficient labeled data.

---

## 3. **DPO (Direct Preference Optimization) Training**
### What it is:
A reinforcement learning method that directly optimizes for human preferences without needing a reward model.

### When to use:
- When aligning models with human feedback.
- When reinforcement learning with reward models is infeasible.

### When not to use:
- When the dataset lacks preference rankings.
- When a reward model is necessary for more fine-grained optimization.

### Why:
DPO simplifies reinforcement learning by directly leveraging human feedback, avoiding the complexity of reward modeling. However, it requires well-annotated preference data.

---

## 4. **GRPO (Gradient-Based Reward Preference Optimization) Training**
### What it is:
A method that optimizes a model based on a differentiable reward function to align its outputs with desired preferences.

### When to use:
- When preference optimization is needed.
- When the reward function is known and differentiable.

### When not to use:
- When using a reward model is unnecessary.
- When computational resources are limited.

### Why:
GRPO provides a more refined way of aligning models with desired behaviors. However, it can be computationally expensive and requires a well-defined reward function.

---

## 5. **Reward Model Training**
### What it is:
Training a model to predict reward scores based on human preferences or other evaluation criteria.

### When to use:
- When reinforcement learning techniques like PPO and DPO require a reward function.
- When defining explicit evaluation criteria is difficult.

### When not to use:
- When human feedback is directly available.
- When training objectives can be optimized without reward modeling.

### Why:
Reward models allow reinforcement learning models to align with human values. However, training them requires large, high-quality preference datasets.

---

## 6. **PPO (Proximal Policy Optimization) Training**
### What it is:
A reinforcement learning method that optimizes a policy by interacting with an environment while maintaining stability in updates.

### When to use:
- When improving model behavior via reinforcement learning.
- When balancing exploration and exploitation.

### When not to use:
- When supervised fine-tuning is sufficient.
- When computational constraints make reinforcement learning infeasible.

### Why:
PPO is a powerful but resource-intensive method for optimizing policies. It is useful in cases where supervised learning does not provide optimal outcomes.

---

## 7. **KTO (Knowledge Transfer Optimization) Training**
### What it is:
A training method where knowledge from a larger model is distilled into a smaller model.

### When to use:
- When deploying models in resource-constrained environments.
- When reducing inference costs without sacrificing performance.

### When not to use:
- When model compression is unnecessary.
- When full-scale models can be deployed.

### Why:
KTO improves efficiency by making models smaller while retaining performance. However, it can sometimes lead to slight reductions in accuracy.

---

## 8. **CPO (Constrained Policy Optimization) Training**
### What it is:
A reinforcement learning method that optimizes policies while enforcing constraints on behavior.

### When to use:
- When policy constraints must be maintained (e.g., safety in autonomous systems).
- When fine-tuning with hard constraints is required.

### When not to use:
- When unconstrained optimization suffices.
- When defining constraints is difficult.

### Why:
CPO ensures compliance with predefined rules, making it ideal for regulated environments. However, constraints can sometimes make training more difficult.

---

## 9. **SimPO (Simulation Policy Optimization) Training**
### What it is:
A reinforcement learning approach that optimizes policies using simulated environments.

### When to use:
- When training on real-world data is expensive or impractical.
- When reinforcement learning needs safe experimentation.

### When not to use:
- When real-world training data is available and sufficient.
- When simulated environments fail to capture real-world complexities.

### Why:
SimPO provides a cost-effective way to train policies safely. However, performance in simulated settings may not always translate perfectly to real-world tasks.

---

## 10. **ORPO (Optimistic Reinforcement Policy Optimization) Training**
### What it is:
A reinforcement learning method that encourages exploration by assigning optimistic rewards to new behaviors.

### When to use:
- When encouraging exploration in reinforcement learning tasks.
- When overcoming local optima in policy learning.

### When not to use:
- When exploration is unnecessary or risky.
- When convergence to a stable policy is preferred.

### Why:
ORPO helps discover better solutions by encouraging exploration but may lead to instability in some applications.

---

## 11. **Classification Model Training**
### What it is:
Training a model to categorize inputs into predefined classes using labeled data.

### When to use:
- When performing text, image, or speech classification.
- When labels are available for supervised learning.

### When not to use:
- When labels are unavailable or too expensive to obtain.
- When unsupervised learning is more appropriate.

### Why:
Classification models are widely used in various applications but require sufficient labeled data for effective training.

---

## 12. **Embedding Model Training**
### What it is:
Training models to generate vector representations of input data for similarity-based tasks.

### When to use:
- When searching, clustering, or retrieval-based tasks are needed.
- When reducing dimensionality while preserving semantic information.

### When not to use:
- When raw features suffice for the given task.
- When computational constraints prevent large-scale embedding models.

### Why:
Embedding models enable efficient similarity-based retrieval but require significant computational resources for training.

---
