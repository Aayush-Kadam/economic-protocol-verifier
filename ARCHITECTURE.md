# Architecture

## Decision

Use a small Python 3.12 package first, not the full proposed monorepo. Layers are one-way:

`EPL source -> parsed syntax -> typed EIR -> canonical JSON -> property witness problem -> backend -> replay/check -> result manifest`.

The reference enumerator and semantic evaluator precede SMT integration. A web application is deferred until M8.

M2 adds strict JSON EPL, source-located syntax/semantic errors, a frozen AST, EIR elaboration, a solver-neutral grounded witness IR, separate cvc5/Z3 AST translators, and independent witness replay. The grounded compiler is deliberately finite and does not establish symbolic real-domain theorems.

## Initial layout

```text
src/epv/{eir,semantics,properties,verification,provenance}
tests/
benchmarks/
docs/{adr,literature,milestones}
```

## ADR summary

- Python 3.12: rapid exact-model prototyping and mature testing; all trusted values use `int` or `fractions.Fraction`.
- Exhaustive backend first: provides a transparent finite oracle for later differential tests.
- cvc5 candidate primary, Z3 candidate differential backend: neither is part of M1.
- Alethe/Carcara experiment in M4: no blanket V3 promise because theory coverage is partial and Carcara is not formally verified.
- Lean 4 deferred as the likely single theorem-prover experiment: active ecosystem and small proof-checking kernel, but integration cost and recent kernel soundness fixes require pinned versions and adversarial validation. Isabelle remains especially relevant prior art and a possible reconstruction target.
- YAML-like syntax deferred until semantic IR stabilizes; canonical JSON is the interchange and hash surface.

## M5 domain architecture

Shared infrastructure consists of grounded witness problems, cvc5/Z3 adapters, provenance, counterexample binding, and Alethe validation. `matching.py` and `fair_division.py` retain separate semantic objects and evaluators. `property_registry.py` enforces domain applicability. No universal utility abstraction is introduced.
