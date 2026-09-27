# Reproducibility audit

Python dependencies remain pinned at cvc5 1.4.1 and z3-solver 5.1.0.0. Carcara is pinned to `051d2f79ccd3d5736bb3d93356f05df3dfc696e9` and identifies as `carcara 1.1.0 [git 051d2f7]`.

The full suite was repeated from a clean Git archive using the existing pinned virtual environment. V1, V2, V3, negative replay, synthesis, repair, and bounded UNSAT all reproduced. Windows hosts require WSL for the pinned Linux Carcara executable.
