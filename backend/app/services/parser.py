import re

HEADER_PATTERN = re.compile(
    r"FOR\s*(?P<semester>[A-Z]+)\s*(?P<year>\d{4})\s*.*?\s*" # semester and year
    r"COLLEGE:\s*(?P<college>[A-Z &,\/-]+(?: [A-Z&,\/-]+)*)\s+" # college or school name
    r"DEPARTMENT:\s*(?P<department>[A-Z &,\.\/-]+(?: [A-Z&,\.\/-]+)*)\s+TOTAL S", # department name
    re.DOTALL | re.IGNORECASE
)


COURSE_PATTERN = re.compile(
    r"(?P<course>[A-Z]+-\d{3})-\d{3}\s+"  # course code without section number
    r"(?P<A>\d+)\s+(?P<B>\d+)\s+(?P<C>\d+)\s+(?P<D>\d+)\s+(?P<F>\d+)\s+"  # grades A-F
    r"(?P<total>\d+)\s+(?P<gpa>\d\.\d{3})\s+"  # total students & GPA
    r"(?P<I>\d+)\s+(?P<S>\d+)\s+(?P<U>\d+)\s+"  # incomplete, satisfactory, unsatisfactory
    r"(?P<Q>\d+)?\s*(?P<X>\d+)\s+\d+\s+"  # drops & no-grade cases (skipping repeated total)
    r"(?P<instructor>[A-Za-z.,\s'\-]+)"  # instructor's name
)