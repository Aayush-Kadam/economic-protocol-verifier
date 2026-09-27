# Formal Problem

Let agents be `N = {0,...,n-1}`. Each agent has a true-type space `T_i` and report space `R_i`; the initial direct fragment requires a declared truth-report embedding and normally `T_i = R_i`. Let `X` be a finite outcome space. A deterministic mechanism is

`M(r) = (x(r), p(r))`, where `r in product_i R_i`, `x(r) in X`, and `p(r) in Q^n`.

Valuation is `v_i : T_i x X -> Q`; utility is `u_i(theta_i, r) = v_i(theta_i, x(r)) - p_i(r)`.

## Properties and negated witnesses

- DSIC violation: `exists i, theta_i, r_-i, r'_i: u_i(theta_i,(r'_i,r_-i)) > u_i(theta_i,(theta_i,r_-i))`.
- Ex-post IR violation: `exists theta: u_i(theta_i,theta) < outside_i(theta_i)` for some `i`.
- Weak budget balance violation: `exists r: sum_i p_i(r) < 0` under the pay-to-mechanism convention.
- Feasibility violation: `exists r: not feasible(x(r))`.

The exhaustive backend enumerates every valuation of each existential witness tuple. `SAT` means a concrete witness must replay through an independent evaluator. Exhaustive absence of witnesses yields `BOUNDED VERIFIED` and includes cardinalities. Exceptions, incomplete evaluation, time/resource limits, or unsupported constructs yield `UNKNOWN` or `OUTSIDE VERIFIED FRAGMENT`.

## Correctness obligations

1. Parsing and elaboration preserve the displayed formal meaning.
2. Canonical serialization is deterministic and hash-bound to results.
3. Each property compiler is extensionally equivalent to its executable reference predicate on finite test instances.
4. Counterexamples replay against the source mechanism semantics.
5. A solver `unsat` is not V3 unless the emitted artifact for the identical formula passes an independent checker.

