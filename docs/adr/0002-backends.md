# ADR 0002: Backend order

Status: accepted.

Implement exhaustive enumeration first. Add cvc5 only after the reference predicates and witness replay are stable; add Z3 as a differential backend. Solver agreement is evidence about translation, not a proof that both encodings are correct.

