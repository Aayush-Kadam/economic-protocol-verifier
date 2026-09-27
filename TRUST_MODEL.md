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

M3 adds solver-case decoding, typed witness construction, exact minimization, canonical certificate serialization, validation, and rendering. Decoder/minimizer/serializer correctness is tested and remains trusted. Replay uses the M1 evaluator rather than backend expressions, but compilation and replay still share EIR semantics. The renderer is untrusted presentation: only certificate validation and replay establish the violation.

## Later solver path

For V2, users additionally trust the IR-to-SMT compiler and solver soundness. For V3, an independently implemented checker must accept a proof for the exact hash-bound SMT formula. The checker itself remains in the TCB unless formally verified. cvc5 documentation states that Alethe output supports only parts of arithmetic and quantifiers; therefore certificate availability must be established experimentally per formula, not inferred from `unsat`.

## Fail-closed rules

- timeout, exception, incomplete enumeration, unsupported operator, parse ambiguity, missing tie-break, and certificate-check failure cannot produce acceptance;
- exact integers/rationals only in the trusted path;
- every witness is replayed;
- every artifact binds source, canonical IR, property version, formula, solver configuration, and checker result by hashes;
- UI labels are derived from machine status and cannot upgrade assurance.

## M5 expansion

Matching ranking validation, deferred-acceptance execution, blocking-pair enumeration, fair-division bundle valuation, EF1/Pareto enumeration, and the domain-to-truth-table compilers join the trusted base. cvc5/Z3 agreement detects backend discrepancies but not a shared evaluator error. New V3 proofs remove trust in cvc5's UNSAT answer only; Carcara and each economic translation remain trusted.

## M6 synthesis

The synthesis-problem compiler, table enumerator, candidate decoder, membership checks, objective/prior evaluator, repair-distance evaluator, minimal-core validator, and status interpreter are trusted. Every SAT candidate is passed through normal property evaluators. Exhaustive enumeration independently establishes the reported tiny-domain optima and repair minima. Carcara checks only the compiled bounded-UNSAT truth table, not completeness of candidate enumeration or economic translation.

## M7 evidence update

Domain evaluators and compilers are differentially validated but remain trusted because all grounded backends consume their materialized cases. Proof syntax is independently checked by pinned Carcara; economic translation is not. EPL parsing was fuzzed, certificate and synthesis bindings were attacked, and independent hand/table oracles supplement production expectations. Python, canonical serialization, SHA-256, and the host/WSL boundary remain trusted.
