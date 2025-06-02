from vanna.openai.openai_chat import OpenAI_Chat
from vanna.chromadb.chromadb_vector import ChromaDB_VectorStore
from config import DB_HOST, DB_NAME, DB_USER, DB_PASS, DB_PORT, OPENAI_API_KEY
import sqlparse

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
            import pandas as pd
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
                    return pd.DataFrame({'result': ['Update completed successfully']})  # Return a simple success message
            except Exception as e:
                conn.rollback()
                raise e
            finally:
                cursor.close()
                conn.close()

        self.run_sql = run_sql_postgres
        self.run_sql_is_set = True

def main():
    print("Vanna Query Interface")
    print("---------------------")
    
    # Initialize Vanna with the same config as training
    vn = MyVanna(config={
        'api_key': OPENAI_API_KEY,
        'model': 'gpt-4',
        'path': './vanna_chromadb'  # Same path to access the training data
    })
    
    # Connect to the database
    vn.connect_to_postgres(
        host=DB_HOST,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASS,
        port=DB_PORT
    )
    
    print("Connected to database. You can now ask questions about your data.")
    print("Type 'exit' to quit")
    
    while True:
        question = input("\nEnter your question: ")
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