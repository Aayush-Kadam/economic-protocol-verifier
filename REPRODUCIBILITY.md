# Reproducibility

## Environment

The validated platform is Windows with Python 3.12 and WSL for pinned Carcara. Exact formal-tool versions are in `tools.lock.json`; Python packages are pinned in `requirements-lock.txt`. Wheel hashes are not included, so this is version-locked but not hermetic.

## Install from a clean archive

```powershell
py -3.12 -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements-lock.txt
.venv\Scripts\python.exe -m pip install --no-deps -e .
epv doctor
python -m epv.reproduce
python -m epv.reproduce --full
```

V3 requires `.tools/carcara-current` built from commit `051d2f79ccd3d5736bb3d93356f05df3dfc696e9`. On Windows the adapter invokes it through WSL. If it is absent, the system correctly reports V3 unavailable rather than silently downgrading.

## Evidence map

- M7 counts: `benchmarks/m7/results.json`
- scaling: `benchmarks/m7/scaling.json`
- synthesis cases: `benchmarks/m6/registry.json`
- release benchmark: `benchmarks/manifest.json`
- proof bundles: `proofs/*/{manifest.json,problem.smt2,proof.alethe}`
- final recorded runs: `release/FINAL_VALIDATION.md` and `release/reproduction.json`
- manuscript source: `paper/EPV_M8_MANUSCRIPT.md`

## Clean-archive rule

Use `git archive` from the tagged commit, extract into a new directory, supply rather than copy the excluded environment/toolchain, then run full reproduction. Proof and SMT files are marked `-text` in `.gitattributes`; exact byte hashes must match.

## Limits

M7 and M8 reuse locally available pinned dependencies rather than downloading and rebuilding every tool from the network. Results therefore establish clean-source/archive reproducibility on the declared platform, not a hermetic or cross-platform build.
