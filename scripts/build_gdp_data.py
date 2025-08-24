from utils.common_imports import *
output_path = "data/processed/gdp_quarterly.csv"

df = pd.read_excel("data/raw/gdp_data.xlsx")
df["year"] = df["year"].astype(str)

# convert quarter to date

quarter_to_month = {
    "Q1": "03-31",
    "Q2": "06-30",
    "Q3": "09-30",
    "Q4": "12-31"
}

# create datetime column by deriving year

dates = []

for _, row in df.iterrows():
    year = row["year"].split("-")[0]
    quarter = row["quarter"]

    if quarter == "Q4":
        # Q4 belongs to next calendar year
        year = str(int(year) + 1)

    date_str = f"{year}-{quarter_to_month[quarter]}"
    dates.append(pd.to_datetime(date_str, format="%Y-%m-%d"))

df["date"] = dates

# keep only date and gdp

df = df[["date", "gdp"]]

# save df as csv

df.to_csv(output_path, index = False)