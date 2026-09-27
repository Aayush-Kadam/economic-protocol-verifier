# Limitations

EPV supports only two-agent, single-indivisible-item, deterministic direct mechanisms over bounded integer domains. EPL 0.1 has four allocation/payment templates rather than general expressions. SMT obligations are finite grounded QF_LIRA disjunctions and share EIR evaluation with the compiler. No proof certificate, symbolic real theorem, randomization, Bayesian semantics, cross-domain model, or implementation conformance is supported.
M3 counterexample certificates are negative evidence artifacts, not proof certificates. Exact minimality is relative to the declared objective and finite witness set. Replay shares the authoritative EIR evaluator with compilation, so it is backend-independent but not fully semantics-independent.

## M5

Matching is one-to-one with strict complete rankings and a 2x2 canonical strategic domain. Fair division uses additive nonnegative integers, complete deterministic allocations, and small exhaustive alternatives. Voting, many-to-one capacities, ties, randomized mechanisms, EFX, cross-domain EPL 0.2, and large-scale performance are not supported. New V3 certificates check compiled propositional truth tables, not translation correctness.

## M6

Full synthesis is limited to two bidders and tiny finite integer tables. Payments are winner-only with explicit constant loser normalization. Optimization and minimality use exhaustive enumeration, not scalable solver optimization. The bounded impossibility core is intentionally a normalization/bound conflict. Matching/fair-division synthesis, continuous parameters, randomized rules, general perturbation radii, and universal impossibility proofs are excluded.

## M7

Generated campaigns cover supported finite fragments, not arbitrary Python mechanisms or hostile operating-system behavior. No second cvc5 version was installed; proof portability across versions is unestablished. Clean reproduction reused the pinned local virtual environment and WSL toolchain rather than rebuilding dependencies from the network. Mutation analysis is targeted rather than exhaustive. Scaling measurements are small and machine-specific.
