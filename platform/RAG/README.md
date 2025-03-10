# Spanda.AI RAG

## Overview

Spanda.AI RAG is a powerful Retrieval Augmented Generation system that combines the capabilities of vector search and large language models to provide context-aware, knowledge-grounded responses. Built on top of Weaviate's vector database technology, Spanda.AI RAG offers a flexible, scalable solution for applications requiring intelligent document retrieval and generation.

## Key Features

### 🚀 High-Performance Vector Search
- Built on Weaviate's cloud-native vector database engine
- Lightning-fast nearest neighbor search on millions of documents in milliseconds
- Production-ready with scaling, replication, and security features

### 🧠 Flexible Component Architecture
- Modular design with pluggable components:
  - **Reader**: Document ingestion and parsing
  - **Chunker**: Intelligent document segmentation
  - **Embedder**: Multiple vector embedding options
  - **Retriever**: Advanced retrieval algorithms
  - **Generator**: Integration with various LLM providers

### 🔄 Versatile Integration Options
- Support for multiple embedding models and services
- Compatible with popular AI frameworks:
  - LangChain
  - LlamaIndex
  - DocArray
  - Haystack
  - Auto-GPT

### 💬 Comprehensive API
- REST and WebSocket interfaces for all operations
- Streaming generation capabilities
- File import and document management
- Configuration management
- Advanced querying and filtering

## Feature Lists

### 🤖 Model Support

| Model | Implemented | Description |
|-------|-------------|-------------|
| Ollama (e.g. Llama3) | ✅ | Local Embedding and Generation Models powered by Ollama |
| HuggingFace (e.g. MiniLMEmbedder) | ✅ | Local Embedding Models powered by HuggingFace |


### 🤖 Embedding Support

| Embedding Provider | Implemented | Description |
|-------------------|-------------|-------------|
| Weaviate | ✅ | Embedding Models powered by Weaviate |
| Ollama | ✅ | Local Embedding Models powered by Ollama |
| SentenceTransformers | ✅ | Embedding Models powered by HuggingFace |


### 📁 Data Support

| Feature | Implemented | Description |
|---------|-------------|-------------|
| UnstructuredIO | ✅ | Import Data through Unstructured |
| PDF Ingestion | ✅ | Import PDF into Verba |
| GitHub & GitLab | ✅ | Import Files from Github and GitLab |
| CSV/XLSX Ingestion | ✅ | Import Table Data into Verba |
| .DOCX | ✅ | Import .docx files |


### ✨ RAG Features

| Feature | Implemented | Description |
|---------|-------------|-------------|
| Hybrid Search | ✅ | Semantic Search combined with Keyword Search |
| Autocomplete Suggestion | ✅ | Verba suggests autocompletion |
| Filtering | ✅ | Apply Filters (e.g. documents, document types etc.) before performing RAG |
| Customizable Metadata | ✅ | Free control over Metadata |
| Async Ingestion | ✅ | Ingest data asynchronously to speed up the process |
| Advanced Querying | planned ⏱️ | Task Delegation Based on LLM Evaluation |
| Reranking | planned ⏱️ | Rerank results based on context for improved results |
| RAG Evaluation | planned ⏱️ | Interface for Evaluating RAG pipelines |

### 🗡️ Chunking Techniques

| Technique | Implemented | Description |
|-----------|-------------|-------------|
| Token | ✅ | Chunk by Token powered by spaCy |
| Sentence | ✅ | Chunk by Sentence powered by spaCy |
| Semantic | ✅ | Chunk and group by semantic sentence similarity |
| Recursive | ✅ | Recursively chunk data based on rules |
| HTML | ✅ | Chunk HTML files |
| Markdown | ✅ | Chunk Markdown files |
| Code | ✅ | Chunk Code files |
| JSON | ✅ | Chunk JSON files |

### 🆒 Cool Bonus

| Feature | Implemented | Description |
|---------|-------------|-------------|
| Docker Support | ✅ | Verba is deployable via Docker |
| Customizable Frontend | ✅ | Verba's frontend is fully-customizable via the frontend |
| Vector Viewer | ✅ | Visualize your data in 3D |

### 🤝 RAG Libraries

| Library | Implemented | Description |
|---------|-------------|-------------|
| LangChain | ✅ | Implement LangChain RAG pipelines |
| Haystack | planned ⏱️ | Implement Haystack RAG pipelines |
| LlamaIndex | planned ⏱️ | Implement LlamaIndex RAG pipelines |

## Getting Started

### Prerequisites
Ensure the RAG component is launched before using the API. For setup instructions, refer to the `/platform` directory.

## Configuration

Spanda.AI RAG offers extensive configuration options for each component:

### Reader Configuration
Configure how documents are read and processed during import.

### Chunker Configuration
Control how documents are segmented into smaller chunks for embedding and retrieval.

### Embedder Configuration
Choose and configure the embedding models used to vectorize your content.

### Retriever Configuration
Adjust retrieval parameters such as search depth, similarity metrics, and filtering options.

### Generator Configuration
Configure the language model used for generation, including model parameters and prompt templates.

## Weaviate Deployment Options

We provide flexibility in connecting to Weaviate instances based on your needs:

### 💻 Weaviate Embedded
Embedded Weaviate runs a Weaviate instance directly from your application code rather than from a stand-alone Weaviate server installation. When you run Spanda.AI RAG in `Local Deployment`, it will setup and manage Embedded Weaviate in the background.

**Note:** Weaviate Embedded is not supported on Windows and is in Experimental Mode which can bring unexpected errors. We recommend using the Docker Deployment or Cloud Deployment instead for production environments.

### 🌩️ Weaviate Cloud Deployment (WCD)
If you prefer a cloud-based solution, Weaviate Cloud (WCD) offers a scalable, managed environment. Learn how to set up a cloud cluster and get the API keys by following the Weaviate Cluster Setup Guide.

### 🐳 Docker Deployment
Another local alternative is deploying Weaviate using Docker. This provides isolation and consistent environments across different machines. For more details, follow the "How to install Spanda.AI RAG with Docker" section.

### ⚙️ Custom Weaviate Deployment
If you're hosting Weaviate yourself, you can use the `Custom` deployment option in Spanda.AI RAG. This allows you to specify the URL, PORT, and API key of your custom Weaviate instance.

## Document Management

Spanda.AI RAG provides comprehensive document management capabilities:

- Import documents through WebSocket or HTTP endpoints
- Retrieve documents by UUID
- Get document content and metadata
- View vector representations
- List all documents with pagination and filtering
- Delete documents when needed

## Advanced Features

### Label-based Organization
Organize and filter documents using labels for improved retrieval precision.

### Query Suggestions
Leverage the suggestions engine to guide users toward effective queries.

### Conversation Memory
Maintain context across multiple interactions for more coherent conversations.

### Theme Customization
Customize the appearance of your Spanda.AI RAG interface.

## API Reference

For detailed API documentation, refer to the full [API Documentation](API_DOCS.md).

## Community and Support

Join our community to get help, share ideas, and contribute to the development of Spanda.AI RAG.

---
