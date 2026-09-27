# Checker support matrix

| Obligation | cvc5 production | Carcara result | M4 classification |
|---|---:|---:|---|
| Canonical propositional truth table (QF_UF) | yes | `valid` | V3 bounded when all bindings match |
| Grounded QF_LIRA economic formula | yes | `holey` | unsupported; at most V2 |
| SAT/counterexample formula | no UNSAT proof | not applicable | M3 counterexample route |
| Unknown/timeout/error | no accepted proof | not accepted | no V3 |

The supported M4 property vocabulary is DSIC, ex-post IR, weak budget balance, strong budget balance, feasibility, and allocative efficiency over finite deterministic direct mechanisms. A particular property earns V3 only when its canonical formula is UNSAT and the checker accepts its proof. Falsified instances do not receive positive certificates.

| Property | Certified mechanism | Result |
|---|---|---|
| DSIC | second-price auction | accepted |
| Ex-post IR | second-price auction | accepted |
| Weak budget balance | second-price auction | accepted |
| Strong budget balance | always-agent-zero, zero transfers | accepted |
| Feasibility | second-price auction | accepted |
| Allocative efficiency | second-price auction | accepted |

The DSIC instance uses two bidders with values and reports `{0,1,2}` and contains 54 concrete deviation candidates. All six bundles are committed under `proofs/`.
