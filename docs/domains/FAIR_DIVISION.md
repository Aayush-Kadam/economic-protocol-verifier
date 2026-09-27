# Fair division

M5 fair division has finite indivisible goods and additive nonnegative integer valuations. An allocation is a tuple of agent bundles. Complete feasibility requires every declared good exactly once and no unknown good.

The deterministic round-robin rule uses a fixed agent order. Each turn selects the remaining good of greatest value to that agent; declared good order breaks ties. Implemented properties are feasibility, envy-freeness, EF1 (remove at most one good from the envied bundle), and Pareto efficiency by exhaustive alternative allocation.

Envy comparisons always use the envying agent's valuation. Pareto dominance requires weak improvement for every agent and strict improvement for at least one; total welfare alone is not used.
