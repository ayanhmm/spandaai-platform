Below is a comprehensive documentation that outlines the various distributed training engines supported by LLaMA-Factory, explains their key differences, and provides detailed examples and configuration instructions. You can use this document as a reference for setting up single-node or multi-node training with DDP, DeepSpeed, and FSDP.

---

# Distributed Training with LLaMA-Factory: A Comprehensive Guide

## Introduction

Distributed training is essential for scaling large models and reducing training time. LLaMA-Factory supports three primary distributed training engines:

- **DDP (DistributedDataParallel)**
- **DeepSpeed**
- **FSDP (Fully Sharded Data Parallel)**

Each engine offers unique benefits—ranging from basic multi-GPU training to advanced memory optimizations—allowing you to choose the best option based on your task requirements and hardware resources.

---

## Table of Contents

1. [Overview of Distributed Training Engines](#overview-of-distributed-training-engines)
   - [DDP (DistributedDataParallel)](#ddp-distributeddataparallel)
   - [DeepSpeed](#deepspeed)
   - [FSDP (Fully Sharded Data Parallel)](#fsdp-fully-sharded-data-parallel)
2. [NativeDDP and Command-Line Examples](#nativeddp-and-command-line-examples)
   - [Using llamafactory-cli](#using-llamafactory-cli)
   - [Using torchrun](#using-torchrun)
   - [Using accelerate](#using-accelerate)
3. [DeepSpeed: Configuration and Usage](#deepspeed-configuration-and-usage)
   - [ZeRO Stages and Offload Options](#zero-stages-and-offload-options)
4. [FSDP: Configuration and Usage](#fsdp-configuration-and-usage)
5. [Additional Notes and References](#additional-notes-and-references)

---

## Overview of Distributed Training Engines

### DDP (DistributedDataParallel)

- **Description:**  
  DDP leverages both model and data parallelism by generating multiple processes and creating a DDP instance on each using `torch.distributed`.  
- **Key Benefits:**  
  - Easy setup for multi-GPU training.
  - Native integration with PyTorch.
- **Usage Scenario:**  
  Ideal when you have a standard multi-GPU environment and want to use PyTorch’s native features.

---

### DeepSpeed

- **Description:**  
  DeepSpeed is a distributed training engine developed by Microsoft that integrates several optimization technologies such as ZeRO, advanced Adam optimizers, and pipeline parallelism.  
- **Optimization Technologies:**  
  - **ZeRO-0:** Basic parameter optimization.
  - **ZeRO-2:** Each GPU holds a complete set of model parameters.
  - **ZeRO-3:** Optimizer parameters, gradients, and model parameters are partitioned across GPUs.
- **Offloading:**  
  Using `offload_param=cpu` can reduce memory usage at the expense of training speed. With sufficient memory, it’s recommended to use `offload_param=none`.
- **Usage Scenario:**  
  Best for training very large models where memory is a constraint.

---

### FSDP (Fully Sharded Data Parallel)

- **Description:**  
  FSDP shards model parameters, gradients, and optimizer states across GPUs, keeping only parts of them on each device. It also supports offloading parameters to the CPU for further memory optimization.
- **Sharding Strategies:**  
  - **FULL_SHARD:** Similar to ZeRO-3.
  - **SHARD_GRAD_OP:** Similar to ZeRO-2.
  - **NO_SHARD:** Similar to ZeRO-0.
- **Usage Scenario:**  
  Ideal for extreme-scale training where memory efficiency is critical.

---

## NativeDDP and Command-Line Examples

### Using llamafactory-cli

NativeDDP is provided by PyTorch and integrated into LLaMA-Factory. Launch training with:

```bash
FORCE_TORCHRUN=1 llamafactory-cli train examples/train_full/llama3_full_sft_ds3.yaml
```

To specify particular GPUs (e.g., GPU 0 and GPU 1):

```bash
FORCE_TORCHRUN=1 CUDA_VISIBLE_DEVICES=0,1 llamafactory-cli train config/config1.yaml
```

---

### Using torchrun

**Single-Node Multi-GPU Training Example:**

```bash
torchrun --standalone --nnodes=1 --nproc-per-node=8 src/train.py \
  --stage sft \
  --model_name_or_path meta-llama/Meta-Llama-3-8B-Instruct \
  --do_train \
  --dataset alpaca_en_demo \
  --template llama3 \
  --finetuning_type lora \
  --output_dir saves/llama3-8b/lora/ \
  --overwrite_cache \
  --per_device_train_batch_size 1 \
  --gradient_accumulation_steps 8 \
  --lr_scheduler_type cosine \
  --logging_steps 100 \
  --save_steps 500 \
  --learning_rate 1e-4 \
  --num_train_epochs 2.0 \
  --plot_loss \
  --bf16
```

**Multi-Node Multi-GPU Training:**

On **Node 0**:

```bash
torchrun --master_port 29500 --nproc_per_node=8 --nnodes=2 --node_rank=0 \
  --master_addr=192.168.0.1 train.py
```

On **Node 1**:

```bash
torchrun --master_port 29500 --nproc_per_node=8 --nnodes=2 --node_rank=1 \
  --master_addr=192.168.0.1 train.py
```

---

### Using accelerate

The `accelerate` tool simplifies configuration for multi-GPU training.

#### Single-Node Configuration

First, generate a configuration file:

```bash
accelerate config
```

Example configuration (`accelerate_singleNode_config.yaml`):

```yaml
compute_environment: LOCAL_MACHINE
debug: true
distributed_type: MULTI_GPU
downcast_bf16: 'no'
enable_cpu_affinity: false
gpu_ids: all
machine_rank: 0
main_training_function: main
mixed_precision: fp16
num_machines: 1
num_processes: 8
rdzv_backend: static
same_network: true
tpu_env: []
tpu_use_cluster: false
tpu_use_sudo: false
use_cpu: false
```

Launch training with:

```bash
accelerate launch --config_file accelerate_singleNode_config.yaml src/train.py training_config.yaml
```

#### Multi-Node Configuration

Generate a multi-node configuration file:

```bash
accelerate config
```

Example configuration (`accelerate_multiNode_config.yaml`):

```yaml
compute_environment: LOCAL_MACHINE
debug: true
distributed_type: MULTI_GPU
downcast_bf16: 'no'
enable_cpu_affinity: false
gpu_ids: all
machine_rank: 0
main_process_ip: '192.168.0.1'
main_process_port: 29500
main_training_function: main
mixed_precision: fp16
num_machines: 2
num_processes: 16
rdzv_backend: static
same_network: true
tpu_env: []
tpu_use_cluster: false
tpu_use_sudo: false
use_cpu: false
```

Launch training with:

```bash
accelerate launch --config_file accelerate_multiNode_config.yaml train.py llm_config.yaml
```

---

## DeepSpeed: Configuration and Usage

DeepSpeed is ideal for large-scale model training, offering several ZeRO optimization stages.

### Using DeepSpeed with LLaMA-Factory

Start training using DeepSpeed with LLaMA-Factory CLI:

```bash
FORCE_TORCHRUN=1 llamafactory-cli train examples/train_full/llama3_full_sft_ds3.yaml
```

In your training configuration, specify the DeepSpeed configuration file:

```yaml
deepspeed: examples/deepspeed/ds_z3_config.json
```

Alternatively, launch using the DeepSpeed command:

```bash
deepspeed --include localhost:1 your_program.py <other args> --deepspeed ds_config.json
```

For multi-node training:

**On Node 0:**

```bash
FORCE_TORCHRUN=1 NNODES=2 NODE_RANK=0 MASTER_ADDR=192.168.0.1 MASTER_PORT=29500 llamafactory-cli train examples/train_lora/llama3_lora_sft_ds3.yaml
```

**On Node 1:**

```bash
FORCE_TORCHRUN=1 NNODES=2 NODE_RANK=1 MASTER_ADDR=192.168.0.1 MASTER_PORT=29500 llamafactory-cli train examples/train_lora/llama3_lora_sft_ds3.yaml
```

### ZeRO Stages and Offload Options

#### ZeRO-0 Configuration (`ds_z0_config.json`):

```json
{
    "train_batch_size": "auto",
    "train_micro_batch_size_per_gpu": "auto",
    "gradient_accumulation_steps": "auto",
    "gradient_clipping": "auto",
    "zero_allow_untested_optimizer": true,
    "fp16": {
        "enabled": "auto",
        "loss_scale": 0,
        "loss_scale_window": 1000,
        "initial_scale_power": 16,
        "hysteresis": 2,
        "min_loss_scale": 1
    },
    "bf16": {
        "enabled": "auto"
    },
    "zero_optimization": {
        "stage": 0,
        "allgather_partitions": true,
        "allgather_bucket_size": 5e8,
        "overlap_comm": true,
        "reduce_scatter": true,
        "reduce_bucket_size": 5e8,
        "contiguous_gradients": true,
        "round_robin_gradients": true
    }
}
```

#### ZeRO-2 Configuration (`ds_z2_config.json`):

Modify the stage parameter:

```json
{
    ...
    "zero_optimization": {
        "stage": 2
    ...
    }
}
```

#### ZeRO-2+offload Configuration (`ds_z2_offload_config.json`):

Add offloading for the optimizer:

```json
{
    ...
    "zero_optimization": {
        "stage": 2,
        "offload_optimizer": {
            "device": "cpu",
            "pin_memory": true
        }
    ...
    }
}
```

#### ZeRO-3 Configuration (`ds_z3_config.json`):

Additional modifications for partitioning:

```json
{
    ...
    "zero_optimization": {
        "stage": 3,
        "overlap_comm": true,
        "contiguous_gradients": true,
        "sub_group_size": 1e9,
        "reduce_bucket_size": "auto",
        "stage3_prefetch_bucket_size": "auto",
        "stage3_param_persistence_threshold": "auto",
        "stage3_max_live_parameters": 1e9,
        "stage3_max_reuse_distance": 1e9,
        "stage3_gather_16bit_weights_on_model_save": true
    }
}
```

#### ZeRO-3+offload Configuration (`ds_z3_offload_config.json`):

Include offloading for both optimizer and parameters:

```json
{
    ...
    "zero_optimization": {
        "stage": 3,
        "offload_optimizer": {
            "device": "cpu",
            "pin_memory": true
        },
        "offload_param": {
            "device": "cpu",
            "pin_memory": true
        }
    ...
    }
}
```

For more details, please refer to the [DeepSpeed documentation](https://www.deepspeed.ai/docs/config-json/).

#### Using accelerate with DeepSpeed

Generate a DeepSpeed configuration with:

```bash
accelerate config
```

Example configuration file (`deepspeed_config.yaml`):

```yaml
compute_environment: LOCAL_MACHINE
debug: false
deepspeed_config:
    deepspeed_multinode_launcher: standard
    gradient_accumulation_steps: 8
    offload_optimizer_device: none
    offload_param_device: none
    zero3_init_flag: false
    zero_stage: 3
distributed_type: DEEPSPEED
downcast_bf16: 'no'
enable_cpu_affinity: false
machine_rank: 0
main_process_ip: '192.168.0.1'
main_process_port: 29500
main_training_function: main
mixed_precision: fp16
num_machines: 2
num_processes: 16
rdzv_backend: static
same_network: true
tpu_env: []
tpu_use_cluster: false
tpu_use_sudo: false
use_cpu: false
```

Launch training with:

```bash
accelerate launch --config_file deepspeed_config.yaml train.py llm_config.yaml
```

---

## FSDP: Configuration and Usage

FSDP uses PyTorch’s Fully Sharded Data Parallel technology to shard model parameters, gradients, and optimizer states across GPUs. This approach reduces memory footprint and enables training of very large models.

### Using llamafactory-cli for FSDP

Launch FSDP training using an example configuration file:

```bash
llamafactory-cli train examples/accelerate/fsdp_config.yaml
```

For QLoRA fine-tuning with FSDP, you can use:

```bash
bash examples/extras/fsdp qlora/train.sh
```

### Using accelerate with FSDP

Generate a configuration file:

```bash
accelerate config
```

Example configuration (`fsdp_config.yaml`):

```yaml
compute_environment: LOCAL_MACHINE
debug: false
distributed_type: FSDP
downcast_bf16: 'no'
# Customize further as needed for your setup
```

---

## Additional Notes and References

- **DeepSpeed Documentation:**  
  [https://www.deepspeed.ai/docs/config-json/](https://www.deepspeed.ai/docs/config-json/)
- **Hugging Face Transformers + DeepSpeed:**  
  [https://huggingface.co/docs/transformers/deepspeed](https://huggingface.co/docs/transformers/deepspeed)
- **Multi-Node DeepSpeed Hostfile:**  
  Create a file (e.g., `hostfile`) with each node specified as:  
  ```
  worker-1 slots=4
  worker-2 slots=4
  ```

---

This document should serve as a detailed guide for configuring and launching distributed training using LLaMA-Factory. Depending on your specific requirements and hardware setup, you can select and tailor the appropriate engine (DDP, DeepSpeed, or FSDP) to optimize your training workflow.