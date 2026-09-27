from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .compiler import WitnessProblem
from .solvers import SolverResult, SolverStatus


@dataclass(frozen=True)
class SymbolicConclusion:
    status: str
    assurance: str
    witness: dict[str, Any] | None


def interpret(problem: WitnessProblem, result: SolverResult) -> SymbolicConclusion:
    if result.status is SolverStatus.SAT:
        if result.case_index is None or not 0 <= result.case_index < len(problem.cases):
            return SymbolicConclusion("ERROR", "none", None)
        return SymbolicConclusion("FALSIFIED / COUNTEREXAMPLE FOUND", "V2 solver witness", problem.cases[result.case_index].payload)
    if result.status is SolverStatus.UNSAT:
        return SymbolicConclusion("BOUNDED VERIFIED", "V2 solver-established bounded result", None)
    if result.status is SolverStatus.TIMEOUT:
        return SymbolicConclusion("UNKNOWN/TIMEOUT", "none", None)
    if result.status is SolverStatus.UNKNOWN:
        return SymbolicConclusion("UNKNOWN", "none", None)
    return SymbolicConclusion("ERROR", "none", None)

