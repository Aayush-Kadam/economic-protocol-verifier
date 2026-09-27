# M4 proof pipeline

EPV M4 proves a deliberately narrow statement. The trusted finite evaluator enumerates every candidate violation of a property using exact `Fraction` arithmetic. It emits a canonical QF_UF truth table: one Boolean atom per concrete witness candidate, an assertion that at least one violation exists, and the exact truth value of every atom. For a valid bounded property this formula is UNSAT.

cvc5 1.4.1 produces an Alethe proof with `produce-proofs=true`, `proof-format-mode=alethe`, `simplification=none`, `dag-thresh=0`, and `proof-granularity=theory-rewrite`. EPV removes only cvc5's outer list wrapper. Carcara 1.1.0 at commit `051d2f79ccd3d5736bb3d93356f05df3dfc696e9` checks the proof and exact SMT-LIB problem.

Only exit code zero plus the exact final output `valid` is acceptance. `holey`, invalid output, parse failure, timeout, missing executable, and operating-system error are non-acceptance. In particular, cvc5 `unsat` alone is only solver evidence, never V3.

## Reproduction

Install Python dependencies with `pip install -e .[m2]`. Build Carcara from the pinned commit with its pinned Rust toolchain (`cargo build --release --locked`) and place the executable at `.tools/carcara-current`. On Windows, validation invokes that Linux binary through WSL. Run `python -m unittest discover -s tests -v`.

The committed `proofs/second_price_dsic` bundle is the representative scientific artifact. Its manifest binds the semantic mechanism, property and version, finite domain, assumptions, exact SMT bytes, proof bytes, producer, checker, and EPV revision.

## Boundary

The independent checker validates propositional unsatisfiability, not EPV's economic evaluation. The evaluator, canonical mechanism materialization, witness enumeration, and truth-table compiler remain trusted. Direct arithmetic Alethe output was tested and Carcara returned `holey`; it is explicitly outside M4 V3.
