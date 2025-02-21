# Spanda AI Fine-Tuning Platform

## 🚀 What We Offer

Spanda AI provides a streamlined fine-tuning framework for Large Language Models (LLMs). Our platform is optimized for efficient adaptation using LoRA (Low-Rank Adaptation) and other advanced techniques, allowing fine-tuning on minimal compute resources.

## 🔹 Key Features

- **Multiple Fine-Tuning Approaches**: Supports Supervised Fine-Tuning (SFT), Unsupervised Pretraining, and RLHF (Reinforcement Learning with Human Feedback).
- **Optimized Performance**: Leverages efficient training methods to enable cost-effective LLM adaptation.
- **Seamless Deployment**: Easily integrates with the Spanda AI Platform for production-ready AI solutions.

## 🛠️ Getting Started

### 1️⃣ Clone the Repository
```sh
git clone https://github.com/spandaai/spandaai-platform.git
cd spandaai-platform/domain/Edtech/Training
```

### 2️⃣ Directory Structure
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

### 3️⃣ Setup Virtual Environment
```sh
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate  # Windows
```

### 4️⃣ Install Dependencies

#### 4.1 General Dependencies
```sh
pip install -r requirements.txt
```

#### 4.2 Unsloth Installation
For fine-tuning with Unsloth, additional dependencies may be required:
```sh
pip install "unsloth[colab-new] @ git+https://github.com/unslothai/unsloth.git"
```
For GPU acceleration:
```sh
pip install "unsloth[cu118] @ git+https://github.com/unslothai/unsloth.git"
```

## 🔍 Fine-Tuning Methods

### 📌 Supervised Fine-Tuning (SFT)
- **Location**: `Supervised_FineTuning/scripts/`
- **Purpose**: Fine-tune an LLM using labeled datasets.
- **Example Command**:
```sh
python SFT_train.py --model_name "unsloth/llama-3.2-1b-Instruct" --dataset "dataset.json"
```

### 📌 Unsupervised Fine-Tuning (Continuous Pretraining)
- **Location**: `Continued_Pre-training/scripts/`
- **Purpose**: Train an LLM on domain-specific text data without labeled supervision.
- **Example Command**:
```sh
python CPT_train.py --model_name "unsloth/llama-3.2-1b-Instruct" --dataset "corpus.txt"
```

### 📌 Reinforcement Learning (RLHF)
- **Location**: `Reinforcement_Learning/scripts/`
- **Purpose**: Fine-tune an LLM based on human feedback and reward modeling.
- **Example Command**:
```sh
python ORPO_train.py --model_name "unsloth/llama-3.2-1b-Instruct"
```

## ⚙️ Running the Fine-Tuning Scripts
Each training script includes configurable parameters such as batch size, learning rate, and optimization settings.

Example command for supervised fine-tuning:
```sh
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

## 💻 Running on Different Environments

### Single GPU:
```sh
CUDA_VISIBLE_DEVICES=0 python SFT_train.py --model_name "llama-3.2-1b-Instruct"
```

### Multi-GPU:
```sh
torchrun --nproc_per_node=2 SFT_train.py --model_name "llama-3.2-1b-Instruct"
```

## 🛠️ Troubleshooting

### Out of Memory (OOM) Errors?
- Reduce `--per_device_train_batch_size`
- Enable `--use_gradient_checkpointing`
- Use `--load_in_4bit`

### Dataset Issues?
- Ensure dataset format is correct (JSON, CSV, Hugging Face dataset)

### Slow Training?
- Optimize using `--optim adamw_8bit`
- Ensure GPU acceleration is enabled
