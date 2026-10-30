# CORRECTED VERSION 

import numpy as np
import pandas as pd
import yfinance as yf
import time
from qiskit import QuantumCircuit, transpile
from qiskit_aer import Aer
from scipy.optimize import minimize, LinearConstraint, Bounds
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
        
        # Convert bitstring to binary weights
        x_binary = np.array([int(b) for b in bitstring[::-1]], dtype=float)
        
        # FIX #1: NORMALIZE WEIGHTS (sum to 1)
        x_sum = x_binary.sum()
        if x_sum > 0:
            x = x_binary / x_sum  # Proper portfolio weights [0,1] summing to 1
        else:
            # Handle edge case: bitstring is all zeros
            x = np.ones(n_qubits) / n_qubits  # Equal weights
        
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
    
    # Handle edge case where total_prob < alpha
    if total_prob > 0:
        return cvar / total_prob  # Normalize by actual accumulated probability
    else:
        return 0  # All outcomes have zero probability (shouldn't happen)

def objective_expectation(theta):
    return compute_expectation(sample(theta))

def objective_cvar(theta):
    return compute_cvar(sample(theta), alpha=0.3)

# 7. CLASSICAL BASELINE (for comparison)

def classical_portfolio_cost(x):
    """Cost function for classical optimization with normalized weights"""
    x = np.array(x)
    # Ensure valid weights
    x = np.clip(x, 0, 1)
    x_sum = x.sum()
    if x_sum > 0:
        x = x / x_sum
    else:
        x = np.ones(n_qubits) / n_qubits
    return portfolio_cost(x)

def optimize_classical_expectation(theta0):
    """Classical optimization of expectation"""
    constraints = {'type': 'eq', 'fun': lambda x: np.sum(x) - 1}  # sum = 1
    bounds = Bounds(0, 1)  # 0 <= x_i <= 1
    
    result = minimize(
        classical_portfolio_cost, 
        theta0, 
        method='SLSQP',
        bounds=bounds,
        constraints=constraints
    )
    return result

# 8. EXPERIMENT LOOP

runs = 50
results = []

for i in range(runs):
    print(f"Run {i+1}/{runs}")
    
    theta0 = np.random.rand(n_qubits)
    
    #  Quantum: Expectation 
    start_exp = time.time()
    res_exp = minimize(objective_expectation, theta0, method='COBYLA')
    time_exp = time.time() - start_exp
    
    #  Quantum: CVaR 
    start_cvar = time.time()
    res_cvar = minimize(objective_cvar, theta0, method='COBYLA')
    time_cvar = time.time() - start_cvar
    
    #  Classical: Baseline 
    start_classical = time.time()
    res_classical = optimize_classical_expectation(theta0)
    time_classical = time.time() - start_classical
    
    # Evaluate final costs (re-sample for accuracy)
    samples_exp = sample(res_exp.x)
    samples_cvar = sample(res_cvar.x)
    best_exp = min(samples_exp, key=lambda x: x[0])[0]
    best_cvar = min(samples_cvar, key=lambda x: x[0])[0]
    best_classical = classical_portfolio_cost(res_classical.x)
    
    results.append({
        "run": i+1,
        "theta0": theta0.tolist(),
        
        "quantum_exp_final": res_exp.fun,
        "quantum_exp_best": best_exp,
        "quantum_exp_time_sec": time_exp,
        
        "quantum_cvar_final": res_cvar.fun,
        "quantum_cvar_best": best_cvar,
        "quantum_cvar_time_sec": time_cvar,
        
        "classical_final": res_classical.fun,
        "classical_best": best_classical,
        "classical_time_sec": time_classical
    })

# 9. DATAFRAME

df = pd.DataFrame(results)

# 10. SUMMARY

summary = {
    "quantum_exp_mean": df["quantum_exp_best"].mean(),
    "quantum_exp_std": df["quantum_exp_best"].std(),
    "quantum_exp_best_case": df["quantum_exp_best"].min(),
    "quantum_exp_avg_time": df["quantum_exp_time_sec"].mean(),
    
    "quantum_cvar_mean": df["quantum_cvar_best"].mean(),
    "quantum_cvar_std": df["quantum_cvar_best"].std(),
    "quantum_cvar_best_case": df["quantum_cvar_best"].min(),
    "quantum_cvar_avg_time": df["quantum_cvar_time_sec"].mean(),
    
    "classical_mean": df["classical_best"].mean(),
    "classical_std": df["classical_best"].std(),
    "classical_best_case": df["classical_best"].min(),
    "classical_avg_time": df["classical_time_sec"].mean()
}

summary_df = pd.DataFrame([summary])

print("\nSUMMARY")
print(summary_df.to_string())

# 11. STATISTICAL TESTS

print("\n WILCOXON TEST: Quantum Expectation vs Quantum CVaR ")
stat_exp_vs_cvar, p_exp_vs_cvar = wilcoxon(df["quantum_exp_best"], df["quantum_cvar_best"])
print(f"Statistic: {stat_exp_vs_cvar}")
print(f"p-value: {p_exp_vs_cvar:.6f}")
if p_exp_vs_cvar < 0.05:
    print("✓ Significant difference between quantum methods")
else:
    print("✗ No significant difference between quantum methods")

print("\n WILCOXON TEST: Quantum Expectation vs Classical ")
stat_exp_vs_classical, p_exp_vs_classical = wilcoxon(df["quantum_exp_best"], df["classical_best"])
print(f"Statistic: {stat_exp_vs_classical}")
print(f"p-value: {p_exp_vs_classical:.6f}")
if p_exp_vs_classical < 0.05:
    print(" Significant difference: quantum vs classical (expectation)")
else:
    print(" No significant difference: quantum vs classical (expectation)")

print("\n WILCOXON TEST: Quantum CVaR vs Classical ")
stat_cvar_vs_classical, p_cvar_vs_classical = wilcoxon(df["quantum_cvar_best"], df["classical_best"])
print(f"Statistic: {stat_cvar_vs_classical}")
print(f"p-value: {p_cvar_vs_classical:.6f}")
if p_cvar_vs_classical < 0.05:
    print("Significant difference: quantum vs classical (CVaR)")
else:
    print("No significant difference: quantum vs classical (CVaR)")

# 12. SAVE CSV

df.to_csv("corrected_experiment_results_v2.csv", index=False)
summary_df.to_csv("corrected_summary_stats_v2.csv", index=False)

print("FILES SAVED:")
print(" corrected_experiment_results_v2.csv")
print(" corrected_summary_stats_v2.csv")
print("KEY FIXES APPLIED:")
print(" FIX #1: Portfolio weights normalized (sum=1)")
print(" FIX #2: CVaR edge case handled properly")
print(" FIX #3: Classical baseline added for comparison")
print(" FIX #4: Expanded statistical tests (3-way comparison)")