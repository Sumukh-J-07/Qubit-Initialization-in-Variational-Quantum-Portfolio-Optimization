"""
Verify every number in the Results section against the raw data.
"""
import itertools
import numpy as np
import pandas as pd
from scipy.stats import wilcoxon

df = pd.read_csv("full_results.csv")

DEPTH_OPTIONS = [1, 3]
OBJECTIVE_OPTIONS = ["Expectation", "CVaR"]

# === 1. Summary statistics verification ===
print("=" * 80)
print("SUMMARY STATISTICS VERIFICATION")
print("=" * 80)

grouped = df.groupby(["initialization", "depth", "objective"])
for (init, depth, obj), group in grouped:
    bc = group["best_cost"]
    fo = group["final_obj"]
    t = group["time_s"]
    nf = group["nfev"]
    print(f"\n{init}, d={depth}, {obj}:")
    print(f"  mean_best_cost = {bc.mean():.10f}  (rounded: {bc.mean():.4f})")
    print(f"  std_best_cost  = {bc.std():.10f}  (rounded: {bc.std():.4f})")
    print(f"  min_best_cost  = {bc.min():.10f}  (rounded: {bc.min():.5f})")
    print(f"  mean_final_obj = {fo.mean():.10f}  (rounded: {fo.mean():.4f})")
    print(f"  std_final_obj  = {fo.std():.10f}")
    print(f"  mean_time_s    = {t.mean():.4f}  (rounded: {t.mean():.3f})")
    print(f"  mean_nfev      = {nf.mean():.1f}")

# === 2. Global optimum verification ===
print(f"\n{'=' * 80}")
print("GLOBAL OPTIMUM")
print(f"{'=' * 80}")
global_best = df["best_cost"].min()
print(f"Global best cost across ALL runs: {global_best:.15f}")
print(f"Rounded to 5 decimals: {global_best:.5f}")

# Check which configs achieved this
print("\nConfigs that achieved global optimum (min_best_cost):")
for (init, depth, obj), group in grouped:
    min_bc = group["best_cost"].min()
    achieved = np.isclose(min_bc, global_best)
    print(f"  {init}, d={depth}, {obj}: min={min_bc:.10f}  achieved_optimum={achieved}")

# === 3. Wilcoxon signed-rank tests ===
print(f"\n{'=' * 80}")
print("WILCOXON SIGNED-RANK TEST RESULTS")
print(f"{'=' * 80}")

def do_wilcoxon(a_vals, b_vals, label):
    a = np.array(a_vals)
    b = np.array(b_vals)
    try:
        stat, p = wilcoxon(a, b)
    except ValueError as e:
        stat, p = float("nan"), float("nan")
        print(f"  WARNING: {e}")
    sig = "YES" if p < 0.05 else "No"
    print(f"  {label}")
    print(f"    W = {stat:.1f}, p = {p:.4f}, significant = {sig}")
    print(f"    a = {np.round(a, 5)}")
    print(f"    b = {np.round(b, 5)}")
    print(f"    diff = {np.round(a - b, 5)}")
    return stat, p

# Family 1: |0⟩ vs Hadamard
print("\n--- Family 1: |0⟩ vs Hadamard ---")
for depth, obj in itertools.product(DEPTH_OPTIONS, OBJECTIVE_OPTIONS):
    a = df[(df["initialization"] == "|0⟩") & (df["depth"] == depth) & (df["objective"] == obj)]
    b = df[(df["initialization"] == "Hadamard") & (df["depth"] == depth) & (df["objective"] == obj)]
    a_sorted = a.sort_values("seed")["best_cost"].values
    b_sorted = b.sort_values("seed")["best_cost"].values
    do_wilcoxon(a_sorted, b_sorted, f"|0⟩ vs H (d={depth}, {obj})")

# Family 2: Depth 1 vs Depth 3
print("\n--- Family 2: Depth 1 vs Depth 3 ---")
for init, obj in itertools.product(["Hadamard", "|0⟩"], OBJECTIVE_OPTIONS):
    a = df[(df["initialization"] == init) & (df["depth"] == 1) & (df["objective"] == obj)]
    b = df[(df["initialization"] == init) & (df["depth"] == 3) & (df["objective"] == obj)]
    a_sorted = a.sort_values("seed")["best_cost"].values
    b_sorted = b.sort_values("seed")["best_cost"].values
    do_wilcoxon(a_sorted, b_sorted, f"D1 vs D3 ({init}, {obj})")

# Family 3: Expectation vs CVaR
print("\n--- Family 3: Expectation vs CVaR ---")
for init, depth in itertools.product(["Hadamard", "|0⟩"], DEPTH_OPTIONS):
    a = df[(df["initialization"] == init) & (df["depth"] == depth) & (df["objective"] == "Expectation")]
    b = df[(df["initialization"] == init) & (df["depth"] == depth) & (df["objective"] == "CVaR")]
    a_sorted = a.sort_values("seed")["best_cost"].values
    b_sorted = b.sort_values("seed")["best_cost"].values
    do_wilcoxon(a_sorted, b_sorted, f"Exp vs CVaR ({init}, d={depth})")

# === 4. Depth improvement calculations ===
print(f"\n{'=' * 80}")
print("DEPTH IMPROVEMENT RATIOS")
print(f"{'=' * 80}")
for init in ["Hadamard", "|0⟩"]:
    for obj in OBJECTIVE_OPTIONS:
        d1 = df[(df["initialization"] == init) & (df["depth"] == 1) & (df["objective"] == obj)]
        d3 = df[(df["initialization"] == init) & (df["depth"] == 3) & (df["objective"] == obj)]
        cost_d1 = d1["best_cost"].mean()
        cost_d3 = d3["best_cost"].mean()
        time_d1 = d1["time_s"].mean()
        time_d3 = d3["time_s"].mean()
        nfev_d1 = d1["nfev"].mean()
        nfev_d3 = d3["nfev"].mean()
        gain = cost_d3 - cost_d1  # both negative, so gain is negative (improvement)
        print(f"\n{init}, {obj}:")
        print(f"  Cost: {cost_d1:.4f} → {cost_d3:.4f}, gain = {abs(gain):.3f}")
        print(f"  Time: {time_d1:.3f} → {time_d3:.3f}, ratio = {time_d3/time_d1:.2f}×")
        print(f"  NFEv: {nfev_d1:.1f} → {nfev_d3:.1f}, ratio = {nfev_d3/nfev_d1:.2f}×")

# === 5. Approximation ratios ===
print(f"\n{'=' * 80}")
print("APPROXIMATION RATIOS (mean_best_cost / global_optimum)")
print(f"{'=' * 80}")
for (init, depth, obj), group in grouped:
    ratio = group["best_cost"].mean() / global_best
    print(f"  {init}, d={depth}, {obj}: {ratio:.4f} ({ratio*100:.1f}%)")
