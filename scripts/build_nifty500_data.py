from utils.common_imports import *
from utils.fetch_nifty500 import nifty500_tickers
output_path = "data/raw/nifty500.csv"

tickers = [ticker for ticker in nifty500_tickers]

# create df with stock price data

df = yf.download(
    tickers,
    start = "2020-01-01",
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

# save as csv

df.to_csv(output_path)


