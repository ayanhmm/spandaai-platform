# Spanda.AI Platform - Data Management
 

## Part One: Data Storage and Management

### Core Data Management Framework
#### FAIR Data Principles
- **Findable**: Implement metadata tagging, DOI assignment, and search indexing
- **Accessible**: Provide multiple access methods via standard protocols (HTTP/HTTPS)
- **Interoperable**: Adopt Educational Data Structure (EDS) standards
- **Reusable**: Clear data use agreements and community standards

#### Data Submission Process
(TBD For EdTech domain - might have to create from scratch, we can do this at the very end, we can setup existing platform pieces first)

- Create a standardized metadata schema (discipline-dependent and independent)
- Implement automated validation similar to BIDS validator
- Ensure de-identification of data (remove 18 personal identifiers per HIPAA)

#### Privacy Protection
- Attribute-Based Access Control (ABAC)
- Decentralized Identifiers (DIDs) for personal data ownership
- Informed consent documentation for data sharing

### Data Architecture

![Data Architecture](./images/data_architecture.png)

Implement a Data Lakehouse architecture that combines:

#### Data Lake
- Store raw, unstructured, and semi-structured data
- Maintain data in original format for maximum flexibility
- Scalable storage on cloud platforms

#### Data Warehouse
- Structured data organization
- Optimized for querying and analysis
- Supports SQL-based tools

#### Processing Layer
- Tools like Apache Spark and Apache Hive
- Data transformation capabilities
- Machine learning and analytics support

![Structured and Unstructured Data to Warehouse](./images/structured_unstructured_data_to_warehouse.png)

![Semi-structured Data to Warehouse](./images/semi-structured_data_to_warehouse.png)

### Implementation Tools

![Data Lakehouse](./images/data_lakehouse.png)

# Building a Data Lakehouse Pipeline with Dremio and Apache Iceberg

## Overview
This guide walks through creating an end-to-end data pipeline from SQLServer to dashboards using Dremio's Data Lakehouse Platform and Apache Iceberg. We'll demonstrate how to simplify what traditionally requires multiple steps (data lake transfer, data warehousing, BI acceleration) into a streamlined workflow that can run on a laptop.

## Components

| Component | Purpose | Role in Our Pipeline |
|-----------|---------|----------------------|
| **SQLServer** | Source database | Stores our operational data that needs to be analyzed |
| **Dremio** | Data Lakehouse Platform | Core engine that queries data across sources and manages the lakehouse |
| **Apache Iceberg** | Table format | Provides advanced data management features for our lake tables |
| **Nessie** | Catalog service | Manages and versions our data lake tables |
| **MinIO** | Object storage | Simulates cloud storage locally for our data lake |
| **Superset** | BI dashboard tool | Creates visualizations from our processed data |

## Implementation Steps

### 1. Setting Up the Environment

Create a `docker-compose.yml` file with the following services:
- **Nessie**: Catalog server using in-memory store (port 19120)
- **MinIO**: Storage server with admin/password credentials (ports 9000/9001)
- **Dremio**: Data lakehouse platform (ports 9047/31010/32010)
- **SQLServer**: Source database with SA user (port 1433)
- **Superset**: BI visualization tool (port 8080)

Start the environment:
```bash
docker compose up
```

### 2. Data Preparation in SQLServer

Access the SQLServer container:
```bash
docker exec -it sqlserver /bin/bash
/opt/mssql-tools/bin/sqlcmd -S localhost -U SA -P 'Yourpassword2024'
```

Create and populate sample data:
```sql
CREATE TABLE DashboardData (RecordID INT PRIMARY KEY, Category NVARCHAR(50), Value INT, DateRecorded DATE);

GO

INSERT INTO DashboardData (RecordID, Category, Value, DateRecorded) 
VALUES (1, 'Category A', 100, '2023-01-01'), 
       (2, 'Category B', 150, '2023-01-02'),
       -- additional sample data rows
       (10, 'Category A', 180, '2023-01-10');

GO
```

### 3. Configuring Data Sources in Dremio

1. **Set up MinIO:**
   - Access MinIO at `localhost:9000` (admin/password)
   - Create a bucket named "warehouse"

2. **Configure Dremio:**
   - Access Dremio at `localhost:9047` and create admin account
   - Add Nessie source:
     - Source Name: nessie
     - Endpoint URL: http://nessie:19120/api/v2
     - AWS Root Path: warehouse
     - AWS Keys: admin/password
     - Connection Properties:
       - fs.s3a.path.style.access: true
       - fs.s3a.endpoint: minio:9000
       - dremio.s3.compat: true

   - Add SQLServer source:
     - Name: sqlserver
     - Host: sqlserver
     - Port: 1433
     - Username: SA
     - Password: Yourpassword2024

### 4. Moving Data to the Data Lake

Use Dremio's SQL Runner to:

1. **Initial data load:**
```sql
CREATE TABLE nessie.dashboard_data AS 
SELECT * FROM sqlserver.master.dbo.DashboardData;
```

2. **Incremental updates:**
```sql
INSERT INTO nessie.dashboard_data
SELECT *
FROM sqlserver.master.dbo.DashboardData
WHERE RecordID > (SELECT COALESCE(MAX(RecordID), 0) FROM nessie.dashboard_data);
```

### 5. Connecting Superset to Dremio

1. Initialize Superset:
```bash
docker exec -it superset superset init
```

2. Configure Dremio connection in Superset:
   - Access Superset at `localhost:8080` (admin/admin)
   - Add database connection with this string:
     ```
     dremio+flight://USERNAME:PASSWORD@dremio:32010/?UseEncryption=false
     ```
   - Create dataset from the `dashboard_data` table
   - Build charts and dashboards based on this dataset

