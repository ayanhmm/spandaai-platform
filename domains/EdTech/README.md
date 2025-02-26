# SpandaAI EdTech Domain

## Overview
The SpandaAI EdTech Domain is a comprehensive educational technology solution built on SpandaAI's modular GenAI platform. It leverages advanced AI capabilities to provide intelligent educational tools, analytics, and content generation services.

## Directory Structure
```
EdTech/
├── api_gateway/            # Kong API gateway configuration
├── data_preprocessing/     # Text and document preprocessing service
├── document_analysis/      # Document analysis and evaluation
├── edu_ai_agents/         # Educational AI agents
├── face_analysis/         # Face detection and analysis
├── microservices/         # Supporting microservices
├── qa_generation/         # Question and answer generation
└── shared/                # Shared utilities and components
```

## Platform-Domain-Solution Layer Architecture

Our three-layer architecture provides significant advantages:

### **Layered Architecture Diagram**
```
+----------------------------+
|        Solutions Layer     |
| (Client-Facing Applications) |
+----------------------------+
            |
            v
+----------------------------+
|        Domain Layer        |
| (Education-Specific AI & APIs) |
+----------------------------+
            |
            v
+---------------------------------+
|        Platform Layer           |
| (Infrastructure & Core Services) |
| - API Gateway (Kong)             |
| - Logging & Monitoring           |
| - Model Serving (LLMs, Embeddings) |
| - Data Storage & Databases       |
| - Distributed Computing          |
| - Task Scheduling & Workflow Orchestration |
+---------------------------------+
```

### **1. Platform Layer (Foundation)**
- **API Gateway (Kong)**: Manages authentication, rate limiting, and routing.
- **Logging & Monitoring**: Provides centralized logging, tracing, and real-time system monitoring.
- **Model Serving**: Hosts AI models for tasks like NLP, embeddings, and document analysis.
- **Data Storage & Databases**: Manages relational (PostgreSQL), NoSQL (MongoDB), and vector databases (Weaviate).
- **Distributed Computing**: Enables parallel processing for large-scale computations.
- **Task Scheduling & Workflow Orchestration**: Manages job execution and automation using Celery or Prefect.

### **2. Domain Layer (EdTech Specific)**
- Houses education-specific AI models
- Implements academic business rules
- Provides specialized APIs for educational needs
- Enables domain-specific fine-tuning

### **3. Solutions Layer (Client-Facing)**
- Delivers customizable end-user applications
- Offers integration capabilities
- Provides tailored UX for educational contexts

## Benefits for EdTech domain
- **Modularity**: Each service (QA generation, document analysis, etc.) can be developed and scaled independently
- **Flexibility**: Easy to add new educational features or modify existing ones
- **Specialization**: Services are optimized for educational use cases
- **Integration**: Seamless connection with existing educational systems

## Quick Start

### 1. **Environment Setup**
```bash
# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # Unix/MacOS
venv\Scripts\activate     # Windows

# Install dependencies
pip install -e .
```

### 2. **Start Services**
```bash
# Start all services
start_edtech_domain_services_locally.bat  # Windows
./start_edtech_domain_services_locally.sh # Unix/MacOS
```

### 3. **Configure Gateway**
```bash
# Import Kong configuration
docker exec -it api_gateway-kong-edtech-domain-1 kong config db_import /usr/local/kong/declarative/kong.yml

# Restart Kong container
# Important: Restart Kong containers to apply configuration
```

## Key Components

### **Document Analysis**
- Dissertation evaluation
- Academic paper analysis
- Content quality assessment

### **Question Generation**
- Automated assessment creation
- Multiple question types
- Difficulty-based generation

### **Data Preprocessing**
- Text chunking and analysis
- Educational content processing
- Document format handling

### **Face Analysis**
- Student engagement monitoring
- Attendance tracking
- Emotion analysis for learning

### **Educational AI Agents**
- Intelligent tutoring
- Learning path optimization
- Student support automation

## Configuration
Copy `env.example` to `.env` and adjust variables as needed:
```env
# Essential environment variables included in env.example
```

## Scaling Capabilities

Our modular architecture enables scaling in multiple dimensions:

### **1. Vertical Scaling**
   - Individual services can be upgraded
   - Resource allocation per component
   - Performance optimization per module

### **2. Horizontal Scaling**
   - Services can be replicated
   - Load balancing across instances
   - Geographic distribution

### **3. Functional Scaling**
   - Easy addition of new services
   - Feature expansion per module
   - Integration of new AI capabilities

## EdTech Domain Advantages

### **1. Comprehensive Coverage**
   - Complete academic document analysis
   - Automated assessment generation
   - Student engagement tracking
   - Intelligent tutoring systems

### **2. Educational Focus**
   - Models trained on academic content
   - Education-specific business rules
   - Academic standard compliance
   - Learning-oriented features

### **3. Integration Ready**
   - LMS integration capabilities
   - API-first design
   - Standard education protocol support
   - Flexible deployment options

For detailed API documentation and endpoint information, please refer to the API documentation provided separately.