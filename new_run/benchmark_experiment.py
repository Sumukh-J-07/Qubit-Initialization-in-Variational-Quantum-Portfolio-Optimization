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

TICKERS = ["AAPL", "MSFT", "GOOG", "AMZN", "META", "NVDA", "TSLA", "JPM", "JNJ", "V", "PG", "UNH"]
NUM_ASSETS = len(TICKERS)
RISK_FACTOR = 0.5  # q

def fetch_market_data(tickers: list[str], period: str = "2y") -> tuple[np.ndarray, np.ndarray]:
    df = yf.download(tickers, period=period, auto_adjust=True)["Close"]
    daily_returns = df.pct_change().dropna()
    mu = daily_returns.mean().values * 252
    sigma = daily_returns.cov().values * 252
    return mu, sigma

def portfolio_cost(weights: np.ndarray, mu: np.ndarray, sigma: np.ndarray, q: float = RISK_FACTOR) -> float:
    return q * weights @ sigma @ weights - (1 - q) * mu @ weights

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

def expectation_objective(theta: np.ndarray, mu: np.ndarray, sigma: np.ndarray, use_hadamard: bool = False, depth: int = 1) -> float:
    samples = sample_circuit(theta, use_hadamard=use_hadamard, depth=depth)
    return sum(prob * portfolio_cost(w, mu, sigma) for w, prob in samples)

MAX_ITER = 200

def optimize_portfolio(mu: np.ndarray, sigma: np.ndarray, use_hadamard: bool, depth: int, objective_type: str, seed: int) -> dict:
    rng = np.random.RandomState(seed)
    n_params = num_parameters(depth)
    init_theta = rng.uniform(0, 2 * np.pi, size=n_params)

    nfev_counter = [0]
    
    def wrapped_obj(theta):
        nfev_counter[0] += 1
        return expectation_objective(theta, mu, sigma, use_hadamard=use_hadamard, depth=depth)

    t0 = time.time()
    result = minimize(wrapped_obj, init_theta, method="COBYLA", options={"maxiter": MAX_ITER, "rhobeg": 0.5})
    elapsed = time.time() - t0

    return {
        "time_s": elapsed,
        "nfev": nfev_counter[0],
    }

def main():
    mu, sigma = fetch_market_data(TICKERS)
    print("Running benchmark: n=12, depth=4, Hadamard, Expectation, seeds=2")
    
    total_time = 0
    for seed in range(2):
        print(f"Seed {seed} starting...")
        res = optimize_portfolio(mu, sigma, True, 4, "Expectation", seed)
        print(f"Seed {seed} finished in {res['time_s']:.2f} seconds (nfev={res['nfev']})")
        total_time += res['time_s']
        
    avg_time = total_time / 2
    print(f"Average time per run: {avg_time:.2f} seconds")
    print(f"Estimated time for 320 runs: {(avg_time * 320) / 3600:.2f} hours")

if __name__ == "__main__":
    main()
