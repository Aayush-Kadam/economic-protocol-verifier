# ADR 0003: Certificate strategy

Status: experimental.

In M4, generate a hash-stable SMT-LIB obligation, request cvc5 proof output, and check it with Carcara only for demonstrated supported theories. A passed Carcara run may qualify as V3 independent checking, with the caveat that Carcara is an independently implemented but not formally verified checker. Unsupported rules or checker failures downgrade the result; they are never bypassed.

