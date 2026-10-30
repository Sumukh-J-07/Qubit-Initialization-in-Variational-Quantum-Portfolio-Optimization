import cvxpy as cp
import numpy as np
import yfinance as yf

# 1. Fetch data
assets = ['AAPL', 'MSFT', 'GOOG']
data = yf.download(assets, start="2020-01-01")

try:
    data = data['Adj Close']
except KeyError:
    data = data['Close']

# 2. Compute returns
returns = data.pct_change().dropna().values

N, n = returns.shape
alpha = 0.95

# 3. Variables
w = cp.Variable(n)     # portfolio weights
v = cp.Variable()      # VaR
u = cp.Variable(N)     # tail losses

# 4. Loss
loss = -returns @ w

# 5. Objective (CVaR)
objective = cp.Minimize(v + (1 / ((1 - alpha) * N)) * cp.sum(u))

# 6. Constraints
constraints = [
    u >= 0,
    u >= loss - v,
    cp.sum(w) == 1
]

# 7. Solve
problem = cp.Problem(objective, constraints)
problem.solve()

# 8. Output
print("Optimal weights:", w.value)
print("Sum of weights:", np.sum(w.value))
print("Optimal CVaR:", problem.value)