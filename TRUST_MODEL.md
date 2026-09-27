# Trust Model

## Threat boundary

Users must trust that the formal mechanism matches their intent. Natural-language translation is outside the trusted boundary and may only propose EPL for review.

## M1 trusted computing base

- EPL/IR definitions and semantic elaborator;
- canonical serializer and hashing implementation;
- executable mechanism evaluator;
- property reference predicates;
- Python runtime and host platform.

The exhaustive backend is not called independent if it shares the same evaluator with witness replay. M1 therefore provides bounded assurance, not certificate independence.

M2 solver adapters translate a shared neutral witness IR separately, but the compiler grounds mechanism behavior through the same EIR evaluator. Three-way agreement detects many translation defects but cannot exclude a common EIR/compiler error. V2 therefore remains bounded and translation-dependent.

## Later solver path

For V2, users additionally trust the IR-to-SMT compiler and solver soundness. For V3, an independently implemented checker must accept a proof for the exact hash-bound SMT formula. The checker itself remains in the TCB unless formally verified. cvc5 documentation states that Alethe output supports only parts of arithmetic and quantifiers; therefore certificate availability must be established experimentally per formula, not inferred from `unsat`.

## Fail-closed rules

- timeout, exception, incomplete enumeration, unsupported operator, parse ambiguity, missing tie-break, and certificate-check failure cannot produce acceptance;
- exact integers/rationals only in the trusted path;
- every witness is replayed;
- every artifact binds source, canonical IR, property version, formula, solver configuration, and checker result by hashes;
- UI labels are derived from machine status and cannot upgrade assurance.
