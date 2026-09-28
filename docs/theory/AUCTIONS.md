# Auctions

EPV's auction fragment is a deterministic direct mechanism `M : R_1 x ... x R_n -> X x Q^n` over explicit finite integer type/report spaces. Transfers are money paid by an agent to the mechanism. Utility is `u_i(theta_i, M(r)) = theta_i * x_i(r) - p_i(r)`, with an explicit outside option and deterministic tie breaking.

DSIC excludes every tuple `(i, theta_i, r'_i, r_-i)` for which deviation utility is strictly greater than truthful utility. Ex-post IR requires truthful utility at least the outside option. Weak/strong budget balance constrain the sum of transfers. Feasibility enforces single-item capacity. Allocative efficiency compares the selected allocation with every declared feasible allocation.

Results are finite: quantifiers range only over the declared spaces. EPL 0.1 supports two-agent templates; the Python reference layer supports selected larger finite second-price experiments.
