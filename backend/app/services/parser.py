import os
import pdfplumber as pdf
import pandas as pd
from pprint import pprint as pp


from patterns import HEADER_PATTERN, COURSE_ROW_PATTERN


# Get the directory of the current script
script_dir = os.path.dirname(os.path.abspath(__file__))
# Go up 3 levels to reach the workspace root, then into data/raw
pdf_path = os.path.join(script_dir, "..", "..", "..", "data", "raw", "f24", "ENGR_F24.pdf")


def parse_pdf(pdf_path: str) -> pd.DataFrame:
    parsed_data = []
    
    with pdf.open(pdf_path) as file:
        for page in file.pages:
            raw_data = page.extract_text().replace("\n", " ").replace("\r", " ").strip() # remove newlines and carriage returns

            header_metadata = HEADER_PATTERN.search(raw_data) # search for header metadata
            if not header_metadata:
                raise ValueError("Header metadata not found")
            
            header_metadata = header_metadata.groupdict() # get the header metadata as a dict

            for match in COURSE_ROW_PATTERN.finditer(raw_data):
                course_row = match.groupdict()
                course_row.update(header_metadata)
                parsed_data.append(course_row)
        

    return pd.DataFrame(parsed_data)

print(parse_pdf(pdf_path))