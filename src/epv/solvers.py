from __future__ import annotations

import time
from dataclasses import dataclass
from enum import Enum
from fractions import Fraction
from typing import Any

from .compiler import Predicate, WitnessProblem


class SolverStatus(str, Enum):
    SAT = "SAT"
    UNSAT = "UNSAT"
    UNKNOWN = "UNKNOWN"
    TIMEOUT = "TIMEOUT"
    ERROR = "ERROR"


@dataclass(frozen=True)
class SolverResult:
    backend: str
    version: str
    status: SolverStatus
    runtime_ms: float
    options: dict[str, Any]
    case_index: int | None = None
    reason_unknown: str | None = None


def _z3_q(z3, value: Fraction):
    return z3.RealVal(f"{value.numerator}/{value.denominator}")


def solve_z3(problem: WitnessProblem, timeout_ms: int = 10_000) -> SolverResult:
    import z3
    start = time.perf_counter()
    solver = z3.Solver(); solver.set(timeout=timeout_ms)
    choice = z3.Int("witness_case")
    clauses = []
    for index, case in enumerate(problem.cases):
        lhs, rhs = _z3_q(z3, case.predicate.lhs), _z3_q(z3, case.predicate.rhs)
        comparison = {">": lhs > rhs, "<": lhs < rhs, "!=": lhs != rhs}[case.predicate.op]
        clauses.append(z3.And(choice == index, comparison))
    solver.add(z3.Or(*clauses) if clauses else z3.BoolVal(False))
    raw = solver.check(); runtime = (time.perf_counter() - start) * 1000
    if raw == z3.sat:
        return SolverResult("z3", z3.get_version_string(), SolverStatus.SAT, runtime,
                            {"timeout_ms": timeout_ms, "logic": "QF_LIRA"}, solver.model()[choice].as_long())
    if raw == z3.unsat:
        return SolverResult("z3", z3.get_version_string(), SolverStatus.UNSAT, runtime,
                            {"timeout_ms": timeout_ms, "logic": "QF_LIRA"})
    reason = solver.reason_unknown()
    status = SolverStatus.TIMEOUT if "timeout" in reason.lower() else SolverStatus.UNKNOWN
    return SolverResult("z3", z3.get_version_string(), status, runtime,
                        {"timeout_ms": timeout_ms, "logic": "QF_LIRA"}, reason_unknown=reason)


def solve_cvc5(problem: WitnessProblem, timeout_ms: int = 10_000) -> SolverResult:
    import cvc5
    from cvc5 import Kind
    start = time.perf_counter(); solver = cvc5.Solver()
    solver.setLogic("QF_LIRA"); solver.setOption("produce-models", "true"); solver.setOption("tlimit-per", str(timeout_ms))
    choice = solver.mkConst(solver.getIntegerSort(), "witness_case")
    clauses = []
    for index, case in enumerate(problem.cases):
        def q(value: Fraction): return solver.mkReal(value.numerator, value.denominator)
        kind = {">": Kind.GT, "<": Kind.LT, "!=": Kind.DISTINCT}[case.predicate.op]
        comparison = solver.mkTerm(kind, q(case.predicate.lhs), q(case.predicate.rhs))
        clauses.append(solver.mkTerm(Kind.AND, solver.mkTerm(Kind.EQUAL, choice, solver.mkInteger(index)), comparison))
    solver.assertFormula((clauses[0] if len(clauses) == 1 else solver.mkTerm(Kind.OR, *clauses)) if clauses else solver.mkFalse())
    raw = solver.checkSat(); runtime = (time.perf_counter() - start) * 1000
    version = getattr(cvc5, "__version__", "unknown")
    if raw.isSat():
        return SolverResult("cvc5", version, SolverStatus.SAT, runtime,
                            {"timeout_ms": timeout_ms, "logic": "QF_LIRA"}, int(str(solver.getValue(choice))))
    if raw.isUnsat():
        return SolverResult("cvc5", version, SolverStatus.UNSAT, runtime,
                            {"timeout_ms": timeout_ms, "logic": "QF_LIRA"})
    reason = raw.getUnknownExplanation().name
    status = SolverStatus.TIMEOUT if "TIMEOUT" in reason else SolverStatus.UNKNOWN
    return SolverResult("cvc5", version, status, runtime,
                        {"timeout_ms": timeout_ms, "logic": "QF_LIRA"}, reason_unknown=reason)
