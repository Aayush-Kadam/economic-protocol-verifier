from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass
from fractions import Fraction
from typing import Any, Union

from .canonical import mechanism_hash
from .compiler import WitnessCase, WitnessProblem
from .eir import DeterministicDirectMechanism
from .replay import replay_case
from .solvers import SolverResult, SolverStatus


def q(value: Fraction) -> str:
    return str(value.numerator) if value.denominator == 1 else f"{value.numerator}/{value.denominator}"


def profile(values) -> tuple[Fraction, ...]:
    return tuple(Fraction(v) for v in values)


def alloc(outcome) -> tuple[str, ...]:
    return tuple(q(v) for v in outcome.allocation.quantities)


@dataclass(frozen=True)
class DSICWitness:
    manipulating_agent: int; true_type: str; truthful_report: str; deviation_report: str
    other_agents_reports: tuple[str, ...]; truthful_allocation: tuple[str, ...]
    deviation_allocation: tuple[str, ...]; truthful_payment: str; deviation_payment: str
    truthful_utility: str; deviation_utility: str; utility_gain: str


@dataclass(frozen=True)
class IRWitness:
    agent: int; true_type: str; truthful_report_profile: tuple[str, ...]; allocation: tuple[str, ...]
    payment: str; utility: str; outside_option: str; ir_gap: str


@dataclass(frozen=True)
class BudgetWitness:
    report_profile: tuple[str, ...]; transfers: tuple[str, ...]; mechanism_balance: str
    allowed_minimum: str; violation_amount: str; balance_kind: str


@dataclass(frozen=True)
class FeasibilityWitness:
    report_profile: tuple[str, ...]; allocation: tuple[str, ...]; resource: str
    capacity: str; total_allocated: str; excess_allocation: str


@dataclass(frozen=True)
class EfficiencyWitness:
    true_type_profile: tuple[str, ...]; mechanism_allocation: tuple[str, ...]; mechanism_welfare: str
    alternative_allocation: tuple[str, ...]; alternative_welfare: str; welfare_improvement: str


PropertyWitness = Union[DSICWitness, IRWitness, BudgetWitness, FeasibilityWitness, EfficiencyWitness]


@dataclass(frozen=True)
class CounterexampleCertificate:
    format: str
    witness_version: str
    mechanism_hash: str
    property_id: str
    property_version: str
    logical_problem_hash: str
    verification_domain: dict[str, Any]
    assumptions: tuple[str, ...]
    backend_origin: dict[str, Any]
    raw_model_identity: str
    minimality: dict[str, Any]
    replay: dict[str, str]
    witness_type: str
    witness: dict[str, Any]

    def canonical_bytes(self) -> bytes:
        return json.dumps(asdict(self), sort_keys=True, separators=(",", ":")).encode()

    def certificate_hash(self) -> str:
        return "sha256:" + hashlib.sha256(self.canonical_bytes()).hexdigest()


def decode_case(mechanism: DeterministicDirectMechanism, property_name: str, case: WitnessCase) -> PropertyWitness:
    d = case.payload
    if property_name == "dsic":
        agent, theta = int(d["agent"]), Fraction(d["true_type"])
        truthful, deviation = profile(d["truthful_reports"]), profile(d["deviation_reports"])
        to, do = mechanism.outcome(truthful), mechanism.outcome(deviation)
        tu, du = mechanism.utility(agent, theta, to), mechanism.utility(agent, theta, do)
        return DSICWitness(agent, q(theta), q(truthful[agent]), q(deviation[agent]),
                           tuple(q(v) for i, v in enumerate(truthful) if i != agent), alloc(to), alloc(do),
                           q(to.transfers[agent]), q(do.transfers[agent]), q(tu), q(du), q(du-tu))
    if property_name == "ex_post_ir":
        agent, types = int(d["agent"]), profile(d["true_types"]); out = mechanism.outcome(types)
        utility = mechanism.utility(agent, types[agent], out); outside = mechanism.outside_options[agent]
        return IRWitness(agent, q(types[agent]), tuple(q(v) for v in types), alloc(out), q(out.transfers[agent]),
                         q(utility), q(outside), q(utility-outside))
    if property_name in {"weak_budget_balance", "strong_budget_balance"}:
        reports = profile(d["reports"]); out = mechanism.outcome(reports)
        balance = sum(out.transfers, Fraction(0))
        amount = -balance if property_name == "weak_budget_balance" else abs(balance)
        kind = "deficit" if balance < 0 else "surplus"
        return BudgetWitness(tuple(q(v) for v in reports), tuple(q(v) for v in out.transfers), q(balance), "0", q(amount), kind)
    if property_name == "feasibility":
        reports = profile(d["reports"]); out = mechanism.outcome(reports)
        total = sum(out.allocation.quantities, Fraction(0))
        return FeasibilityWitness(tuple(q(v) for v in reports), alloc(out), "single_indivisible_item",
                                  "1", q(total), q(total-1))
    if property_name == "allocative_efficiency":
        types = profile(d["true_types"]); chosen = mechanism.outcome(types).allocation
        alternative = mechanism.feasible_allocations[int(d["alternative_index"])]
        if not mechanism.feasible(alternative):
            raise ValueError("efficiency alternative is not feasible")
        cw, aw = mechanism.welfare(types, chosen), mechanism.welfare(types, alternative)
        return EfficiencyWitness(tuple(q(v) for v in types), tuple(q(v) for v in chosen.quantities), q(cw),
                                 tuple(q(v) for v in alternative.quantities), q(aw), q(aw-cw))
    raise ValueError(property_name)


