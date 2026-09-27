# Certificate attacks

Nineteen committed attacks mutate every manifest binding class, delete problem/proof files, and truncate proof bytes at multiple offsets after recomputing the proof hash. All fail closed. Historical cross-property, cross-mechanism, and cross-domain reuse tests also pass.

Checker identity/version, timeout, missing executable, malformed status, and `holey` remain non-accepting. Validation always reruns pinned Carcara; manifest assurance text cannot grant V3.
