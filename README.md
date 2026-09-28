# Economic Protocol Verifier (EPV)

EPV is a research-preview framework for **bounded** verification and finite synthesis of selected economic protocols. It combines typed finite semantics, exhaustive and SMT-backed checking, replayable minimal counterexamples, and independently checked Alethe proof certificates for specific compiled obligations.

EPV does not prove arbitrary markets or universal economic theorems. Its economic-semantics-to-logic translation is trusted, synthesis searches tiny declared classes, and all results are limited to explicit finite bounds.

## Supported scope

- deterministic single-item auctions with finite integer values and quasi-linear utility;
- one-to-one two-sided matching with strict complete ordinal preferences;
- indivisible-goods fair division with additive nonnegative integer valuations;
- auction-table synthesis, payment-only repair, and integer reserve search in small finite classes.

Voting, randomized/Bayesian mechanisms, continuous domains, many-to-one matching, symbolic unbounded proofs, and deployed-code conformance are unsupported.

## Install

```powershell
py -3.12 -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements-lock.txt
.venv\Scripts\python.exe -m pip install --no-deps -e .
```

V3 additionally requires the pinned Carcara binary described in `tools.lock.json`; on the validated Windows setup it runs through WSL.

## First result

```powershell
epv verify examples/second_price.epl --property dsic
epv verify examples/first_price.epl --property dsic --assurance v2 --certificate-out counterexample.json
epv replay counterexample.json --source examples/first_price.epl --property dsic
epv doctor
```

Use `--json` on verification and replay commands for machine-readable output. Run `python -m epv.reproduce` for representative evidence or `python -m epv.reproduce --full` for the full suite.

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