def _numbers(value: Any):
    if isinstance(value, dict):
        for item in value.values(): yield from _numbers(item)
    elif isinstance(value, (list, tuple)):
        for item in value: yield from _numbers(item)
    elif isinstance(value, int): yield Fraction(value)
    elif isinstance(value, str):
        try: yield Fraction(value)
        except ValueError: return


def minimization_objective(witness: PropertyWitness) -> tuple[Any, ...]:
    document = asdict(witness); numbers = tuple(_numbers(document))
    return (sum(v != 0 for v in numbers), sum(abs(v) for v in numbers),
            sum(v.denominator for v in numbers), json.dumps(document, sort_keys=True, separators=(",", ":")))


def exact_minimum(mechanism: DeterministicDirectMechanism, problem: WitnessProblem) -> tuple[int, PropertyWitness]:
    candidates = [(i, decode_case(mechanism, problem.property, case)) for i, case in enumerate(problem.cases)
                  if replay_case(mechanism, problem.property, case)]
    if not candidates: raise ValueError("problem has no replayable counterexample")
    return min(candidates, key=lambda pair: minimization_objective(pair[1]))


def make_certificate(mechanism: DeterministicDirectMechanism, problem: WitnessProblem,
                     result: SolverResult) -> CounterexampleCertificate:
    if result.status is not SolverStatus.SAT or result.case_index is None:
        raise ValueError("a SAT solver result with case index is required")
    raw = problem.cases[result.case_index]
    if not replay_case(mechanism, problem.property, raw):
        raise RuntimeError("INTERNAL WITNESS REPLAY FAILURE")
    minimum_index, witness = exact_minimum(mechanism, problem)
    if not replay_case(mechanism, problem.property, problem.cases[minimum_index]):
        raise RuntimeError("minimized witness failed replay")
    return CounterexampleCertificate(
        "epv-counterexample-v1", "epv.witness.v1", mechanism_hash(mechanism), problem.property,
        problem.property_version, problem.problem_hash(),
        {"kind": problem.domain_kind, "type_spaces": [[q(v) for v in s] for s in mechanism.domain.type_spaces],
         "report_spaces": [[q(v) for v in s] for s in mechanism.domain.report_spaces]},
        tuple(a.name for a in mechanism.assumptions),
        {"backend": result.backend, "version": result.version, "raw_case_index": result.case_index},
        f"{result.backend}:case:{result.case_index}",
        {"status": "EXACT LEXICOGRAPHIC MINIMUM", "selected_case_index": minimum_index,
         "objective": "nonzero numeric fields; absolute magnitude sum; denominator sum; canonical JSON"},
        {"status": "PASS", "semantics": "M1 authoritative evaluator"},
        type(witness).__name__, asdict(witness))


def validate_certificate(certificate: CounterexampleCertificate, mechanism: DeterministicDirectMechanism,
                         problem: WitnessProblem) -> bool:
    if certificate.format != "epv-counterexample-v1" or certificate.witness_version != "epv.witness.v1": return False
    if certificate.mechanism_hash != mechanism_hash(mechanism): return False
    if certificate.property_id != problem.property or certificate.property_version != problem.property_version: return False
    if certificate.logical_problem_hash != problem.problem_hash(): return False
    try: index, witness = exact_minimum(mechanism, problem)
    except (ValueError, KeyError, TypeError): return False
    return (certificate.minimality.get("selected_case_index") == index and certificate.witness == asdict(witness)
            and certificate.replay.get("status") == "PASS")


def render_trace(certificate: CounterexampleCertificate) -> str:
    lines = ["EPV COUNTEREXAMPLE", f"Property: {certificate.property_version}",
             "Status: COUNTEREXAMPLE FOUND — EXACT MINIMUM", f"Mechanism: {certificate.mechanism_hash}"]
    for key, value in certificate.witness.items():
        lines.append(f"{key.replace('_', ' ').title()}: {value}")
    lines.extend(["Replay: PASS", "Minimality: EXACT LEXICOGRAPHIC MINIMUM"])
    return "\n".join(lines)

