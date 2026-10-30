"""
Hybrid Quantum-Classical Portfolio Optimization Framework
=========================================================
Studies the impact of initialization (Hadamard vs |0⟩) and ansatz depth
on convergence behavior and solution quality in variational quantum
portfolio optimization under Expectation and CVaR objectives.
"""

import time
import warnings
import itertools

import numpy as np
import pandas as pd
import yfinance as yf
from scipy.optimize import minimize
from scipy.stats import wilcoxon
import matplotlib.pyplot as plt
import seaborn as sns

from qiskit import QuantumCircuit
from qiskit_aer import AerSimulator

warnings.filterwarnings("ignore")

# PART 1 — DATA + COST FUNCTION

TICKERS = ["AAPL", "MSFT", "GOOG", "AMZN", "META", "NVDA", "TSLA"]
NUM_ASSETS = len(TICKERS)
RISK_FACTOR = 0.5  # q


def fetch_market_data(tickers: list[str],
                      period: str = "2y") -> tuple[np.ndarray, np.ndarray]:
    #Download historical data and compute annualized mu and Sigma.
    print(f"[DATA] Downloading {tickers} — period={period} ...")
    df = yf.download(tickers, period=period, auto_adjust=True)["Close"]
    daily_returns = df.pct_change().dropna()

    mu = daily_returns.mean().values * 252          # annualized mean
    sigma = daily_returns.cov().values * 252         # annualized covariance
    print(f"[DATA] mu   = {np.round(mu, 4)}")
    print(f"[DATA] Σ shape = {sigma.shape}")
    return mu, sigma


def portfolio_cost(weights: np.ndarray,
                   mu: np.ndarray,
                   sigma: np.ndarray,
                   q: float = RISK_FACTOR) -> float:
    return q * weights @ sigma @ weights - (1 - q) * mu @ weights


# PART 2 — QUANTUM CIRCUIT

def create_circuit(theta: np.ndarray,
                   use_hadamard: bool = False,
                   depth: int = 1) -> QuantumCircuit:
    """
    Parametrised ansatz circuit.

    Parameters
    ----------
    theta : array of shape (depth * NUM_ASSETS,)
    use_hadamard : prepend H gates on every qubit
    depth : number of RY + CX layers
    """
    n = NUM_ASSETS
    qc = QuantumCircuit(n)

    # Optional Hadamard initialisation
    if use_hadamard:
        for i in range(n):
            qc.h(i)

    # Variational layers
    idx = 0 # optimizer used: COBYLA
    for _ in range(depth):
        # RY rotation layer
        for i in range(n):
            qc.ry(theta[idx], i)
            idx += 1
        # Linear‐chain CX entanglement
        for i in range(n - 1):
            qc.cx(i, i + 1) #cx => CNOT entanglement, it couples qubits

    qc.measure_all()
    return qc


def num_parameters(depth: int = 1) -> int:
    return depth * NUM_ASSETS


# PART 3 — SAMPLING + MAPPING

BACKEND = AerSimulator() #to run circuits on classical systems
NUM_SHOTS = 1024 #times to run the circuit

#theta is the array of rotation angles (5 or 15 depending on the depth)
def sample_circuit(theta: np.ndarray,
                   use_hadamard: bool = False,
                   depth: int = 1) -> list[tuple[np.ndarray, float]]:
    """
    Run the circuit, map bitstrings -> portfolio weights, return
    list of (weight_vector, probability) tuples.
    """
    qc = create_circuit(theta, use_hadamard=use_hadamard, depth=depth)
    job = BACKEND.run(qc, shots=NUM_SHOTS)
    counts = job.result().get_counts()

    samples = []
    for bitstring, count in counts.items():
        bits = np.array([int(b) for b in bitstring[::-1]], dtype=float)
        s = bits.sum()
        if s > 0:
            weights = bits / s
        else:
            weights = np.ones(NUM_ASSETS) / NUM_ASSETS
        prob = count / NUM_SHOTS
        samples.append((weights, prob))
    return samples


# PART 4 — OBJECTIVES (Expectation & CVaR)

ALPHA_CVAR = 0.3
#higher alpha = more risk sensitive optimization.

def expectation_objective(theta: np.ndarray,
                          mu: np.ndarray,
                          sigma: np.ndarray,
                          use_hadamard: bool = False,
                          depth: int = 1) -> float:
    #E[cost] = Σ_i  p_i * cost(x_i)
    samples = sample_circuit(theta, use_hadamard=use_hadamard, depth=depth)
    return sum(
        prob * portfolio_cost(w, mu, sigma) for w, prob in samples
    )


