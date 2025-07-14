import sqlite3
from pathlib import Path
from typing import Sequence, Dict, Any


ROOT_DIR = Path(__file__).resolve().parents[2]
DB_PATH   = ROOT_DIR / "backend" / "db" / "aggieadvisor.db"
SCHEMA_SQL = ROOT_DIR / "backend" / "db" / "schema.sql"

# check if database exists

def _get_db_connection() -> sqlite3.Connection:
    """Get a connection to the database."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def test_connection() -> bool:
    """Test if we can connect to the database and if it has the courses table."""
    try:
        with _get_db_connection() as conn:
            # Try to query the courses table
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='courses';")
            table_exists = cursor.fetchone() is not None
            
            if table_exists:
                print("Successfully connected to database and found courses table!")
            else:
                print("Connected to database but courses table not found. Did you run create_db.py?")
            
            return table_exists
    except sqlite3.Error as e:
        print(f"Error connecting to database: {e}")
        print(f"Database path: {DB_PATH}")
        print("Make sure you've run create_db.py to initialize the database.")
        return False

if __name__ == "__main__":
    test_connection()







