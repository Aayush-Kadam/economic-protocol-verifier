# Inspect a bounded result

EPV is for finite mechanism experiments, not deployed-market certification.

## Architecture and trust

```text
EPL source -> typed finite mechanism -> property compiler
                                  -> exhaustive check (V1)
                                  -> cvc5 / Z3 (V2) -> witness -> replay
                                  -> proof bundle -> Carcara (V3)
```

The compiler and economic semantics remain trusted even when a proof checker
accepts the compiled obligation. Solver agreement is differential evidence,
not independent validation of the economic model.

## A first result

Install as described in the README. Use the environment's Python throughout:

```powershell
.venv\Scripts\python.exe -m epv verify examples/second_price.epl --property dsic --json
.venv\Scripts\python.exe -m epv verify examples/first_price.epl --property dsic --assurance v2 --certificate-out counterexample.json --json
.venv\Scripts\python.exe -m epv replay counterexample.json --source examples/first_price.epl --property dsic --json
```

Expected sequence: `BOUNDED VERIFIED` (exit 0), `COUNTEREXAMPLE FOUND`
(exit 2), and replay `PASS` (exit 0). Hashes and runtime depend on the
input/version and machine; do not compare wall-clock time as a benchmark.

## Verify the artifact

```powershell
.venv\Scripts\python.exe -m unittest discover -s tests -v
.venv\Scripts\python.exe -m epv doctor
.venv\Scripts\python.exe -m epv.reproduce
```

The last command intentionally exits 1 and reports `FAIL` without the pinned
Carcara binary. A green core test suite with explicit V3 skips does not establish
V3. Install the exact checker in `tools.lock.json` and rerun to validate proofs;
never substitute a dummy checker. See [reproducibility](../REPRODUCIBILITY.md).

The portfolio repair was exercised from an environment outside the repository's
usual `.venv` directory. It fixes interpreter selection, preserves the negative
missing-checker result, and adds Ubuntu/Windows core CI. It changes no theorem,
formal semantics, benchmark denominator, or assurance level.

## Boundaries and next work

See [limitations](../LIMITATIONS.md), [contributing](../CONTRIBUTING.md),
and [license](../LICENSE). Independent economic review and fresh pinned-checker
reproduction remain necessary. Do not expose untrusted solver/proof workloads
as a public service without separate resource isolation and security review.
