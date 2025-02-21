# Fine-Tuning with Unsloth

## 1. Overview
This repository provides scripts and datasets for fine-tuning large language models using Unsloth within the **Spanda AI Platform**. The fine-tuning process leverages **LoRA (Low-Rank Adaptation)** to enable efficient training with minimal computational resources.

The training process supports three different methodologies:
- **Supervised Fine-Tuning (SFT)**
- **Unsupervised Fine-Tuning (Continuous Pretraining)**
- **Reinforcement Learning (RLHF)**

## 2. Cloning and Setup
To begin, clone the **Spanda AI Platform** repository and navigate to the training scripts:
```bash
# Clone the repository
git clone https://github.com/spandaai/spandaai-platform.git

# Navigate to the appropriate directory
cd spandaai-platform/domain/Edtech/Training
```

## 3. Directory Structure
```
training/
├── Continued_Pre-training/
│   ├── outputs/
│   └── scripts/
│       └── CPT_train.py
├── Datasets/
├── Reinforcement_Learning/
│   ├── outputs/
│   └── scripts/
│       └── ORPO_train.py
└── Supervised_FineTuning/
    ├── outputs/
    └── scripts/
        └── SFT_train.py
```

## 4. Virtual Environment Setup
It is recommended to use a virtual environment for dependency management.

### 4.1 Create and Activate Virtual Environment
```bash
# Create a virtual environment
python3 -m venv venv

# Activate the virtual environment (Linux/Mac)
source venv/bin/activate

# Activate the virtual environment (Windows)
venv\Scripts\activate
```

### 4.2 Install Dependencies
Install the required dependencies:
```bash
pip install -r requirements.txt
```
For fine-tuning with Unsloth, additional dependencies may be required:
```bash
pip install "unsloth[colab-new] @ git+https://github.com/unslothai/unsloth.git"
```
For GPU acceleration:
```bash
pip install "unsloth[cu118] @ git+https://github.com/unslothai/unsloth.git"
```
For CPU-only users:
```bash
pip install "unsloth[huggingface] @ git+https://github.com/unslothai/unsloth.git"
```

## 5. Training Methods
### 5.1 Supervised Fine-Tuning (SFT)
- **Location:** `Supervised_FineTuning/scripts/`
- **Purpose:** Fine-tune an LLM using labeled datasets.
- **Example Command:**
```bash
python SFT_train.py --model_name "unsloth/llama-3.2-1b-Instruct" --dataset "dataset.json"
```

### 5.2 Unsupervised Fine-Tuning (Continuous Pretraining)
- **Location:** `Continued_Pre-training/scripts/`
- **Purpose:** Train an LLM on domain-specific text data without labeled supervision.
- **Example Command:**
```bash
python CPT_train.py --model_name "unsloth/llama-3.2-1b-Instruct" --dataset "corpus.txt"
```

### 5.3 Reinforcement Learning (RLHF)
- **Location:** `Reinforcement_Learning/scripts/`
- **Purpose:** Fine-tune an LLM based on human feedback and reward modeling.
- **Example Command:**
```bash
python ORPO_train.py --model_name "unsloth/llama-3.2-1b-Instruct" --reward_model "reward_model.pt"
```

## 6. Running the Fine-Tuning Scripts
Each training script includes configurable parameters such as batch size, learning rate, and optimization settings. An example command for supervised fine-tuning:
```bash
python SFT_train.py \
    --model_name "unsloth/llama-3.2-1b-Instruct" \
    --max_seq_length 512 \
    --dtype fp16 \
    --load_in_4bit \
    --r 32 \
    --lora_alpha 32 \
    --lora_dropout 0.1 \
    --bias "none" \
    --use_gradient_checkpointing True \
    --random_state 3407 \
    --per_device_train_batch_size 1 \
    --gradient_accumulation_steps 16 \
    --warmup_steps 10 \
    --max_steps 500 \
    --learning_rate 2e-5 \
    --logging_steps 5 \
    --optim adamw_8bit \
    --lr_scheduler_type "linear" \
    --weight_decay 0.01 \
    --seed 3407 \
    --output_dir "outputs" \
    --report_to "tensorboard" \
    --save_model \
    --save_path "model"
```

## 7. Running on Different Environments
### 7.1 Running on a Single GPU
```bash
CUDA_VISIBLE_DEVICES=0 python SFT_train.py --model_name "unsloth/llama-3.2-1b-Instruct"
```

### 7.2 Running on Multiple GPUs
Using PyTorch distributed training:
```bash
torchrun --nproc_per_node=2 SFT_train.py --model_name "unsloth/llama-3.2-1b-Instruct"
```

### 7.3 Running on CPU-Only Mode
For CPU-only training (not recommended for large models):
```bash
python SFT_train.py --model_name "unsloth/llama-3.2-1b-Instruct" --dtype bf16
```

## 8. Troubleshooting
- **Out of Memory (OOM) Errors?**
  - Reduce `--per_device_train_batch_size`
  - Enable `--use_gradient_checkpointing`
  - Use `--load_in_4bit`
- **Dataset Issues?**
  - Ensure dataset format is correct (JSON, CSV, Hugging Face dataset)
- **Slow Training?**
  - Optimize using `--optim adamw_8bit`
  - Ensure GPU acceleration is enabled

---

This README provides step-by-step guidance for setting up and fine-tuning LLMs using Unsloth within the **Spanda AI Platform**. Follow the instructions carefully to ensure a smooth training process.

