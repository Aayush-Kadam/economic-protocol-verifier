# Benchmarks

M1 will begin with hand-auditable finite instances:

- second-price single-item auction: expected bounded DSIC positive case;
- first-price auction: expected DSIC counterexample;
- deficit mechanism: weak-budget-balance counterexample;
- double-allocation mutant: feasibility counterexample;
- truth/report conflation mutant and tie-breaking mutants.

Each benchmark declares exact agents, domains, tie-breaking, payments, expected status, and a hand-checkable rationale. Expected outcomes are not silently changed to match implementation.

M2 runs six properties across six EPL mechanisms: 36 three-way enumeration/cvc5/Z3 comparisons. Every SAT selection is replayed against the M1 evaluator.

M3 adds 60 systematic allocation/payment mutants, 360 property evaluations, 19 property vectors, and 180 exact-minimum negative witnesses. See `benchmarks/mutants/README.md`.
