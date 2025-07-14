import sqlite3
from pathlib import Path
from typing import Sequence, Dict, Any


ROOT_DIR = Path(__file__).resolve().parents[2]
DB_PATH   = ROOT_DIR / "backend" / "db" / "aggieadvisor.db"
SCHEMA_SQL = ROOT_DIR / "backend" / "db" / "schema.sql"

# Required columns in the correct order
REQUIRED_COLUMNS = [
    'course', 'professor', 'semester', 'year', 'college', 'department',
    'a_count', 'b_count', 'c_count', 'd_count', 'f_count',
    'total_count', 'gpa', 'q_drop'
]


def _get_db_connection() -> sqlite3.Connection:
    """Get a connection to the database."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def test_connection() -> bool:
    """Test database connection and verify courses table exists."""
    try:
        with _get_db_connection() as conn:
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


def _validate_insert_data(rows: Sequence[Dict[str, Any]], conflict_cols: Sequence[str]) -> None:
    """Validate rows and conflict columns before insertion.
    
    Raises ValueError if validation fails.
    """
    if not rows:
        raise ValueError("No rows provided for insertion")
    
    # Validate conflict columns exist in required columns
    invalid_cols = set(conflict_cols) - set(REQUIRED_COLUMNS)
    if invalid_cols:
        raise ValueError(f"Invalid conflict columns: {invalid_cols}")
    
    # Validate all required columns are present in each row
    for i, row in enumerate(rows):
        missing = set(REQUIRED_COLUMNS) - set(row.keys())
        if missing:
            raise ValueError(f"Missing required columns in row {i}: {missing}")


def bulk_insert(rows: Sequence[Dict[str, Any]], conflict_cols: Sequence[str] = ['course', 'semester', 'year', 'professor']) -> int:
    """Insert rows into courses table, ignoring duplicates based on conflict_cols.
    
    Returns number of new rows inserted.
    """
    # Test connection to database
    test_connection()

    # Validate input data
    _validate_insert_data(rows, conflict_cols)
    
    # Create the INSERT statement with ON CONFLICT clause
    placeholders = ','.join(['?' for _ in REQUIRED_COLUMNS])
    conflict_clause = f"ON CONFLICT({','.join(conflict_cols)}) DO NOTHING"
    
    insert_sql = f"""
    INSERT INTO courses (
        {','.join(REQUIRED_COLUMNS)}
    ) VALUES ({placeholders})
    {conflict_clause}
    """

    try:
        with _get_db_connection() as conn:
            cursor = conn.cursor()
            
            # Get initial row count
            cursor.execute("SELECT COUNT(*) FROM courses")
            initial_count = cursor.fetchone()[0]
            
            # Convert rows to list of tuples in the correct column order
            values = [[row[col] for col in REQUIRED_COLUMNS] for row in rows]
            
            # Perform the bulk insert
            cursor.executemany(insert_sql, values)
            conn.commit()
            
            # Get final row count
            cursor.execute("SELECT COUNT(*) FROM courses")
            final_count = cursor.fetchone()[0]
            
            # Return number of new rows inserted
            return final_count - initial_count
            
    except sqlite3.Error as e:
        print(f"Error during bulk insert: {e}")
        raise


if __name__ == "__main__":
    test_connection()







