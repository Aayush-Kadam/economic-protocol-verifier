# Counterexample Model

`epv-counterexample-v1` is a canonical JSON certificate envelope. It binds a typed property witness to the mechanism semantic hash, versioned property, logical-problem hash, finite domain, assumptions, backend origin, replay result, and declared minimality result.

Property payloads are separate frozen dataclasses for DSIC, IR, budget balance, feasibility, and efficiency. Exact numbers serialize as normalized integer/rational strings; floats are never used. A witness proves existence of the displayed violation in the declared domain. It does not prove that the mechanism has no other defects or that the witness is globally simplest under any objective other than the recorded one.

