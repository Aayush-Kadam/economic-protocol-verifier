# Recovery

Project: Economic Protocol Verifier

Current branch: main

Current HEAD: the commit referenced by annotated tag `m2-epl-semantic-compiler`

Latest completed milestone: M2

Latest milestone tag: m2-epl-semantic-compiler

Scientific verdict: M0 PASS WITH NARROWING; M1 PASS; M2 PASS WITH LIMITATIONS

Tests: full M0-M2 suite plus 36 three-way differential comparisons and 20 solver-witness replays; see M2 report

Known blockers: no independent proof checker or theorem prover; not required until M4

Known limitations: EPL 0.1 is two-agent/single-item/template-based; finite grounding; V1/V2 bounded assurance; no certificates

Exact next step: M3 counterexample correctness/minimization work, only when separately authorized

Commands to reproduce current state:

```powershell
.venv\Scripts\python.exe -m unittest discover -s tests -v
python -m json.tool docs/literature/sources.json > $null
git status --short
```
