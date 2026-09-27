# Recovery

Project: Economic Protocol Verifier

Current branch: main

Current HEAD: the commit referenced by annotated tag `m3-counterexample-engine`

Latest completed milestone: M3

Latest milestone tag: m3-counterexample-engine

Scientific verdict: M0 PASS WITH NARROWING; M1 PASS; M2 PASS WITH LIMITATIONS; M3 PASS WITH LIMITATIONS

Tests: full M0-M3 suite; 60 mutants, 360 property evaluations, 180 exact minima; see M3 report

Known blockers: no independent proof checker or theorem prover; not required until M4

Known limitations: finite fragment; counterexample replay shares EIR semantics; M4 V3 proof certificates independently check only the canonical propositional truth table, while economic evaluation/translation remain trusted; direct arithmetic Alethe checking is `holey` and is not V3.

M4 recovery: install the M2 Python extras, build Carcara commit `051d2f79ccd3d5736bb3d93356f05df3dfc696e9` with its pinned Rust toolchain, place it at `.tools/carcara-current`, and run `python -m unittest discover -s tests -v`. The representative bundle is `proofs/second_price_dsic`.

Exact next step: M4 proof-certificate research, only when separately authorized

## M5 recovery

Project: Economic Protocol Verifier

Repository: `C:\Users\AAYUSH\Documents\Codex\2026-09-27\files-mentioned-by-the-user-economic\outputs\economic-protocol-verifier`

Branch: `main`

Latest milestone: M5

Verdict: PASS WITH LIMITATIONS

Tag: `m5-cross-domain-semantics`

Supported domains: auctions; strict one-to-one matching; additive indivisible-goods fair division.

V1/V2 cover the documented new-domain property matrix. V3 covers bounded matching stability and bounded fair-division EF1. Known limitations include trusted translation, 2x2 canonical matching, small fair-division instances, and deferred voting.

Exact next step: M6 only when separately authorized.

Reproduce with `.venv\Scripts\python.exe -m unittest discover -s tests -v`, then verify `git status --short` and replay the proof tests with pinned Carcara.

Commands to reproduce current state:

```powershell
.venv\Scripts\python.exe -m unittest discover -s tests -v
python -m json.tool docs/literature/sources.json > $null
git status --short
```
