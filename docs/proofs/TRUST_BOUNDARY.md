# M4 trust boundary

For the committed V3 result, the trusted computing base includes Python and exact rational arithmetic, EIR construction and validation, mechanism/property semantics, finite enumeration, canonical serialization, the truth-table compiler, SHA-256, filesystem/process behavior, Carcara, and the operating system. cvc5 is the untrusted proof producer in the proof-checking step, although its API is used to build terms.

Carcara is independently implemented but not formally verified. The certificate eliminates the need to trust cvc5's UNSAT answer; it does not eliminate the need to trust Carcara or the economic-to-propositional translation.

This is strictly narrower than a direct independently checked arithmetic proof. The attempted direct QF_LIRA path yielded `holey`, so it is not represented as V3. The scope remains finite and bounded; no unbounded theorem is claimed.
