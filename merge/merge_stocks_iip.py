from utils.common_imports import *

stocks_path = "data/processed/nifty500_daily.csv"
iip_path = "data/processed/iip_monthly.csv"
output_path = "data/interim/stocks_iip_merged.csv"

stocks = pd.read_csv(stocks_path)
iip = pd.read_csv(iip_path)

# parse dates

stocks["Date"] = pd.to_datetime(stocks["Date"], errors="coerce")
iip["Date"] = pd.to_datetime(iip["Date"], errors="coerce")

# keep only close columns

close_cols = [c for c in stocks.columns if c.endswith("_Close")]
stocks = stocks[["Date"] + close_cols].copy()

# sort by date

stocks = stocks.sort_values("Date")
iip = iip.sort_values("Date")

# merge asof

merged = pd.merge_asof(stocks, iip, on="Date", direction="backward")
iip_dates = pd.to_datetime(iip["Date"], errors="coerce").dropna().unique()
merged = merged[merged["Date"].isin(iip_dates)].reset_index(drop=True)

# ensure close columns are numeric

merged[close_cols] = merged[close_cols].apply(pd.to_numeric, errors="coerce")

# calculate rates

rates = merged[close_cols].pct_change(fill_method=None)
rates.columns = [f"{c}_rate" for c in close_cols]

merged["IIP_rate"] = merged["IIP"].pct_change()

# combine

out = pd.concat([merged, rates], axis=1)

# save merged df as csv

out.to_csv(output_path, index=False)