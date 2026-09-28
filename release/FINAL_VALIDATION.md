# M8 final validation

Status: local research release candidate; not published or submitted.

## Integrated source-tree gate

- Full repository suite: 151 passed, 0 failed, 0 skipped in 42.666 seconds (43.513 seconds wall time).
- Full reproduction command: PASS in 27.35 seconds, including 151 tests in 21.840 seconds.
- User story A: canonical second-price DSIC returned `BOUNDED VERIFIED` at V1.
- User story B: first-price DSIC produced a V2 counterexample and authoritative replay returned `PASS`.
- User story C: tiny synthesis returned `SAT_CANDIDATE_FOUND`; payment repair returned `OPTIMAL_REPAIR_FOUND` with distance `(1, 1)`.
- Historical proof bundles: replayed by the complete suite, including all auction families, matching stability, fair-division EF1, and bounded synthesis UNSAT.
- Manuscript: rebuilt from `paper/EPV_M8_MANUSCRIPT.md`; five rendered pages inspected with no clipping, overlap, blank page, path leakage, or missing-reference marker.

## Dependency reconstruction boundary

The source tree and release archive are cleanly reconstructable with the declared Python and tool versions. The final gate reuses the existing pinned Python 3.12 environment and pinned Carcara/WSL binary because cvc5 and Z3 wheels were not available in the local pip cache. This is a clean-source reproduction, not a hermetic network-independent toolchain rebuild.

## Pending gate at this record's creation

The final commit, annotated tag, and post-commit clean-archive reproduction are performed after this file is added. Their identities and results are reported in `docs/milestones/M8.md` and the final M8 report.
