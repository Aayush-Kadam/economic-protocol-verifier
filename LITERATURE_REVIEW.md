# Literature Review

Search date: 2026-09-27. Sources prioritize peer-reviewed papers, publisher pages, official documentation, and primary repositories. Structured records are in `docs/literature/sources.json`.

## Findings

### Automated mechanism design and synthesis

Conitzer and Sandholm established automated mechanism design and complexity results in the early 2000s; important deterministic variants are NP-complete. Thus synthesis is not an EPV novelty. Mittelmann, Maubert, Murano, and Perrussel's 2025 *Artificial Intelligence* paper uses Strategy Logic to model, verify, and synthesize social-choice mechanisms. This is the closest high-level overlap and makes any general “verification plus synthesis” priority claim untenable.

### Proof-assistant verification

Caminati et al. and the ForMaRE line specify Vickrey/VCG auctions in Isabelle/HOL, prove functional and allocation properties, and generate verified executable code. Barthe et al. use formal proof methods for incentive compatibility of VCG and a randomized Bayesian reduction. The `mech.v` Coq/Mathematical Components project supplies reusable definitions for deterministic mechanisms, auctions, truthfulness, VCG, and matching-related work. Hence machine-checked economic mechanism semantics and proofs are established.

### SAT/SMT and social choice

Tang and Lin initiated SAT-supported impossibility proofs; later work searched for strategy-proof rules and impossibility cores. Brandl et al. encode efficiency/strategy-proofness constraints in quantifier-free linear real arithmetic, extract a minimal unsatisfiable set, and reconstruct a proof in Isabelle/HOL. The COMSOC codebase provides reusable SAT-based reasoning and MUS tooling. Automated axiom reasoning, countermodels, and impossibility search are therefore established.

### Proof production

cvc5 can emit Alethe proofs, but its documentation explicitly limits support to equality/uninterpreted functions and parts of arithmetic and quantifiers. Carcara independently checks and elaborates Alethe proofs, but cvc5 documentation notes that Carcara is not formally verified. Certificate support must be measured for EPV-generated formulas; it cannot be promised for every conclusive SMT result.

### Theorem-prover choice

Isabelle has directly relevant auction and SMT-reconstruction precedents. Coq has `mech.v` and mature Mathematical Components infrastructure. Lean 4 offers a compact kernel, extensibility, and active libraries, but recent releases document kernel soundness fixes; a pinned and independently auditable toolchain is necessary. M0 defers the integration decision while tentatively selecting Lean for a narrow M4 reconstruction experiment, not wholesale reimplementation.

## Landscape conclusion

No reviewed source combines every proposed EPV operational feature, but nearly every individual scientific ingredient has strong prior art. The defensible research question is whether an integrated, explicit, reproducible workflow can improve assurance and usability without hiding the formalization gap. This is primarily an integration/verification-engineering hypothesis until evaluation demonstrates a scientific contribution.

## Search limitations

Keyword and citation-chain search cannot prove nonexistence. The 2025 Strategy Logic work is recent and requires deeper artifact-level comparison before publication claims. M0 should be revisited before any paper submission.

