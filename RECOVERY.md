# Recovery

Project: Economic Protocol Verifier

Current branch: main

Current HEAD: the commit referenced by annotated tag `m5-cross-domain-semantics`

Latest completed milestone: M5

Latest milestone tag: m5-cross-domain-semantics

Scientific verdict: M0 PASS WITH NARROWING; M1 PASS; M2–M5 PASS WITH LIMITATIONS

Tests: 98 passed, 0 failed, 0 skipped; includes all M0–M5 regressions and proof replays

Known blockers: none for bounded M5; voting and broader domains are deferred

Known limitations: finite fragment; counterexample replay shares EIR semantics; M4 V3 proof certificates independently check only the canonical propositional truth table, while economic evaluation/translation remain trusted; direct arithmetic Alethe checking is `holey` and is not V3.

M4 recovery: install the M2 Python extras, build Carcara commit `051d2f79ccd3d5736bb3d93356f05df3dfc696e9` with its pinned Rust toolchain, place it at `.tools/carcara-current`, and run `python -m unittest discover -s tests -v`. The representative bundle is `proofs/second_price_dsic`.

Exact next step: M6 only when separately authorized

## M6 recovery

Project: Economic Protocol Verifier

Repository: `C:\Users\AAYUSH\Documents\Codex\2026-09-27\files-mentioned-by-the-user-economic\outputs\economic-protocol-verifier`

Branch: `main`

HEAD: annotated tag `m6-synthesis-repair`

Working tree: clean at release

Latest milestone: M6

Verdict: PASS WITH LIMITATIONS

Tag: `m6-synthesis-repair`

Tests: 124 passed, 0 failed, 0 skipped

Synthesis benchmark cases: 5

V3 synthesis/impossibility certificates: 1 bounded search-class UNSAT bundle

Synthesis domains: auction only. Search classes: fixed-efficient or all-feasible two-bidder tables with bounded winner payments. Repair metric: changed cells, absolute adjustment, lexical tie-break. Impossibility support: exhaustive bounded-class UNSAT plus Carcara truth-table certificate. Parameter synthesis: integer reserve grids. Approximate metrics: exact manipulation gain, IR shortfall, deficit, welfare loss.

Known limitations: tiny exhaustive classes; trusted synthesis compiler; matching and fair-division synthesis deferred.

Exact next step: M7 only when separately authorized.

## M7 recovery

Project: Economic Protocol Verifier

Repository: `C:\Users\AAYUSH\Documents\Codex\2026-09-27\files-mentioned-by-the-user-economic\outputs\economic-protocol-verifier`

Branch: `main`

HEAD: annotated tag `m7-hostile-validation`

Working tree: clean at release

Latest milestone: M7

Verdict: PASS WITH LIMITATIONS

Tag: `m7-hostile-validation`

Generated verification cases: 120 instances and 584 property evaluations. Differential cases: 584 per backend. Mutation cases: 18. Parser fuzz cases: 206. Certificate attacks: 19. Synthesis attacks: 32.

Critical defects found/unresolved: 0/0. High defects found/unresolved: 3/0. Clean reproduction: clean Git archive passed. Scaling envelope: verification measured through four bidders/two values; synthesis through 81 candidates.

Known limitations: trusted translation, targeted mutation scope, one cvc5 version, WSL Carcara dependency, and tiny synthesis scale.

Exact M8 readiness: M8 may begin only when separately authorized.

## M5 recovery

Project: Economic Protocol Verifier

Repository: `C:\Users\AAYUSH\Documents\Codex\2026-09-27\files-mentioned-by-the-user-economic\outputs\economic-protocol-verifier`

Branch: `main`

Latest milestone: M5

Verdict: PASS WITH LIMITATIONS

Tag: `m5-cross-domain-semantics`

Implementation commit: `88ee18ae32ddd3c4147e71ae6c989ee9d8b2fdb1`

Working tree: clean at release

Tests: 98 passed, 0 failed, 0 skipped

Benchmark cases: 12 total; four per domain; six positive and six negative

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
