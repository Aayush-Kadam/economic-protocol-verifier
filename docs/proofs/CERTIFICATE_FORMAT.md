# Proof certificate format

`epv-proof-certificate-v1` is a directory containing `manifest.json`, `problem.smt2`, and `proof.alethe`.

The manifest records `assurance`, `property`, `property_version`, `mechanism_hash`, the full canonical mechanism document, `domain`, sorted `assumptions`, `logical_problem_hash`, `proof_hash`, `proof_format`, producer identity/version, checker identity/version/required result, and `epv_commit`.

Validation recomputes the mechanism, domain, assumptions, property formula, and both byte hashes before invoking Carcara. The stored mechanism document is audit evidence; the semantic hash is recomputed from the caller's mechanism. A certificate cannot be replayed against another mechanism, property, domain, assumption set, formula, or proof.

V3 is an outcome of successful validation, not a trusted string in the manifest. The `assurance` field is descriptive and never consulted to bypass validation.
