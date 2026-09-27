# EPV Benchmark v0.1

The machine-readable corpus is `benchmarks/m5/registry.json`: 12 cases, four per supported domain, with six positive and six negative cases. Every entry identifies its domain, mechanism, immutable property ID, expected status, assumptions, polarity, and certificate availability.

Property vectors deliberately separate guarantees: deferred acceptance is stable on the declared market while the fixed rule is not; round robin is feasible and EF1 on the canonical instance but not envy-free; Vickrey and first-price auctions differ on DSIC.

Canonical theorem motivation follows [Vickrey's original second-price auction paper](https://doi.org/10.1111/j.1540-6261.1961.tb02789.x), [Gale and Shapley's original deferred-acceptance analysis](https://doi.org/10.1080/00029890.1962.11989827), and published round-robin/EF1 research such as [Amanatidis et al.](https://arxiv.org/abs/2301.13652). M5's claims remain independently established only for the committed finite instances, not inferred as unrestricted theorems.
