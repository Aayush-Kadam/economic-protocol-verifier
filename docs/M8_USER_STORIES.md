# M8 fresh-user stories

## A - verify a supplied auction

Command: `epv verify examples/second_price.epl --property dsic --json`. Result: bounded V1 verification with mechanism/property/problem hashes, assumptions, domain, runtime, and limitations. Initial friction: the package was not installed in the frozen virtual environment; the external quickstart now installs editable after locked dependencies.

## B - diagnose a broken mechanism

Command: V2 verification of `first_price.epl` with `--certificate-out`, followed by `epv replay`. Result: counterexample certificate and successful replay. Initial friction: JSON changes tuples to lists, causing an otherwise valid witness to reject. The CLI now restores tuple-valued witness fields at the serialization boundary, with regression coverage.

## C - synthesize and repair

Commands: `epv synthesize` and `epv repair`. Results disclose class, size, candidate/repair, post-verification or distance, and exhaustive optimality. Friction: the CLI intentionally exposes only the canonical tiny M6 class; custom research problems continue through the Python API.

No independent human participant was recruited. These are scripted cold-path stories and must not be described as a user study.
