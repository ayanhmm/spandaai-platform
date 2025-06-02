import pandas as pd
import numpy as np
import os
from sqlalchemy import create_engine, text,inspect
from vanna.openai.openai_chat import OpenAI_Chat
from vanna.chromadb.chromadb_vector import ChromaDB_VectorStore
import sqlparse


# Define your custom Vanna class
class MyVanna(ChromaDB_VectorStore, OpenAI_Chat):
    def __init__(self, config=None):
        ChromaDB_VectorStore.__init__(self, config=config)
        OpenAI_Chat.__init__(self, config=config)
    
    # Override is_sql_valid to allow UPDATE statements
    def is_sql_valid(self, sql: str) -> bool:
        """
        Checks if the SQL query is valid. This method has been overridden
        to allow both SELECT and UPDATE statements.
        
        Args:
            sql (str): The SQL query to check.
            
        Returns:
            bool: True if the SQL query is valid (SELECT or UPDATE), False otherwise.
        """
        parsed = sqlparse.parse(sql)
        
        for statement in parsed:
            stmt_type = statement.get_type()
            if stmt_type in ['SELECT', 'UPDATE']:
                return True
        
        return False
    
    # Override connect_to_postgres to accept empty password
    def connect_to_postgres(
        self,
        host: str = None,
        dbname: str = None,
        user: str = None,
        password: str = None,
        port: int = None,
        **kwargs
    ):
        """
        Connects to a PostgreSQL database.

        Args:
            host (str): Database host.
            dbname (str): Database name.
            user (str): Database user.
            password (str): Database password.
            port (int): Database port.
        """
        try:
            import psycopg2
        except ImportError:
            raise ImportError(
                "The psycopg2 package is required to connect to a PostgreSQL database."
            )

        try:
            import sqlalchemy
        except ImportError:
            raise ImportError(
                "The sqlalchemy package is required to connect to a PostgreSQL database."
            )

        # Build connection string even with empty password
        conn_string = f"postgresql://{user}"
        if password:  # Only add password if it's not empty
            conn_string += f":{password}"
        conn_string += f"@{host}:{port}/{dbname}"

        def connect_to_db():
            return psycopg2.connect(
                host=host,
                dbname=dbname,
                user=user,
                password=password if password else None,
                port=port,
            )

        def run_sql_postgres(sql: str):
            conn = connect_to_db()
            cursor = conn.cursor()

            try:
                # Execute the query
                cursor.execute(sql)

                # For SELECT queries, return the result as a pandas DataFrame
                if sql.strip().upper().startswith("SELECT") or sql.strip().upper().startswith("WITH"):
                    columns = [desc[0] for desc in cursor.description]
                    df = pd.DataFrame(cursor.fetchall(), columns=columns)
                    return df
                # For other queries, just commit the transaction and return None
                else:
                    conn.commit()
                    return None
            except Exception as e:
                conn.rollback()
                raise e
            finally:
                cursor.close()
                conn.close()

        self.run_sql = run_sql_postgres
        self.run_sql_is_set = True

# Step 1: Load CSVs into a PostgreSQL database
def load_csvs_to_postgres(csv_files, conn_string):
    engine = create_engine(conn_string)
    dataframes = {}
    
    # Load each CSV and store in the database
    for csv_file in csv_files:
        # Get file name without extension as table name
        table_name = os.path.splitext(os.path.basename(csv_file))[0]
        print(f"Loading {csv_file} into table {table_name}...")
        
        # Read CSV
        df = pd.read_csv(csv_file)
        dataframes[table_name] = df
        
        # Upload to PostgreSQL
        df.to_sql(table_name, engine, if_exists='replace', index=False)
        print(f"Loaded {len(df)} rows into {table_name}")
    
    return engine, dataframes

# Step 2: Generate DDL statements for each table
def generate_ddl_statements(engine):
    inspector = inspect(engine)
    ddl_statements = []
    
    for table_name in inspector.get_table_names():
        columns = inspector.get_columns(table_name)
        column_defs = []
        
        for column in columns:
            column_name = column['name']
            column_type = str(column['type'])
            nullable = "" if column.get('nullable', True) else "NOT NULL"
            column_defs.append(f"    {column_name} {column_type} {nullable}")
        
        ddl = f"CREATE TABLE {table_name} (\n"
        ddl += ",\n".join(column_defs)
        ddl += "\n);"
        ddl_statements.append(ddl)
    
    return ddl_statements

