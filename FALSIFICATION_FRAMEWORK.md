# Falsification Framework

## Central hypothesis

A restricted economic-mechanism language can support useful, auditable results that are materially safer and more usable than ad hoc solver encodings, while clearly separating bounded evidence, solver conclusions, and independently checked proofs.

## Kill or narrow criteria

- Stop if the typed semantics cannot prevent truth/report conflation or underspecified tie-breaking.
- Stop if a result can reach a verified status after timeout, partial enumeration, floating-point evaluation, decoder failure, or checker failure.
- Narrow to counterexample discovery if proof artifacts for the required theories cannot be independently checked.
- Narrow to one domain if a common IR obscures rather than clarifies domain semantics.
- Reclassify as engineering only if evaluation finds no research contribution beyond composition of established tools.
- Reject cross-domain claims until at least two domains share independently tested semantic infrastructure without property distortion.
- Reject scalability claims unless benchmark curves and timeout/unknown rates support them.
- Reject general theorem claims derived only from bounded instances.

## Adversarial experiments

Seed mutations for truth/report swaps, payment-sign reversal, omitted ties, duplicate allocation, strict-versus-weak inequality, integer/real mismatch, unstable canonical ordering, stale certificate/formula pairing, and timeout-as-unsat. Any surviving mutation that can create false acceptance is release-blocking.

## Decision rule

One false positive `VERIFIED` is a critical failure. False negatives or `UNKNOWN` results are defects or limitations, but do not justify unsound shortcuts.

