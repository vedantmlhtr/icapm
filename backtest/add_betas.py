from utils.common_imports import *
import os

def main():

    daily_returns = pd.read_csv("data/output/daily_returns.csv", index_col=0, parse_dates=True)

    portfolio_names = ["GDP", "IIP", "CPI"]

    stock_names = [col for col in daily_returns.columns if col not in portfolio_names]

    betas = []

    for stock in stock_names:
        for portfolio in portfolio_names:
            cov = daily_returns[stock].cov(daily_returns[portfolio])
            var = daily_returns[portfolio].var()
            beta = cov / var if var != 0 else float("nan")

            betas.append({
                "Stock": stock,
                "Portfolio": portfolio,
                "Beta": beta
            })

    betas_df = pd.DataFrame(betas)

    output_path = "data/output/betas.csv"
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    betas_df.to_csv(output_path, index=False)

if __name__ == "__main__":
    main()
