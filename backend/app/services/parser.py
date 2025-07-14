import pdfplumber as pdf
import pandas as pd
from pprint import pprint as pp
from pathlib import Path


from patterns import HEADER_PATTERN, COURSE_ROW_PATTERN

# Get base paths using pathlib
CURR_FILE_PATH = Path(__file__).resolve()
PROJECT_ROOT = CURR_FILE_PATH.parents[3]  # Go up 3 levels to reach project root
DATA_DIR = PROJECT_ROOT / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"

# Test paths
test_pdf_path = RAW_DATA_DIR / "f24" / "ENGR_F24.pdf"

def parse_pdf(pdf_path: str | Path) -> pd.DataFrame:
    parsed_data = []
    
    with pdf.open(pdf_path) as file:
        for page in file.pages:
            raw_data = page.extract_text().replace("\n", " ").replace("\r", " ").strip()

            header_metadata = HEADER_PATTERN.search(raw_data)
            if not header_metadata:
                raise ValueError("Header metadata not found")
            
            header_metadata = header_metadata.groupdict()

            for match in COURSE_ROW_PATTERN.finditer(raw_data):
                course_row = match.groupdict()
                course_row.update(header_metadata)
                parsed_data.append(course_row)

    return pd.DataFrame(parsed_data)

def parse_pdf_to_csv(pdf_path: str | Path) -> None:
    df = parse_pdf(pdf_path)
    output_file = PROCESSED_DATA_DIR / "ENGR_F24.csv"
    df.to_csv(output_file, index=False)

if __name__ == "__main__":
    parse_pdf_to_csv(test_pdf_path)