import ast
import pandas as pd
import numpy as np
from scipy.stats import wilcoxon
import itertools

def run_statistical_tests(df: pd.DataFrame):
    print("\nStatistical Tests (Wilcoxon Signed-Rank)")
    DEPTH_OPTIONS = [1, 2, 3, 4]
    OBJECTIVE_OPTIONS = ["Expectation", "CVaR"]
    
    # 1) Hadamard vs |0⟩
    for depth, obj in itertools.product(DEPTH_OPTIONS, OBJECTIVE_OPTIONS):
        a = df[(df["initialization"] == "|0⟩") & (df["depth"] == depth) & (df["objective"] == obj)]
        b = df[(df["initialization"] == "Hadamard") & (df["depth"] == depth) & (df["objective"] == obj)]
        if len(a) > 0 and len(b) > 0:
            a_vals = a.sort_values("seed")["final_r"].values
            b_vals = b.sort_values("seed")["final_r"].values
            try:
                stat, p = wilcoxon(a_vals, b_vals)
                sig = "*" if p < 0.05 else ""
                print(f"|0⟩ vs Had (d={depth}, {obj}): p={p:.4f} {sig}")
            except:
                pass

    # 2) Expectation vs CVaR
    for init, depth in itertools.product(["Hadamard", "|0⟩"], DEPTH_OPTIONS):
        a = df[(df["initialization"] == init) & (df["depth"] == depth) & (df["objective"] == "Expectation")]
        b = df[(df["initialization"] == init) & (df["depth"] == depth) & (df["objective"] == "CVaR")]
        if len(a) > 0 and len(b) > 0:
            a_vals = a.sort_values("seed")["final_r"].values
            b_vals = b.sort_values("seed")["final_r"].values
            try:
                stat, p = wilcoxon(a_vals, b_vals)
                sig = "*" if p < 0.05 else ""
                print(f"Exp vs CVaR (Init={init}, d={depth}): p={p:.4f} {sig}")
            except:
                pass

def compute_t95(best_cost_history, c_star, max_iter=200):
    for i, cost in enumerate(best_cost_history):
        r_k = cost / c_star
        if r_k >= 0.95:
            return i + 1  # 1-indexed iterations
    return max_iter

def main():
    print("Loading results.csv...")
    try:
        df = pd.read_csv("results.csv")
    except FileNotFoundError:
        print("results.csv not found. Run expanded_experiment.py first.")
        return

    metrics_rows = []

    for _, row in df.iterrows():
        seed = row["seed"]
        depth = row["depth"]
        objective = row["objective"]
        initialization = row["initialization"]
        final_cost = row["final_cost"]
        final_r = row["approximation_ratio"]
        
        if final_r != 0:
            c_star = final_cost / final_r
        else:
            c_star = -1.0 
            
        best_cost_history = ast.literal_eval(row["best_cost_history"])
        
        t95 = compute_t95(best_cost_history, c_star)
        reached_95 = (final_r >= 0.95)
        
        metrics_rows.append({
            "seed": seed,
            "depth": depth,
            "objective": objective,
            "initialization": initialization,
            "T95": t95,
            "final_r": final_r,
            "reached_95": reached_95
        })

    metrics_df = pd.DataFrame(metrics_rows)
    metrics_df.to_csv("convergence_metrics.csv", index=False)
    print("Saved convergence_metrics.csv")
    
    # Run statistical tests
    run_statistical_tests(metrics_df)

    # Compute Success Rate S95
    print("\nSuccess Rate (S95) by Configuration:")
    configs = metrics_df.groupby(["initialization", "depth", "objective"])
    
    summary_rows = []
    for (init, depth, obj), group in configs:
        success_count = group["reached_95"].sum()
        s95 = success_count / 20.0
        avg_t95 = group["T95"].mean()
        
        summary_rows.append({
            "initialization": init,
            "depth": depth,
            "objective": obj,
            "S95": s95,
            "avg_T95": avg_t95
        })
        print(f"  {init} | d={depth} | {obj}: S95 = {s95:.2f} ({success_count}/20), Avg T95 = {avg_t95:.1f}")

    summary_df = pd.DataFrame(summary_rows)
    summary_df.to_csv("summary_table.csv", index=False)
    print("\nSaved summary_table.csv")

if __name__ == "__main__":
    main()
