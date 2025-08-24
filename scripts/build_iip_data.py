from utils.common_imports import *

raw_path = "data/raw/iip.csv"
out_path = "data/processed/iip_monthly.csv"

df = pd.read_csv(raw_path)

# transpose

df_t = df.set_index("Date").T.reset_index()
df_t.columns = ["Date", "IIP"]

# offset MM-YY format to end-of-month dates

df_t["Date"] = pd.to_datetime(df_t["Date"], format="%b-%y") + pd.offsets.MonthEnd(0)

# sort by date

df_t = df_t.sort_values("Date").reset_index(drop=True)

# convert IIP to numeric

df_t["IIP"] = pd.to_numeric(df_t["IIP"], errors="coerce")

# save df as csv

df_t.to_csv(out_path, index = False)