#!/usr/bin/env python3
"""
🦥 Starter Script for Fine-Tuning FastLanguageModel with Unsloth and ORPO
This script supports multiple data formats (Alpaca, ChatML, Custom) and includes configurable options for model loading, PEFT parameters, training arguments, and model saving/pushing functionalities.
Usage:
    python unsloth-orpo-cli.py --model_name "unsloth/llama-3-8b" --max_seq_length 2048 --dtype None --load_in_4bit \
    --csv_path "path/to/your/file.csv" --data_format "custom" --r 16 --lora_alpha 16 --lora_dropout 0 --bias "none" \
    --use_gradient_checkpointing "unsloth" --random_state 3407 --use_rslora --loftq_config None \
    --per_device_train_batch_size 2 --gradient_accumulation_steps 4 --warmup_steps 5 --max_steps 400 \
    --learning_rate 2e-4 --optim "adamw_8bit" --weight_decay 0.01 --lr_scheduler_type "linear" --seed 3407 \
    --report_to "tensorboard" --logging_steps 1 --output_dir "outputs" --save_model --save_method "merged_16bit" \
    --save_gguf --save_path "model" --quantization "q8_0" --push_model --push_gguf --hub_path "hf/model" --hub_token "your_hf_token"
To see a full list of configurable options, use:
    python unsloth-orpo-cli.py --help
Happy fine-tuning!
"""

import argparse
import os
from transformers.utils import strtobool
from trl import ORPOConfig, ORPOTrainer
from transformers import TrainingArguments
from unsloth import FastLanguageModel, is_bfloat16_supported
from datasets import load_dataset
import logging

