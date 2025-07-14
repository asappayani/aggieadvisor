import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[3]))


import pandas as pd
from parser import parse_pdf
from backend.db.insert import bulk_insert


ROOT_DIR = Path(__file__).resolve().parents[3]
DB_PATH = ROOT_DIR / "backend" / "db" / "aggieadvisor.db"
RAW_DATA_DIR = ROOT_DIR / "data" / "raw"
DB_COLUMNS = {
    "A":"a_count","B":"b_count","C":"c_count","D":"d_count","F":"f_count",
    "total":"total_count","gpa":"gpa","Q":"q_drop",
    "semester":"semester","year":"year","college":"college","department":"department",
    "course":"course","professor":"professor"
}


def clean_data(df: pd.DataFrame) -> pd.DataFrame: 
    """ Clean data to match database schema """

    df = df.rename(columns=DB_COLUMNS)

    ints = ["a_count", "b_count", "c_count", "d_count", "f_count", "total_count", "q_drop", "year"]

    df[ints] = df[ints].astype(int)
    df["gpa"] = df["gpa"].astype(float)
    df["semester"] = df["semester"].str.upper()
    df["department"] = df["department"].str.upper()
    df["professor"] = df["professor"].str.upper()
    df["course"] = df["course"].str.upper()
    df["college"] = df["college"].str.upper()

    return df


def get_pdf_files() -> list[Path]:
    """Get list of all PDF files in the raw data directory."""

    if not RAW_DATA_DIR.exists():
        raise FileNotFoundError(f"Raw data directory not found: {RAW_DATA_DIR}")
    
    # Find all PDF files recursively
    pdf_files = list(RAW_DATA_DIR.rglob("*.pdf"))
    
    if not pdf_files:
        print(f"No PDF files found in {RAW_DATA_DIR}")
    else:
        print(f"Found {len(pdf_files)} PDF files")
    
    return pdf_files


def process_pdfs(pdf_files: list[Path]) -> None:
    """Process PDF files and insert data into database."""

    total_processed = 0
    total_rows = 0
    
    for pdf_path in pdf_files:
        try:
            print(f"\nProcessing {pdf_path.name}...")
            
            # Parse PDF to DataFrame
            df = parse_pdf(pdf_path)
            if df.empty:
                print(f"No data found in {pdf_path.name}, skipping...")
                continue
                
            # Clean the data
            df_cleaned = clean_data(df)
            
            # Convert DataFrame to list of dictionaries
            rows = df_cleaned.to_dict('records')
            
            # Insert into database
            rows_inserted = bulk_insert(rows)
            
            print(f"Successfully processed {pdf_path.name}")
            print(f"Inserted {rows_inserted} new rows")
            
            total_processed += 1
            total_rows += rows_inserted
            
        except Exception as e:
            print(f"Error processing {pdf_path.name}: {e}")
            continue
    
    print(f"\nSummary:")
    print(f"Total files processed: {total_processed}/{len(pdf_files)}")
    print(f"Total rows inserted: {total_rows}")


def load_all_data() -> None:
    """Main function to load all PDF data into database."""
    
    try:
        pdf_files = get_pdf_files()
        if pdf_files:
            process_pdfs(pdf_files)
    except Exception as e:
        print(f"Error loading data: {e}")

if __name__ == "__main__":
    load_all_data()







