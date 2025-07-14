import sqlite3
from pathlib import Path
from typing import Sequence, Dict, Any, Optional


ROOT_DIR = Path(__file__).resolve().parents[2]
DB_PATH   = ROOT_DIR / "backend" / "db" / "aggieadvisor.db"
SCHEMA_SQL = ROOT_DIR / "backend" / "db" / "schema.sql"

# Required columns in the correct order
COURSE_COLUMNS = [
    'course', 'professor', 'professor_id', 'semester', 'year', 'college', 'department',
    'a_count', 'b_count', 'c_count', 'd_count', 'f_count',
    'total_count', 'gpa', 'q_drop'
]

PROFESSOR_COLUMNS = [
    'name', 'rmp_avg', 'rmp_difficulty', 'rmp_count', 'rmp_url', 'rmp_updated'
]


def _get_db_connection() -> sqlite3.Connection:
    """Get a connection to the database."""

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def test_connection() -> bool:
    """Test database connection and verify required tables exist."""
    
    try:
        with _get_db_connection() as conn:
            cursor = conn.cursor()
            
            # Check both tables
            cursor.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name IN ('courses', 'professors');
            """)
            tables = {row[0] for row in cursor.fetchall()}
            
            if 'courses' in tables and 'professors' in tables:
                print("Successfully connected to database and found required tables!")
                return True
            else:
                missing = {'courses', 'professors'} - tables
                print(f"Connected to database but missing tables: {missing}")
                print("Did you run create_db.py?")
                return False
                
    except sqlite3.Error as e:
        print(f"Error connecting to database: {e}")
        print(f"Database path: {DB_PATH}")
        print("Make sure you've run create_db.py to initialize the database.")
        return False


def _validate_professor_data(rows: Sequence[Dict[str, Any]]) -> None:
    """Validate professor data before insertion."""
    if not rows:
        raise ValueError("No rows provided for insertion")
    
    # Only name is required, other fields can be null
    for i, row in enumerate(rows):
        if 'name' not in row:
            raise ValueError(f"Missing required 'name' column in row {i}")


def _validate_course_data(rows: Sequence[Dict[str, Any]], conflict_cols: Sequence[str]) -> None:
    """Validate course data before insertion."""
    if not rows:
        raise ValueError("No rows provided for insertion")
    
    # Validate conflict columns exist in required columns
    invalid_cols = set(conflict_cols) - set(COURSE_COLUMNS)
    if invalid_cols:
        raise ValueError(f"Invalid conflict columns: {invalid_cols}")
    
    # Validate all required columns are present in each row
    required = set(COURSE_COLUMNS) - {'professor_id'}  # professor_id can be null during migration
    for i, row in enumerate(rows):
        missing = required - set(row.keys())
        if missing:
            raise ValueError(f"Missing required columns in row {i}: {missing}")


def insert_professors(rows: Sequence[Dict[str, Any]]) -> Dict[str, int]:
    """Insert professors into professors table, returning dict of professor names to IDs."""
    _validate_professor_data(rows)
    
    # First get existing professors to avoid duplicates
    with _get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, name FROM professors")
        existing = {row['name']: row['id'] for row in cursor.fetchall()}
    
    # Insert new professors
    insert_sql = f"""
    INSERT INTO professors (
        {','.join(PROFESSOR_COLUMNS)}
    ) VALUES ({','.join('?' for _ in PROFESSOR_COLUMNS)})
    ON CONFLICT(name) DO NOTHING
    """
    
    try:
        with _get_db_connection() as conn:
            cursor = conn.cursor()
            
            # Insert each professor
            for row in rows:
                if row['name'] not in existing:
                    values = [row.get(col) for col in PROFESSOR_COLUMNS]
                    cursor.execute(insert_sql, values)
                    if cursor.rowcount > 0:
                        existing[row['name']] = cursor.lastrowid
            
            conn.commit()
            return existing
            
    except sqlite3.Error as e:
        print(f"Error inserting professors: {e}")
        raise


def bulk_insert_courses(rows: Sequence[Dict[str, Any]], conflict_cols: Sequence[str] = ['course', 'semester', 'year', 'professor']) -> int:
    """Insert rows into courses table, ignoring duplicates based on conflict_cols.
    
    Returns number of new rows inserted.
    """

    # Test connection to database
    test_connection()

    # Validate input data
    _validate_course_data(rows, conflict_cols)
    
    # First insert/get professors to get their IDs
    professor_rows = [{'name': row['professor']} for row in rows]
    professor_ids = insert_professors(professor_rows)
    
    # Create the INSERT statement with ON CONFLICT clause
    placeholders = ','.join(['?' for _ in COURSE_COLUMNS])
    conflict_clause = f"ON CONFLICT({','.join(conflict_cols)}) DO NOTHING"
    
    insert_sql = f"""
    INSERT INTO courses (
        {','.join(COURSE_COLUMNS)}
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
            values = []
            for row in rows:
                row_copy = dict(row)
                row_copy['professor_id'] = professor_ids.get(row['professor'])
                values.append([row_copy.get(col) for col in COURSE_COLUMNS])
            
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







