# Limitations

EPV supports only two-agent, single-indivisible-item, deterministic direct mechanisms over bounded integer domains. EPL 0.1 has four allocation/payment templates rather than general expressions. SMT obligations are finite grounded QF_LIRA disjunctions and share EIR evaluation with the compiler. No proof certificate, symbolic real theorem, randomization, Bayesian semantics, cross-domain model, or implementation conformance is supported.
M3 counterexample certificates are negative evidence artifacts, not proof certificates. Exact minimality is relative to the declared objective and finite witness set. Replay shares the authoritative EIR evaluator with compilation, so it is backend-independent but not fully semantics-independent.
