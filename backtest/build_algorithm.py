from utils.common_imports import *
import os
import numpy as np
import pandas as pd

RETURNS_PATH = "data/output/daily_returns.csv"          
BETAS_PATH   = "data/output/betas.csv"                   
OUTPUT_PATH  = "data/output/icapm_trading_results.csv"  
START_DATE   = pd.to_datetime("2024-08-24")              
END_DATE     = None                                      
THRESHOLD    = 0.0                                       

df = pd.read_csv(RETURNS_PATH, parse_dates=["Date"])
if END_DATE is not None:
    end_date_ts = pd.to_datetime(END_DATE)
else:
    end_date_ts = df["Date"].max()

# restrict backtest window
df = df[(df["Date"] >= START_DATE) & (df["Date"] <= end_date_ts)].reset_index(drop=True)

if df.empty:
    raise ValueError("No return data in the requested backtest window. Check dates or input file.")

betas_long = pd.read_csv(BETAS_PATH)

# map factor portfolios
candidate_sets = [
    ["GDP", "IIP", "CPI"],
    ["GDP_Portfolio", "IIP_Portfolio", "CPI_Portfolio"]
]

factor_cols = None
for cset in candidate_sets:
    if all(c in df.columns for c in cset):
        factor_cols = cset
        break

if factor_cols is None:
    raise ValueError("Could not find factor columns (GDP/IIP/CPI) in daily_returns.csv.")

canonical_names = ["GDP", "IIP", "CPI"]
factor_col_map = {}
for can, col in zip(canonical_names, factor_cols):
    factor_col_map[can] = col

factors_df = df[["Date"] + list(factor_col_map.values())].rename(columns={v: k for k, v in factor_col_map.items()})
factors_df.set_index("Date", inplace=True)

# build stock list
non_stock = set(["Date"] + list(factor_col_map.values()))
stock_cols = [c for c in df.columns if c not in non_stock]

if len(stock_cols) == 0:
    raise ValueError("No stock columns detected in daily_returns.csv (after excluding factors).")

stocks_df = df[["Date"] + stock_cols].set_index("Date")

# prepare betas
required_beta_cols = {"Stock", "Portfolio", "Beta"}
if not required_beta_cols.issubset(set(betas_long.columns)):
    raise ValueError("betas.csv must have columns: Stock, Portfolio, Beta.")

# normalise portfolio names
betas_long["Portfolio"] = betas_long["Portfolio"].str.replace("_Portfolio", "", regex=False)
betas_long = betas_long[betas_long["Portfolio"].isin(canonical_names)]
if betas_long.empty:
    raise ValueError("betas.csv has no rows for portfolios GDP/IIP/CPI.")

betas_wide = betas_long.pivot_table(index="Stock", columns="Portfolio", values="Beta", aggfunc="first")

common_stocks = [s for s in stock_cols if s in betas_wide.index]
if len(common_stocks) == 0:
    raise ValueError("No overlap between stock returns and betas. Check naming consistency.")

# filter
stocks_df = stocks_df[common_stocks]
betas_wide = betas_wide.loc[common_stocks, canonical_names].fillna(0.0)

# compute icapm daily expected returns
expected_df = pd.DataFrame(
    data=factors_df.values @ betas_wide.values.T,
    index=factors_df.index,
    columns=betas_wide.index
)

# align with real returns
stocks_df, expected_df = stocks_df.align(expected_df, join="inner", axis=0)

# build signals
alpha_df = stocks_df - expected_df
signals = pd.DataFrame(0, index=alpha_df.index, columns=alpha_df.columns, dtype=float)
signals[alpha_df > THRESHOLD] = 1.0
signals[alpha_df < -THRESHOLD] = -1.0

# strategy returns
active_pnl = signals * stocks_df
active_pnl = active_pnl.where(signals != 0, np.nan)

# mean across active positions
strategy_ret = active_pnl.mean(axis=1, skipna=True).fillna(0.0)

# ---------------- crucial update: log compounding ----------------
cum_curve = np.exp(np.log1p(strategy_ret).cumsum())
total_return = cum_curve.iloc[-1] - 1.0
avg_daily_return = strategy_ret.mean()

# bookkeeping
long_count  = (signals == 1).sum(axis=1)
short_count = (signals == -1).sum(axis=1)
active_count = long_count + short_count
avg_active_positions = active_count.replace(0, np.nan).mean()

# save per-day results
out = pd.DataFrame({
    "Strategy_Return": strategy_ret,
    "Cumulative_Equity": cum_curve,
    "Long_Count": long_count,
    "Short_Count": short_count,
    "Active_Count": active_count,
}, index=strategy_ret.index).reset_index().rename(columns={"index": "Date"})

os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
out.to_csv(OUTPUT_PATH, index=False)

# print summary
print("\n========== ICAPM Trading Algorithm Summary ==========")
print(f"Backtest window           : {stocks_df.index.min().date()} to {stocks_df.index.max().date()}")
print(f"Universe size (with betas): {len(common_stocks)} stocks")
print(f"Threshold (abs alpha)     : {THRESHOLD:.6f}")
print(f"Avg active positions/day  : {0 if np.isnan(avg_active_positions) else round(avg_active_positions, 2)}")
print(f"Avg daily return          : {avg_daily_return:.4%}")
print(f"Total return              : {total_return:.2%}")
print("Last cumulative equity    : {:.4f}".format(cum_curve.iloc[-1]))
print("Per-day results saved to  :", OUTPUT_PATH)
print("=====================================================\n")