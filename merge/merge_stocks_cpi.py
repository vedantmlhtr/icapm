from utils.common_imports import *

stocks_path = "data/processed/nifty500_daily.csv"
cpi_path = "data/processed/cpi_monthly.csv"
output_path = "data/interim/stocks_cpi_merged.csv"

stocks = pd.read_csv(stocks_path)
cpi = pd.read_csv(cpi_path)

merged_df = pd.merge(stocks, cpi[['Date', 'CPI']], on='Date', how='left')

# parse dates

stocks["Date"] = pd.to_datetime(stocks["Date"], errors="coerce")
cpi["Date"] = pd.to_datetime(cpi["Date"], errors="coerce")

# keep only close columns

close_cols = [c for c in stocks.columns if c.endswith("_Close")]
stocks = stocks[["Date"] + close_cols].copy()

# sort by date

stocks = stocks.sort_values("Date")
cpi = cpi.sort_values("Date")

# merge asof

merged = pd.merge_asof(stocks, cpi, on="Date", direction="backward")
cpi_dates = pd.to_datetime(cpi["Date"], errors="coerce").dropna().unique()
merged = merged[merged["Date"].isin(cpi_dates)].reset_index(drop=True)

# ensure close columns are numeric

merged[close_cols] = merged[close_cols].apply(pd.to_numeric, errors="coerce")

# calculate rates

rates = merged[close_cols].pct_change(fill_method=None)
rates.columns = [f"{c}_rate" for c in close_cols]

merged["CPI_rate"] = merged["CPI"].pct_change()

# combine

out = pd.concat([merged, rates], axis=1)

# save merged df as csv

out.to_csv(output_path, index=False)