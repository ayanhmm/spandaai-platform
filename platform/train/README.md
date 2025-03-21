# Model Fine-Tuning & Training Pipeline

## Domain-Specific Model Pipeline
![Domain-Specific Model Pipeline](images/domain-specific-pipeline.png)
- **Pre-training & Knowledge Extraction**: Cleaning, entity recognition.
- **Model Training**: Foundation & custom models, hyperparameter tuning.
- **Integration**: RAG, GraphRAG, structured/unstructured data.


## Fine-Tuning Workflow
![Fine-Tuning Pipeline](images/application-finetuning-pipeline.png)
- **Data Collection**: PDFs, PPTs, textbooks, reference materials.
- **Data Preparation**: Labeling (manual & automatic), quality checks.
- **Training**: Supervised fine-tuning for specific applications.
- **Testing & Deployment**: Evaluations using Evidently AI & Promptfoo.


## Reinforcement Learning (RLHF)
![RLHF Pipeline](images/rlhf-pipeline.png)
- **Reward Model Training**: Learning from human feedback.
- **Optimization**: Using PPO and comparative evaluations.

This document provides a high-level overview of our model development process.

