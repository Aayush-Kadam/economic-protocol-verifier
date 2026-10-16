# Reproducibility

## Environment

The validated platform is Windows with Python 3.12 and WSL for pinned Carcara. Exact formal-tool versions are in `tools.lock.json`; Python packages are pinned in `requirements-lock.txt`. Wheel hashes are not included, so this is version-locked but not hermetic.

## Install from a clean archive

```powershell
py -3.12 -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements-lock.txt
.venv\Scripts\python.exe -m pip install --no-deps -e .
.venv\Scripts\python.exe -m epv doctor
.venv\Scripts\python.exe -m epv.reproduce
.venv\Scripts\python.exe -m epv.reproduce --full
```

V3 requires `.tools/carcara-current` built from commit `051d2f79ccd3d5736bb3d93356f05df3dfc696e9`. On Windows the adapter invokes it through WSL. If it is absent, the system correctly reports V3 unavailable rather than silently downgrading.

## Provision the authentic checker

Upstream: [ufmg-smite/carcara](https://github.com/ufmg-smite/carcara).
The pinned source's Cargo manifest requires **Rust 1.93 or newer**; the public
installation website may describe an older minimum. The local M1-R builds used
Rust/Cargo 1.93.1 in Ubuntu on WSL2; the separate CI job pins 1.98.1.
The build uses the committed Cargo.lock with `--locked`.
Cargo may need network access on first installation. A populated trusted cache
can use `CARGO_NET_OFFLINE=true`; this is not a hermetic or bit-reproducible build.

From the repository root on Linux, with Git and Rust/Cargo already installed:

```bash
bash scripts/setup_carcara.sh
python -m epv doctor
python -m epv.reproduce --full
```

Use the Python environment where EPV and the pinned solvers are installed.
On Windows, with an existing Ubuntu WSL distribution and Rust/Cargo inside it:

```powershell
wsl.exe --cd "$PWD" bash -lc 'bash scripts/setup_carcara.sh'
.venv\Scripts\python.exe -m epv doctor
.venv\Scripts\python.exe -m epv.reproduce --full
```

The script checks the official source origin, refuses a dirty source checkout,
checks out the full pinned commit and builds into ignored `.tools/` directories.
It does not install globally or replace a verifier with another program.
The generated binary and lockfile hashes belong in the reproduction record.
No build/source-signature authenticity beyond the stated upstream/revision trust
is inferred from a hash.

Git can lengthen its unique abbreviated commit as repository history grows.
The pinned build may print `carcara 1.1.0 [git 051d2f79]` while frozen manifests
retain the historical seven-character label. EPV accepts only version 1.1.0 and
a 7–40 character hexadecimal prefix of the exact pinned full commit; wrong
versions/revisions, dirty suffixes, malformed output and failed probes reject.
This identity string is a compatibility check, not cryptographic binary attestation.
Proof and formula hashes and all other bundle bindings are still checked exactly.
Only exit zero with the complete trimmed output `valid` is accepted; a final
`valid` line cannot override contradictory preceding checker output.

Core CI tests missing-checker behavior with explicit V3 skips. A separate Linux
job builds the real pinned checker with Rust 1.98.1 and runs full assurance
reproduction. A core-only green run does not establish V3.

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
