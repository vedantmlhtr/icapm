from utils.common_imports import *
import os

RETURNS_PATH = "data/output/daily_returns.csv"
BETAS_PATH   = "data/output/betas.csv"
OUTPUT_PATH  = "data/output/icapm_trading_results.csv"
START_DATE   = pd.to_datetime("2015-08-22")
END_DATE     = pd.to_datetime("2025-08-22")

# risk free rate

RF = 0.0001784487467864082

# load returns

df = pd.read_csv(RETURNS_PATH, parse_dates=["Date"])
end_date_ts = pd.to_datetime(END_DATE) if END_DATE else df["Date"].max()
df = df[(df["Date"] >= START_DATE) & (df["Date"] <= end_date_ts)].reset_index(drop=True)
if df.empty:
    raise ValueError("no return data in backtest window")

# load betas

betas_long = pd.read_csv(BETAS_PATH)

# factor portfolios

candidate_sets = [["GDP", "IIP", "CPI"], ["GDP_Portfolio", "IIP_Portfolio", "CPI_Portfolio"]]
factor_cols = next((cset for cset in candidate_sets if all(c in df.columns for c in cset)), None)
if factor_cols is None:
    raise ValueError("no factor portfolios found")

canonical = ["GDP", "IIP", "CPI"]
factors_df = df[["Date"] + factor_cols].rename(columns=dict(zip(factor_cols, canonical)))
factors_df.set_index("Date", inplace=True)

# stock list

non_stock = set(["Date"] + factor_cols)
stock_cols = [c for c in df.columns if c not in non_stock]
stocks_df = df[["Date"] + stock_cols].set_index("Date")

# reshape betas

betas_long["Portfolio"] = betas_long["Portfolio"].str.replace("_Portfolio", "", regex=False)
betas_wide = betas_long.pivot_table(index="Stock", columns="Portfolio", values="Beta", aggfunc="first")
betas_wide = betas_wide.loc[:, canonical].fillna(0.0)

common_stocks = [s for s in stock_cols if s in betas_wide.index]
stocks_df = stocks_df[common_stocks]
betas_wide = betas_wide.loc[common_stocks]

# rolling mean factor returns (start immediately)

mean_factors = factors_df.rolling(252, min_periods=1).mean()

# align

stocks_df, mean_factors = stocks_df.align(mean_factors, join="inner", axis=0)
if stocks_df.empty or mean_factors.empty:
    raise ValueError("no overlapping dates between stock returns and factors")

# equilibrium returns

eq_df = pd.DataFrame(
    RF
    + (mean_factors["GDP"] - RF).values[:, None] * betas_wide["GDP"].values[None, :]
    + (mean_factors["IIP"] - RF).values[:, None] * betas_wide["IIP"].values[None, :]
    + (mean_factors["CPI"] - RF).values[:, None] * betas_wide["CPI"].values[None, :],
    index=mean_factors.index,
    columns=betas_wide.index,
)

# trading signals + positions (simple rule)

signals = pd.DataFrame(index=stocks_df.index, columns=stocks_df.columns, dtype=object)
positions = pd.DataFrame(0, index=stocks_df.index, columns=stocks_df.columns, dtype=int)

for stock in stocks_df.columns:
    ret = stocks_df[stock]
    eq = eq_df[stock]
    for t in range(len(ret)):
        r, e = ret.iloc[t], eq.iloc[t]
        if r < e:
            signals.iat[t, signals.columns.get_loc(stock)] = "sell"
            positions.iat[t, positions.columns.get_loc(stock)] = -1
        elif r > e:
            signals.iat[t, signals.columns.get_loc(stock)] = "buy"
            positions.iat[t, positions.columns.get_loc(stock)] = 1

# strategy returns

strategy_ret = (positions.shift(1) * stocks_df).mean(axis=1)
if strategy_ret.empty or strategy_ret.dropna().empty:
    raise ValueError("strategy produced no returns (check signals)")

cum_curve = np.exp(np.log1p(strategy_ret.fillna(0)).cumsum())
total_return = cum_curve.iloc[-1] - 1
avg_daily = strategy_ret.mean()
median_daily = strategy_ret.median()

# save df as csv

out = pd.DataFrame({
    "Strategy_Return": strategy_ret,
    "Cumulative_Equity": cum_curve
}, index=strategy_ret.index).reset_index().rename(columns={"index": "Date"})

os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
out.to_csv(OUTPUT_PATH, index=False)

# summary

print("\n========== icapm trading results ==========")
print(f"window         : {stocks_df.index.min().date()} to {stocks_df.index.max().date()}")
print(f"universe size  : {len(common_stocks)} stocks")
print(f"avg daily ret  : {avg_daily:.4%}")
print(f"median daily   : {median_daily:.4%}")
print(f"total return   : {total_return:.2%}")
print(f"last equity    : {cum_curve.iloc[-1]:.4f}")
print(f"output saved   : {OUTPUT_PATH}")
print("===========================================\n")
