## Part A: Transforming the Dissertation Analysis Repository

### As-Is State:
A research-focused, monolithic codebase with notebooks, scripts, and modules for processing dissertation data.

### Target (“To-Be”) State:
- **Domain Layer:** Contains all dissertation-specific logic (data ingestion/cleaning, NLP analysis, domain business logic) placed in a dedicated package.
- **Solutions Layer:** Provides client-facing APIs (and optionally dashboards/CLI tools) that expose the domain functions.
- **Platform Integration:** Removes duplicated infrastructure code in favor of thin client wrappers that call shared SpandaAI Platform services.

### Step-by-Step Instructions:

#### Inventory & Planning:
1. Review all current files (scripts, notebooks, modules) to identify what is domain-specific versus generic or infrastructure-related.
2. Document dependencies and integration points.

#### Create a New Directory Structure:
```
Dissertation-Analysis/
├── docs/                      # Updated documentation & architecture diagrams
├── notebooks/                 # Updated Jupyter notebooks using new APIs
├── tests/                     # Unit and integration tests
├── dissertation_analysis/
│   ├── __init__.py
│   ├── common/                # Shared utilities (configuration, logging)
│   │   └── config.py
│   ├── platform/              # Thin client wrappers for external Platform services
│   │   └── service_client.py  # Functions to call model serving or data pipelines
│   ├── domain/                # Domain-specific logic (EdTech)
│   │   ├── __init__.py
│   │   ├── data_preprocessing.py   # Functions to clean and structure dissertation data
│   │   ├── analysis_algorithms.py  # Core NLP/analysis algorithms
│   │   ├── nlp_utils.py            # Utilities for language processing
│   │   └── business_logic.py       # Domain-specific evaluation and business rules
│   └── solutions/             # Client-facing APIs and interfaces
│       ├── __init__.py
│       ├── api.py             # REST API (Flask/FastAPI) exposing domain functionality
│       ├── dashboard.py       # (Optional) Web dashboard components
│       └── cli.py             # Command-line interface for running analyses
├── requirements.txt           # Consolidated dependencies
├── setup.py                   # Packaging/installation script
└── README.md                  # Updated overview and instructions
```

#### Extract and Refactor:
- **Domain Layer:** Move dissertation-specific functions from the current code into `dissertation_analysis/domain/` and expose clear APIs.
- **Solutions Layer:** Create a REST API in `api.py`, and optionally develop a CLI and dashboards.
- **Platform Integration:** Remove internal infrastructure code and replace it with thin client functions in `dissertation_analysis/platform/service_client.py`.
- **Common Utilities:** Consolidate shared configurations and utility functions in the `common/` folder.

#### Update Notebooks, Tests & Documentation:
- Modify notebooks to use the new domain and API interfaces.
- Write unit tests for each module in `tests/`.
- Update the `README.md` with an architecture diagram and deployment instructions.

#### Containerization & CI/CD:
- Create a `Dockerfile` to containerize the Dissertation Analysis app.
- Set up CI/CD pipelines to build, test, and deploy the new structure independently.

---

## Part B: Transforming the SpandaAI Platform Repository

### As-Is State:
- **Main Branch & `components-addition` Branch:** Includes multiple backend components for inference, training, analytics, observability, testing, and a research lab section.
- **Kubernetes-based but not yet grouped by layer.**

### Target (“To-Be”) State:
- **Platform Layer:** Consolidate all core services into functional pipelines (orchestration/infrastructure, inference, training, analytics, observability, and testing).
- **Domain Layer:** Create a dedicated module for the EdTech domain that includes Dissertation Analysis, plus stub directories for HRTech and Oil & Gas.
- **Solutions Layer:** Build a unified API gateway, dashboards, and SDKs.

### Step-by-Step Instructions:

#### Merge & Inventory:
1. Review the code in both the `main` branch and the `components-addition` branch.
2. Map each component to a functional group.
3. Determine which components belong to the Platform, Domain, or Solutions layer.

#### Restructure the Repository:
```
spandaai-platform/
├── docs/                         # Updated architectural documentation
├── deployments/                  # Kubernetes manifests, Helm charts, etc.
├── tests/                        # Unit/integration tests
├── common/                       # Shared libraries/utilities (logging, config, auth)
├── platform/                     # CORE services (grouped by functional pipelines)
│   ├── inference/                # Inference engines (Verba, vLLM, Ollama, Weaviate, Agents)
│   ├── training/                 # Training frameworks & libraries (LangChain, DeepSpeed, etc.)
│   ├── analytics/                # Data processing & visualization
│   ├── observability/            # Monitoring & logging
│   ├── testing/                  # Testing & experimentation
│   ├── orchestration/            # Kubernetes automation
├── domains/                      # Domain-specific modules
│   ├── edtech/                   # EdTech domain implementation
│   ├── hrtech/                   # Future HRTech domain
│   └── oil_and_gas/              # Future Oil & Gas domain
├── solutions/                    # Client-facing interfaces & integration tools
│   ├── api_gateway.py            # API gateway (REST/GraphQL endpoints)
│   ├── dashboards/               # Web portals/dashboards
│   └── sdk/                      # SDKs and client libraries
├── requirements.txt              # Consolidated dependencies
├── setup.py                      # Packaging script
└── README.md                     # Updated overview and instructions
```

