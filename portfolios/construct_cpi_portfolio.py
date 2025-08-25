from utils.common_imports import *

df = pd.read_csv("data/interim/stocks_cpi_merged.csv")

# ensure CPI rate is numeric

df["CPI_rate"] = pd.to_numeric(df["CPI_rate"], errors="coerce")

# identify stock columns

stock_cols = [col for col in df.columns if col not in ["Date", "CPI", "CPI_rate"]]

# calculate correlations with CPI

cpi_corr = {}
for stock in stock_cols:
    cpi_corr[stock] = df[stock].corr(df["CPI_rate"])

# calculate stock-stock correlations

stock_corr = df[stock_cols].corr()

# select top k stocks

def rank_stocks(top_k=10):
    ranked = sorted(cpi_corr.items(), key=lambda x: abs(x[1]) if pd.notna(x[1]) else 0, reverse=True)
    selected = [s for s, _ in ranked[:top_k]]
    return selected

# randomise weights and simulate

def simulate_portfolios(selected_stocks, n_iter=10000):
    best_corr = 0
    best_weights = None
    best_portfolio = None
    
    stock_data = df[selected_stocks]
    cpi_data = df["CPI_rate"]

    for _ in range(n_iter):
        weights = np.random.dirichlet(np.ones(len(selected_stocks)))
        portfolio_return = stock_data.values @ weights

        # align with CPI and drop NaNs
        aligned = pd.DataFrame({
            "portfolio": portfolio_return,
            "cpi": cpi_data.values
        }).dropna()

        if aligned.shape[0] < 2:
            continue  # not enough data

        corr = np.corrcoef(aligned["portfolio"], aligned["cpi"])[0, 1]

        if np.isnan(corr):
            continue

        if abs(corr) > abs(best_corr):
            best_corr = corr
            best_weights = weights
            best_portfolio = aligned["portfolio"]

    return best_corr, best_weights, selected_stocks

if __name__ == "__main__":
    subset_size = 15  # changeable
    selected_stocks = rank_stocks(subset_size)
    best_corr, best_weights, selected_stocks = simulate_portfolios(selected_stocks, n_iter=5000)

    print(f"Selected {len(selected_stocks)} stocks: {selected_stocks}")
    print("Best correlation with CPI:", best_corr)
    print("Best weights:", best_weights)

# extra fn

def get_portfolio(subset_size=15, n_iter=5000):
    selected_stocks = rank_stocks(subset_size)
    best_corr, best_weights, selected_stocks = simulate_portfolios(selected_stocks, n_iter=n_iter)
    return selected_stocks, best_weights