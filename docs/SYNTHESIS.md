# Finite synthesis and repair

EPV synthesis searches a declared finite mechanism class. It is exhaustive search, not a general mechanism-design oracle.

## Worked payment-table example

- Agents: two bidders.
- Values/reports: `{0,1}`.
- Allocation: efficient, lowest-index tie break.
- Variables: one winner-payment value for each of four report profiles.
- Payment bounds: `{0,1}`.
- Search size: `2^4 = 16` candidates.
- Requirements: DSIC, ex-post IR, weak budget balance, feasibility, and allocative efficiency.
- Candidate: the canonical lexicographically smallest satisfying payment table.
- Post-verification: every requirement is re-evaluated by the normal property path.

Run `epv synthesize`. Adding the explicit uniform prior and expected-revenue objective in the Python API yields an exhaustively established optimum of `1/2` for the committed benchmark.

`epv repair` holds the efficient allocation table fixed and minimizes, lexicographically, changed payment cells, total absolute adjustment, then table serialization. For the `{0,1}` first-price baseline, one cell changes by one unit. The baseline is rejected if its allocation lies outside the repair class.

The bounded-UNSAT benchmark fixes winner payments to `{1}`. No candidate in that one-element declared class satisfies the required constraints. This is not an unrestricted impossibility theorem.
