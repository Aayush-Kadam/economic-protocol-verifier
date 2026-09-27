# Auctions

The historical EPL 0.1 two-bidder semantics are unchanged. M5 additionally exposes a programmatic N-bidder finite Vickrey benchmark for 2–4 bidders. The highest report wins; lowest index breaks ties; the winner pays the second-highest report; losers pay zero. Types and reports are exact finite private values and utility remains quasi-linear.

M5 verifies bounded DSIC, ex-post IR, weak budget balance, feasibility, and allocative efficiency for values `{0,1}` with 2–4 bidders through the reference compiler and both solver adapters. This is not a scalability claim or a change to EPL 0.1.
