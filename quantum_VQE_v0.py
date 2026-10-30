import numpy as np
from qiskit import QuantumCircuit
from qiskit.primitives import StatevectorSampler as Sampler
from scipy.optimize import minimize

#more of a subset selection. 000 -> no assets to be chosen, 011 -> assets 1 and 2 and so on.
#No portfolio weights, just whether to include an asset or not.

# 1. DATA
# -------------------------------

mu = np.array([0.1, 0.12, 0.08])

Sigma = np.array([
    [0.005, -0.010, 0.004],
    [-0.010, 0.040, -0.002],
    [0.004, -0.002, 0.023]
])

q = 0.5
n_qubits = len(mu)

# 2. COST FUNCTION

def portfolio_cost(x):
    x = np.array(x)
    return q * x @ Sigma @ x - (1 - q) * mu @ x

# -------------------------------
# 3. CIRCUIT
# -------------------------------

def create_circuit(theta):
    qc = QuantumCircuit(n_qubits)
    
    for i in range(n_qubits):
        qc.ry(theta[i], i)
    
    for i in range(n_qubits - 1):
        qc.cx(i, i+1)
    
    return qc

# -------------------------------
# 4. SAMPLING
# -------------------------------

sampler = Sampler()

def sample(theta):
    qc = create_circuit(theta)
    qc.measure_all()

    result = sampler.run([qc]).result()
    counts = result[0].data.meas.get_counts()

    total = sum(counts.values())
    
    samples = []
    
    for bitstring, count in counts.items():
        prob = count / total
        
        # Convert bitstring → portfolio vector
        x = np.array([int(b) for b in bitstring[::-1]])
        
        cost = portfolio_cost(x)
        
        samples.append((cost, prob))
    
    return samples

# -------------------------------
# 5. EXPECTATION
# -------------------------------

def compute_expectation(samples):
    return sum(cost * prob for cost, prob in samples)

# -------------------------------
# 6. CVaR
# -------------------------------

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

# -------------------------------
# 7. OBJECTIVES
# -------------------------------

def objective_expectation(theta):
    samples = sample(theta)
    return compute_expectation(samples)

def objective_cvar(theta):
    samples = sample(theta)
    return compute_cvar(samples, alpha=0.3)

# -------------------------------
# 8. OPTIMIZATION
# -------------------------------

theta0 = np.random.rand(n_qubits)

print("Running Expectation Optimization...")
res_exp = minimize(objective_expectation, theta0, method='COBYLA')

print("\nRunning CVaR Optimization...")
res_cvar = minimize(objective_cvar, theta0, method='COBYLA')

# -------------------------------
# 9. RESULTS
# -------------------------------

def get_best_portfolio(theta):
    samples = sample(theta)
    return min(samples, key=lambda x: x[0])

best_exp = get_best_portfolio(res_exp.x)
best_cvar = get_best_portfolio(res_cvar.x)

print("\n========== RESULTS ==========")
print("Expectation Best Portfolio:", best_exp)
print("CVaR Best Portfolio:", best_cvar)

print("\nOptimal Parameters (Expectation):", res_exp.x)
print("Optimal Parameters (CVaR):", res_cvar.x)