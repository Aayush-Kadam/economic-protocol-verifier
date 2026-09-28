# Quickstart

## 1. Check the environment

Create Python 3.12 environment, install `requirements-lock.txt`, install EPV editable, and run:

```powershell
epv doctor
```

The command distinguishes Python/solver availability from V3 readiness. Missing Carcara means V1/V2 may work, but V3 is unavailable.

## 2. Verify a supplied auction

```powershell
epv verify examples/second_price.epl --property dsic --assurance v1
epv verify examples/second_price.epl --property dsic --assurance v2 --backend cvc5 --json
```

The printed domain (`2 agents; integer values/reports in [0,2]`) is part of the claim. `BOUNDED VERIFIED` never means an unrestricted theorem.

## 3. Diagnose and replay a failure

```powershell
epv verify examples/first_price.epl --property dsic --assurance v2 --certificate-out counterexample.json
epv replay counterexample.json --source examples/first_price.epl --property dsic
```

Replay checks the certificate's hashes, property version, exact-minimum witness, and violation against the authoritative evaluator. A certificate from a different mechanism or property is rejected.

## 4. Check a positive certificate

```powershell
epv check-proof proofs/second_price_dsic --source examples/second_price.epl --property dsic
```

Expected success is `BOUNDED VERIFIED - V3`. This requires the exact pinned Carcara identity and a fresh `valid` result.

## 5. Search or repair a tiny auction class

```powershell
epv synthesize
epv repair
```

Both commands disclose the search size. Optimality means exhaustive optimality inside the declared finite class only.

## 6. Reproduce the release evidence

```powershell
python -m epv.reproduce
python -m epv.reproduce --full
```

See `REPRODUCIBILITY.md` for clean-archive instructions and known platform constraints.
