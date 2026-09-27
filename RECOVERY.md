# Recovery

Project: Economic Protocol Verifier

Current branch: main

Current HEAD: the commit referenced by annotated tag `m1-formal-kernel`

Latest completed milestone: M1

Latest milestone tag: m1-formal-kernel

Scientific verdict: M0 PASS WITH NARROWING; M1 PASS

Tests: kernel, six properties, canonical benchmarks, exact arithmetic, provenance hash, and witness replay; see M1 report

Known blockers: no local SMT solver, independent checker, or theorem prover detected; M2 SMT work requires a backend decision or dependency installation

Known limitations: finite deterministic direct mechanisms only; V1 bounded assurance; no parser or solver certificates

Exact next step: define and validate EPL for the M1 fragment, then prove compiler/backend agreement against enumeration

Commands to reproduce current state:

```powershell
python -m unittest discover -s tests -v
python -m json.tool docs/literature/sources.json > $null
git status --short
```