# Step 3: Generate documentation based on the data
def generate_documentation(dataframes):
    documentation = "# Data Documentation\n\n"
    
    for table_name, df in dataframes.items():
        documentation += f"## Table: {table_name}\n\n"
        documentation += f"This table contains {len(df)} records.\n\n"
        documentation += "### Columns:\n\n"
        
        for column in df.columns:
            data_type = str(df[column].dtype)
            sample_values = df[column].dropna().head(3).tolist()
            sample_str = ", ".join([str(val) for val in sample_values])
            documentation += f"- **{column}** ({data_type}): Sample values: {sample_str}\n"
        
        documentation += "\n"
        
        # Add basic statistics for numeric columns
        numeric_columns = df.select_dtypes(include=['number']).columns
        if len(numeric_columns) > 0:
            documentation += "### Numeric Statistics:\n\n"
            for column in numeric_columns:
                documentation += f"- **{column}**: Min={df[column].min()}, Max={df[column].max()}, Mean={df[column].mean():.2f}\n"
            documentation += "\n"
    
    return documentation

# Step 4: Generate example SQL queries
def generate_example_queries(dataframes):
    examples = []
    
    for table_name, df in dataframes.items():
        # Basic count query
        examples.append({
            "question": f"How many records are in the {table_name} table?",
            "sql": f"SELECT COUNT(*) FROM {table_name}"
        })
        
        # Sample data query
        examples.append({
            "question": f"Show me a sample of data from {table_name}",
            "sql": f"SELECT * FROM {table_name} LIMIT 10"
        })
        
        # If numeric columns exist, add aggregation example
        numeric_columns = df.select_dtypes(include=['number']).columns
        if len(numeric_columns) > 0:
            column = numeric_columns[0]
            examples.append({
                "question": f"What is the average {column} in {table_name}?",
                "sql": f"SELECT AVG({column}) FROM {table_name}"
            })
        
        # If date columns exist, add time-based example
        date_columns = df.select_dtypes(include=['datetime']).columns
        if len(date_columns) > 0:
            column = date_columns[0]
            examples.append({
                "question": f"Show me the distribution of {table_name} by {column}",
                "sql": f"SELECT DATE_TRUNC('month', {column}) as month, COUNT(*) FROM {table_name} GROUP BY month ORDER BY month"
            })
    
    return examples

# Main function
def main():
    # Import configuration
    from config import DB_HOST, DB_NAME, DB_USER, DB_PASS, DB_PORT, OPENAI_API_KEY, CSV_FILES
    
    # Build connection string
    conn_string = f"postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    
    # Print CSV files found
    print(f"Found {len(CSV_FILES)} CSV files:")
    for csv_file in CSV_FILES:
        print(f"  - {csv_file}")
    
    # Step 1: Load CSVs into PostgreSQL
    engine, dataframes = load_csvs_to_postgres(CSV_FILES, conn_string)
    
    # Step 2: Generate DDL statements
    ddl_statements = generate_ddl_statements(engine)
    
    # Step 3: Generate documentation
    documentation = generate_documentation(dataframes)
    
    # Step 4: Generate example queries
    example_queries = generate_example_queries(dataframes)
    
    # Step 5: Initialize Vanna
    vn = MyVanna(config={
        'api_key': OPENAI_API_KEY,
        'model': 'gpt-4',
        'path': './vanna_chromadb'
    })
    
    # Step 6: Connect to the database
    vn.connect_to_postgres(
        host=DB_HOST,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASS,
        port=DB_PORT
    )
    
    # Step 7: Train Vanna with DDL
    print("Training Vanna with schema information...")
    for ddl in ddl_statements:
        vn.train(ddl=ddl)
    
    # Step 8: Train Vanna with documentation
    print("Training Vanna with documentation...")
    vn.train(documentation=documentation)
    
    # Step 9: Train Vanna with example queries
    print("Training Vanna with example queries...")
    for example in example_queries:
        vn.train(question=example["question"], sql=example["sql"])
    
    # Step 10: Train with complex examples (NEW)
    include_complex = input("Do you want to include complex query examples? (y/n): ").lower().strip() == 'y'
    if include_complex:
        try:
            from complex_training import generate_complex_examples
            complex_examples = generate_complex_examples()
            print(f"Training Vanna with {len(complex_examples)} complex examples...")
            for i, example in enumerate(complex_examples):
                print(f"Training example {i+1}/{len(complex_examples)}: {example['question']}")
                vn.train(question=example["question"], sql=example["sql"])
            print("Training with complex examples complete!")
        except ImportError:
            print("complex_training.py module not found. Skipping complex examples.")
    
    print("Training complete! You can now ask Vanna questions about your data.")
    
    # Interactive query mode (optional)
    while True:
        question = input("\nEnter your question (or 'exit' to quit): ")
        if question.lower() == 'exit':
            break
            
        try:
            result = vn.ask(question)
            print("\nResult:")
            print(result)
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    main()







