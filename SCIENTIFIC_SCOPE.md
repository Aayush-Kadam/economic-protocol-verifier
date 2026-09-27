# Scientific Scope

## Initial verified fragment

EPV M1 targets deterministic direct-revelation mechanisms with:

- a finite, explicitly enumerated agent set;
- finite integer or exact rational type and report spaces;
- finite outcomes and deterministic allocation/payment rules;
- quasi-linear utility `u_i(theta_i, x, p) = v_i(theta_i, x) - p_i`;
- payments signed as money paid by the agent to the mechanism;
- explicit deterministic tie-breaking;
- total mechanism functions; and
- exhaustive verification of DSIC, ex-post IR, weak budget balance, and feasibility.

The M1 status for a universally quantified property is `BOUNDED VERIFIED`, never unrestricted `VERIFIED`, because all declared spaces are finite.

## Semantics

A mechanism consumes reports, not true types:

`M : R_1 x ... x R_n -> X x Q^n`.

Utility evaluates the resulting outcome and payment using the agent's true type. A DSIC violation is a tuple `(i, theta_i, r'_i, r_-i)` with

`u_i(theta_i, M(r'_i, r_-i)) > u_i(theta_i, M(theta_i, r_-i))`.

Truth and report are distinct typed values even when their carrier sets coincide.

## Explicit exclusions

M1 excludes randomized mechanisms, Bayesian properties, continuous/unbounded domains, indirect mechanisms, interdependent values, dynamic games, coalitions, approximate arithmetic, and implementation conformance. These require separate semantics and gates.

## Defensible contribution hypothesis

The plausible contribution is not a new theorem prover or a new concept of strategy-proofness. It is an integrated, fail-closed workflow combining a readable economic specification, typed canonical IR, property-to-witness compilation, exhaustive oracle comparison, replayable economic counterexamples, explicit assumption/provenance manifests, and independently checked solver evidence where the proof format supports the exact theory.

## M5 cross-domain scope

M5 adds strict one-to-one ordinal matching and finite additive-cardinal fair division alongside auctions. Matching comparisons use rank relations only; fair division uses exact nonnegative integers. Voting is deferred. All claims remain bounded to declared instances and report/valuation spaces.

## M6 synthesis scope

M6 searches explicit finite two-bidder auction tables and integer reserve grids. SAT, optimality, repair, and UNSAT statements apply only to the declared allocation family, payment values, normalization, property versions, and prior. No bounded result is promoted to a general impossibility or characterization theorem.

## M7 validation scope

M7 supplies adversarial evidence for the existing bounded fragments. It does not expand supported economics. Generated differential tests, parser fuzzing, mutation analysis, certificate attacks, clean-archive replay, and scaling measurements reduce—but do not eliminate—the risk of common-mode translation errors.
