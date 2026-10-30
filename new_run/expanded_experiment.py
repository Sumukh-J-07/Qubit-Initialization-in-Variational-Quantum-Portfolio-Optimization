import time
import warnings
import itertools

import numpy as np
import pandas as pd
import yfinance as yf
from scipy.optimize import minimize

from qiskit import QuantumCircuit
from qiskit_aer import AerSimulator

warnings.filterwarnings("ignore")

# PART 1 — DATA + COST FUNCTION

TICKERS = ["AAPL", "MSFT", "GOOG", "AMZN", "META", "NVDA", "TSLA", "JPM", "JNJ", "V", "PG", "UNH"]
NUM_ASSETS = len(TICKERS)
RISK_FACTOR = 0.5  # q

def fetch_market_data(tickers: list[str], period: str = "2y") -> tuple[np.ndarray, np.ndarray]:
    print(f"[DATA] Downloading {tickers} — period={period} ...")
    df = yf.download(tickers, period=period, auto_adjust=True)["Close"]
    daily_returns = df.pct_change().dropna()

    mu = daily_returns.mean().values * 252
    sigma = daily_returns.cov().values * 252
    print(f"[DATA] mu   = {np.round(mu, 4)}")
    print(f"[DATA] Σ shape = {sigma.shape}")
    return mu, sigma

def portfolio_cost(weights: np.ndarray, mu: np.ndarray, sigma: np.ndarray, q: float = RISK_FACTOR) -> float:
    return q * weights @ sigma @ weights - (1 - q) * mu @ weights

# PART 2 — QUANTUM CIRCUIT

def create_circuit(theta: np.ndarray, use_hadamard: bool = False, depth: int = 1) -> QuantumCircuit:
    n = NUM_ASSETS
    qc = QuantumCircuit(n)

    if use_hadamard:
        for i in range(n):
            qc.h(i)

    idx = 0
    for _ in range(depth):
        for i in range(n):
            qc.ry(theta[idx], i)
            idx += 1
        for i in range(n - 1):
            qc.cx(i, i + 1)

    qc.measure_all()
    return qc

def num_parameters(depth: int = 1) -> int:
    return depth * NUM_ASSETS

# PART 3 — SAMPLING + MAPPING

BACKEND = AerSimulator()
NUM_SHOTS = 1024

def sample_circuit(theta: np.ndarray, use_hadamard: bool = False, depth: int = 1) -> list[tuple[np.ndarray, float]]:
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

def expectation_objective(samples: list, mu: np.ndarray, sigma: np.ndarray) -> float:
    return sum(prob * portfolio_cost(w, mu, sigma) for w, prob in samples)

def cvar_objective(samples: list, mu: np.ndarray, sigma: np.ndarray, alpha: float = ALPHA_CVAR) -> float:
    cost_prob = [(portfolio_cost(w, mu, sigma), prob) for w, prob in samples]
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

def optimize_portfolio(mu: np.ndarray, sigma: np.ndarray, use_hadamard: bool, depth: int, objective_type: str, seed: int, C_star: float) -> dict:
    rng = np.random.RandomState(seed)
    n_params = num_parameters(depth)
    init_theta = rng.uniform(0, 2 * np.pi, size=n_params)

    nfev_counter = [0]
    history_obj = []
    best_cost_history = []
    
    current_best_cost = float('inf')

    def wrapped_obj(theta):
        nfev_counter[0] += 1
        
        samples = sample_circuit(theta, use_hadamard=use_hadamard, depth=depth)
        
        if objective_type == "Expectation":
            val = expectation_objective(samples, mu, sigma)
        else:
            val = cvar_objective(samples, mu, sigma, alpha=ALPHA_CVAR)
            
        history_obj.append(val)
        
        # Calculate true minimum cost in this evaluation
        min_cost = min(portfolio_cost(w, mu, sigma) for w, _ in samples)
        
        nonlocal current_best_cost
        if min_cost < current_best_cost:
            current_best_cost = min_cost
            
        best_cost_history.append(current_best_cost)
        return val

    t0 = time.time()
    result = minimize(wrapped_obj, init_theta, method="COBYLA", options={"maxiter": MAX_ITER, "rhobeg": 0.5})
    elapsed = time.time() - t0

    final_samples = sample_circuit(result.x, use_hadamard=use_hadamard, depth=depth)
    best_cost = min(portfolio_cost(w, mu, sigma) for w, _ in final_samples)
    
    approximation_ratio = best_cost / C_star

    return {
        "final_cost": best_cost,
        "runtime": round(elapsed, 3),
        "nfev": nfev_counter[0],
        "cost_history": history_obj,
        "best_cost_history": best_cost_history,
        "approximation_ratio": approximation_ratio
    }

