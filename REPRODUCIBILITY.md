# Reproducibility

M0 is documentation-only. Primary evidence is recorded in `docs/literature/sources.json` and `PRIOR_ART_MATRIX.csv` with stable DOI or project URLs where available. Tool baseline observed on 2026-09-27: Git 2.55.0.windows.3 and CPython 3.12.10. cvc5, Z3, Carcara, Lean, Coq/Rocq, and Isabelle were not found on PATH.

M2 uses project-local Python packages cvc5 1.4.1 and z3-solver 5.1.0.0 (solver-reported Z3 5.1.0). The Python APIs are used directly; no solver executable path is required.

Reproduce M0 checks with:

```powershell
python -m json.tool docs/literature/sources.json > $null
python -m unittest discover -s tests -v
git status --short
```

For M2 use `.venv\Scripts\python.exe` so both solver bindings are present.

M3 counterexample and mutant metrics are reproduced by the full test suite. The corpus is deterministic and has no external data dependency.

## M5

Run `.venv\Scripts\python.exe -m unittest discover -s tests -v`. This evaluates all three domain reference semantics, cvc5/Z3 differential cases, counterexample replays, applicability attacks, historical M4 bundles, and the two new-domain Carcara bundles. Carcara must be the pinned binary described in `docs/proofs/PROOF_PIPELINE.md`.

## M6

The same command exhaustively replays every tiny synthesis, optimization, repair, MUS, parameter, and severity benchmark, then validates the M6 Carcara bundle. Validate `benchmarks/m6/registry.json` with Python's JSON parser. No network access is required.

## M7

Run the full suite under at least two `PYTHONHASHSEED` values and validate `benchmarks/m7/results.json` and `scaling.json`. A clean Git archive should be tested with `PYTHONPATH=<archive>/src` using the pinned `.venv` interpreter; Carcara remains at the original repository's pinned `.tools/carcara-current` path unless copied into the archive.
