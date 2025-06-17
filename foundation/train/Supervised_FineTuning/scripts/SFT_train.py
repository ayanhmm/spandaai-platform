#!/usr/bin/env python3
"""
🦥 Starter Script for Fine-Tuning FastLanguageModel with Unsloth
This script supports multiple data formats (Alpaca, ChatML, Custom) and includes configurable options for model loading, PEFT parameters, training arguments, and model saving/pushing functionalities.
Usage:
    python unsloth-cli.py --model_name "unsloth/llama-3-8b" --max_seq_length 2048 --dataset "path/to/your/file.json" --data_format "json" --r 16 --lora_alpha 16 --lora_dropout 0 --bias "none" --use_gradient_checkpointing "unsloth" --random_state 3407 --use_rslora --loftq_config None --per_device_train_batch_size 2 --gradient_accumulation_steps 4 --warmup_steps 5 --max_steps 400 --learning_rate 2e-4 --optim "adamw_8bit" --weight_decay 0.01 --lr_scheduler_type "linear" --seed 3407 --report_to "tensorboard" --logging_steps 1 --output_dir "outputs" --save_model --save_method "merged_16bit" --save_gguf --save_path "model" --quantization "q8_0" --push_model --push_gguf --hub_path "hf/model" --hub_token "your_hf_token"
To see a full list of configurable options, use:
    python unsloth-cli.py --help
Happy fine-tuning!
"""
import argparse
import os
from transformers.utils import strtobool
from trl import SFTTrainer
from transformers import TrainingArguments
from unsloth import FastLanguageModel, is_bfloat16_supported
from unsloth.chat_templates import get_chat_template  # Import get_chat_template for chat formatting
from datasets import load_dataset  # Import load_dataset for CSV support
import logging
import pandas as pd
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

    def formatting_prompts_alpaca(examples):
        instructions = examples["instruction"]
        inputs = examples["input"]
        outputs = examples["output"]
        texts = []
        for instruction, input, output in zip(instructions, inputs, outputs):
            text = alpaca_prompt.format(instruction, input, output) + EOS_TOKEN
            texts.append(text)
        return {"text": texts}

    def formatting_prompts_chatml(examples):
        # Apply chat template using get_chat_template
        tokenizer = get_chat_template(
            tokenizer,
            chat_template="chatml",  # Use ChatML format
            mapping={"role": "from", "content": "value", "user": "human", "assistant": "gpt"},
            map_eos_token=True,
        )
        instructions = examples["instruction"]
        inputs = examples["input"]
        outputs = examples["output"]
        # Combine instruction and input into a single user message
        user_messages = [f"{instruction} {input}".strip() for instruction, input in zip(instructions, inputs)]
        # Create ChatML format
        chatml_data = [
            [
                {"role": "user", "content": user_msg},
                {"role": "assistant", "content": output}
            ]
            for user_msg, output in zip(user_messages, outputs)
        ]
        # Convert ChatML to text using the tokenizer's apply_chat_template
        texts = [tokenizer.apply_chat_template(chat, tokenize=False, add_generation_prompt=False) + tokenizer.eos_token for chat in chatml_data]
        return {"text": texts}
      
    def formatting_prompts_custom(examples):
        # Example: Assume the dataset has 'question' and 'answer' fields
        questions = examples["question"]
        answers = examples["answer"]
        texts = [f"Q: {q}\nA: {a}{EOS_TOKEN}" for q, a in zip(questions, answers)]
        return {"text": texts}

    # Load dataset
    if args.dataset.endswith(".txt"):
        dataset = load_dataset("text", data_files=args.dataset, split="train")
        # Preprocess TXT file to extract fields
        def preprocess_txt(example):
            parts = example["text"].split("\t")  # Assuming tab-separated values
            return {
                "instruction": parts[0],
                "input": parts[1] if len(parts) > 1 else "",
                "output": parts[2] if len(parts) > 2 else "",
            }
        dataset = dataset.map(preprocess_txt)
    elif args.dataset.endswith(".json"):
        dataset = load_dataset("json", data_files=args.dataset, split="train")
    elif args.dataset.endswith(".csv"):
        dataset = load_dataset("csv", data_files=args.dataset, split="train")
    elif args.dataset.endswith(".xlsx"):
        # Load Excel file using Pandas
        df = pd.read_excel(args.dataset)
        
        # Ensure the required columns are present
        required_columns = ["instruction", "course_no", "course_title", "topic", "marks", "question"]
        if not all(col in df.columns for col in required_columns):
            raise ValueError(f"Missing required columns in the dataset. Expected: {required_columns}")
        
        # Convert Pandas DataFrame to Hugging Face Dataset
        dataset = load_dataset("pandas", pd_df=df, split="train")
    else:
        raise ValueError(f"Unsupported dataset format: {args.dataset}")
    
    def map_columns(example):
    # Map your dataset columns here
        instruction = example["instruction"]
        input_context = (
            f"Generate a question for the course id {example['course_no']}, "
            f"course name {example['course_title']} under the topic {example['topic']} "
            f"appropriate for marks {example['marks']}"
        )
        output = example["question"]  # Use the 'question' field as the output
        return {
            "instruction": instruction,
            "input": input_context,
            "output": output,
        }
    
    # Apply column mapping
    dataset = dataset.map(map_columns)


    # Preprocess dataset based on data format
    if args.data_format == "alpaca":
        dataset = dataset.map(formatting_prompts_alpaca, batched=True)
    elif args.data_format == "chatml":
        dataset = dataset.map(formatting_prompts_chatml, batched=True)
    elif args.data_format == "custom":
        dataset = dataset.map(formatting_prompts_custom, batched=True)
    else:
        raise ValueError(f"Unsupported data format: {args.data_format}")

    print("Data is formatted and ready!")

    # Configure training arguments
    training_args = TrainingArguments(
        per_device_train_batch_size=args.per_device_train_batch_size,
        gradient_accumulation_steps=args.gradient_accumulation_steps,
        warmup_steps=args.warmup_steps,
        max_steps=args.max_steps ,
        num_train_epochs=args.num_train_epochs,
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

    # Initialize trainer
    trainer = SFTTrainer(
        model=model,
        tokenizer=tokenizer,
        train_dataset=dataset,
        dataset_text_field="text",
        max_seq_length=args.max_seq_length,
        dataset_num_proc=2,
        packing=False,
        args=training_args,
    )

    # Train model
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
            model.save_pretrained_merged(args.save_path, tokenizer, args.save_method)
            if args.push_model:
                model.push_to_hub_merged(args.save_path, tokenizer, args.hub_token)
    else:
        print("Warning: The model is not saved!")


if __name__ == "__main__":
    # Define argument parser
    parser = argparse.ArgumentParser(description="🦥 Fine-tune your LLM faster using Unsloth!")
    
    # Model Options
    model_group = parser.add_argument_group("🤖 Model Options")
    model_group.add_argument('--model_name', type=str, default="unsloth/llama-3.2-1b-Instruct", help="Model name to load")
    model_group.add_argument('--max_seq_length', type=int, default=2048, help="Maximum sequence length, default is 2048.")
    model_group.add_argument('--dtype', type=str, default=None, help="Data type for model (None for auto detection)")
    model_group.add_argument('--load_in_4bit', action='store_true', help="Use 4-bit quantization to reduce memory usage")
    
    # Dataset Options
    dataset_group = parser.add_argument_group("📋 Dataset Options")
    dataset_group.add_argument('--dataset', type=str, required=True, help="Path to dataset file (.txt, .json, .csv)")
    dataset_group.add_argument('--data_format', type=str,default= "alpaca", choices=["alpaca", "chatml", "custom"], required=True, help="Dataset format: 'alpaca', 'chatml', or 'custom'")
    
    # LoRA Options
    lora_group = parser.add_argument_group("🧠 LoRA Options", "These options are used to configure the LoRA model.")
    lora_group.add_argument('--r', type=int, default=8, help="Rank for LoRA model, default is 8.")
    lora_group.add_argument('--lora_alpha', type=int, default=16, help="LoRA alpha parameter, default is 16.")
    lora_group.add_argument('--lora_dropout', type=float, default=0.05, help="LoRA dropout rate, default is 0.05.")
    lora_group.add_argument('--bias', type=str, default="none", help="Bias setting for LoRA.")
    lora_group.add_argument('--use_gradient_checkpointing', type=str, default="unsloth", help="Use gradient checkpointing.")
    lora_group.add_argument('--random_state', type=int, default=3407, help="Random state for reproducibility, default is 3407.")
    lora_group.add_argument('--use_rslora', action='store_true', default=False, help="Use rank stabilized LoRA.")
    lora_group.add_argument('--loftq_config', type=str, default=None, help="Configuration for LoftQ.")
    
    # Training Options
    training_group = parser.add_argument_group("🎓 Training Options")
    training_group.add_argument('--per_device_train_batch_size', type=int, default=4, help="Batch size per device during training, default is 4.")
    training_group.add_argument('--gradient_accumulation_steps', type=int, default=8, help="Number of gradient accumulation steps, default is 8.")
    training_group.add_argument('--warmup_steps', type=int, default=5, help="Number of warmup steps, default is 5.")
    training_group.add_argument('--max_steps', type=int, default=400, help="Maximum number of training steps, default is 400.")
    training_group.add_argument('--num_train_epochs', type=int, default=3, help="Number of training epochs, default is 3.")
    training_group.add_argument('--learning_rate', type=float, default=2e-4, help="Learning rate, default is 2e-4.")
    training_group.add_argument('--optim', type=str, default="adamw_8bit", help="Optimizer type, default is adamw_8bit.")
    training_group.add_argument('--weight_decay', type=float, default=0.01, help="Weight decay, default is 0.01.")
    training_group.add_argument('--lr_scheduler_type', type=str, default="linear", help="Learning rate scheduler type, default is 'linear'.")
    training_group.add_argument('--seed', type=int, default=3407, help="Seed for reproducibility, default is 3407.")
    
    # Report/Logging Options
    report_group = parser.add_argument_group("📊 Report Options")
    report_group.add_argument('--report_to', type=str, default="tensorboard", choices=["azure_ml", "clearml", "codecarbon", "comet_ml", "dagshub", "dvclive", "flyte", "mlflow", "neptune", "tensorboard", "wandb", "all", "none"], help="The list of integrations to report the results and logs to.")
    report_group.add_argument('--logging_steps', type=int, default=10, help="Logging steps, default is 10.")
    
    # Saving and Pushing Options
    save_group = parser.add_argument_group('💾 Save Model Options')
    save_group.add_argument('--output_dir', type=str, default="training/SFT/outputs", help="Output directory.")
    save_group.add_argument('--save_model', action='store_true', default=True, help="Save the model after training.")
    save_group.add_argument('--save_method', type=str, default="merged_16bit", choices=["merged_16bit", "merged_4bit", "lora"], help="Save method for the model, default is 'merged_16bit'.")
    save_group.add_argument('--save_gguf', action='store_true', default=True, help="Convert the model to GGUF after training.")
    save_group.add_argument('--save_path', type=str, default="./outputs/model", help="Path to save the model.")
    save_group.add_argument('--quantization', type=str, default="q4_k_m", nargs="+", help="Quantization method for saving the model. Common values ('f16', 'q4_k_m', 'q8_0').")
    
    push_group = parser.add_argument_group('🚀 Push Model Options')
    push_group.add_argument('--push_model', action='store_true', default=False, help="Push the model to Hugging Face Hub after training.")
    push_group.add_argument('--push_gguf', action='store_true', default=False, help="Push the model as GGUF to Hugging Face Hub after training.")
    push_group.add_argument('--hub_path', type=str, default="hf/model", help="Path on Hugging Face Hub to push the model.")
    push_group.add_argument('--hub_token', type=str, default=None, help="Token for pushing the model to Hugging Face Hub.")
    
    # Parse arguments and run
    args = parser.parse_args()
    run(args)