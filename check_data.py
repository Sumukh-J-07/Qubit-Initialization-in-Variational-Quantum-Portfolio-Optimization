import yfinance as yf
import numpy as np
import pandas as pd
import datetime

# 7-asset
TICKERS_7 = ["AAPL", "MSFT", "GOOG", "AMZN", "META", "NVDA", "TSLA"]

# 12-asset
TICKERS_12 = ["AAPL", "MSFT", "GOOG", "AMZN", "META", "NVDA", "TSLA", "JPM", "JNJ", "V", "PG", "UNH"]

def fetch_market_data(tickers):
    data = yf.download(tickers, period="2y", auto_adjust=True)["Close"]
    returns = data.pct_change().dropna()
    mu = returns.mean().values * 252
    sigma = returns.cov().values * 252
    return mu, sigma, len(returns)

def portfolio_cost(w, mu, sigma, q=0.5):
    return q * np.dot(w.T, np.dot(sigma, w)) - (1 - q) * np.dot(mu.T, w)

def get_c_star(mu, sigma, n):
    best_cost = float('inf')
    import itertools
    for bitstring in itertools.product([0, 1], repeat=n):
        if sum(bitstring) == 0:
            continue
        w = np.array(bitstring) / sum(bitstring)
        cost = portfolio_cost(w, mu, sigma)
        if cost < best_cost:
            best_cost = cost
    return best_cost

print(f"Current Date: {datetime.datetime.now().isoformat()}")

mu7, sig7, nobs7 = fetch_market_data(TICKERS_7)
cstar7 = get_c_star(mu7, sig7, 7)

print("=== 7-Asset ===")
print("Obs:", nobs7)
print("Historical C* = -0.17435")
print(f"Current C*    = {cstar7:.5f}")

mu12, sig12, nobs12 = fetch_market_data(TICKERS_12)
cstar12 = get_c_star(mu12, sig12, 12)

print("\n=== 12-Asset ===")
print("Obs:", nobs12)
print("Historical C* = -0.1642")
print(f"Current C*    = {cstar12:.5f}")
