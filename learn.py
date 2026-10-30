import numpy as np

alpha = 0.95
losses = np.array([0.1, 0.2, 0.3, 0.5, 2.0, 5.0])

VaR = np.percentile(losses, alpha * 100)
print(VaR)

CVaR = losses[losses >= VaR].mean()
print(CVaR)