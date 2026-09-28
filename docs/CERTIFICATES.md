# Certificate inspection and tamper testing

## Negative certificate

Create and replay:

```powershell
epv verify examples/first_price.epl --property dsic --assurance v2 --certificate-out counterexample.json
epv replay counterexample.json --source examples/first_price.epl --property dsic
```

Inspect the JSON fields `mechanism_hash`, `property_id`, `property_version`, `logical_problem_hash`, `minimality`, and `witness`. Change any hash or witness value and replay again; the command must return `CERTIFICATE REJECTED` with a nonzero exit status.

## Positive V3 bundle

Each directory under `proofs/` contains `manifest.json`, byte-exact `problem.smt2`, and `proof.alethe`. Inspect hashes with any SHA-256 tool, then run:

```powershell
epv check-proof proofs/second_price_dsic --source examples/second_price.epl --property dsic
```

Copy the bundle to a temporary directory, change one byte in the proof or formula, and check the copy. EPV rejects it before or during checking. Do not edit committed proof bytes: `.gitattributes` deliberately disables line-ending normalization for them.

Carcara validates the compiled propositional refutation. It does not validate EPV's economic translation; see `TRUST_AND_ASSURANCE.md`.
