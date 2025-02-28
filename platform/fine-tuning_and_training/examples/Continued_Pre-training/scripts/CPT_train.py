#!/usr/bin/env python3
"""
🦥 Starter Script for Continued Pretraining with Unsloth
This script supports .txt, .json, and .csv datasets with a unified data format (Subject, Topic, Text).
It uses UnslothTrainer and UnslothTrainingArguments for faster and more efficient training.
Usage:
    python unsloth-cpt.py --model_name "unsloth/llama-3-8b" --dataset "path/to/dataset.csv" \
    --data_format "csv" --max_seq_length 2048 --per_device_train_batch_size 2 \
    --gradient_accumulation_steps 4 --max_steps 1000 --learning_rate 5e-5 --save_model
To see a full list of configurable options, use:
    python unsloth-cpt.py --help
Happy pretraining!
"""
import argparse
import os
import pandas as pd
from datasets import Dataset
from transformers.utils import strtobool
from unsloth import FastLanguageModel, is_bfloat16_supported
from unsloth import UnslothTrainer, UnslothTrainingArguments  # Import Unsloth-specific components
import logging

logging.getLogger('hf-to-gguf').setLevel(logging.WARNING)

def run(args):
    import torch

    # Load model and tokenizer
    try:
        model, tokenizer = FastLanguageModel.from_pretrained(
            model_name=args.model_name,
            max_seq_length=args.max_seq_length,
            dtype=args.dtype,
            load_in_4bit=args.load_in_4bit,
        )
    except Exception as e:
        raise RuntimeError(f"Failed to load model: {str(e)}")

    # Configure PEFT model
    target_modules = args.target_modules.split(",") if args.target_modules else [
        "q_proj", "k_proj", "v_proj", "o_proj",
        "gate_proj", "up_proj", "down_proj",
        "lm_head", "embed_tokens",  # Include lm_head and embed_tokens for CPT
    ]
    model = FastLanguageModel.get_peft_model(
        model,
        r=args.r,
        target_modules=target_modules,
        lora_alpha=args.lora_alpha,
        lora_dropout=args.lora_dropout, 
        bias=args.bias,
        use_gradient_checkpointing=args.use_gradient_checkpointing,
        random_state=args.random_state,
        use_rslora=args.use_rslora,
        loftq_config=args.loftq_config,
    )

    # Define a customizable prompt template
    def get_prompt_template():
        return """Subject: {}\nTopic: {}\nText: {}"""

    EOS_TOKEN = tokenizer.eos_token  # Must add EOS_TOKEN

    # Load and preprocess dataset based on format
    def load_and_preprocess_dataset(dataset_path, data_format):
        if data_format == "txt":
            # Assume tab-separated values: Subject<TAB>Topic<TAB>Text
            with open(dataset_path, "r", encoding="utf-8") as f:
                lines = f.readlines()
            examples = [line.strip().split("\t") for line in lines]
            subjects, topics, texts = zip(*examples)
        elif data_format == "json":
            # Assume JSON file with "Subject", "Topic", and "Text" keys
            import json
            with open(dataset_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            subjects = [item["Subject"] for item in data]
            topics = [item["Topic"] for item in data]
            texts = [item["Text"] for item in data]
        elif data_format == "csv":
            # Assume CSV file with "Subject", "Topic", and "Text" columns
            df = pd.read_csv(dataset_path)
            subjects = df["Subject"].tolist()
            topics = df["Topic"].tolist()
            texts = df["Text"].tolist()
        else:
            raise ValueError(f"Unsupported data format: {data_format}")

        # Combine Subject, Topic, and Text into a single string
        prompt_template = get_prompt_template()
        formatted_texts = [
            prompt_template.format(subject, topic, text) + EOS_TOKEN
            for subject, topic, text in zip(subjects, topics, texts)
        ]

        return Dataset.from_dict({"text": formatted_texts})

    # Load dataset
    dataset = load_and_preprocess_dataset(args.dataset, args.data_format)

    # Configure UnslothTrainingArguments with separate learning rates for embeddings
    training_args = UnslothTrainingArguments(
        per_device_train_batch_size=args.per_device_train_batch_size,
        gradient_accumulation_steps=args.gradient_accumulation_steps,
        warmup_steps=args.warmup_steps,
        max_steps=args.max_steps,
        learning_rate=args.learning_rate,
        embedding_learning_rate=args.embedding_learning_rate,  # Separate learning rate for embeddings
        fp16=not is_bfloat16_supported(),
        bf16=is_bfloat16_supported(),
        logging_steps=args.logging_steps,
        optim=args.optim,
        weight_decay=args.weight_decay,
        lr_scheduler_type=args.lr_scheduler_type,
        seed=args.seed,
        output_dir=args.output_dir,
        report_to=args.report_to,
    )

    # Initialize UnslothTrainer
    trainer = UnslothTrainer(
        model=model,
        tokenizer=tokenizer,
        train_dataset=dataset,
        args=training_args,
    )

    # Train model
    print("Starting continued pretraining...")
    trainer_stats = trainer.train()

    # Save model
    if args.save_model:
        if args.save_gguf:
            if isinstance(args.quantization, list):
                for quantization_method in args.quantization:
                    print(f"Saving model with quantization method: {quantization_method}")
                    model.save_pretrained_gguf(
                        args.save_path,
                        tokenizer,
                        quantization_method=quantization_method,
                    )
                    if args.push_model:
                        model.push_to_hub_gguf(
                            hub_path=args.hub_path,
                            hub_token=args.hub_token,
                            quantization_method=quantization_method,
                        )
            else:
                print(f"Saving model with quantization method: {args.quantization}")
                model.save_pretrained_gguf(
                    args.save_path,
                    tokenizer,
                    quantization_method=args.quantization,
                )
                if args.push_model:
                    model.push_to_hub_gguf(
                        hub_path=args.hub_path,
                        hub_token=args.hub_token,
                        quantization_method=args.quantization,
                    )
        else:
            # Save merged model
            model.save_pretrained_merged(args.save_path, tokenizer, args.save_method)
            if args.push_model:
                model.push_to_hub_merged(args.save_path, tokenizer, args.hub_token)
    else:
        print("Warning: The model is not saved!")

if __name__ == "__main__":
    # Define argument parser
    parser = argparse.ArgumentParser(description="🦥 Continue pretraining your llm faster using unsloth!")

    # Model Options
    model_group = parser.add_argument_group("🤖 Model Options")
    model_group.add_argument('--model_name', type=str, default="unsloth/llama-3.2-1b-Instruct", help="Model name to load")
    model_group.add_argument('--max_seq_length', type=int, default=512, help="Maximum sequence length, default is 2048.")
    model_group.add_argument('--dtype', type=str, default=None, help="Data type for model (None for auto detection)")
    model_group.add_argument('--load_in_4bit', action='store_true', help="Use 4bit quantization to reduce memory usage")
    model_group.add_argument('--dataset', type=str, default="test.json",required=True, help="Path to dataset file (.txt, .json, .csv)")
    model_group.add_argument('--data_format', type=str, choices=["txt", "json", "csv"], required=True, help="Dataset format: 'txt', 'json', or 'csv'")

    # LoRA Options
    lora_group = parser.add_argument_group("🧠 LoRA Options", "These options are used to configure the LoRA model.")
    lora_group.add_argument('--r', type=int, default=16, help="Rank for Lora model, default is 16. (common values: 8, 16, 32, 64, 128)")
    lora_group.add_argument('--lora_alpha', type=int, default=16, help="LoRA alpha parameter, default is 16. (common values: 8, 16, 32, 64, 128)")
    lora_group.add_argument('--lora_dropout', type=float, default=0, help="LoRA dropout rate, default is 0.0 which is optimized.")
    lora_group.add_argument('--bias', type=str, default="none", help="Bias setting for LoRA")
    lora_group.add_argument('--use_gradient_checkpointing', type=str, default="unsloth", help="Use gradient checkpointing")
    lora_group.add_argument('--random_state', type=int, default=3407, help="Random state for reproducibility, default is 3407.")
    lora_group.add_argument('--use_rslora', action='store_true', help="Use rank stabilized LoRA")
    lora_group.add_argument('--loftq_config', type=str, default=None, help="Configuration for LoftQ")
    lora_group.add_argument('--target_modules', type=str, default=None, help="Comma-separated list of target modules to fine-tune (e.g., 'q_proj,k_proj,v_proj,o_proj')")

    # Training Options
    training_group = parser.add_argument_group("🎓 Training Options")
    training_group.add_argument('--per_device_train_batch_size', type=int, default=1, help="Batch size per device during training, default is 2.")
    training_group.add_argument('--gradient_accumulation_steps', type=int, default=2, help="Number of gradient accumulation steps, default is 4.")
    training_group.add_argument('--warmup_steps', type=int, default=5, help="Number of warmup steps, default is 5.")
    training_group.add_argument('--max_steps', type=int, default=1000, help="Maximum number of training steps.")
    training_group.add_argument('--learning_rate', type=float, default=5e-5, help="Learning rate, default is 5e-5.")
    training_group.add_argument('--embedding_learning_rate', type=float, default=5e-6, help="Learning rate for lm_head and embed_tokens, default is 5e-6.")
    training_group.add_argument('--optim', type=str, default="adamw_8bit", help="Optimizer type.")
    training_group.add_argument('--weight_decay', type=float, default=0.01, help="Weight decay, default is 0.01.")
    training_group.add_argument('--lr_scheduler_type', type=str, default="linear", help="Learning rate scheduler type, default is 'linear'.")
    training_group.add_argument('--seed', type=int, default=3407, help="Seed for reproducibility, default is 3407.")

    # Report/Logging Options
    report_group = parser.add_argument_group("📊 Report Options")
    report_group.add_argument('--report_to', type=str, default="tensorboard",
        choices=["azure_ml", "clearml", "codecarbon", "comet_ml", "dagshub", "dvclive", "flyte", "mlflow", "neptune", "tensorboard", "wandb", "all", "none"],
        help="The list of integrations to report the results and logs to.")
    report_group.add_argument('--logging_steps', type=int, default=1, help="Logging steps, default is 1")

    # Saving and Pushing Options
    save_group = parser.add_argument_group('💾 Save Model Options')
    save_group.add_argument('--output_dir', type=str, default="./outputs", help="Output directory")
    save_group.add_argument('--save_model', action='store_true', help="Save the model after training")
    save_group.add_argument('--save_method', type=str, default="merged_16bit", choices=["merged_16bit", "merged_4bit", "lora"], help="Save method for the model, default is 'merged_16bit'")
    save_group.add_argument('--save_gguf', action='store_true', help="Convert the model to GGUF after training")
    save_group.add_argument('--save_path', type=str, default="pretrained_model", help="Path to save the model")
    save_group.add_argument('--quantization', type=str, default="q8_0", nargs="+",
        help="Quantization method for saving the model. Common values ('f16', 'q4_k_m', 'q8_0'), Check our wiki for all quantization methods https://github.com/unslothai/unsloth/wiki#saving-to-gguf ")

    push_group = parser.add_argument_group('🚀 Push Model Options')
    push_group.add_argument('--push_model', action='store_true', help="Push the model to Hugging Face hub after training")
    push_group.add_argument('--push_gguf', action='store_true', help="Push the model as GGUF to Hugging Face hub after training")
    push_group.add_argument('--hub_path', type=str, default="hf/pretrained-model", help="Path on Hugging Face hub to push the model")
    push_group.add_argument('--hub_token', type=str, help="Token for pushing the model to Hugging Face hub")

    # Parse arguments and run
    args = parser.parse_args()
    run(args)