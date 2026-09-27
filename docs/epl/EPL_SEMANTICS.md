# EPL 0.1 Semantics

Domains are inclusive integer intervals and elaborate to exact `Fraction` values with denominator one. M2 requires equal type and report intervals so truthful direct reporting is total.

Rules consume reports. `highest_report` allocates the item to the greatest report and, on equality, the lowest agent index. `agent_zero` always allocates to agent zero. `all_agents` deliberately allocates one unit to both agents and is an infeasibility benchmark.

`second_highest` charges the winner the losing report. `own_report` charges the winner its report. `winner_subsidy_one` assigns transfer `-1` to the winner. `zero` assigns zero transfers. A positive transfer is paid to the mechanism.

Valuation is true type multiplied by allocated quantity. Utility is valuation minus transfer. Social welfare excludes transfers. Feasibility is total allocated quantity at most one. Allocative efficiency compares the truthful allocation against the declared feasible allocation set.

The property compiler produces a finite disjunction of exact, ground failure-witness cases. Each case is guarded by an integer case selector. cvc5 and Z3 independently translate the solver-neutral comparison IR into QF_LIRA terms. `SAT` selects a replayable witness; `UNSAT` establishes absence only over the enumerated EPL domain.
