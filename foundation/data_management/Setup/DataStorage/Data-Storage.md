# Setup Instructions

### 1. Create Docker Compose File

- Create a new directory for the project, then create a copy of the file named `Data-Storage.yml` 

### 2. Set Up a network 
- Create a new network for communication with other modules of the pipeline and list all networks to check if network properly created
   ```bash
   docker network create Spanda-Net
   docker network ls
   ```


## Start PostgreSQL and Populate Data

- Start the Postgres service:
   ```bash
   docker-compose -f Data-Storage.yml up -d postgres
   ```

- Check if the containr is connected to the required network
   ```bash
   docker network inspect Spanda-Net
   ```

- Access the PostgreSQL shell for database named `mydb`:
   ```bash
   docker exec -it postgres psql -U myuser mydb
   ```

- Create a table and add sample data:
   - Create a table for a mock BI dashboard dataset
      ```sql
      CREATE TABLE sales_data (
         id SERIAL PRIMARY KEY,
         product_name VARCHAR(255),
         category VARCHAR(50),
         sales_amount DECIMAL(10, 2),
         sales_date DATE
      );
      ```
   - Insert sample data into the table
      ```sql
      INSERT INTO sales_data (product_name, category, sales_amount, sales_date)
      VALUES
         ('Product A', 'Electronics', 1000.50, '2024-03-01'),
         ('Product B', 'Clothing', 750.25, '2024-03-02'),
         ('Product C', 'Home Goods', 1200.75, '2024-03-03'),
         ('Product D', 'Electronics', 900.00, '2024-03-04'),
         ('Product E', 'Clothing', 600.50, '2024-03-05');
      ```
   - Check if data properly uploaded
      ```sql
      select * from sales_data limit 5;
      ```
   
   

- Exit the PostgreSQL shell:
   ```
   \q
   ```

## Set Up Postgres Database Automatically utilizing spark
Refer to the readme file associated with Data Ingestion



