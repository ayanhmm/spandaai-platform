# PostgreSQL configuration
DB_HOST = "localhost"
DB_NAME = "vanna_db"  
DB_USER = "your_username"  # Update with your PostgreSQL username
DB_PASS = "your_password"  # Update with your PostgreSQL password
DB_PORT = 5432

# OpenAI configuration
import os
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")  # Set this using environment variable

# Path to CSV files
import os
DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
CSV_FILES = [os.path.join(DATA_DIR, f) for f in os.listdir(DATA_DIR) if f.endswith('.csv')] 