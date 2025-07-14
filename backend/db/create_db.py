import sqlite3
from pathlib import Path

# Get the current directory and database paths
CURR_DIR = Path(__file__).resolve().parent
DB_PATH = CURR_DIR / "aggieadvisor.db"
SCHEMA_PATH = CURR_DIR / "schema.sql"

def create_database():
    """Create a new database and initialize it with the schema."""
    print(f"Creating database at {DB_PATH}")
    
    # Read the schema file
    with open(SCHEMA_PATH, 'r') as f:
        schema = f.read()
    
    # Connect to SQLite (this will create the database if it doesn't exist)
    with sqlite3.connect(DB_PATH) as conn:
        print("Executing schema...")
        # Execute the schema
        conn.executescript(schema)
        conn.commit()
    
    print("Database created successfully!")

if __name__ == "__main__":
    # Check if database already exists
    if DB_PATH.exists():
        user_input = input("Database already exists. Do you want to recreate it? (y/N): ")
        if user_input.lower() != 'y':
            print("Aborted.")
            exit()
        DB_PATH.unlink()  # Delete the existing database
    
    create_database()
