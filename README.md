# Economic Protocol Verifier (EPV)

EPV is a research-preview framework for **bounded** verification and finite synthesis of selected economic protocols. It combines typed finite semantics, exhaustive and SMT-backed checking, replayable minimal counterexamples, and independently checked Alethe proof certificates for specific compiled obligations.

EPV does not prove arbitrary markets or universal economic theorems. Its economic-semantics-to-logic translation is trusted, synthesis searches tiny declared classes, and all results are limited to explicit finite bounds.

## Supported scope

- deterministic single-item auctions with finite integer values and quasi-linear utility;
- one-to-one two-sided matching with strict complete ordinal preferences;
- indivisible-goods fair division with additive nonnegative integer valuations;
- auction-table synthesis, payment-only repair, and integer reserve search in small finite classes.

Voting, randomized/Bayesian mechanisms, continuous domains, many-to-one matching, symbolic unbounded proofs, and deployed-code conformance are unsupported.

## Start here

For researchers and engineers inspecting small mechanism models, the shortest path is a V1 check and a V2 counterexample replay. See [the reviewer walkthrough](docs/REVIEWER_WALKTHROUGH.md) for expected statuses, exit codes, architecture, and checker limitations.

This public source snapshot has **no published GitHub release** at the portfolio audit baseline (16 October 2026). Its [LICENSE](LICENSE) grants no redistribution or production-use permission; public visibility does not make it open-source licensed.

## Install

```powershell
py -3.12 -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements-lock.txt
.venv\Scripts\python.exe -m pip install --no-deps -e .
```

V3 additionally requires the pinned Carcara binary described in `tools.lock.json`; on the validated Windows setup it runs through WSL.

## First result

```powershell
.venv\Scripts\python.exe -m epv verify examples/second_price.epl --property dsic
.venv\Scripts\python.exe -m epv verify examples/first_price.epl --property dsic --assurance v2 --certificate-out counterexample.json
.venv\Scripts\python.exe -m epv replay counterexample.json --source examples/first_price.epl --property dsic
.venv\Scripts\python.exe -m epv doctor
```

Use `--json` on verification and replay commands for machine-readable output. A counterexample exits **2**; successful bounded verification or replay exits **0**. Run the commands separately so an expected counterexample does not prevent replay in a fail-on-error shell.

On macOS/Linux, create the environment with `python3 -m venv .venv` and use `.venv/bin/python`. The CLI tests use the active interpreter rather than assuming an environment directory.

Run `python -m epv.reproduce` for representative evidence or `python -m epv.reproduce --full` for the full suite. Both require the pinned Carcara checker for overall `PASS`; missing V3 checking intentionally produces `FAIL`. Core CI runs the test suite and doctor without claiming V3 validation.

## Assurance

- **V1:** bounded exhaustive verification.
- **V2:** bounded solver-established verification; translation and solver remain trusted.
- **V3:** bounded independently certificate-checked verification; Carcara freshly checks the exact hash-bound propositional obligation, while economic translation remains trusted.

The canonical explanation is [TRUST_AND_ASSURANCE.md](TRUST_AND_ASSURANCE.md).

## Research artifact map

- [Quickstart](docs/QUICKSTART.md)
- [Property registry](docs/PROPERTY_REGISTRY.md) and [machine-readable registry](property-registry.json)
- [Certificates](docs/CERTIFICATES.md)
- [Synthesis and repair](docs/SYNTHESIS.md)
- [Benchmark manifest](benchmarks/manifest.json)
- [Reproducibility](REPRODUCIBILITY.md)
- [Manuscript](paper/EPV_M8_MANUSCRIPT.md)
- [Release notes](RELEASE_NOTES.md)
- [Limitations](LIMITATIONS.md)

Version `0.1.0` denotes a research preview: the scientific scope is frozen for external review, but the API and artifact format are not promised stable.
