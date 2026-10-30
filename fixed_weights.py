import numpy as np
import yfinance as yf

# 1. Fetch data
assets = ['AAPL', 'MSFT', 'GOOG']
data = yf.download(assets, start="2020-01-01")

# Handle column format
try:
    data = data['Adj Close']
except KeyError:
    data = data['Close']

# 2. Returns
returns = data.pct_change().dropna().values

# 3. Equal weights
weights_eq = np.array([1/3, 1/3, 1/3])

# 4. Portfolio returns
portfolio_returns_eq = returns @ weights_eq

# 5. Losses
losses_eq = -portfolio_returns_eq

# 6. VaR & CVaR
alpha = 0.95
VaR_eq = np.percentile(losses_eq, alpha * 100)
CVaR_eq = losses_eq[losses_eq >= VaR_eq].mean()

print("Equal Weights VaR:", VaR_eq)
print("Equal Weights CVaR:", CVaR_eq)
