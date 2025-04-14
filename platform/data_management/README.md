# Spanda.AI Platform - Data Management
## Spark, Dremio, Nessie, MinIO, and Superset

### Analytics/Lakehouse

**Purpose**: Data storage, analysis, and intelligence.

| Component | Status | Description | Supported Sources |
|-----------|--------|-------------|--------------------|
| **Apache Superset** | Done ✅ | Business intelligence web application. | Connects to databases like PostgreSQL, MySQL, Snowflake, and more. |
| **Iceberg** | Done ✅ | Table format for large analytical datasets. | Works with Spark, Flink, Hive, Dremio, and Presto. |
| **Dremio** | Done ✅ | Data lake engine. | Supports sources like Amazon S3, Azure Data Lake, Google Cloud Storage, HDFS, PostgreSQL, MySQL, MongoDB, Snowflake, and Elasticsearch. |
| **Apache Spark** | Done ✅ | Analytics engine for large-scale data processing. | Works with Hadoop, S3, Delta Lake, Kafka, and JDBC-compatible sources. |
| **MinIO** | Done ✅ | High-performance object storage. | Compatible with Amazon S3 APIs and integrates with Spark, Presto, and Dremio. |
| **Nesse** | Done ✅ | Data processing framework. | Works with various databases and file systems. |

Note: The above stack provides extensive capabilities beyond what's listed, supporting integrations with various data sources.

**Integration Points**: Will provide analytical capabilities across the platform.


![Data Architecture](images/data_architecture.png)


This guides you through setting up a complete data engineering environment that demonstrates the Data Lakehouse architecture. You'll learn how to move data from an operational database (PostgreSQL) to a data lake (MinIO with Apache Iceberg tables managed by Nessie), and then query the data using Dremio and visualize it through Apache Superset.

## Prerequisites

