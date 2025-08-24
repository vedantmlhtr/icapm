import yfinance as yf
from utils.common_imports import *
from utils.fetch_nifty500 import nifty500_tickers
output_path = "data/processed/nifty500_daily.csv"

tickers = [ticker for ticker in nifty500_tickers]

# create df with stock price data

df = yf.download(
    tickers,
    start = "2011-01-01",
    interval = "1d",
    group_by = "ticker",
    progress = True,
    auto_adjust = False,
    threads = True
)

# keep only open and close

df = df.loc[:, (slice(None), ["Open", "Close"])]

# flatten column names

df.columns = [f"{col[0]}_{col[1]}" for col in df.columns]

# slice out stocks by most common start date

start_dates = {}

for ticker in tickers:
    col = f"{ticker}_Open"
    if col in df.columns:
        first_valid = df[col].first_valid_index()
        start_dates[ticker] = first_valid

common_start = pd.Series(start_dates).mode()[0]

sliced_out = [t for t, d in start_dates.items() if d is not None and d > common_start]

for t in sliced_out:
    df = df.drop(columns=[f"{t}_Open", f"{t}_Close"], errors = "ignore")

df = df[df.index >= common_start]

# save as csv

df.to_csv(output_path)