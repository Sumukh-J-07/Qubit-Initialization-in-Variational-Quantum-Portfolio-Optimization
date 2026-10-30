import ast
import pandas as pd

df = pd.read_csv("new_run/results.csv")
table3 = pd.read_csv("new_run/summary_table.csv")

def compute_t95(best_cost_history, c_star):
    for i, cost in enumerate(best_cost_history):
        if cost / c_star >= 0.95:
            return i + 1
    return -1 # -1 means failed

data = []
for _, row in df.iterrows():
    c_star = row["final_cost"] / row["approximation_ratio"] if row["approximation_ratio"] != 0 else -1.0
    history = ast.literal_eval(row["best_cost_history"])
    t95 = compute_t95(history, c_star)
    data.append({
        "init": row["initialization"],
        "depth": row["depth"],
        "obj": row["objective"],
        "seed": row["seed"],
        "t95_actual": t95,
        "reached_95": t95 != -1
    })

audit_df = pd.DataFrame(data)

print(f"{'Init':<10} | {'d':<1} | {'Obj':<11} | {'Succ/20':<7} | {'S95':<4} | {'MeanT95(Succ)':<13} | {'MeanT95(Fail=200)':<17} | {'Table3 T95':<10}")
print("-" * 105)

for (init, d, obj), group in audit_df.groupby(["init", "depth", "obj"]):
    succ_count = group["reached_95"].sum()
    s95 = succ_count / 20.0
    
    succ_t95_vals = group[group["reached_95"]]["t95_actual"]
    mean_succ = succ_t95_vals.mean() if succ_count > 0 else float('nan')
    
    t95_with_200 = group["t95_actual"].replace(-1, 200)
    mean_200 = t95_with_200.mean()
    
    # lookup Table 3 value
    t3_val = table3[(table3["initialization"] == init) & 
                    (table3["depth"] == d) & 
                    (table3["objective"] == obj)]["avg_T95"].values[0]
                    
    print(f"{init:<10} | {d} | {obj:<11} | {succ_count:>2}/20   | {s95:.2f} | {mean_succ:>13.2f} | {mean_200:>17.2f} | {t3_val:>10.2f}")

