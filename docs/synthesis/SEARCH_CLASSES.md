# Search classes

M6 supports two two-bidder table classes on explicitly listed values. `efficient-lowest-index-tie` fixes the allocation rule and searches one bounded winner payment per report profile. `all-feasible` searches `none`, bidder 0, or bidder 1 per profile plus bounded winner payments. Loser payment is an explicit normalization.

For `k` profiles, `a` allowed allocation choices, and `p` payment values, the naive size is `(a*p)^k`; fixed allocation reduces this to `p^k`. No anonymity constraint is silently imposed.
