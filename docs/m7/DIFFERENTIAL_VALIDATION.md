# Differential validation

Seed `7001` generated 64 auction tables, 24 strict matching markets, and 32 fair-division instances. These produced 584 property evaluations and 1,168 solver runs. Reference, cvc5, and Z3 agreed on every result; unknown, timeout, error, and unexplained discrepancy counts were zero.

Auction expectations additionally came from a separately coded direct table oracle. Matching and fair-division witness truth was compared with grounded solver obligations and exact domain enumeration.
