import re

with open("springer.tex", "r") as f:
    text = f.read()

# 1. Abstract
text = text.replace(
    "Selecting asset allocations that jointly optimize return and control downside risk remains a central challenge in computational finance. Classical approaches struggle with the combinatorial complexity of binary asset selection as the asset universe grows. In this work, a hybrid quantum-classical variational circuit is proposed to address portfolio optimization across five NASDAQ-listed assets. Qubit initialization strategy is a critical yet underexplored design choice in variational quantum algorithms that is systematically investigated by comparing Hadamard initialization against computational zero state initialization. Experiments are conducted under 2 objective functions, Expectation value and Conditional Value-at-risk, at circuit depths of 1 and 3, across 10 independent random seeds using the Qiskit Aer simulator \cite{qiskit}. Results demonstrate that Hadamard initialization achieves lower mean portfolio cost and greater consistency at shallow circuit depth, while this advantage diminishes at greater depth and reverses under the Conditional Value-at-Risk objective. Statistical significance is assessed using the Wilcoxon signed-rank test.",
    "Selecting asset allocations that jointly optimize return and control downside risk remains a central challenge in computational finance. Classical approaches struggle with the combinatorial complexity of binary asset selection as the asset universe grows. In this work, a hybrid quantum-classical variational circuit is proposed to address portfolio optimization across seven NASDAQ-listed assets. Qubit initialization strategy is a critical yet underexplored design choice in variational quantum algorithms that is systematically investigated by comparing Hadamard initialization against computational zero state initialization. Experiments are conducted under 2 objective functions, Expectation value and Conditional Value-at-risk, at circuit depths of 1 and 3, across 20 independent random seeds using the Qiskit Aer simulator \cite{qiskit}. Results demonstrate that Hadamard initialization achieves slightly lower mean portfolio cost and greater consistency at shallow circuit depth, while this advantage diminishes at greater depth. Circuit depth exerts a strongly significant effect on solution quality across all configurations, dwarfing the impact of initial state selection. Statistical significance is assessed using the Wilcoxon signed-rank test."
)

# 2. Introduction
text = text.replace(
    "In this work, we investigate the impact of qubit initialization strategy on variational quantum portfolio optimization across five NASDAQ-listed assets: AAPL, MSFT, GOOG, AMZN and META. We compare Hadamard and $|0\\rangle$ initialization under two objective functions - Expectation and Conditional Value-at-Risk (CVaR) \cite{rockafellar2000} at circuit depths of 1 and 3, across 10 independent random seeds.",
    "In this work, we investigate the impact of qubit initialization strategy on variational quantum portfolio optimization across seven NASDAQ-listed assets: AAPL, MSFT, GOOG, AMZN, META, NVDA, and TSLA. We compare Hadamard and $|0\\rangle$ initialization under two objective functions - Expectation and Conditional Value-at-Risk (CVaR) \cite{rockafellar2000} at circuit depths of 1 and 3, across 20 independent random seeds."
)

# 3. Methodology 4.1
text = text.replace(
    "The portfolio optimization problem is formulated as a combinatorial asset selection task over $n = 5$ NASDAQ-listed equities: AAPL, MSFT, GOOG, AMZN and META.",
    "The portfolio optimization problem is formulated as a combinatorial asset selection task over $n = 7$ NASDAQ-listed equities: AAPL, MSFT, GOOG, AMZN, META, NVDA, and TSLA."
)

text = text.replace(
    "evaluation of all $2^n -1 = 31$ non-empty portfolios",
    "evaluation of all $2^n -1 = 127$ non-empty portfolios"
)

text = text.replace(
    "The small asset universe ($n = 5$) is a deliberate experimental choice. With only 31 non-empty binary portfolios",
    "The small asset universe ($n = 7$) is a deliberate experimental choice. With only 127 non-empty binary portfolios"
)

# 4. Methodology 4.2
text = text.replace(
    "A parameterized ansatz is constructed over $n = 5$ qubits",
    "A parameterized ansatz is constructed over $n = 7$ qubits"
)

