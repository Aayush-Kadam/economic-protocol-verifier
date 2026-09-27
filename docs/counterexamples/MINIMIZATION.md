# Exact Minimization

M3 enumerates every replay-valid case in the finite compiled witness problem and chooses the global lexicographic minimum under:

1. number of nonzero numeric witness fields;
2. sum of absolute numeric magnitudes;
3. sum of rational denominators;
4. canonical JSON lexical order.

The result is labeled `EXACT LEXICOGRAPHIC MINIMUM`, meaning minimum only under this declared objective and domain. No heuristic simplifier is used. Transfers and derived gaps are included because minimization operates on the complete typed economic witness.

