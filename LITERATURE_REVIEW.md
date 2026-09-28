# Literature review

Search date: 2026-09-28. This M8 review compares prior work with EPV as implemented, not with the original proposal.

## Automated mechanism design

Conitzer and Sandholm introduced automated mechanism design and analyzed its computational complexity in 2002. Consequently, EPV's finite search is neither a new research area nor a new synthesis paradigm. EPV contributes explicit search-class manifests, exhaustive post-verification, certificate binding for one bounded-UNSAT case, and repair provenance at tiny scale.

Mittelmann, Maubert, Murano, and Perrussel's *Formal verification and synthesis of mechanisms for social choice* (Artificial Intelligence 339, 2025) is the closest conceptual overlap: one formal setting supports both checking and synthesis. It prevents any claim that integrated verification and synthesis is new. EPV differs operationally in its cross-domain executable semantics, economic counterexample artifacts, hash-bound Alethe path, and hostile release validation; the comparative scientific value remains to be judged externally.

## Formal mechanism and auction verification

Caminati, Kerber, Lange, and Rowat use Isabelle/HOL to specify VCG auctions, establish intended properties, and generate verified executable code. Related ForMaRE work compares theorem provers for auction theory. Barthe and collaborators verify incentive properties including VCG truthfulness and Bayesian constructions. The `mech.v` project supplies a Coq/Mathematical Components foundation for mechanism definitions and proofs, including auctions and matching-related material. These systems provide stronger theorem-level assurance than EPV's finite checking for their formalized results.

EPV therefore claims neither formal-semantics priority nor stronger proof foundations. Its difference is a bounded, automatic, certificate-and-counterexample workflow aimed at rapid inspection of small protocol instances.

## SAT/SMT social choice and countermodels

SAT/SMT encodings, countermodels, impossibility search, and minimal cores are established in computational social choice. Brandl et al. notably combine QF_LRA solving, minimal inconsistent sets, and Isabelle/HOL reconstruction for a strategyproofness/efficiency incompatibility. EPV's exact-minimum economic witnesses and uniform replay format are an artifact design choice, not the invention of counterexample-guided analysis or MUS extraction.

## Proof-producing SMT

Alethe is an SMT proof format, cvc5 produces Alethe for supported fragments, and Carcara is an independent checker/elaborator. EPV reuses this infrastructure. Its contribution is the binding policy from economic identity and assumptions to exact problem/proof bytes, plus fail-closed fresh checking. Carcara checks the compiled refutation; it does not validate the economic translation and is not itself a formally verified kernel.

## Verification DSLs and proof-carrying systems

Domain-specific verification languages and proof-carrying artifacts are broad established ideas. EPL 0.1 is intentionally small and template-based. Its research value, if any, lies in making assumptions, report/type separation, bounds, and provenance explicit; no language-theory novelty is claimed.

## Cross-domain scope

EPV applies one assurance vocabulary to deterministic single-item auctions, strict one-to-one matching, and additive indivisible-goods fair division. Prior libraries and logics are often more general, and individual domain algorithms/theorems are classical. Cross-domain packaging is an engineering contribution unless external evaluation demonstrates a deeper reusable abstraction.

## Conclusion

The appropriate framing is an assurance-oriented research artifact and systems/demo contribution. A workshop, demo, or software/artifact paper is better supported than a theorem-focused formal-methods paper or an economics-theory paper. The next gate is independent review, not publication.

## Primary sources

- Conitzer and Sandholm, *Complexity of Mechanism Design*, UAI 2002, https://arxiv.org/abs/cs/0205075
- Caminati et al., *Sound Auction Specification and Implementation*, 2015, https://doi.org/10.1145/2764468.2764511
- Barthe et al., *Computer-aided Verification in Mechanism Design*, https://arxiv.org/abs/1502.04052
- Jouvelot and Gallego Arias, `mech.v`, https://github.com/jouvelot/mech.v
- Brandl et al., *Proving the Incompatibility of Efficiency and Strategyproofness via SMT Solving*, https://arxiv.org/abs/1604.05692
- Mittelmann et al., *Formal verification and synthesis of mechanisms for social choice*, https://doi.org/10.1016/j.artint.2024.104272
- Carcara project and TACAS paper, https://github.com/ufmg-smite/carcara