# 5. Methodology 4.5
text = text.replace(
    "Each of the 10 seeds produces a distinct initial parameter vector $\\boldsymbol{\\theta}_0$, ensuring that performance statistics reflect the distribution of outcomes across the initialization landscape rather than a single favorable or unfavorable starting point.\n\nThe full factorial design crosses 2 initialization strategies $\\times$ 2 depths ($d \\in \\{1,3\\}$) $\\times$ 2 objectives, yielding 8 configurations each repeated across 10 independent seeds, totaling 80 runs.",
    "Each of the 20 seeds produces a distinct initial parameter vector $\\boldsymbol{\\theta}_0$, ensuring that performance statistics reflect the distribution of outcomes across the initialization landscape rather than a single favorable or unfavorable starting point.\n\nThe full factorial design crosses 2 initialization strategies $\\times$ 2 depths ($d \\in \\{1,3\\}$) $\\times$ 2 objectives, yielding 8 configurations each repeated across 20 independent seeds, totaling 160 runs."
)


# Section 5 and 6 block replace
old_block = r"""All 80 optimization runs completed successfully across the eight configurations. The globally optimal portfolio cost, obtained by exhaustive evaluation of all $2^n -1 = 31$ non empty binary portfolios, was $\mathcal{C}^* = -0.14998$, serving as the classical reference benchmark. All eight configurations reached this optimum in at least one seed , confirming that both initialization strategies are capable of finding the optimal solution, but the key distinction lies in average-case performance and consistency.

\subsection{Summary of Results}

Table~\ref{tab:summary} reports per configuration aggregate statistics across 10 seeds, including the approximation ratio $r = \overline{\mathcal{C}}_{\text{best}} /\mathcal{C}^*$, where a value of $1.0$ indicates perfect average recovery of the global optimum.

\begin{table}[t]
\caption{Per configuration summary statistics across 10 seeds. $r$ denotes the approximation ratio relative to the classical optimum $\mathcal{C}^* = -0.14998$.}
\label{tab:summary}
\centering
\resizebox{\textwidth}{!}{%
\begin{tabular}{lllllllll}
\hline\textbf{Init} & \textbf{$d$} & \textbf{Obj} &
\textbf{Mean Cost} & \textbf{Std} &
\textbf{$r$} &
\textbf{Mean Obj} & \textbf{Time (s)} &
\textbf{NFEv} \\
\hline
$H$         & 1 & Exp  & $-0.1228$ & $0.0151$ & $0.819$ & $-0.1059$ & $0.076$ & $59.0$ \\
$H$         & 1 & CVaR & $-0.1126$ & $0.0208$ & $0.751$ & $-0.0592$ & $0.067$ & $53.4$ \\
$H$         & 3 & Exp  & $-0.1434$ & $0.0106$ & $0.956$ & $-0.1149$ & $0.237$ & $150.2$ \\
$H$         & 3 & CVaR & $-0.1320$ & $0.0181$ & $0.880$ & $-0.0666$ & $0.230$ & $142.9$ \\
$|0\rangle$ & 1 & Exp  & $-0.1221$ & $0.0191$ & $0.814$ & $-0.1163$ & $0.072$ & $60.5$ \\
$|0\rangle$ & 1 & CVaR & $-0.1084$ & $0.0271$ & $0.723$ & $-0.0492$ & $0.065$ & $54.5$ \\
$|0\rangle$ & 3 & Exp  & $-0.1388$ & $0.0161$ & $0.925$ & $-0.1219$ & $0.249$ & $162.6$ \\
$|0\rangle$ & 3 & CVaR & $-0.1385$ & $0.0166$ & $0.924$ & $-0.0573$ & $0.213$ & $134.9$ \\
\hline
\end{tabular}%
}
\end{table}

Two broad patterns emerge from Table~\ref{tab:summary}. First, CVaR mean objective values ($-0.049$ to $-0.067$) are systematically less negative than Expectation values ($-0.106$ to $-0.122$). This is expected: CVaR optimizes only the worst -$\alpha$ tail rather than the full distribution, so its objective reflects a narrower, higher-cost subset of outcomes. Despite this, CVaR produces competitive best cost and approximation ratio values, confirming that tail-focused optimization effectively steers the circuit toward favorable regions. Second, increasing depth consistently reduces both mean and variance of best cost regardless of initialization or objective.

\subsection{Effect of Initialization Strategy}

At circuit depth $d = 1$, Hadamard initialization achieves marginally better mean best cost than $|0\rangle$ under both objectives: $-0.1228$ versus $-0.1221$ for Expectation, and $-0.1126$ versus $-0.1084$ for CVaR. Hadamard also yield lower standard deviation ($0.0151$ vs.\ $0.0191$ for 
Expectation; $0.0208$ vs.\ $0.0271$ for CVaR) suggesting more consistent convergence at shallow depth. With only $d \times n = 5$ parameters, the circuit has limited ability to reshape the probability distribution independently of its initial state - making the uniform superposition of Hadamard a more favorable starting point.

At depth $d = 3$, the ranking shifts. Under Expectation, Hadamard retains a clear advantage ($r = 0.956$ vs.\ $0.925$). However, under CVaR, $|0\rangle$ surpasses Hadamard ($-0.1385$ vs.\ 
$-0.1320$; $r = 0.924$ vs.\ $0.880$) with lower variance ($0.0166$ vs.\ $0.0181$). With 15 parameters at depth 3, the ansatz has sufficient expressibility to overcome its initial bias and the structured starting point of $|0\rangle$ appears better suited to CVaR's tail-focused landscape at greater depth.

\subsection{Effect of Circuit Depth}

Increasing depth from $d = 1$ to $d = 3$ improves mean best cost across all four combinations, at the cost of $3.1$--$3.5\times$ longer runtime and $2.5$--$2.7\times$ more function evaluations. The largest gain occurs for $|0\rangle$-CVaR: mean 
best cost improves from $-0.1084$ to $-0.1385$ ($r$ from 
$72.3\%$ to $92.4\%$). For Hadamard-Expectation the 
gain is from $-0.1228$ to $-0.1434$ ($r$ from $81.9\%$ 
to $95.6\%$). A single layer provides only 5 rotation parameters and one entanglement round; tripling the depth to 15 parameters and three entanglement rounds substantially expands the expressible hypothesis space.

\subsection{Statistical significance}

Table~\ref{tab:wilcoxon} reports Wilcoxon signed-rank test results for all three comparison families, paired by seed.

\begin{table}[h!]
\caption{Wilcoxon signed-rank test results on best cost, 
paired by seed ($n = 10$). Significance threshold: 
$p < 0.05$.}
\label{tab:wilcoxon}
\centering
\resizebox{\textwidth}{!}{%
\begin{tabular}{llll}
\hline
\textbf{Comparison} & \textbf{$W$} & 
\textbf{$p$-value} & \textbf{Significant} \\
\hline
\multicolumn{4}{l}{\textit{Initialization: 
$|0\rangle$ vs.\ $H$}} \\
\quad $d=1$, Exp  & $6.5$  & $0.8750$ & No \\
\quad $d=1$, CVaR & $10.0$ & $0.5781$ & No \\
\quad $d=3$, Exp  & $5.0$  & $0.7500$ & No \\
\quad $d=3$, CVaR & $8.0$  & $0.6250$ & No \\
\hline
\multicolumn{4}{l}{\textit{Depth: $d=1$ vs.\ $d=3$}} \\
\quad $H$, Exp           & $0.0$ & $0.0078$ & \textbf{Yes} \\
\quad $H$, CVaR          & $2.5$ & $0.0312$ & \textbf{Yes} \\
\quad $|0\rangle$, Exp   & $0.0$ & $0.0312$ & \textbf{Yes} \\
\quad $|0\rangle$, CVaR  & $1.0$ & $0.0312$ & \textbf{Yes} \\
\hline
\multicolumn{4}{l}{\textit{Objective: Exp vs.\ CVaR}} \\
\quad $H$, $d=1$         & $0.0$ & $0.1250$ & No \\
\quad $H$, $d=3$         & $2.5$ & $0.1562$ & No \\
\quad $|0\rangle$, $d=1$ & $4.0$ & $0.2500$ & No \\
\quad $|0\rangle$, $d=3$ & $7.0$ & $1.0000$ & No \\
\hline
\end{tabular}%
}
\end{table}

Three findings emerge. First, no initialization comparison reaches significance ($p \geq 0.578$). The observed differences between Hadamard and $|0\rangle$ are directionally consistent but not statistically distinguishable at $n = 10$ - a limitation of the current sample size given the discrete nature of the best-cost metric. Second, all four depth comparisons are significant ($p \leq 0.0312$), with the Hadamard-Expectation pair yielding the strongest result ($W = 0.0$, $p = 0.0078$), confirming that depth improvement is robust and reproducible. Third, no objective comparison reaches significance ($p \geq 0.125$), indicating that Expectation and CVaR produce comparable best-cost distributions despite their different optimization landscapes.

\subsection{Discussion}

The results presented above reveal an interaction between initialization strategy, circuit depth, and objective function that warrants closer examination. At shallow depth ($d = 1$), the circuit contains only $n = 5$ trainable parameters and a single round of entanglement. Under these conditions, the parameterized layers have limited capacity to reshape the probability distribution over bitstrings. Hadamard initialization begins with uniform probability across all $2^n = 32$ basis states, meaning the optimizer needs only to sharpen the existing distribution toward favorable portfolios --- a task that requires relatively small parameter adjustments. In contrast, $|0\rangle$ initialization concentrates all probability mass on a single bitstring ($|00000\rangle$), requiring the optimizer to redistribute amplitude across multiple basis states before any meaningful portfolio cost can be evaluated. This asymmetry in the starting landscape plausibly explains the slight advantage of Hadamard initialization at $d = 1$.

At depth $d = 3$, the ansatz contains 15 parameters and three entanglement rounds, providing substantially greater expressibility. The additional capacity allows the circuit to construct complex probability distributions regardless of the initial state, diminishing the relative importance of the starting point. Under the Expectation objective, Hadamard retains a modest advantage, possibly because the uniform starting distribution continues to provide a more favorable gradient signal across the full bitstring space. Under CVaR, however, $|0\rangle$ initialization produces better outcomes. One plausible explanation lies in the geometry of the CVaR landscape itself. Because CVaR restricts the objective computation to the lowest-cost $\alpha$ fraction of sampled bitstrings, small parameter changes can cause different bitstrings to enter or exit the tail set $\mathcal{T}_\alpha$, producing discontinuities in the objective surface. Starting from $|0\rangle$ places nearly all probability mass on a single bitstring, creating a concentrated and predictable tail composition that COBYLA's trust-region mechanism can track incrementally. Hadamard initialization, by contrast, spreads probability uniformly across all bitstrings, making the tail set highly sensitive to minor parameter perturbations --- a condition that may impede the convergence of a derivative-free optimizer operating on a non-smooth surface.

The non-significance of all initialization comparisons under the Wilcoxon signed-rank test ($p \geq 0.578$) should be interpreted with caution. With $n = 10$ paired observations, the test has limited statistical power to detect small-to-moderate effect sizes. The minimum achievable $p$-value for a two-sided Wilcoxon test at $n = 10$ is $p \approx 0.002$ (when all ranks favor one group), and the observed directional trends --- particularly the CVaR reversal at depth 3 --- may represent genuine effects that the current sample size cannot resolve. A study with 30 or more seeds per configuration would provide substantially greater power to distinguish between initialization strategies, if the observed effect sizes persist.

Several limitations of the present study should be noted. All experiments are conducted on the Qiskit Aer statevector simulator \cite{qiskit}, which executes circuits without gate errors, decoherence, or readout noise. On physical quantum hardware, these noise sources introduce additional stochasticity that may interact with initialization strategy in ways not captured here. For instance, Hadamard initialization produces a deeper effective circuit (due to the additional layer of single-qubit gates), which may suffer disproportionately from decoherence on devices with short $T_2$ times. The asset universe is restricted to $n = 5$ equities, yielding only 31 candidate portfolios. At this scale, the combinatorial advantage of quantum approaches over classical enumeration is absent; the experiment isolates algorithmic behavior rather than computational advantage. Scaling to $n = 10$--$20$ assets, where exhaustive search becomes impractical, would test whether the observed initialization effects persist or change character in higher-dimensional Hilbert spaces. Additionally, only a single ansatz architecture ($R_Y$ rotations with linear CNOT entanglement) is evaluated. Alternative designs, such as QAOA-inspired ans\"atze or problem-tailored unitaries that encode the covariance structure of the asset universe, may respond differently to initialization. Finally, the hyperparameters $q = 0.5$, $\alpha = 0.3$, 1024 shots, and 200 COBYLA iterations are held constant throughout; sensitivity to these choices remains unexplored.

These considerations point to several directions for future work. Evaluation on noisy quantum backends --- such as IBM Quantum processors --- would determine whether hardware noise amplifies or suppresses the initialization effects observed in simulation. Scaling the asset universe beyond the classical tractability threshold would test the practical relevance of initialization strategy in settings where quantum approaches offer a genuine computational benefit. Comparison across multiple ansatz families, including QAOA and problem-specific circuits, would clarify whether the initialization--depth--objective interaction is ansatz-dependent. Finally, adaptive initialization schemes --- where the starting state is selected or learned based on properties of the cost Hamiltonian --- represent a promising direction that could unify the advantages of both strategies studied here.

\section{Conclusion}

This paper presented a systematic empirical study of qubit 
initialization strategies — Hadamard versus computational 
zero-state $|0\rangle$ — in variational quantum portfolio 
optimization across five NASDAQ-listed assets. Experiments 
were conducted under two objective functions, Expectation 
and CVaR, at circuit depths of 1 and 3, over 10 independent 
random seeds, yielding 80 optimization runs in total.

The dominant experimental result is that circuit depth, rather 
than initialization strategy, governs solution quality. All 
depth comparisons are statistically significant ($p \leq 0.0312$), 
while none of the initialization comparisons reach significance 
at the current sample size. Nevertheless, initialization is not 
irrelevant. At shallow depth ($d = 1$), Hadamard initialization 
produces slightly lower mean cost and variance under both 
Expectation and CVaR objectives, indicating more stable 
optimization behavior when the ansatz has limited expressibility.

This behavior changes at $d = 3$. Under the CVaR objective, 
$|0\rangle$ initialization achieves both a higher approximation 
ratio ($92.4\%$ versus $88.0\%$) and lower variance, suggesting 
that structured initial states may interact more favorably with 
tail-focused optimization landscapes once sufficient circuit 
depth is available.

These findings suggest that initialization strategy is a secondary but non-trivial design choice in variational quantum circuits, whose effect is modulated by both circuit depth and objective function. The non-significance of initialization comparisons under the Wilcoxon test should be weighed against the limited statistical power of $n = 10$ paired observations; the directional trends observed --- particularly the reversal under CVaR at depth 3 --- may reflect genuine effects that require larger sample sizes to confirm."""