def cvar_objective(theta: np.ndarray,
                   mu: np.ndarray,
                   sigma: np.ndarray,
                   use_hadamard: bool = False,
                   depth: int = 1,
                   alpha: float = ALPHA_CVAR) -> float:
    """
    Discrete version: sort by cost (descending/worst), accumulate
    the worst α‑fraction of probability mass, normalise.
    """
    samples = sample_circuit(theta, use_hadamard=use_hadamard, depth=depth)
    # Compute cost for each sample
    cost_prob = [
        (portfolio_cost(w, mu, sigma), prob) for w, prob in samples
    ]
    # Sort ASCENDING by cost (lower = better), so worst = highest cost last
    # CVaR picks the WORST tail → sort descending
    cost_prob.sort(key=lambda x: x[0], reverse=True)

    accumulated_prob = 0.0
    accumulated_cost = 0.0
    for cost_val, prob in cost_prob:
        if accumulated_prob >= alpha:
            break
        take = min(prob, alpha - accumulated_prob)
        accumulated_cost += take * cost_val
        accumulated_prob += take

    if accumulated_prob > 0:
        return accumulated_cost / accumulated_prob
    return 0.0


# PART 5 — OPTIMIZATION (COBYLA)

MAX_ITER = 200


def optimize_portfolio(mu: np.ndarray,
                       sigma: np.ndarray,
                       use_hadamard: bool,
                       depth: int,
                       objective_type: str,
                       seed: int) -> dict:
    """
    Single optimisation run.

    Returns dict with: init_theta, final_obj, best_cost, time_s, nfev
    """
    rng = np.random.RandomState(seed)
    n_params = num_parameters(depth)
    init_theta = rng.uniform(0, 2 * np.pi, size=n_params)

#COBYLA tries to minimize the objective function by iteratively sampling the circuit with different theta values, evaluating the objective, and updating theta based on the results. The optimization continues until it reaches the maximum number of iterations or converges to a solution.
    obj_fn = expectation_objective if objective_type == "Expectation" else cvar_objective

    nfev_counter = [0]
    history_obj = []

    def wrapped_obj(theta):
        nfev_counter[0] += 1
        val = obj_fn(theta, mu, sigma,
                      use_hadamard=use_hadamard, depth=depth)
        history_obj.append(val)
        return val

    t0 = time.time()
    result = minimize(wrapped_obj, init_theta,
                      method="COBYLA",
                      options={"maxiter": MAX_ITER, "rhobeg": 0.5})
    elapsed = time.time() - t0

    # Evaluate best sampled cost from final parameters
    final_samples = sample_circuit(result.x,
                                   use_hadamard=use_hadamard, depth=depth)
    best_cost = min(
        portfolio_cost(w, mu, sigma) for w, _ in final_samples
    )

    return {
        "init_theta": init_theta.tolist(),
        "final_obj": result.fun,
        "best_cost": best_cost,
        "time_s": round(elapsed, 3),
        "nfev": nfev_counter[0],
        "history": history_obj,
    }


# PART 6–9 — EXPERIMENTAL LOOP + DATA STORAGE

NUM_SEEDS = 20
DEPTH_OPTIONS = [1, 3]
HADAMARD_OPTIONS = [False, True]
OBJECTIVE_OPTIONS = ["Expectation", "CVaR"]


def run_experiments(mu: np.ndarray, sigma: np.ndarray) -> pd.DataFrame:
    configs = list(itertools.product(
        HADAMARD_OPTIONS, DEPTH_OPTIONS, OBJECTIVE_OPTIONS
    ))
    total = len(configs) * NUM_SEEDS
    print(f"\n{'='*70}")
    print(f"  RUNNING {len(configs)} configurations × {NUM_SEEDS} seeds = "
          f"{total} total runs")
    print(f"{'='*70}\n")

    rows = []
    run_idx = 0
    for use_h, depth, obj_type in configs:
        init_label = "Hadamard" if use_h else "|0⟩"
        config_tag = f"Init={init_label}  Depth={depth}  Obj={obj_type}"
        print(f"[CONFIG] {config_tag}")

        for seed in range(NUM_SEEDS):
            run_idx += 1
            print(f"  Run {run_idx}/{total}  (seed={seed}) ... ", end="",
                  flush=True)
            res = optimize_portfolio(mu, sigma, use_h, depth, obj_type, seed)
            print(f"obj={res['final_obj']:.6f}  best_cost={res['best_cost']:.6f}  "
                  f"t={res['time_s']}s  nfev={res['nfev']}")

            rows.append({
                "initialization": init_label,
                "depth": depth,
                "objective": obj_type,
                "seed": seed,
                **res,
            })

    return pd.DataFrame(rows)


# PART 10 — ANALYSIS + STATISTICAL TESTS

def compute_summary(df: pd.DataFrame) -> pd.DataFrame:
    """Aggregate metrics per configuration."""
    grouped = df.groupby(["initialization", "depth", "objective"])
    summary = grouped.agg(
        mean_best_cost=("best_cost", "mean"),
        std_best_cost=("best_cost", "std"),
        min_best_cost=("best_cost", "min"),
        mean_final_obj=("final_obj", "mean"),
        std_final_obj=("final_obj", "std"),
        mean_time_s=("time_s", "mean"),
        mean_nfev=("nfev", "mean"),
    ).reset_index()
    return summary


