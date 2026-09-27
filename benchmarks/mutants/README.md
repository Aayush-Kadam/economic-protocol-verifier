# M3 Mutant Corpus

The deterministic generator in `src/epv/mutants.py` produces 60 mechanisms from six allocation mutations crossed with ten payment mutations. Every record identifies the second-price base, mutation operator, allocation/payment location, and an intentionally non-guessed expected-impact statement.

The reproducible 60 x 6 matrix contains 360 evaluations and 19 distinct property vectors. Failure totals are: DSIC 29, IR 29, WBB 18, SBB 54, feasibility 10, and efficiency 40. All 60 mutants fail at least one property; 180 failing evaluations have an exact minimized witness.