new_block = r"""All 160 optimization runs completed successfully across the eight configurations. The globally optimal portfolio cost, obtained by exhaustive evaluation of all $2^n -1 = 127$ non empty binary portfolios, was $\mathcal{C}^* = -0.17435$, serving as the classical reference benchmark. All eight configurations reached this optimum in at least one seed, confirming that both initialization strategies are capable of finding the optimal solution, but the key distinction lies in average-case performance and consistency.

\subsection{Summary of Results}

Table~\ref{tab:summary} reports per configuration aggregate statistics across 20 seeds, including the approximation ratio $r = \overline{\mathcal{C}}_{\text{best}} /\mathcal{C}^*$, where a value of $1.0$ indicates perfect average recovery of the global optimum.

\begin{table}[t]
\caption{Per configuration summary statistics across 20 seeds. $r$ denotes the approximation ratio relative to the classical optimum $\mathcal{C}^* = -0.17435$.}
\label{tab:summary}
\centering
\resizebox{\textwidth}{!}{%
\begin{tabular}{lllllllll}
\hline\textbf{Init} & \textbf{$d$} & \textbf{Obj} &
\textbf{Mean Cost} & \textbf{Std} &
\textbf{$r$} &
\textbf{Mean Obj} & \textbf{Time (s)} &
\textbf{NFEv} \\
\hline
$H$         & 1 & Exp  & $-0.1508$ & $0.0151$ & $0.865$ & $-0.1223$ & $0.120$ & $77.9$ \\
$H$         & 1 & CVaR & $-0.1431$ & $0.0159$ & $0.821$ & $-0.0887$ & $0.111$ & $72.8$ \\
$H$         & 3 & Exp  & $-0.1689$ & $0.0096$ & $0.969$ & $-0.1421$ & $0.424$ & $194.1$ \\
$H$         & 3 & CVaR & $-0.1645$ & $0.0131$ & $0.944$ & $-0.0953$ & $0.411$ & $190.6$ \\
$|0\rangle$ & 1 & Exp  & $-0.1453$ & $0.0190$ & $0.833$ & $-0.1319$ & $0.109$ & $79.5$ \\
$|0\rangle$ & 1 & CVaR & $-0.1421$ & $0.0203$ & $0.815$ & $-0.0917$ & $0.100$ & $71.2$ \\
$|0\rangle$ & 3 & Exp  & $-0.1695$ & $0.0089$ & $0.972$ & $-0.1433$ & $0.407$ & $197.5$ \\
$|0\rangle$ & 3 & CVaR & $-0.1582$ & $0.0117$ & $0.907$ & $-0.0899$ & $0.402$ & $189.7$ \\
\hline
\end{tabular}%
}
\end{table}

Two broad patterns emerge from Table~\ref{tab:summary}. First, CVaR mean objective values ($-0.088$ to $-0.095$) are systematically less negative than Expectation values ($-0.122$ to $-0.143$). This is expected: CVaR optimizes only the worst -$\alpha$ tail rather than the full distribution, so its objective reflects a narrower, higher-cost subset of outcomes. Despite this, CVaR produces competitive best cost and approximation ratio values, confirming that tail-focused optimization effectively steers the circuit toward favorable regions. Second, increasing depth consistently reduces both mean and variance of best cost regardless of initialization or objective.

Figure~\ref{fig:boxplot} visualizes the distribution of best costs across the $20$ independent seeds for all configurations. The boxplots reveal that depth $d=3$ configurations exhibit substantially reduced variance and tighter interquartile ranges compared to their $d=1$ counterparts. Notably, the median performance approaches the theoretical optimum across both initialization strategies when $d=3$, whereas $d=1$ runs exhibit numerous high-cost outliers. The presence of these outliers underscores the susceptibility of shallow variational circuits to local minima, an effect that is visibly mitigated by the expanded parameter space of deeper ans\"atze.

\begin{figure}[h!]
\centering
\includegraphics[width=\textwidth]{boxplot.png}
\caption{Distribution of best portfolio costs achieved across 20 independent seeds. Configurations are grouped by objective function, circuit depth, and initialization strategy. The red dashed line denotes the globally optimal portfolio cost $\mathcal{C}^* = -0.17435$.}
\label{fig:boxplot}
\end{figure}

\subsection{Effect of Initialization Strategy}

At circuit depth $d = 1$, Hadamard initialization achieves slightly better mean best cost than $|0\rangle$ under both objectives: $-0.1508$ versus $-0.1453$ for Expectation, and $-0.1431$ versus $-0.1421$ for CVaR. Hadamard also yields lower standard deviation ($0.0151$ vs.\ $0.0190$ for Expectation; $0.0159$ vs.\ $0.0203$ for CVaR), suggesting more consistent convergence at shallow depth. With only $d \times n = 7$ parameters, the circuit has limited ability to reshape the probability distribution independently of its initial state --- making the uniform superposition of Hadamard a more favorable starting point.

At depth $d = 3$, the differences between initialization strategies diminish. Under Expectation, $|0\rangle$ slightly overtakes Hadamard ($-0.1695$ vs.\ $-0.1689$; $r = 0.972$ vs.\ $0.969$), while under CVaR, Hadamard maintains an advantage over $|0\rangle$ ($-0.1645$ vs.\ $-0.1582$; $r = 0.944$ vs.\ $0.907$). With 21 parameters at depth 3, the ansatz possesses sufficient expressibility to largely overcome its initial bias, rendering the optimization trajectory less dependent on the starting quantum state.

\subsection{Effect of Circuit Depth}

Increasing depth from $d = 1$ to $d = 3$ improves mean best cost across all four combinations, at the cost of $3.5$--$4.0\times$ longer runtime and $2.4$--$2.7\times$ more function evaluations. The largest gain occurs for $|0\rangle$-Expectation: mean best cost improves from $-0.1453$ to $-0.1695$ ($r$ from $83.3\%$ to $97.2\%$). For Hadamard-CVaR, the gain is from $-0.1431$ to $-0.1645$ ($r$ from $82.1\%$ to $94.4\%$). A single layer provides only 7 rotation parameters and one entanglement round; tripling the depth to 21 parameters and three entanglement rounds substantially expands the expressible hypothesis space.

Figure~\ref{fig:convergence} illustrates the average convergence behavior across all $20$ seeds, plotting the cumulative minimum objective value against COBYLA function evaluations. The convergence trajectories confirm that $d=3$ configurations descend significantly deeper into the cost landscape than their $d=1$ counterparts. While shallow circuits often plateau prematurely due to limited expressibility, the $d=3$ runs maintain a steeper descent profile before asymptoting closer to the theoretical minimum. The trajectories further demonstrate that while the final values are largely determined by depth, the optimization pathways are reasonably uniform across initialization strategies.

\begin{figure}[h!]
\centering
\includegraphics[width=\textwidth]{convergence.png}
\caption{Average convergence profiles showing cumulative minimum objective values against COBYLA function evaluations. Lines represent the mean trajectory across 20 independent seeds for each configuration.}
\label{fig:convergence}
\end{figure}

\subsection{Statistical significance}

Table~\ref{tab:wilcoxon} reports Wilcoxon signed-rank test results for all three comparison families, paired by seed.

\begin{table}[h!]
\caption{Wilcoxon signed-rank test results on best cost, paired by seed ($n = 20$). Significance threshold: $p < 0.05$.}
\label{tab:wilcoxon}
\centering
\resizebox{\textwidth}{!}{%
\begin{tabular}{llll}
\hline
\textbf{Comparison} & \textbf{$W$} & 
\textbf{$p$-value} & \textbf{Significant} \\
\hline
\multicolumn{4}{l}{\textit{Initialization: $|0\rangle$ vs.\ $H$}} \\
\quad $d=1$, Exp  & $67.5$ & $0.4330$ & No \\
\quad $d=1$, CVaR & $67.0$ & $0.4204$ & No \\
\quad $d=3$, Exp  & $22.0$ & $0.9489$ & No \\
\quad $d=3$, CVaR & $33.0$ & $0.1233$ & No \\
\hline
\multicolumn{4}{l}{\textit{Depth: $d=1$ vs.\ $d=3$}} \\
\quad $H$, Exp           & $3.0$ & $0.0008$ & \textbf{Yes} \\
\quad $H$, CVaR          & $8.0$ & $0.0011$ & \textbf{Yes} \\
\quad $|0\rangle$, Exp   & $12.0$ & $0.0013$ & \textbf{Yes} \\
\quad $|0\rangle$, CVaR  & $23.0$ & $0.0064$ & \textbf{Yes} \\
\hline
\multicolumn{4}{l}{\textit{Objective: Exp vs.\ CVaR}} \\
\quad $H$, $d=1$         & $19.0$ & $0.0355$ & \textbf{Yes} \\
\quad $H$, $d=3$         & $0.0$ & $0.0431$ & \textbf{Yes} \\
\quad $|0\rangle$, $d=1$ & $34.0$ & $0.6949$ & No \\
\quad $|0\rangle$, $d=3$ & $0.0$ & $0.0014$ & \textbf{Yes} \\
\hline
\end{tabular}%
}
\end{table}

Three findings emerge. First, no initialization comparison reaches significance ($p \geq 0.123$). The observed differences between Hadamard and $|0\rangle$ remain directionally consistent but statistically indistinguishable even at the expanded sample size of $n = 20$. Second, all four depth comparisons are highly significant ($p \leq 0.0064$), confirming that the capacity expansion provided by deeper circuits is robustly beneficial. Third, objective comparisons are now significant in three out of four cases ($p \leq 0.0431$), with the Expectation objective demonstrating a measurable advantage over CVaR in final best-cost discovery for this specific experimental scale.

\subsection{Discussion}

The results presented above reveal an interaction between initialization strategy, circuit depth, and objective function that warrants closer examination. At shallow depth ($d = 1$), the circuit contains only $n = 7$ trainable parameters and a single round of entanglement. Under these conditions, the parameterized layers have limited capacity to reshape the probability distribution over bitstrings. Hadamard initialization begins with uniform probability across all $2^n = 128$ basis states, meaning the optimizer needs only to sharpen the existing distribution toward favorable portfolios --- a task that requires relatively small parameter adjustments. In contrast, $|0\rangle$ initialization concentrates all probability mass on a single bitstring ($|0000000\rangle$), requiring the optimizer to redistribute amplitude across multiple basis states before any meaningful portfolio cost can be evaluated. This asymmetry in the starting landscape plausibly explains the slight advantage of Hadamard initialization at $d = 1$.

At depth $d = 3$, the ansatz contains 21 parameters and three entanglement rounds, providing substantially greater expressibility. The additional capacity allows the circuit to construct complex probability distributions regardless of the initial state, diminishing the relative importance of the starting point. Under the Expectation objective, $|0\rangle$ and Hadamard initialization perform similarly, suggesting the expanded gradient landscape provides sufficient pathways to the optimum. Under CVaR, however, Hadamard initialization maintains a minor empirical advantage. Because CVaR restricts the objective computation to the lowest-cost $\alpha$ fraction of sampled bitstrings, small parameter changes can cause different bitstrings to enter or exit the tail set $\mathcal{T}_\alpha$, producing discontinuities in the objective surface. Starting from $|0\rangle$ places nearly all probability mass on a single bitstring, creating a concentrated and predictable tail composition that COBYLA's trust-region mechanism can track incrementally. Hadamard initialization, by contrast, spreads probability uniformly across all bitstrings, making the tail set highly sensitive to minor parameter perturbations --- a condition that may impede the convergence of a derivative-free optimizer operating on a non-smooth surface.

The non-significance of all initialization comparisons under the Wilcoxon signed-rank test ($p \geq 0.123$) is a notable finding at the expanded sample size of $n = 20$. While earlier low-sample exploratory runs suggested potential initialization sensitivity, the robust $n=20$ paired analysis demonstrates that these initial state differences do not yield statistically significant advantages in final objective attainment. This reinforces the core finding that while initialization provides directional shifts early in the optimization trajectory, the algorithm's ultimate capacity to find high-quality portfolios is constrained primarily by circuit depth rather than the starting quantum state.

Several limitations of the present study should be noted. All experiments are conducted on the Qiskit Aer statevector simulator \cite{qiskit}, which executes circuits without gate errors, decoherence, or readout noise. On physical quantum hardware, these noise sources introduce additional stochasticity that may interact with initialization strategy in ways not captured here. For instance, Hadamard initialization produces a deeper effective circuit (due to the additional layer of single-qubit gates), which may suffer disproportionately from decoherence on devices with short $T_2$ times. The asset universe is restricted to $n = 7$ equities, yielding only 127 candidate portfolios. At this scale, the combinatorial advantage of quantum approaches over classical enumeration is absent; the experiment isolates algorithmic behavior rather than computational advantage. Scaling to $n = 15$--$30$ assets, where exhaustive search becomes impractical, would test whether the observed initialization effects persist or change character in higher-dimensional Hilbert spaces. Additionally, only a single ansatz architecture ($R_Y$ rotations with linear CNOT entanglement) is evaluated. Alternative designs, such as QAOA-inspired ans\"atze or problem-tailored unitaries that encode the covariance structure of the asset universe, may respond differently to initialization. Finally, the hyperparameters $q = 0.5$, $\alpha = 0.3$, 1024 shots, and 200 COBYLA iterations are held constant throughout; sensitivity to these choices remains unexplored.

These considerations point to several directions for future work. Evaluation on noisy quantum backends --- such as IBM Quantum processors --- would determine whether hardware noise amplifies or suppresses the initialization effects observed in simulation. Scaling the asset universe beyond the classical tractability threshold would test the practical relevance of initialization strategy in settings where quantum approaches offer a genuine computational benefit. Comparison across multiple ansatz families, including QAOA and problem-specific circuits, would clarify whether the initialization--depth--objective interaction is ansatz-dependent. Finally, adaptive initialization schemes --- where the starting state is selected or learned based on properties of the cost Hamiltonian --- represent a promising direction that could unify the advantages of both strategies studied here.

\section{Conclusion}

This paper presented a systematic empirical study of qubit initialization strategies --- Hadamard versus computational zero-state $|0\rangle$ --- in variational quantum portfolio optimization across seven NASDAQ-listed assets. Experiments were conducted under two objective functions, Expectation and CVaR, at circuit depths of 1 and 3, over 20 independent random seeds, yielding 160 optimization runs in total.

The dominant experimental result is that circuit depth, rather than initialization strategy, governs solution quality. All depth comparisons are highly significant ($p \leq 0.0064$), while none of the initialization comparisons reach significance at the current $n=20$ sample size. Nevertheless, initialization is not entirely irrelevant. At shallow depth ($d = 1$), Hadamard initialization produces slightly lower mean cost and variance under both Expectation and CVaR objectives, indicating more stable optimization behavior when the ansatz has severely limited expressibility.

At $d = 3$, the initial bias is largely overcome by the increased expressibility of the deeper parameterized layers, allowing the optimizer to navigate toward similar high-quality regions regardless of whether the circuit began in $|0\rangle$ or a uniform superposition.

These findings suggest that initialization strategy is a secondary design choice in variational quantum circuits, whose effect is rapidly superseded by the structural capacity of the ansatz itself. The non-significance of initialization comparisons across an expanded paired analysis confirms that circuit depth remains the primary determinant of success. All results reported here are obtained under ideal noiseless simulation, and the behavior of initialization strategies on physical quantum processors, where decoherence, gate infidelity, and readout error introduce additional variability, remains an open question. A natural extension of this work includes evaluation on noisy quantum hardware, scaling to larger asset universes where classical enumeration becomes infeasible, and comparison across alternative ansatz architectures to determine the generality of the observed interaction effects."""


if old_block in text:
    print("Old block matched perfectly! Replacing...")
    text = text.replace(old_block, new_block)
else:
    print("Old block did not match. Please investigate.")


with open("springer.tex", "w") as f:
    f.write(text)

