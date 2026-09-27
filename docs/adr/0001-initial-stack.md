# ADR 0001: Initial stack

Status: accepted for M1.

Use Python 3.12 with frozen dataclasses, enums, static type annotations, `fractions.Fraction`, and the standard-library test runner. Avoid third-party runtime dependencies in M1. This minimizes installation and makes exhaustive semantics easy to audit. Revisit only after profiling or soundness evidence.