- [Docker](https://www.docker.com/products/docker-desktop/) installed on your machine
- Basic knowledge of SQL and data engineering concepts

## Architecture Overview

This setup demonstrates a modern Data Lakehouse architecture with the following components:

- **PostgreSQL**: Operational database
- **Apache Spark**: Data processing and ETL
- **MinIO**: S3-compatible object storage (data lake)
- **Nessie**: Catalog service for Apache Iceberg tables
- **Dremio**: Data lakehouse platform and query engine
- **Apache Superset**: Business intelligence and visualization tool

## Setup Instructions

### 1. Create Docker Compose File

Create a new directory for the project, then create a file named `docker-compose.yml` with the following content:

```yaml
version: "3"

services:
  # Nessie Catalog Server Using In-Memory Store
  nessie:
    image: projectnessie/nessie:latest
    container_name: nessie
    networks:
      de-end-to-end:
    ports:
      - 19120:19120
  # Minio Storage Server
  minio:
    image: minio/minio:latest
    container_name: minio
    environment:
      - MINIO_ROOT_USER=admin
      - MINIO_ROOT_PASSWORD=password
      - MINIO_DOMAIN=storage
      - MINIO_REGION_NAME=us-east-1
      - MINIO_REGION=us-east-1
    networks:
      de-end-to-end:
    ports:
      - 9001:9001
      - 9000:9000
    command: ["server", "/data", "--console-address", ":9001"]
  # Dremio
  dremio:
    platform: linux/x86_64
    image: dremio/dremio-oss:latest
    ports:
      - 9047:9047
      - 31010:31010
      - 32010:32010
    container_name: dremio
    networks:
      de-end-to-end:
  # Spark
  spark:
    platform: linux/x86_64
    image: alexmerced/spark35nb:latest
    ports: 
      - 8080:8080  # Master Web UI
      - 7077:7077  # Master Port
      - 8888:8888  # Notebook
    environment:
      - AWS_REGION=us-east-1
      - AWS_ACCESS_KEY_ID=admin #minio username
      - AWS_SECRET_ACCESS_KEY=password #minio password
    container_name: spark
    networks:
      de-end-to-end:
  # Postgres
  postgres:
    image: postgres:latest
    container_name: postgres
    environment:
      POSTGRES_DB: mydb
      POSTGRES_USER: myuser
      POSTGRES_PASSWORD: mypassword
    ports:
      - "5435:5432"
    networks:
      de-end-to-end:
  #Superset
  superset:
    image: alexmerced/dremio-superset
    container_name: superset
    networks:
      de-end-to-end:
    ports:
      - 8088:8088
networks:
  de-end-to-end:
```

### 2. Start PostgreSQL and Populate Data

1. Start the PostgreSQL container:
   ```bash
   docker-compose up -d postgres
   ```

2. Access the PostgreSQL shell:
   ```bash
   docker exec -it postgres psql -U myuser mydb
   ```

3. Create a table and add sample data:
   ```sql
   -- Create a table for a mock BI dashboard dataset
   CREATE TABLE sales_data (
       id SERIAL PRIMARY KEY,
       product_name VARCHAR(255),
       category VARCHAR(50),
       sales_amount DECIMAL(10, 2),
       sales_date DATE
   );

   -- Insert sample data into the table
   INSERT INTO sales_data (product_name, category, sales_amount, sales_date)
   VALUES
       ('Product A', 'Electronics', 1000.50, '2024-03-01'),
       ('Product B', 'Clothing', 750.25, '2024-03-02'),
       ('Product C', 'Home Goods', 1200.75, '2024-03-03'),
       ('Product D', 'Electronics', 900.00, '2024-03-04'),
       ('Product E', 'Clothing', 600.50, '2024-03-05');
   ```

4. Exit the PostgreSQL shell:
   ```
   \q
   ```

### 3. Start the Data Lake Components

1. Start the MinIO, Nessie, Spark, and Dremio services:
   ```bash
   docker-compose up -d spark nessie minio dremio
   ```

### 4. Set Up MinIO Bucket

1. Open MinIO console in your browser: http://localhost:9001
2. Login with:
   - Username: `admin`
   - Password: `password`
3. Create a new bucket named `warehouse`

### 5. Use Spark to Move Data to the Data Lake

1. Access the Jupyter Notebook interface at http://localhost:8888
2. Create a new Python notebook
3. Add the following PySpark code:

```python
import pyspark
from pyspark.sql import SparkSession
import os

## DEFINE SENSITIVE VARIABLES
CATALOG_URI = "http://nessie:19120/api/v1" ## Nessie Server URI
WAREHOUSE = "s3://warehouse/" ## S3 Address to Write to
STORAGE_URI = "http://minio:9000"

conf = (
    pyspark.SparkConf()
        .setAppName('app_name')
          #packages
        .set('spark.jars.packages', 'org.postgresql:postgresql:42.7.3,org.apache.iceberg:iceberg-spark-runtime-3.5_2.12:1.5.0,org.projectnessie.nessie-integrations:nessie-spark-extensions-3.5_2.12:0.77.1,software.amazon.awssdk:bundle:2.24.8,software.amazon.awssdk:url-connection-client:2.24.8')
          #SQL Extensions
        .set('spark.sql.extensions', 'org.apache.iceberg.spark.extensions.IcebergSparkSessionExtensions,org.projectnessie.spark.extensions.NessieSparkSessionExtensions')
          #Configuring Catalog
        .set('spark.sql.catalog.nessie', 'org.apache.iceberg.spark.SparkCatalog')
        .set('spark.sql.catalog.nessie.uri', CATALOG_URI)
        .set('spark.sql.catalog.nessie.ref', 'main')
        .set('spark.sql.catalog.nessie.authentication.type', 'NONE')
        .set('spark.sql.catalog.nessie.catalog-impl', 'org.apache.iceberg.nessie.NessieCatalog')
        .set('spark.sql.catalog.nessie.s3.endpoint', STORAGE_URI)
        .set('spark.sql.catalog.nessie.warehouse', WAREHOUSE)
        .set('spark.sql.catalog.nessie.io-impl', 'org.apache.iceberg.aws.s3.S3FileIO')
)
## Start Spark Session
spark = SparkSession.builder.config(conf=conf).getOrCreate()
print("Spark Running")
# Define the JDBC URL for the Postgres database
jdbc_url = "jdbc:postgresql://postgres:5432/mydb"
properties = {
    "user": "myuser",
    "password": "mypassword",
    "driver": "org.postgresql.Driver"
}
# Load the table from Postgres
postgres_df = spark.read.jdbc(url=jdbc_url, table="sales_data", properties=properties)
# Write the DataFrame to an Iceberg table
postgres_df.writeTo("nessie.sales_data").createOrReplace()
# Show the contents of the Iceberg table
spark.read.table("nessie.sales_data").show()
# Stop the Spark session
spark.stop()
```

**Note:** If you encounter an "Unknown Host" issue with `http://minio:9000`, you may need to replace `minio` with the container's actual IP address. You can find this by running `docker inspect minio` and looking for the IP address in the network section.

### 6. Configure Dremio to Connect to Nessie/MinIO

1. Access the Dremio UI at http://localhost:9047 and set up an admin account
2. Add a new source:
   - Click "Add a Source" and select "Nessie"
   - **General settings tab:**
     - Source Name: `nessie`
     - Nessie Endpoint URL: `nessie:19120/api/v2`
     - Auth Type: `None`
   - **Storage settings tab:**
     - AWS Root Path: `warehouse`
     - AWS Access Key: `admin`
     - AWS Secret Key: `password`
     - Uncheck "Encrypt Connection" Box
   - **Connection Properties:**
     - Key: `fs.s3a.path.style.access` | Value: `true`
     - Key: `fs.s3a.endpoint` | Value: `minio:9000`
     - Key: `dremio.s3.compat` | Value: `true`
   - Click "Save"

### 7. Set Up Superset for BI Dashboards

1. Start the Superset service:
   ```bash
   docker-compose up -d superset
   ```

2. Initialize Superset:
   ```bash
   docker exec -it superset superset init
   ```

3. Access Superset at http://localhost:8080 and log in:
   - Username: `admin`
   - Password: `admin`

4. Add a database connection:
   - Go to "Settings" > "Database Connections"
   - Click "Add a database" > Select "Other"
   - Enter connection string:
     ```
     dremio+flight://USERNAME:PASSWORD@dremio:32010/?UseEncryption=false
     ```
     (Replace USERNAME and PASSWORD with your Dremio credentials)
   - Test connection and save

5. Create a dataset:
   - Click the "+" icon > "Create dataset"
   - Select the database connection you just created
   - Choose the `sales_data` table
   - Save

6. Build dashboards:
   - Create charts based on your dataset
   - Add charts to dashboards for visualization

## Troubleshooting

### Spark Connection Issues

If the Spark notebook can't connect to MinIO using the hostname, use the container's IP address:
1. Run `docker inspect minio`
2. Find the IP address in the Network section
3. Update the `STORAGE_URI` variable in your PySpark code, e.g., `STORAGE_URI = "http://172.18.0.6:9000"`

### Dremio Connection Issues

If Dremio can't connect to Nessie or MinIO:
1. Make sure all services are running: `docker-compose ps`
2. Check if the network is properly configured
3. Try using container IP addresses instead of hostnames in connection settings

## Additional Resources

- [Dremio Documentation](https://docs.dremio.com/)
- [Apache Iceberg Documentation](https://iceberg.apache.org/docs/latest/)
- [Nessie Documentation](https://projectnessie.org/documentation/)
- [Apache Superset Documentation](https://superset.apache.org/docs/intro)

## Next Steps

After completing this tutorial, you might want to:
1. Add more data sources to Dremio
2. Create more complex transformations with Spark
3. Build comprehensive dashboards in Superset
4. Implement data governance policies

---

*Based on the "End-to-End Basic Data Engineering Tutorial" by Alex Merced, https://medium.com/data-engineering-with-dremio/end-to-end-basic-data-engineering-tutorial-spark-dremio-superset-c076a56eaa75*