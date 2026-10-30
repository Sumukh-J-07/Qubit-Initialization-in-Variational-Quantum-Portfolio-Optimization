import pandas as pd
from scipy.stats import wilcoxon

# Load 12-asset results
df12 = pd.read_csv('new_run/results.csv')

# Metric used for 12-asset statistical tests was found to be final_r in the convergence analysis
# Wait, convergence metrics computed final_r. The raw results.csv has 'approximation_ratio'.
print("12-Asset Comparisons (Hadamard vs |0⟩):")
min_p_12 = 1.0
for d in [1, 2, 3, 4]:
    for obj in ['Expectation', 'CVaR']:
        a = df12[(df12['initialization'] == '|0⟩') & (df12['depth'] == d) & (df12['objective'] == obj)].sort_values('seed')['approximation_ratio'].values
        b = df12[(df12['initialization'] == 'Hadamard') & (df12['depth'] == d) & (df12['objective'] == obj)].sort_values('seed')['approximation_ratio'].values
        stat, p = wilcoxon(a, b)
        print(f"Depth {d}, {obj}: W={stat}, p={p:.6f}, p<0.05={p<0.05}")
        if p < min_p_12:
            min_p_12 = p

print(f"\nMinimum 12-asset p-value: {min_p_12:.6f}")

# Load 7-asset results
df7 = pd.read_csv('new_run/full_results.csv')
print("\n7-Asset Comparisons (Hadamard vs |0⟩):")
min_p_7 = 1.0
for d in [1, 3]:
    for obj in ['Expectation', 'CVaR']:
        a = df7[(df7['initialization'] == '|0⟩') & (df7['depth'] == d) & (df7['objective'] == obj)].sort_values('seed')['best_cost'].values
        b = df7[(df7['initialization'] == 'Hadamard') & (df7['depth'] == d) & (df7['objective'] == obj)].sort_values('seed')['best_cost'].values
        stat, p = wilcoxon(a, b)
        print(f"Depth {d}, {obj}: W={stat}, p={p:.6f}, p<0.05={p<0.05}")
        if p < min_p_7:
            min_p_7 = p

print(f"\nMinimum 7-asset p-value: {min_p_7:.6f}")
