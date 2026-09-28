# Theory trust boundary

The formal claim begins only after the user's intended institution has been represented in EPV's finite semantics. That representation step is a human responsibility.

The semantic pipeline is `EPL/source -> typed EIR or domain object -> economic evaluation -> violation cases -> exhaustive/SMT result -> optional certificate`. Carcara checks only the final compiled SMT refutation. It does not check the earlier arrows. Backend agreement, hand oracles, mutation testing, and hostile validation test those arrows but do not prove them.

See the repository-root `TRUST_AND_ASSURANCE.md` for the canonical operational statement.
