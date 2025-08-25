# menial work : adding hedging portfolios to nifty dataset

from utils.common_imports import *

nifty_df = pd.read_csv("data/processed/nifty500_daily.csv", parse_dates=["Date"])
output_path = "data/output/nifty500_hedging_portfolios_merged.csv"

# portfolio definitions

portfolios = {
    "GDP": {
        "stocks": [
            "M&M.NS_Close_rate", "BAJAJHLDNG.NS_Close_rate", "GLENMARK.NS_Close_rate",
            "MARUTI.NS_Close_rate", "IDEA.NS_Close_rate", "RELIANCE.NS_Close_rate",
            "TATACOMM.NS_Close_rate", "MASTEK.NS_Close_rate", "ACC.NS_Close_rate",
            "HEROMOTOCO.NS_Close_rate", "INDUSINDBK.NS_Close_rate", "GODREJCP.NS_Close_rate",
            "MARICO.NS_Close_rate", "COFORGE.NS_Close_rate", "BHARATFORG.NS_Close_rate"
        ],
        "weights": np.array([
            0.03964227, 0.03815848, 0.08588467, 0.04537473, 0.09783008,
            0.14538263, 0.04174465, 0.02557982, 0.05425784, 0.01559454,
            0.12377298, 0.04973633, 0.00640875, 0.20360108, 0.02703115
        ])
    },
    "IIP": {
        "stocks": [
            "ALOKINDS.NS_Close_rate", "JPPOWER.NS_Close_rate", "IDBI.NS_Close_rate",
            "EIDPARRY.NS_Close_rate", "IDEA.NS_Close_rate", "GODREJIND.NS_Close_rate",
            "ALOKINDS.NS_Close", "IFCI.NS_Close_rate", "TATAPOWER.NS_Close_rate",
            "JINDALSTEL.NS_Close_rate"
        ],
        "weights": np.array([
            0.52032027, 0.02086383, 0.00582804, 0.10170502, 0.05954808,
            0.06136103, 0.00690946, 0.00432043, 0.19787501, 0.02126882
        ])
    },
    "CPI": {
        "stocks": [
            "ASTRAL.NS_Close_rate", "BATAINDIA.NS_Close_rate", "AJANTPHARM.NS_Close_rate",
            "DABUR.NS_Close_rate", "TIMKEN.NS_Close_rate", "HINDUNILVR.NS_Close_rate",
            "SOLARINDS.NS_Close_rate", "GRANULES.NS_Close_rate", "MARICO.NS_Close_rate",
            "ATUL.NS_Close_rate"
        ],
        "weights": np.array([
            0.06841426, 0.15407618, 0.15971764, 0.08906008, 0.01574297,
            0.20326462, 0.10482, 0.0609054, 0.11097459, 0.03302426
        ])
    }
}

# helper function to add portfolio open and close columns

def build_portfolio(df, stock_list, weights, ticker):
    open_cols, close_cols, used_weights = [], [], []

    missing = []
    for s, w in zip(stock_list, weights):
        s_base = s.replace("_Close_rate", "").replace("_Close", "")
        open_col, close_col = f"{s_base}_Open", f"{s_base}_Close"
        if open_col in df.columns and close_col in df.columns:
            open_cols.append(open_col)
            close_cols.append(close_col)
            used_weights.append(w)
        else:
            missing.append(s)

    if missing:
        print(f"⚠️ WARNING: {ticker} missing stocks in CSV: {missing}")

    if not open_cols:
        print(f"❌ No valid stocks for {ticker}, skipping.")
        return df

    used_weights = np.array(used_weights)
    used_weights = used_weights / used_weights.sum()  # normalize if any missing

    df[f"{ticker}_Open"] = df[open_cols].values @ used_weights
    df[f"{ticker}_Close"] = df[close_cols].values @ used_weights

    return df


# construct all portfolios

for ticker, pdata in portfolios.items():
    nifty_df = build_portfolio(nifty_df, pdata["stocks"], pdata["weights"], ticker)


# save df as csv

nifty_df.to_csv(output_path, index=False)
