from utils.common_imports import *

# fetch nifty500 constituents

url = "https://www.niftyindices.com/IndexConstituent/ind_nifty500list.csv"
df = pd.read_csv(url)

# pull stock tickers and make nifty500_tickers array

symbols = df["Symbol"].astype(str).str.strip().tolist()
nifty500_tickers = [symbol + ".NS" for symbol in symbols]