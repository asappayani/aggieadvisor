import re


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