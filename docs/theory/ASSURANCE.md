# Assurance levels

| Level | Meaning | Evidence | Still trusted |
|---|---|---|---|
| V1 | bounded exhaustive verification | every declared finite case evaluated | semantics, evaluator, predicate, runtime |
| V2 | bounded solver-established verification | cvc5 or Z3 establishes no compiled violation | shared translation plus selected solver |
| V3 | bounded independently certificate-checked verification | pinned Carcara freshly accepts hash-bound Alethe for the compiled obligation | economic translation, Carcara, runtime/platform |

`BOUNDED VERIFIED` is never an unrestricted theorem. A failed or missing checker cannot produce V3.
