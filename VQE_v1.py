
# FINAL CLEAN VERSION (NO BUGS)

import numpy as np
import pandas as pd
import yfinance as yf
import time
from qiskit import QuantumCircuit, transpile
from qiskit_aer import Aer
from scipy.optimize import minimize
from scipy.stats import wilcoxon

# 1. REAL DATA

assets = ["AAPL", "MSFT", "GOOG", "AMZN", "META"]

data = yf.download(assets, start="2022-01-01")["Close"]
returns = data.pct_change().dropna()

mu = returns.mean().values * 252
Sigma = returns.cov().values * 252

n_qubits = len(assets)
q = 0.5

# 2. COST FUNCTION

def portfolio_cost(x):
    x = np.array(x)
    return q * x @ Sigma @ x - (1 - q) * mu @ x

# 3. CIRCUIT (NO MEASUREMENT HERE)

def create_circuit(theta):
    qc = QuantumCircuit(n_qubits)
    
    for i in range(n_qubits):
        qc.ry(theta[i], i)
    
    for i in range(n_qubits - 1):
        qc.cx(i, i+1)
    
    return qc

backend = Aer.get_backend('aer_simulator')

# 4. SAMPLING (CORRECT)

def sample(theta):
    qc = create_circuit(theta)
    
    qc.measure_all()
    
    compiled = transpile(qc, backend)
    result = backend.run(compiled, shots=1024).result()
    counts = result.get_counts()
    
    samples = []
    
    for bitstring, count in counts.items():
        prob = count / 1024
        
        # Fix endian
        x = [int(b) for b in bitstring[::-1]]
        
        cost = portfolio_cost(x)
        samples.append((cost, prob))
    
    return samples

# 5. OBJECTIVES

def compute_expectation(samples):
    return sum(cost * prob for cost, prob in samples)

def compute_cvar(samples, alpha=0.3):
    samples = sorted(samples, key=lambda x: x[0])
    
    total_prob = 0
    cvar = 0
    
    for cost, prob in samples:
        if total_prob >= alpha:
            break
        
        weight = min(prob, alpha - total_prob)
        cvar += cost * weight
        total_prob += weight
    
    return cvar / alpha

def objective_expectation(theta):
    return compute_expectation(sample(theta))

def objective_cvar(theta):
    return compute_cvar(sample(theta), alpha=0.3)

# 6. BEST COST

def get_best_cost(theta):
    samples = sample(theta)
    best = min(samples, key=lambda x: x[0])
    return best[0]

# 7. EXPERIMENT LOOP

runs = 50
results = []

for i in range(runs):
    print(f"Run {i+1}/{runs}")
    
    theta0 = np.random.rand(n_qubits)
    
    # Expectation
    start_exp = time.time()
    res_exp = minimize(objective_expectation, theta0, method='COBYLA')
    time_exp = time.time() - start_exp
    
    # CVaR
    start_cvar = time.time()
    res_cvar = minimize(objective_cvar, theta0, method='COBYLA')
    time_cvar = time.time() - start_cvar
    
    best_exp = get_best_cost(res_exp.x)
    best_cvar = get_best_cost(res_cvar.x)
    
    results.append({
        "run": i+1,
        "theta0": theta0.tolist(),
        
        "exp_final": res_exp.fun,
        "exp_best": best_exp,
        "exp_time_sec": time_exp,
        
        "cvar_final": res_cvar.fun,
        "cvar_best": best_cvar,
        "cvar_time_sec": time_cvar
    })

# 8. DATAFRAME

df = pd.DataFrame(results)

# 9. SUMMARY

summary = {
    "exp_mean": df["exp_best"].mean(),
    "exp_std": df["exp_best"].std(),
    "exp_best_case": df["exp_best"].min(),
    "exp_avg_time": df["exp_time_sec"].mean(),
    
    "cvar_mean": df["cvar_best"].mean(),
    "cvar_std": df["cvar_best"].std(),
    "cvar_best_case": df["cvar_best"].min(),
    "cvar_avg_time": df["cvar_time_sec"].mean()
}

summary_df = pd.DataFrame([summary])

print("\n========== SUMMARY ==========")
print(summary_df)

# 10. WILCOXON TEST

stat, p = wilcoxon(df["exp_best"], df["cvar_best"])

print("\n========== WILCOXON TEST ==========")
print("Statistic:", stat)
print("p-value:", p)

if p < 0.05:
    print("Significant difference")
else:
    print("No significant difference")

# 11. SAVE CSV

df.to_csv("paired_experiment_results_v1.csv", index=False)
summary_df.to_csv("paired_summary_stats_v1.csv", index=False)

print("\nSaved:")
print("- paired_experiment_results_v1.csv")
print("- paired_summary_stats_v1.csv")