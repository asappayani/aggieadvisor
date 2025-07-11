import re, os
import pdfplumber as pdf
import pandas as pd
from pprint import pprint as pp


from .patterns import HEADER_PATTERN, COURSE_ROW_PATTERN


# Get the directory of the current script
script_dir = os.path.dirname(os.path.abspath(__file__))
# Go up 3 levels to reach the workspace root, then into data/raw
pdf_path = os.path.join(script_dir, "..", "..", "..", "data", "raw", "f24", "ENGR_F24.pdf")


with pdf.open(pdf_path) as file:
    raw_data = file.pages[0].extract_text().replace("\n", "").replace("\r", "").strip()

    for match in COURSE_ROW_PATTERN.finditer(raw_data):
        print(match.groupdict())

