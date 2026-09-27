# Reproducibility

M0 is documentation-only. Primary evidence is recorded in `docs/literature/sources.json` and `PRIOR_ART_MATRIX.csv` with stable DOI or project URLs where available. Tool baseline observed on 2026-09-27: Git 2.55.0.windows.3 and CPython 3.12.10. cvc5, Z3, Carcara, Lean, Coq/Rocq, and Isabelle were not found on PATH.

Reproduce M0 checks with:

```powershell
python -m json.tool docs/literature/sources.json > $null
python -m unittest discover -s tests -v
git status --short
```

