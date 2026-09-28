# Trust and Assurance

This is EPV's canonical trust statement.

## V1 - bounded exhaustive verification

V1 enumerates every case in the declared finite domain using EPV's reference semantics. A successful result means no violating case was found in that domain. Users trust the EPL parser/elaborator, EIR data model, economic evaluator, property predicate, exact arithmetic, Python runtime, canonical serialization, and host platform.

## V2 - bounded solver-established verification

V2 compiles violation cases into a neutral witness problem and asks cvc5 or Z3 whether a violating case exists. It adds independently implemented backend adapters and catches many backend-specific defects through agreement. It does not remove trust in the shared economic evaluator or grounding compiler. Users additionally trust the selected solver's answer.

## V3 - bounded independently certificate-checked verification

For supported small obligations, cvc5 emits Alethe evidence and pinned Carcara freshly checks the exact SMT-LIB problem/proof pair. Manifest hashes bind mechanism or semantic identity, property/version, domain, assumptions, problem bytes, proof bytes, producer, checker, and EPV commit. Acceptance requires exact bindings and Carcara's `valid` result.

V3 removes the need to trust cvc5's UNSAT answer for that compiled obligation. It does **not** independently validate the translation from economic semantics to the propositional truth table. Carcara is an independent checker, not a formally verified kernel, and remains trusted.

## Counterexamples

Negative certificates bind a mechanism hash, property version, logical-problem hash, domain, assumptions, backend origin, typed witness, exact-minimum criterion, and replay status. Replay recomputes the global minimum violating witness and evaluates it through the authoritative semantics. The solver model and renderer are not trusted for acceptance. The shared evaluator still is.

## Synthesis and repair

The problem compiler, finite-class enumerator, objective, candidate decoder, class-membership checks, and result interpreter are trusted. SAT candidates are post-verified. Exhaustive enumeration establishes reported optimum/minimum within the declared class. One bounded-UNSAT truth-table obligation has a V3 bundle; that certificate does not prove the search class is economically complete or general.

## Fail-closed behavior

Timeout, missing checker, unexpected checker version, malformed input, unsupported construct, missing artifact, hash mismatch, replay failure, and unsupported proof rule never become acceptance. UI/CLI presentation cannot upgrade assurance.

## What hashes do and do not protect

SHA-256 bindings detect accidental or adversarial substitution of the bound bytes and context, assuming SHA-256 and serialization are correct. They do not show that the source captures the user's intent, that the compiler is correct, or that the host is uncompromised.

## Explicitly not formally verified

EPL parsing, EIR elaboration, economic evaluators, property compilers, synthesis enumeration, Python, canonical serialization, hash implementation, Carcara, operating-system/WSL transport, and the mapping from real institutions to EPL are not machine-verified.
