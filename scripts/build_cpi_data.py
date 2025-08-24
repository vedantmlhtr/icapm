from utils.common_imports import *
from pathlib import Path

raw_path = "data/raw/cpi.csv"
processed_path = "data/processed/cpi_monthly.csv"

df = pd.read_csv(raw_path)

# rename columns

if "observation_date" in df.columns and "INDCPIALLMINMEI" in df.columns:
    df = df.rename(columns={"observation_date": "Date", "INDCPIALLMINMEI": "CPI"})

# parse dates

df["Date"] = pd.to_datetime(df["Date"], errors="coerce")

# keep only date and CPI columns

df = df[["Date", "CPI"]].copy()

# sort by date

df = df.sort_values("Date").reset_index(drop=True)

# save df as csv

df.to_csv(processed_path, index=False)