# Suppress unnecessary logging
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
    model = FastLanguageModel.get_peft_model(
        model,
        r=args.r,
        target_modules=["q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj"],
        lora_alpha=args.lora_alpha,
        lora_dropout=args.lora_dropout,
        bias=args.bias,
        use_gradient_checkpointing=args.use_gradient_checkpointing,
        random_state=args.random_state,
        use_rslora=args.use_rslora,
        loftq_config=args.loftq_config,
    )

    # Define Alpaca prompt template
    alpaca_prompt = """Below is an instruction that describes a task, paired with an input that provides further context. Write a response that appropriately completes the request.
    ### Instruction:
    {}
    ### Input:
    {}
    ### Response:
    {}"""
    EOS_TOKEN = tokenizer.eos_token  # Must add EOS_TOKEN

    def format_prompt(samples):
        instructions = samples["instruction"]
        inputs = samples["input"]
        accepteds = samples["accepted"]
        rejecteds = samples["rejected"]

        # Ensure accepteds and rejecteds are strings (in case they are lists)
        if isinstance(accepteds[0], list):
            accepteds = [" ".join(accepted) for accepted in accepteds]
        if isinstance(rejecteds[0], list):
            rejecteds = [" ".join(rejected) for rejected in rejecteds]

        # Format prompts for all rows in the batch
        prompts = [alpaca_prompt.format(instr, inp, "") for instr, inp in zip(instructions, inputs)]
        chosens = [accepted + EOS_TOKEN for accepted in accepteds]
        rejecteds = [rejected + EOS_TOKEN for rejected in rejecteds]

        return {
            "prompt": prompts,
            "chosen": chosens,
            "rejected": rejecteds,
        }

    # Load dataset
    if args.csv_path:
        # Load dataset from CSV
        dataset = load_dataset("csv", data_files=args.csv_path, split="train")
    else:
        use_modelscope = strtobool(os.environ.get('UNSLOTH_USE_MODELSCOPE', 'False'))
        if use_modelscope:
            from modelscope import MsDataset
            dataset = MsDataset.load(args.dataset, split="train")
        else:
            dataset = load_dataset(args.dataset, split="train")

    # Preprocess dataset
    dataset = dataset.map(format_prompt, batched=True)
    print("Data is formatted and ready!")

    # Configure training arguments
    training_args = TrainingArguments(
        per_device_train_batch_size=args.per_device_train_batch_size,
        gradient_accumulation_steps=args.gradient_accumulation_steps,
        warmup_steps=args.warmup_steps,
        max_steps=args.max_steps,
        learning_rate=args.learning_rate,
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

    # Initialize ORPOTrainer
    orpo_trainer = ORPOTrainer(
        model=model,
        train_dataset=dataset,
        tokenizer=tokenizer,
        args=ORPOConfig(
            max_length=args.max_seq_length,
            max_prompt_length=args.max_seq_length // 2,
            max_completion_length=args.max_seq_length // 2,
            per_device_train_batch_size=args.per_device_train_batch_size,
            gradient_accumulation_steps=args.gradient_accumulation_steps,
            beta=0.1,
            logging_steps=args.logging_steps,
            optim=args.optim,
            lr_scheduler_type=args.lr_scheduler_type,
            max_steps=args.max_steps,
            fp16=not is_bfloat16_supported(),
            bf16=is_bfloat16_supported(),
            output_dir=args.output_dir,
            report_to=args.report_to,
        ),
    )

    # Train model
    orpo_trainer.train()

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
            model.save_pretrained_merged(args.save_path, tokenizer, args.save_method)
            if args.push_model:
                model.push_to_hub_merged(args.save_path, tokenizer, args.hub_token)
    else:
        print("Warning: The model is not saved!")


if __name__ == "__main__":
    # Define argument parser
    parser = argparse.ArgumentParser(description="🦥 Fine-tune your LLM faster using Unsloth and ORPO!")
    
    # Model Options
    model_group = parser.add_argument_group("🤖 Model Options")
    model_group.add_argument('--model_name', type=str, default="unsloth/", help="Model name to use for training.")
    model_group.add_argument('--max_seq_length', type=int, default=2048, help="Maximum sequence length, default is 2048.")
    model_group.add_argument('--dtype', type=str, default=None, help="Data type for model (None for auto detection).")
    model_group.add_argument('--load_in_4bit', action='store_true', help="Use 4-bit quantization to reduce memory usage.")
    model_group.add_argument('--dataset', type=str, default="reciperesearch/dolphin-sft-v0.1-preference", help="Huggingface dataset to use for training.")
    model_group.add_argument('--csv_path', type=str, default=None, help="Path to a CSV file for training.")

    # LoRA Options
    lora_group = parser.add_argument_group("🧠 LoRA Options", "These options are used to configure the LoRA model.")
    lora_group.add_argument('--r', type=int, default=16, help="Rank for Lora model, default is 16.")
    lora_group.add_argument('--lora_alpha', type=int, default=16, help="LoRA alpha parameter, default is 16.")
    lora_group.add_argument('--lora_dropout', type=float, default=0, help="LoRA dropout rate, default is 0.")
    lora_group.add_argument('--bias', type=str, default="none", help="Bias setting for LoRA.")
    lora_group.add_argument('--use_gradient_checkpointing', type=str, default="unsloth", help="Use gradient checkpointing.")
    lora_group.add_argument('--random_state', type=int, default=3407, help="Random state for reproducibility, default is 3407.")
    lora_group.add_argument('--use_rslora', action='store_true', help="Use rank stabilized LoRA.")
    lora_group.add_argument('--loftq_config', type=str, default=None, help="Configuration for LoftQ.")

    # Training Options
    training_group = parser.add_argument_group("🎓 Training Options")
    training_group.add_argument('--per_device_train_batch_size', type=int, default=2, help="Batch size per device during training, default is 2.")
    training_group.add_argument('--gradient_accumulation_steps', type=int, default=4, help="Number of gradient accumulation steps, default is 4.")
    training_group.add_argument('--warmup_steps', type=int, default=5, help="Number of warmup steps, default is 5.")
    training_group.add_argument('--max_steps', type=int, default=400, help="Maximum number of training steps, default is 400.")
    training_group.add_argument('--learning_rate', type=float, default=2e-4, help="Learning rate, default is 2e-4.")
    training_group.add_argument('--optim', type=str, default="adamw_8bit", help="Optimizer type, default is adamw_8bit.")
    training_group.add_argument('--weight_decay', type=float, default=0.01, help="Weight decay, default is 0.01.")
    training_group.add_argument('--lr_scheduler_type', type=str, default="linear", help="Learning rate scheduler type, default is 'linear'.")
    training_group.add_argument('--seed', type=int, default=3407, help="Seed for reproducibility, default is 3407.")

    # Report/Logging Options
    report_group = parser.add_argument_group("📊 Report Options")
    report_group.add_argument('--report_to', type=str, default="tensorboard",
        choices=["azure_ml", "clearml", "codecarbon", "comet_ml", "dagshub", "dvclive", "flyte", "mlflow", "neptune", "tensorboard", "wandb", "all", "none"],
        help="The list of integrations to report the results and logs to.")
    report_group.add_argument('--logging_steps', type=int, default=1, help="Logging steps, default is 1.")

    # Saving and Pushing Options
    save_group = parser.add_argument_group('💾 Save Model Options')
    save_group.add_argument('--output_dir', type=str, default="./outputs", help="Output directory.")
    save_group.add_argument('--save_model', action='store_true', help="Save the model after training.")
    save_group.add_argument('--save_method', type=str, default="merged_16bit", choices=["merged_16bit", "merged_4bit", "lora"], help="Save method for the model, default is 'merged_16bit'.")
    save_group.add_argument('--save_gguf', action='store_true', help="Convert the model to GGUF after training.")
    save_group.add_argument('--save_path', type=str, default="./outputs/model", help="Path to save the model.")
    save_group.add_argument('--quantization', type=str, default="q8_0", nargs="+",
        help="Quantization method for saving the model. Common values ('f16', 'q4_k_m', 'q8_0').")
    push_group = parser.add_argument_group('🚀 Push Model Options')
    push_group.add_argument('--push_model', action='store_true', help="Push the model to Hugging Face hub after training.")
    push_group.add_argument('--push_gguf', action='store_true', help="Push the model as GGUF to Hugging Face hub after training.")
    push_group.add_argument('--hub_path', type=str, default="hf/model", help="Path on Hugging Face hub to push the model.")
    push_group.add_argument('--hub_token', type=str, help="Token for pushing the model to Hugging Face hub.")

    # Parse arguments and run
    args = parser.parse_args()
    run(args)