#### Migrate Components:
- **Platform Layer:** Move all core services into `platform/`.
- **Domain Layer:** Extract EdTech logic into `domains/edtech/` and create stub directories for `hrtech/` and `oil_and_gas/`.
- **Solutions Layer:** Develop an API gateway in `solutions/api_gateway.py`.

#### CI/CD & Deployment:
- Define separate `Dockerfile`s for each functional group.
- Update CI/CD pipelines for independent deployment of each layer.
- Update Kubernetes manifests in `deployments/`.

### Final Outcome:
- **Dissertation Analysis Repository:** Modular, containerized application integrated with the SpandaAI Platform.
- **SpandaAI Platform Repository:** A scalable, modular system with clearly defined Platform, Domain, and Solutions layers.
- **Common Security & Authentication:** Integrate Keycloak across all layers for authentication & authorization.
- **CI/CD Pipelines:** Independent builds and deployments for Platform, Domain, and Solutions layers.


# Recommended Integration Strategy

## Primary Goal
We want to ensure that the Dissertation Analysis application remains decoupled from the internal implementation details of the Spanda.AI Platform. This decoupling simplifies security, maintenance, and future upgrades.

## Our Recommended Approach

### Via the API Gateway (Preferred for External Integration)

#### **Usage:**
The Dissertation Analysis Domain (and any thin client wrappers in its Platform layer) should generally make calls to the Spanda.AI Platform through the unified API gateway provided in the Solutions layer.

#### **Benefits:**
- **Security & Consistency:** All calls are mediated by Keycloak-enabled, secure endpoints that enforce consistent authentication and authorization.
- **Abstraction:** The API gateway abstracts away the underlying service implementations, so if internal services change (e.g., a new inference engine or training service), the Dissertation Analysis app remains unaffected as long as the gateway’s contract is maintained.
- **Decoupling:** This approach decouples the Dissertation Analysis application from the specific details of the Platform services, making maintenance and future upgrades easier.

#### **When to Use:**
This is ideal for external API calls and interactions where a unified, secure access point is required.

---

### Direct Calls via Thin Client Wrappers (If Tightly Coupled in the Same Deployment Environment)

#### **Usage:**
If the Dissertation Analysis app is deployed within the same Kubernetes cluster or tightly integrated environment as the Spanda.AI Platform, you might choose to use the thin client wrappers (provided in the Dissertation Analysis Platform layer) that call the underlying Platform services directly.

#### **Benefits:**
- **Low Latency:** Direct calls can reduce overhead and latency if both systems reside in the same environment.
- **Internal Optimization:** When service-to-service communication is internal and controlled, direct calls using shared libraries can simplify the architecture.

#### **When to Use:**
This approach might be adopted when internal microservices are closely coupled and managed under a single operational domain. However, it’s less preferred if you want to maintain a strict separation of concerns and allow for independent evolution of the systems.

---

## Our Recommendation for Our Vision
For the full vision of the Spanda‑AI Platform and to maximize decoupling, security, and maintainability, the Dissertation Analysis Domain and Platform layers should primarily call the Spanda.AI Platform via the unified API gateway (Solutions layer). This ensures:

- **Centralized Security:** All external calls are uniformly secured by Keycloak.
- **Clear Separation:** The Dissertation Analysis application does not need to know the internal details of the Platform’s implementation.
- **Future Flexibility:** The Spanda.AI Platform can evolve internally (changing services, scaling, etc.) without requiring changes in the Dissertation Analysis code as long as the API gateway’s interface remains stable.

If there is a need for very low latency or if both systems are deployed very tightly together, the use of thin client wrappers for direct calls is acceptable—but even then, it is wise to design these wrappers so that they eventually route through the same API contracts defined by the gateway.


In our envisioned architecture, the Dissertation Analysis Domain and Platform layers should primarily call the Spanda.AI Platform through the API gateway provided in the Solutions layer. This approach provides a consistent, secure, and decoupled integration point. Direct calls via thin client wrappers may be considered in tightly coupled deployments, but the best practice is to use the API gateway to ensure long-term maintainability and security.

---
