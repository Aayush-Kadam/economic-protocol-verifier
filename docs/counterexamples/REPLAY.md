# Counterexample Replay

Replay checks mechanism hash, property identifier/version, logical-problem hash, exact minimized witness, selected case, and replay status. The expected witness is recomputed from the authoritative M1 mechanism evaluator and finite property problem. Any mismatch is rejected.

Replay is independent of the cvc5/Z3 backend AST and raw model decoding, but it still shares the M1 EIR mechanism semantics with compilation. This reduces backend-decoder risk without eliminating the M2 common-mode EIR risk. A replay failure is an internal verifier error, never a user-facing counterexample.