def run_statistical_tests(df: pd.DataFrame) -> list[dict]:
    """Wilcoxon signed rank tests for paired comparisons."""
    results = []

    def _wilcox(group_a: pd.DataFrame, group_b: pd.DataFrame,
                label: str, metric: str = "best_cost"):
        a = group_a.sort_values("seed")[metric].values
        b = group_b.sort_values("seed")[metric].values
        if len(a) != len(b) or len(a) < 5:
            return
        try:
            stat, p = wilcoxon(a, b)
        except ValueError:
            stat, p = float("nan"), float("nan")
        results.append({
            "comparison": label,
            "metric": metric,
            "statistic": round(stat, 4),
            "p_value": round(p, 6),
            "significant_005": p < 0.05,
        })

    # 1) Hadamard vs |0⟩  — for each (depth, objective) combo
    for depth, obj in itertools.product(DEPTH_OPTIONS, OBJECTIVE_OPTIONS):
        a = df[(df["initialization"] == "|0⟩") &
               (df["depth"] == depth) &
               (df["objective"] == obj)]
        b = df[(df["initialization"] == "Hadamard") &
               (df["depth"] == depth) &
               (df["objective"] == obj)]
        _wilcox(a, b,
                f"|0⟩ vs Hadamard (depth={depth}, obj={obj})")

    # 2) Depth 1 vs Depth 3 — for each (init, objective) combo
    for init, obj in itertools.product(["Hadamard", "|0⟩"], OBJECTIVE_OPTIONS):
        a = df[(df["initialization"] == init) &
               (df["depth"] == 1) &
               (df["objective"] == obj)]
        b = df[(df["initialization"] == init) &
               (df["depth"] == 3) &
               (df["objective"] == obj)]
        _wilcox(a, b,
                f"Depth1 vs Depth3 (init={init}, obj={obj})")

    # 3) Expectation vs CVaR — for each (init, depth) combo
    for init, depth in itertools.product(["Hadamard", "|0⟩"], DEPTH_OPTIONS):
        a = df[(df["initialization"] == init) &
               (df["depth"] == depth) &
               (df["objective"] == "Expectation")]
        b = df[(df["initialization"] == init) &
               (df["depth"] == depth) &
               (df["objective"] == "CVaR")]
        _wilcox(a, b,
                f"Expectation vs CVaR (init={init}, depth={depth})")

    return results


# PART 11 — OUTPUT + MAIN

def pretty_print_summary(summary: pd.DataFrame):
    print(f"\n{'='*80}")
    print("  SUMMARY TABLE — Per Configuration Aggregates")
    print(f"{'='*80}")
    pd.set_option("display.max_columns", None)
    pd.set_option("display.width", 200)
    print(summary.to_string(index=False))


def pretty_print_tests(test_results: list[dict]):
    print(f"\n{'='*80}")
    print("  STATISTICAL TESTS — Wilcoxon Signed‑Rank")
    print(f"{'='*80}")
    tdf = pd.DataFrame(test_results)
    print(tdf.to_string(index=False))


def plot_results(df: pd.DataFrame):
    print("\n[PLOT] Generating boxplot and convergence plot...")
    # Boxplot
    plt.figure(figsize=(12, 8))
    df['Config'] = df['initialization'] + " | d=" + df['depth'].astype(str) + " | " + df['objective']
    sns.boxplot(data=df, x='best_cost', y='Config')
    plt.title(f"Best Cost Distribution by Configuration ({NUM_SEEDS} Seeds, {NUM_ASSETS} Assets)")
    plt.tight_layout()
    plt.savefig("boxplot.png")
    plt.close()

    # Convergence Plot
    plt.figure(figsize=(12, 8))
    configs = df.groupby(["initialization", "depth", "objective"])
    
    for name, group in configs:
        histories = group['history'].tolist()
        cum_mins = []
        for h in histories:
            cum_min = np.minimum.accumulate(h)
            cum_mins.append(cum_min)
        
        max_len = max(len(h) for h in cum_mins)
        padded = np.array([np.pad(h, (0, max_len - len(h)), 'edge') for h in cum_mins])
        
        mean_convergence = padded.mean(axis=0)
        label = f"{name[0]}, d={name[1]}, {name[2]}"
        plt.plot(mean_convergence, label=label)
        
    plt.title(f"Average Convergence (Cumulative Minimum Objective)")
    plt.xlabel("Function Evaluations")
    plt.ylabel("Objective Value")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.savefig("convergence.png")
    plt.close()
    print("[PLOT] Saved boxplot.png and convergence.png")

def main():
    # Data 
    mu, sigma = fetch_market_data(TICKERS)

    #  Experiments
    df = run_experiments(mu, sigma)

    #  Save full results 
    full_csv = "full_results.csv"
    df.to_csv(full_csv, index=False)
    print(f"\n[SAVE] Full results → {full_csv}")

    #  Summary 
    summary = compute_summary(df)
    summary_csv = "summary_statistics.csv"
    summary.to_csv(summary_csv, index=False)
    print(f"[SAVE] Summary      → {summary_csv}")
    pretty_print_summary(summary)

    #  Statistical tests 
    test_results = run_statistical_tests(df)
    pretty_print_tests(test_results)

    # Plot results
    plot_results(df)

    print(f"\n{'='*80}")
    print("  DONE — All experiments complete.")
    print(f"{'='*80}\n")


if __name__ == "__main__":
    main()
