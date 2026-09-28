# Limitations

- All verification is finite and bounded; EPV establishes no unrestricted economic theorem.
- Auctions are deterministic single-item direct mechanisms over exact finite values/reports. EPL 0.1 has fixed templates.
- Matching is one-to-one with strict complete rankings; strategic evidence is confined to a canonical 2x2 domain.
- Fair division uses additive nonnegative integer values and small complete allocations.
- Voting, Bayesian/randomized mechanisms, continuous domains, dynamic games, coalitions, ties/capacities, EFX, and deployed-code conformance are unsupported.
- Economic source/EIR to logical obligation remains trusted. Counterexample replay shares authoritative economic semantics.
- V3 checks compiled propositional truth tables, not the economic translation. Carcara is independently implemented but not formally verified.
- Full synthesis and repair are auction-only and tiny. Optimality/minimality and UNSAT apply only to the declared finite class.
- Current proof checking uses a pinned Carcara build through WSL on the validated Windows setup.
- Dependency versions are pinned, but wheel hashes are not locked and the M8 clean install reuses locally available distributions/toolchains; hermetic network rebuild is not claimed.
- Mutation analysis is targeted; solver validation used one cvc5 and one Z3 version.
- Scaling evidence is machine-specific and reaches only selected four-bidder/two-value DSIC checks and 81-candidate synthesis.
- Fresh-user stories are scripted, not independent human-subject evaluation.
- No local web playground was implemented; the CLI is the demonstration interface.
