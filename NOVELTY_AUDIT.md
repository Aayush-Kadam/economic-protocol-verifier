# Novelty Audit

## Verdict

**PASS WITH NARROWING.** The broad concept is not novel. Automated mechanism design, theorem-prover formalizations of auctions and incentive compatibility, SAT/SMT social-choice reasoning, and formal verification plus synthesis in Strategy Logic are established. A credible contribution may remain in the disciplined integration of a readable DSL, typed/canonical economic IR, systematic witness compilation, assumption auditing, counterexample replay/minimization, cross-backend differential checks, and proof-artifact provenance.

## Claims EPV must not make

- first formal verification of mechanisms, auctions, VCG, or incentive compatibility;
- first automated synthesis of mechanisms;
- first SAT/SMT application to social choice;
- first machine-checked impossibility result;
- solver `unsat` is inherently independently verified;
- bounded exhaustive checking proves an unrestricted theorem.

## Highest-risk overlap

Mittelmann et al. (Artificial Intelligence, 2025) already present formal verification and synthesis of social-choice mechanisms in Strategy Logic. `mech.v` provides a Coq/Mathematical Components foundation for deterministic mechanisms and auction properties. Caminati and collaborators formalized Vickrey/VCG specifications and executable code in Isabelle/HOL. Barthe et al. formally verified VCG truthfulness and a randomized BIC reduction. Brandl et al. used SMT plus Isabelle/HOL reconstruction for a social-choice impossibility.

## Remaining hypothesis

No source reviewed in M0 demonstrated the complete user-facing bundle under one auditable artifact format: readable economic DSL; explicit truth/report semantics; canonical hashes; multiple properties compiled to witnesses; minimal replayable economic counterexamples; exhaustive oracle differential testing; and formula-bound independently checked certificates. This is an absence-of-evidence observation, not a priority claim. It requires continued search and empirical comparison.

