# M8 hostile referee audit

This document records questions and evidence-based responses, not fictional reviewer quotations.

## Formal-methods referee

**Is the property compiler formally verified?** No. It is tested by exhaustive reference comparison, two solver adapters, hand oracles, mutation analysis, and metamorphic tests. Common-mode semantic errors remain possible.

**What does Carcara certify?** It checks the Alethe refutation of the exact hash-bound propositional SMT problem. It does not certify the economic source-to-formula translation.

**Are proofs bounded?** Yes. Every current proof represents an explicitly finite truth table.

**How is solver disagreement handled?** It is reported as a discrepancy and cannot become verification. M7 observed none across 1,168 solver runs.

**Why trust EIR?** EIR and evaluators remain in the trusted base. Evidence reduces risk but is not a proof of correctness.

**Is synthesis brute force?** Yes, for current table classes. This is stated as a limitation and used as an independent finite optimality oracle.

**How novel is the integration?** Individual ingredients are established. Novelty is plausible only in the complete assurance-oriented workflow and hostile artifact methodology; no priority claim is made.

**Are benchmarks circular?** Production expectations are supplemented by hand oracles, classical examples, independent solver adapters, mutation tests, and adversarially constructed failures. Shared semantic code remains a circularity risk.

**Does scaling make EPV impractical?** Beyond small instances, probably without new representations. Current measurements are explicitly not extrapolated.

## Economist referee

**Are assumptions explicit?** Auction private values, quasi-linearity, transfer sign, outside option, tie break, matching ordinal structure, and fair-division additivity are represented and documented.

**Are ordinal and cardinal semantics separated?** Yes. Matching uses rankings only; fair division and auctions use exact cardinal values.

**Are utility and transfers correct?** Utility uses true type and agent-paid transfer; regressions separate true types from deviation reports and check sign errors. The evaluator is still trusted.

**Are benchmark theorems used under correct assumptions?** Classical results motivate cases; EPV independently claims only committed finite instances.

**Does bounded checking teach anything?** It can falsify implementations/specifications, provide complete coverage within pedagogical or regression bounds, and expose exact witnesses. It does not replace theory.

**Is synthesis tautological?** The class is heavily constrained and tiny. Its value is demonstrating auditable search/post-verification, not discovering broad mechanisms.

**What does fairness mean?** Only the named property—envy-free, EF1, feasibility, or Pareto efficiency—under additive valuations. No generic fairness guarantee is claimed.

## Programming-languages referee

**What is the DSL contribution?** EPL 0.1 makes a narrow auction fragment readable and fail-closed. It is a useful interface experiment, not a new general-purpose language.

**Is there a formal grammar?** The accepted JSON schema and semantic restrictions are executable; there is no mechanized grammar/semantics proof.

**What is the TCB?** It is enumerated in `TRUST_AND_ASSURANCE.md`, including parser, EIR, evaluators, compilers, runtime, hashing, and checker.

**Are hashes/versioning principled?** Canonical serialization and explicit schema/property versions bind artifacts. M7's line-ending defect shows the design must include release transport, now guarded by binary attributes and clean-archive tests.

**Is this a Python wrapper around solvers?** More than a thin call wrapper because it defines economic semantics, violation enumeration, typed witnesses, replay, assurance levels, and synthesis. It is less than a verified-language implementation because those components remain trusted Python.

## Systems referee

**Is it reproducible?** Representative and full commands exist; a clean Git-archive run is required. A truly hermetic network rebuild is not claimed because the pinned Carcara/WSL toolchain is reused locally.

**How much setup is required?** Python 3.12 plus locked cvc5/Z3 wheels; V3 additionally requires pinned Carcara and WSL on the validated Windows path.

**Are failures safe?** Parser, solver, certificate, timeout, missing-file, and version errors fail closed. User-facing CLI errors avoid stack traces for expected failures.

**Is the architecture maintainable?** The CLI is a thin layer over existing APIs and does not duplicate verification logic. The compact kernel is readable, but some M6 modules are intentionally terse and deserve refactoring after review, not during release freeze.

## Decision

Strongest objections are the trusted semantic translation, small scale, limited DSL, and uncertain integration novelty. They preclude a strong formal-verification or economics-theory claim but do not preclude external review of a bounded research artifact.
