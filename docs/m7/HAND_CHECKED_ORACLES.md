# Hand-checked oracles

## Tiny DSIC failure

In first price at reports `(2,0)`, bidder 0 with true value 2 pays 2 and receives utility 0. Reporting 0 ties and wins by lowest-index tie-break while paying 0, giving utility 2. The gain is exactly 2.

## Budget failure

The subsidy mechanism at `(0,0)` transfers `-1` from the winner and `0` from the loser. Mechanism balance is `-1`, so maximum deficit is at least and, by enumeration, exactly 1.

## Blocking pair

In the canonical fixed matching, `p0-r0` and `p1-r1`, both `p1` and `r0` prefer each other to their assigned partners. They form a blocking pair.

## Envy and EF1

For values `a1=(3,3,3)` and bundles `a0={g0,g2}`, `a1={g1}`, agent 1 values its bundle at 3 and agent 0's at 6. Removing either one good leaves value 3, so envy exists but EF1 holds.

## Synthesis optimum

The 16 payment tables on `{0,1}` can be listed directly. Filtering DSIC, IR, WBB, feasibility, and efficiency and applying the uniform prior gives maximum expected revenue `1/2`.
