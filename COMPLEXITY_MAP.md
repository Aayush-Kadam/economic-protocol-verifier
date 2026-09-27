# Complexity and Decidability Map

| Fragment / property | Reference decision method | Formula shape | Complexity / risk | M1 stance |
|---|---|---|---|---|
| Finite DSIC checking | enumerate agent, true type, deviation, other reports | existential witness after negation | polynomial in explicit normal-form table size; exponential in succinct per-agent domain encoding | supported |
| Finite ex-post IR | enumerate truthful profiles | existential linear-rational inequality | proportional to profile count | supported |
| Finite weak budget balance | enumerate report profiles | existential sum inequality | proportional to profile count | supported |
| Finite feasibility | enumerate reports and run total predicate | existential predicate failure | depends on feasibility predicate; finite/decidable | supported only for built-in finite predicates |
| Bounded synthesis | existential rule-table cells plus universal finite constraints, flattened to SAT/SMT | QF finite-domain / LIA/LRA depending encoding | generally combinatorial; automated mechanism design is NP-hard in important settings | deferred to M6 |
| Symbolic linear integer DSIC | negated existential with piecewise allocation | QF_LIA if finite branching is fully expanded | decidable but can blow up | experimental after oracle |
| Symbolic linear rational/real DSIC | negated existential | QF_LRA under linear restrictions | decidable; certificate coverage must be tested | experimental |
| Nonlinear utilities | nonlinear arithmetic | QF_NIA/NRA or quantified variants | hard; solver completeness/proof support limited | outside initial fragment |
| Randomized/BIC | exact probabilities and expectations with priors | sums, products, quantifier alternation | semantic and arithmetic complexity; prior formal work exists | excluded |
| General voting impossibility | rule variables with axiom constraints | SAT/SMT, often symmetry reduction | finite reductions can be large; lifting requires proof | research-only |
| Matching stability | finite preference profiles and blocking-pair witness | finite existential | finite but domain-specific semantics | not before M5 |

Enumeration counts are always reported from the declared Cartesian products; no asymptotic label substitutes for measured instance size.

