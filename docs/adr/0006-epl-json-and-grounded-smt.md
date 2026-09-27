# ADR 0006: JSON EPL and grounded finite SMT

Status: accepted for M2.

EPL uses strict JSON syntax rather than YAML to avoid implicit types and dependency-specific parsing. The initial compiler grounds the finite witness space into exact QF_LIRA comparison cases, then translates the solver-neutral IR independently to cvc5 and Z3 ASTs. This is intentionally bounded and not a claim of symbolic generality. Its advantage is auditability against M1 enumeration; its limitation is formula growth and shared dependence on EIR mechanism evaluation.
