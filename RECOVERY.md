# Recovery

Project: Economic Protocol Verifier

Current branch: main

Current HEAD: the commit referenced by annotated tag `m3-counterexample-engine`

Latest completed milestone: M3

Latest milestone tag: m3-counterexample-engine

Scientific verdict: M0 PASS WITH NARROWING; M1 PASS; M2 PASS WITH LIMITATIONS; M3 PASS WITH LIMITATIONS

Tests: full M0-M3 suite; 60 mutants, 360 property evaluations, 180 exact minima; see M3 report

Known blockers: no independent proof checker or theorem prover; not required until M4

Known limitations: finite fragment; replay shares EIR semantics; counterexample certificates are negative artifacts, not V3 proof certificates

Exact next step: M4 proof-certificate research, only when separately authorized

Commands to reproduce current state:

```powershell
.venv\Scripts\python.exe -m unittest discover -s tests -v
python -m json.tool docs/literature/sources.json > $null
git status --short
```