## Key Benefits

1. **Simplified Architecture**: Eliminates the need for separate data lake, data warehouse, and BI extract layers
2. **SQL-Based Integration**: Replaces complex Spark jobs with simple SQL commands
3. **Resource Optimization**: Prevents analytical queries from competing with operational workloads
4. **Scalability**: Leverages Dremio's horizontal and vertical scaling capabilities
5. **Modern Data Format**: Uses Apache Iceberg for advanced data management features

## Conclusion

This implementation demonstrates how Dremio's Data Lakehouse Platform streamlines the traditionally complex process of moving operational data to analytical dashboards. By using Dremio with Apache Iceberg, we can build a modern, efficient data pipeline that eliminates unnecessary complexity while providing enhanced functionality.

## Part Two: Data Annotation, Pipeline Debt, and Testing in MLOps

### Table of Contents
1. Introduction
2. Data Annotation with Label Studio
3. Managing Pipeline Debt
4. Data Testing with Great Expectations
5. Model Testing Strategies
6. Implementation Roadmap
7. GitHub Repositories and Resources

### Introduction
This guide provides a comprehensive overview of essential MLOps components to build robust machine learning systems that avoid the "Debt Collection Day" scenario. It covers:
- Data annotation tools to improve data quality and model training
- Pipeline debt management to prevent cascading failures
- Data validation to ensure data quality and detect drift
- Model testing strategies to verify model behavior beyond simple metrics

Each section explains the component's function, its importance in production ML systems, and practical implementation steps.

### Data Annotation with Label Studio

![Data Labelling Overview](./images/data_labelling_one.png)

![Data Labelling Process](./images/data_labelling_two.jpg)

#### What It Does
Label Studio is an open-source data labeling tool that provides:
- A configurable interface for annotating text, images, and audio
- Machine learning integration for pre-labeling and active learning
- Team collaboration support
- Export capabilities to common ML formats (COCO, VOC, CONLL, etc.)
- Model prediction comparison for verification

#### Why We Need It
High-quality labeled data is essential for successful ML projects. Label Studio addresses key challenges:
- Data Quality Improvement: Ensures consistent labeling
- Unstructured Data Handling: Supports text, images, and audio
- Model Validation: Compares predictions from different models
- Edge Case Management: Identifies and labels difficult examples
- Human-in-the-Loop Learning: Integrates human feedback for improvements

#### Getting Started
```
pip install label-studio
label-studio start my_project --init
```

### Managing Pipeline Debt

#### What It Is
Pipeline debt arises from undocumented, untested, and unstable data pipelines, leading to brittle ML systems. Symptoms include:
- Entangled dependencies
- Lack of visibility in data transformations
- Difficult debugging and maintenance
- Cascading failures affecting multiple teams

#### Prevention Strategies
- Documentation: Track all pipeline components and transformations
- Testing: Implement tests for data pipelines
- Monitoring: Track pipeline health and data quality metrics
- Governance: Establish standards for modifications
- Visibility: Use dashboards to track dependencies

### Data Testing with Great Expectations

#### What It Does
Great Expectations provides:
- Declarative syntax for defining data quality expectations
- Automatic data documentation generation
- Integration with Pandas, SQL, and Spark
- CI/CD integration for automated validation

#### Why We Need It
- Preventing Bad Data: Stops problematic data from reaching models
- Early Warning: Detects data drift
- Documentation: Generates data quality reports
- Knowledge Sharing: Makes data assumptions explicit
- Outlier Detection: Prevents model failures

#### Getting Started
```
pip install great_expectations
great_expectations init
great_expectations suite new
```

### Model Testing Strategies

![Pre-train Tests and Post-train Tests](./images/pre-train_tests_and_post-train_tests.png)

#### Key Strategies
- Pre-train tests: Validate architecture and data setup
- Post-train tests: Verify trained model behaviors
- Invariance tests: Ensure consistent predictions with specific input changes
- Directional expectation tests: Verify expected changes in outputs
- Minimum functionality tests: Validate performance in critical scenarios

#### Implementation Approaches
- Automated test suites: Use GitHub Actions or Jenkins
- Smoke tests: Quick validation of model training and prediction
- Behavioral test suites: Tests organized around model capabilities
- Manual validation: Expert review of test results
- A/B testing: Compare models in production

### Implementation Roadmap

#### Phase 1: Set Up Data Annotation
- Install Label Studio and configure data types
- Define annotation guidelines
- Set up ML-assisted labeling
- Begin annotating datasets

#### Phase 2: Implement Data Testing
- Install Great Expectations
- Profile existing datasets
- Create expectation suites
- Integrate validation into ingestion pipelines

#### Phase 3: Address Pipeline Debt
- Document all pipelines and dependencies
- Implement pipeline health monitoring
- Establish governance standards
- Refactor unstable pipelines

#### Phase 4: Implement Model Testing
- Create pre-train test suites
- Develop invariance and directional tests
- Automate testing in CI/CD pipelines
- Establish manual validation processes

### GitHub Repositories and Resources

#### Data Annotation
- Label Studio
- LLM Data Annotation

#### Data Testing
- Great Expectations
- Pandera
- Deepchecks

#### Model Testing (Let me know if anything here overlaps with Promptfoo)
- CheckList
- Snorkel
- Alibi Detect

#### Drift Monitoring
- Drift Monitoring
- EvidentialyAI
- Whylogs

#### MLOps Frameworks
- MLflow
- Kubeflow
- DVC