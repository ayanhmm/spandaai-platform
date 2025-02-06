# Spanda‑AI Platform Refactoring Roadmap

This document outlines a comprehensive, step‑by‑step plan to refactor our current "as‑is" repositories into the desired "to‑be" state for the Spanda‑AI Platform. Our vision is to achieve a modular, three‑layer architecture with functional (pipeline) groupings. This refactoring effort is divided among three teams: **Platform**, **Domain**, and **Solutions**. In addition, this document covers how to handle common components and Keycloak integration for security.

---

## Final Vision Overview

The final architecture is divided into three layers:

1. **Platform Layer (Core, Foundational Services):**  
   Provides shared infrastructure and services for:
   - **Infrastructure & Orchestration:** Kubernetes, Kubefirst, Argo CD, etc.
   - **Inference & Model Serving:** Services like Verba, vLLM, Ollama, Weaviate, and supporting agents.
   - **Training & Hardware Optimization:** Trainer (LangChain), DeepSpeed, Unsloth, hardware scripts, plus research lab tools integrated here if generic.
   - **Analytics & Data Lakehouse:** Tools such as Apache Superset, Spark, Iceberg, MiniIO, Demio, Nesse.
   - **Observability & Testing:** Prometheus, Grafana, Dockprom, AlertManager, Tester, Promptfoo, Predator.
   - **Common Security:** Keycloak deployed centrally, with shared adapters/middleware.

2. **Domain Layer (Industry‑Specific Logic):**  
   Wraps the Platform capabilities with domain‑specific logic.  
   **Initial Focus: EdTech Domain** (includes Dissertation Analysis, Question Bank Generator, Automated Grading Assistant, Paper Variants, Faculty Evaluation).  
   Stub directories are created for future domains: **HRTech** and **Oil & Gas**.  
   Functional grouping includes:
   - **Preprocessing Pipeline:** Data cleaning, normalization, feature extraction.
   - **Analysis & Modeling Pipeline:** Custom NLP/GenAI algorithms and business logic.
   - **Post‑Processing & Integration Pipeline:** Reporting, dashboards, and adapters.

3. **Solutions Layer (Client‑Facing Interfaces & Integration):**  
   Exposes unified APIs, dashboards, SDKs, and CLI tools that allow external applications to access the Platform and Domain services.  
   Functional grouping includes:
   - **API Gateway & SDK Pipeline:** REST/GraphQL endpoints secured with Keycloak.
   - **User Interface & Dashboard Pipeline:** Web portals and dashboards.
   - **CLI & Integration Pipeline:** Command‑line tools and integration adapters.

**Common Components:**  
A top‑level `common/` directory will house shared configuration, logging, error handling, and Keycloak adapters. These components will be used by all three layers.

---

## A. Platform Team Instructions

**Objective:**  
Refactor and consolidate all core infrastructure and shared services into the Platform Layer, organized by functional pipelines.

### 1. Inventory & Mapping
- **Review the "as‑is" state** in both the main and `components-addition` branches.
- Map each existing component (inference engines, training scripts, analytics tools, monitoring, testing, research lab tools) to its functional group.
- Identify overlaps and decide which components are generic and need re‑organization.

### 2. Restructure the Directory Layout
Create the following new directory structure at the root of `spandaai-platform/`:

```
spandaai-platform/
├── docs/                     # Updated architecture diagrams and documentation
├── deployments/              # Kubernetes manifests, Helm charts, etc.
├── tests/                    # Unit and integration tests for platform services
├── common/                   # Shared libraries/utilities
│   ├── init.py
│   ├── config.py             # Centralized configuration and secrets
│   ├── logging_utils.py      # Standardized logging functions
│   ├── error_handling.py     # Common error/exception handling
│   └── keycloak_adapter.py   # Keycloak integration and middleware
├── platform/                 # Core services, grouped by functional pipelines
│   ├── init.py
│   ├── orchestration/        # Kubernetes scripts, Kubefirst, Argo CD configs
│   ├── inference/            # Verba, vLLM, Ollama, Weaviate, Agents
│   ├── training/             # Trainer (LangChain), DeepSpeed, Unsloth, HW scripts
│   ├── analytics/            # Superset, Spark, Iceberg, MiniIO, Demio, Nesse
│   ├── observability/        # Prometheus, Grafana, Dockprom, AlertManager
│   └── testing/              # Tester, Promptfoo, Predator
├── domains/                  # Domain-specific modules (stubs for now)
│   ├── edtech/               # EdTech implementation (see Domain Team instructions)
│   ├── hrtech/               # Stub for future HRTech domain
│   │   └── init.py           # Placeholder
│   └── oil_and_gas/          # Stub for future Oil & Gas domain
│       └── init.py           # Placeholder
├── solutions/                # Client-facing interfaces & integration tools
│   ├── init.py
│   ├── api_gateway.py        # Unified API endpoints
│   ├── dashboards/           # Web portals and dashboards
│   └── sdk/                  # SDKs for external integration
├── requirements.txt          # Consolidated dependencies
├── setup.py                  # Packaging script
└── README.md                 # Updated overview and instructions
```

### 3. Migrate & Refactor Core Services
- **Orchestration:** Move all Kubernetes-related scripts and configurations to `platform/orchestration/`.
- **Inference:** Migrate inference engine code (Verba, vLLM, Ollama, Weaviate) and supporting agents to `platform/inference/`.
- **Training:** Consolidate training frameworks and libraries into `platform/training/`.
- **Analytics:** Move data processing and visualization tools into `platform/analytics/` and adjust configurations.
- **Observability & Testing:** Migrate monitoring and testing tools to `platform/observability/` and `platform/testing/`.
- **Common Components:** Ensure every microservice references shared modules from `common/` for configuration, logging, and error handling.

---

## B. Domain Team Instructions

**Objective:**  
Extract and refactor all domain‑specific (EdTech) logic into a dedicated Domain Layer and create stubs for future HRTech and Oil & Gas domains.

### 1. Inventory & Planning
- **Review Existing Code:** Identify all dissertation‑specific processing routines, NLP algorithms, business logic, and models.
- **Define Interfaces:** Document clear APIs for data preprocessing, analysis/modeling, and post‑processing.

---

## C. Solutions Team Instructions

**Objective:**  
Build client‑facing interfaces that expose the Platform and Domain capabilities via APIs, dashboards, and SDKs.

### 1. Create Solutions Directory Structure
```
solutions/
├── init.py
├── api_gateway.py  # Centralized API gateway (REST/GraphQL endpoints)
├── dashboards/     # Web portals and dashboard interfaces
│   └── edtech_dashboard.py  # Dashboard for EdTech use cases
└── sdk/
    ├── init.py
    └── spandaai_sdk.py  # Example SDK module
```

### 2. Develop the API Gateway & SDK
- Build REST/GraphQL endpoints in `api_gateway.py`.
- Integrate Keycloak via middleware from `common/keycloak_adapter.py`.
- Develop SDK functions in `solutions/sdk/spandaai_sdk.py`.

By following this plan, we ensure a modular, scalable, and secure Spanda‑AI Platform.


