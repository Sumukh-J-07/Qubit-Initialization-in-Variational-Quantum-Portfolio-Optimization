import ast
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

def main():
    print("Loading data...")
    try:
        df_results = pd.read_csv("results.csv")
        df_metrics = pd.read_csv("convergence_metrics.csv")
    except FileNotFoundError:
        print("Required CSV files not found. Run expanded_experiment.py and convergence_analysis.py first.")
        return

    # Create config column for labeling
    df_results['Config'] = df_results['initialization'] + " | d=" + df_results['depth'].astype(str) + " | " + df_results['objective']
    df_metrics['Config'] = df_metrics['initialization'] + " | d=" + df_metrics['depth'].astype(str) + " | " + df_metrics['objective']

    print("Generating boxplots...")
    plt.figure(figsize=(14, 10))
    sns.boxplot(data=df_results, x='approximation_ratio', y='Config')
    plt.title("Approximation Ratio Distribution by Configuration (n=12)")
    plt.xlabel("Approximation Ratio (r = C_best / C*)")
    plt.axvline(x=1.0, color='r', linestyle='--', alpha=0.5, label='Global Optimum (r=1)')
    plt.axvline(x=0.95, color='orange', linestyle=':', alpha=0.8, label='Target (r=0.95)')
    plt.legend()
    plt.tight_layout()
    plt.savefig("boxplots.png", dpi=300)
    plt.close()

    print("Generating convergence curves...")
    plt.figure(figsize=(12, 8))
    configs = df_results.groupby(["initialization", "depth", "objective"])
    
    for name, group in configs:
        histories = [ast.literal_eval(h) for h in group['best_cost_history']]
        
        # Determine C_star for this group (it's the same for all, but we can compute it for the first run)
        first_row = group.iloc[0]
        c_star = first_row["final_cost"] / first_row["approximation_ratio"] if first_row["approximation_ratio"] != 0 else -1
        
        max_len = max(len(h) for h in histories)
        padded = np.array([np.pad(h, (0, max_len - len(h)), 'edge') for h in histories])
        
        # Convert costs to approximation ratios for a normalized convergence plot
        mean_convergence = padded.mean(axis=0) / c_star
        
        label = f"{name[0]}, d={name[1]}, {name[2]}"
        plt.plot(mean_convergence, label=label)

    plt.axhline(y=1.0, color='r', linestyle='--', alpha=0.5, label='Global Optimum (r=1)')
    plt.axhline(y=0.95, color='orange', linestyle=':', alpha=0.8, label='Target (r=0.95)')
    plt.title("Average Convergence (Approximation Ratio r_k)")
    plt.xlabel("Function Evaluations")
    plt.ylabel("Approximation Ratio (r_k)")
    plt.ylim(0, 1.05)
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.grid(True)
    plt.tight_layout()
    plt.savefig("convergence_curves.png", dpi=300)
    plt.close()

    print("Generating T95 vs depth...")
    plt.figure(figsize=(10, 6))
    sns.lineplot(data=df_metrics, x="depth", y="T95", hue="initialization", style="objective", markers=True, errorbar=None)
    plt.title("Average Iterations to Reach 95% Optimality (T95) vs Depth")
    plt.xlabel("Circuit Depth")
    plt.ylabel("Iterations (T95)")
    plt.xticks([1, 2, 3, 4])
    plt.grid(True)
    plt.tight_layout()
    plt.savefig("t95_vs_depth.png", dpi=300)
    plt.close()

    print("Generating Success Rate vs depth...")
    # Calculate Success Rate S95 for each group
    s95_df = df_metrics.groupby(["depth", "initialization", "objective"])["reached_95"].mean().reset_index()
    s95_df.rename(columns={"reached_95": "S95"}, inplace=True)

    plt.figure(figsize=(10, 6))
    sns.barplot(data=s95_df, x="depth", y="S95", hue="initialization", errorbar=None)
    plt.title("Success Rate (S95) vs Depth")
    plt.xlabel("Circuit Depth")
    plt.ylabel("Success Rate (S95)")
    plt.ylim(0, 1.05)
    plt.axhline(y=1.0, color='r', linestyle='--', alpha=0.5)
    
    # Differentiate by objective (since barplot with 2 hue dimensions is tricky, we use catplot)
    plt.tight_layout()
    plt.savefig("success_rate_vs_depth_simple.png", dpi=300)
    plt.close()
    
    # Better plot for S95 using catplot to show both initialization and objective
    g = sns.catplot(data=s95_df, kind="bar", x="depth", y="S95", hue="initialization", col="objective", height=5, aspect=1.2)
    g.fig.suptitle("Success Rate (S95) vs Depth by Objective", y=1.05)
    for ax in g.axes.flat:
        ax.axhline(1.0, color='r', linestyle='--', alpha=0.5)
        ax.set_ylim(0, 1.05)
    plt.savefig("success_rate_vs_depth.png", dpi=300)
    plt.close()

    print("Done! Saved boxplots.png, convergence_curves.png, t95_vs_depth.png, and success_rate_vs_depth.png")

if __name__ == "__main__":
    main()
