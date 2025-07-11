import re, os
import pdfplumber as pdf
import pandas as pd


HEADER_PATTERN = re.compile(
    r"FOR\s*(?P<semester>[A-Z]+)\s*(?P<year>\d{4})\s*.*?\s*" # semester and year
    r"COLLEGE:\s*(?P<college>[A-Z &,\/-]+(?: [A-Z&,\/-]+)*)\s+" # college or school name
    r"DEPARTMENT:\s*(?P<department>[A-Z &,\.\/-]+(?: [A-Z&,\.\/-]+)*)\s+TOTAL S", # department name
    re.DOTALL | re.IGNORECASE
)


COURSE_ROW_PATTERN = re.compile(
    r"""(?P<course>[A-Z]+-\d{3})-\d{3}\s+                # course prefix-number
        (?P<A>\d+)\s+(?P<B>\d+)\s+(?P<C>\d+)\s+          # A-C counts
        (?P<D>\d+)\s+(?P<F>\d+)\s+                       # D, F counts
        (?P<total>\d+)\s+(?P<gpa>\d\.\d{3})\s+           # section total & GPA
        (?:\d+\s+){3}                                    # I  S  U   ← non-capturing, ignored
        (?P<Q>\d+)\s+                                    # Q-drops (we still want this)
        (?:\d+\s+)                                       # X column   ← ignored
        \d+\s+                                           # repeated total column (ignored)
        (?P<instructor>[A-Za-z.,\s'\-]+)                 # instructor
    """,
    re.VERBOSE
)

# Get the directory of the current script
script_dir = os.path.dirname(os.path.abspath(__file__))
# Go up 3 levels to reach the workspace root, then into data/raw
pdf_path = os.path.join(script_dir, "..", "..", "..", "data", "raw", "f24", "ENGR_F24.pdf")

with pdf.open(pdf_path) as file:
    print(file.pages[0].extract_text())
    raw_data = file.pages[0].extract_text().replace("\n", "").replace("\r", "").strip()

    for match in COURSE_ROW_PATTERN.finditer(raw_data):
        print(match.groupdict())

