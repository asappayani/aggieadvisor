import pandas as pd

from pathlib import Path
from parser import parse_pdf


DB_COLUMNS = {
    "A":"a_count","B":"b_count","C":"c_count","D":"d_count","F":"f_count",
    "total":"total_count","gpa":"gpa","Q":"q_drop",
    "semester":"semester","year":"year","college":"college","department":"department",
    "course":"course","professor":"professor"
}


def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    df = df.rename(columns=DB_COLUMNS) # rename dataframe columns to match database schema
    ints = ["a_count", "b_count", "c_count", "d_count", "f_count", "total_count", "q_drop", "year"]
    df[ints] = df[ints].astype(int)
    df["gpa"] = df["gpa"].astype(float)
    df["semester"] = df["semester"].str.upper()
    df["department"] = df["department"].str.upper()
    df["professor"] = df["professor"].str.upper()
    df["course"] = df["course"].str.upper()
    df["college"] = df["college"].str.upper()
    return df  




