# SpandaAI Platform

## Overview

The **SpandaAI Platform** is a cutting-edge Generative AI (GenAI) ecosystem designed to support multiple domains such as FinTech, Healthcare, and EdTech. The platform leverages a modular, 3-layer architecture to ensure scalability, flexibility, and seamless integration of GenAI capabilities.

This repository houses the core components of the SpandaAI ecosystem, including foundational services, domain-specific functionalities, and solutions tailored for end-users.

---

## Platform Architecture

The SpandaAI GenAI Platform is structured into a **3-layered architecture**:

```plaintext
                 +-----------------------------------------------------+
                 |                  3. Solutions Layer                |
                 +-----------------------------------------------------+
                 |  Client-Facing Applications:                       |
                 |  - Web Portals, APIs, SDKs                         |
                 |  - Integration Adapters, UX Layers                 |
                 |  - Customizable Features for End-User Systems      |
                 +-----------------------------------------------------+
                                  │
                 Builds on Domain-Specific Features
                                  │
          +-----------------------------------------------------+
          |                   2. Domain Layer                  |
          +-----------------------------------------------------+
          |  Industry-Specific Logic:                          |
          |  - Custom Models                                   |
          |  - Business Rules Engines                         |
          |  - APIs & Fine-Tuning Interfaces                  |
          |  (e.g., Fintech, Healthcare, EdTech)              |
          +-----------------------------------------------------+
                                  │
                   Utilizes Foundational Services
                                  │
          +-----------------------------------------------------+
          |                 1. Platform Layer                  |
          +-----------------------------------------------------+
          |  Foundational Services:                            |
          |  - Compute Resources (Kubernetes, GPU Instances)   |
          |  - Data Management (MySQL, Redis, Zookeeper)       |
          |  - Model Serving (Verba, Ollama, Kafka)            |
          |  - Monitoring (Prometheus, Dockprom)               |
          |  - Logging and Alerts (Kafka)                      |
          |  - Configuration Management (Dockprom)             |
          +-----------------------------------------------------+
```

### Component Highlights

#### Platform Layer:
- Foundational services like Kubernetes, MySQL, Redis, Zookeeper, and Prometheus.
- Model serving via Verba, Ollama, and Kafka.
- Monitoring and logging using Prometheus and Dockprom.

#### Domain Layer:
- Encapsulates domain-specific GenAI models and business rules tailored for industries like FinTech and Healthcare.

#### Solutions Layer:
- Provides client-facing applications, integration adapters, and user experience layers for end-user systems.

---

## Getting Started

### Prerequisites
- **Docker**: Ensure Docker is installed and running.
- **Git**: Clone the repository using Git.

### Installation

1. **Clone the Repository:**
   ```bash
   git clone https://github.com/spandaai/spandaai-platform.git
   cd spandaai-platform
   ```

2. **Run the Application:**

   For Linux/MacOS:
   ```bash
   ./quickstart.sh
   ```

   For Windows:
   ```bash
   ./quickstart.bat
   ```

---

## Features

- Modular, 3-layered architecture for scalability and flexibility.
- Domain-specific GenAI solutions for multiple industries.
- Built-in monitoring and logging with Prometheus and Dockprom.

---

## Documentation

For detailed guides, best practices, and contribution guidelines, visit our [Central Documentation](https://github.com/spandaai/spandaai-docs).

---

## Migration Script Documentation

### Overview

This repository includes a Python script for analyzing and introspecting multiple repositories. The script automates:
- Cloning repositories.
- Identifying project types and dependencies.
- Detecting external services in Docker/Kubernetes manifests.
- Generating a detailed JSON report of repository structures.

---

## Components

The `spandaai-platform` repository contains the following core components:

- **MegaParse**: Advanced data parsing utilities.
- **Verba**: Core model serving component.
- **Dockprom**: Monitoring and logging stack.
- **Kafka**: Message broker for data pipelines.
- **MySQL & Redis**: Backend storage and caching solutions.
- **Ollama**: LLM serving platform.
- **Prometheus**: Monitoring and alerting toolkit.
- **Zookeeper**: Coordination service for distributed systems.

---

## Support

For assistance or to report issues, please contact the SpandaAI support team or submit a ticket in the [issue tracker](https://github.com/spandaai/spandaai-platform/issues).

---

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.

