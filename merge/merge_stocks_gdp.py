from utils.common_imports import *
from pathlib import Path

stocks_path = "data/processed/nifty500_daily.csv"
gdp_path = "data/processed/gdp_quarterly.csv"
output_path = "data/interim/stocks_gdp_merged.csv"

stocks = pd.read_csv(stocks_path)
gdp = pd.read_csv(gdp_path)

# normalise gdp date column name

if "Date" not in gdp.columns and "date" in gdp.columns:
    gdp = gdp.rename(columns={"date": "Date"})

# parse dates

stocks["Date"] = pd.to_datetime(stocks["Date"], errors="coerce")
gdp["Date"] = pd.to_datetime(gdp["Date"], errors="coerce")

# keep only dates and close columns

close_cols = [c for c in stocks.columns if c.endswith("_Close")]
stocks = stocks[["Date"] + close_cols].copy()

# sort by date

stocks = stocks.sort_values("Date")
gdp = gdp.sort_values("Date")

# merge asof

merged = pd.merge_asof(stocks, gdp, on="Date", direction="backward")
gdp_dates = pd.to_datetime(gdp["Date"], errors="coerce").dropna().unique()
merged = merged[merged["Date"].isin(gdp_dates)].reset_index(drop=True)

# ensure close columns are numeric

merged[close_cols] = merged[close_cols].apply(pd.to_numeric, errors="coerce")

# calculate rates

rates = merged[close_cols].pct_change(fill_method=None)
rates.columns = [f"{c}_rate" for c in close_cols]

merged["gdp_rate"] = merged["gdp"].pct_change()

# combine

out = pd.concat([merged, rates], axis=1)

# save merged df as csv

out.to_csv(output_path, index=False)
print(f"Wrote {len(out):,} rows to {output_path}")