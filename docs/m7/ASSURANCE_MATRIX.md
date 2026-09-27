# Component assurance matrix

| Component | Unit | Differential | Mutation | Fuzz/attack | Independent checker |
|---|---:|---:|---:|---:|---:|
| EPL parser | yes | semantic formatting | yes | 206 inputs | N/A |
| Auction property compiler | yes | 384 cases | yes | generated tables | partial truth-table path |
| Matching compiler | yes | 72 cases | yes | generated rankings | partial truth-table path |
| Fair-division compiler | yes | 128 cases | yes | generated values | partial truth-table path |
| Witness replay/minimizer | yes | cvc5/Z3 witnesses | yes | tamper/tie cases | no |
| Proof validator | yes | historical bundles | yes | 19 new attacks | Carcara |
| Synthesis/repair | yes | 32 requirement sets | yes | bounds/prior/tamper | post-verification; one UNSAT Carcara proof |

Static review found 17 source/test references to V3, ACCEPTED, or BOUNDED VERIFIED. Production V3 manifests are written only by proof-bundle constructors and are never accepted without exact binding checks plus a fresh pinned-Carcara `valid` result.