# EXHAUSTIVE ENUMERATION

def compute_classical_optimum(mu: np.ndarray, sigma: np.ndarray) -> float:
    print(f"\n[EXHAUSTIVE] Enumerating 2^{NUM_ASSETS}-1 portfolios...")
    t0 = time.time()
    min_cost = float('inf')
    num_portfolios = 2**NUM_ASSETS
    
    for i in range(1, num_portfolios):
        binary = bin(i)[2:].zfill(NUM_ASSETS)
        bits = np.array([int(b) for b in binary], dtype=float)
        weights = bits / bits.sum()
        cost = portfolio_cost(weights, mu, sigma)
        if cost < min_cost:
            min_cost = cost
            
    elapsed = time.time() - t0
    print(f"[EXHAUSTIVE] C* = {min_cost:.6f} found in {elapsed:.3f}s\n")
    return min_cost

# PART 6–9 — EXPERIMENTAL LOOP + DATA STORAGE

NUM_SEEDS = 20
DEPTH_OPTIONS = [1, 2, 3, 4]
HADAMARD_OPTIONS = [False, True]
OBJECTIVE_OPTIONS = ["Expectation", "CVaR"]

def run_experiments(mu: np.ndarray, sigma: np.ndarray, C_star: float) -> pd.DataFrame:
    configs = list(itertools.product(HADAMARD_OPTIONS, DEPTH_OPTIONS, OBJECTIVE_OPTIONS))
    total = len(configs) * NUM_SEEDS
    print(f"\n{'='*70}")
    print(f"  RUNNING {len(configs)} configurations × {NUM_SEEDS} seeds = {total} total runs")
    print(f"{'='*70}\n")

    rows = []
    run_idx = 0
    for use_h, depth, obj_type in configs:
        init_label = "Hadamard" if use_h else "|0⟩"
        config_tag = f"Init={init_label}  Depth={depth}  Obj={obj_type}"
        print(f"[CONFIG] {config_tag}")

        for seed in range(NUM_SEEDS):
            run_idx += 1
            print(f"  Run {run_idx}/{total}  (seed={seed}) ... ", end="", flush=True)
            res = optimize_portfolio(mu, sigma, use_h, depth, obj_type, seed, C_star)
            print(f"best_cost={res['final_cost']:.6f}  r={res['approximation_ratio']:.4f}  t={res['runtime']}s  nfev={res['nfev']}")

            rows.append({
                "seed": seed,
                "depth": depth,
                "objective": obj_type,
                "initialization": init_label,
                "runtime": res["runtime"],
                "nfev": res["nfev"],
                "cost_history": str(res["cost_history"]),
                "best_cost_history": str(res["best_cost_history"]),
                "final_cost": res["final_cost"],
                "approximation_ratio": res["approximation_ratio"]
            })

    return pd.DataFrame(rows)

def main():
    mu, sigma = fetch_market_data(TICKERS)
    C_star = compute_classical_optimum(mu, sigma)

    df = run_experiments(mu, sigma, C_star)
    
    full_csv = "results.csv"
    df.to_csv(full_csv, index=False)
    print(f"\n[SAVE] Full results → {full_csv}")

if __name__ == "__main__":
    main()
