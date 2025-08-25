from utils.common_imports import *
import os

prices = pd.read_csv("data/output/nifty500_hedging_portfolios_merged.csv", parse_dates=["Date"])

# identify tickers/portfolios

tickers = [col.replace("_Close", "") for col in prices.columns if col.endswith("_Close")]

# initialise returns df

daily_returns = pd.DataFrame()
daily_returns["Date"] = prices["Date"]

# calculate daily returns

for ticker in tickers:
    open_col = f"{ticker}_Open"
    close_col = f"{ticker}_Close"
    daily_returns[ticker] = (prices[close_col] - prices[open_col]) / prices[open_col]

# save df as csv

os.makedirs("data/output", exist_ok=True)
daily_returns.to_csv("data/output/daily_returns.csv", index=False)