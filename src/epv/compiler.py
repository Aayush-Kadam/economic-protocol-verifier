from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from fractions import Fraction
from itertools import product
from typing import Any, Iterable

from .eir import DeterministicDirectMechanism


PROPERTY_VERSIONS = {
    "dsic": "epv.property.dsic.v1",
    "ex_post_ir": "epv.property.ex_post_ir.v1",
    "weak_budget_balance": "epv.property.weak_budget_balance.v1",
    "strong_budget_balance": "epv.property.strong_budget_balance.v1",
    "feasibility": "epv.property.feasibility.v1",
    "allocative_efficiency": "epv.property.allocative_efficiency.v1",
}


@dataclass(frozen=True)
class Predicate:
    op: str
    lhs: Fraction
    rhs: Fraction

    def holds(self) -> bool:
        return {">": self.lhs > self.rhs, "<": self.lhs < self.rhs, "!=": self.lhs != self.rhs}[self.op]


@dataclass(frozen=True)
class WitnessCase:
    predicate: Predicate
    payload: dict[str, Any]


@dataclass(frozen=True)
class WitnessProblem:
    property: str
    property_version: str
    cases: tuple[WitnessCase, ...]
    domain_kind: str = "finite-exact-integer"

    def canonical_document(self) -> dict[str, Any]:
        def q(value: Fraction): return [value.numerator, value.denominator]
        return {"schema": "epv-witness-problem-0.1", "property": self.property,
                "property_version": self.property_version, "domain_kind": self.domain_kind,
                "cases": [{"op": c.predicate.op, "lhs": q(c.predicate.lhs), "rhs": q(c.predicate.rhs),
                           "payload": c.payload} for c in self.cases]}

    def canonical_bytes(self) -> bytes:
        return json.dumps(self.canonical_document(), sort_keys=True, separators=(",", ":")).encode()

    def problem_hash(self) -> str:
        return "sha256:" + hashlib.sha256(self.canonical_bytes()).hexdigest()


def _payload(**values: Any) -> dict[str, Any]:
    def encode(value):
        if isinstance(value, Fraction):
            return str(value.numerator) if value.denominator == 1 else f"{value.numerator}/{value.denominator}"
        if isinstance(value, tuple):
            return tuple(encode(v) for v in value)
        return value
    return {key: encode(value) for key, value in values.items()}


def compile_property(mechanism: DeterministicDirectMechanism, property_name: str) -> WitnessProblem:
    if property_name not in PROPERTY_VERSIONS:
        raise ValueError(f"unsupported property: {property_name}")
    cases: list[WitnessCase] = []
    n = len(mechanism.agents)
    if property_name == "dsic":
        for agent in range(n):
            others = tuple(i for i in range(n) if i != agent)
            for theta in mechanism.domain.type_spaces[agent]:
                for other_values in product(*(mechanism.domain.report_spaces[i] for i in others)):
                    truthful = [Fraction(0)] * n
                    for index, value in zip(others, other_values, strict=True): truthful[index] = value
                    truthful[agent] = mechanism.truthful_report(agent, theta)
                    truth_out = mechanism.outcome(tuple(truthful))
                    truth_u = mechanism.utility(agent, theta, truth_out)
                    for deviation in mechanism.domain.report_spaces[agent]:
                        deviating = list(truthful); deviating[agent] = deviation
                        dev_out = mechanism.outcome(tuple(deviating))
                        dev_u = mechanism.utility(agent, theta, dev_out)
                        cases.append(WitnessCase(Predicate(">", dev_u, truth_u), _payload(
                            agent=agent, true_type=theta, truthful_reports=tuple(truthful),
                            deviation_reports=tuple(deviating))))
    elif property_name == "ex_post_ir":
        for types in mechanism.domain.type_profiles():
            out = mechanism.outcome(types)
            for agent, theta in enumerate(types):
                cases.append(WitnessCase(Predicate("<", mechanism.utility(agent, theta, out),
                                                    mechanism.outside_options[agent]),
                                         _payload(agent=agent, true_types=types)))
    elif property_name in {"weak_budget_balance", "strong_budget_balance"}:
        for reports in mechanism.domain.report_profiles():
            revenue = sum(mechanism.outcome(reports).transfers, Fraction(0))
            op = "<" if property_name == "weak_budget_balance" else "!="
            cases.append(WitnessCase(Predicate(op, revenue, Fraction(0)), _payload(reports=reports)))
    elif property_name == "feasibility":
        for reports in mechanism.domain.report_profiles():
            allocation = mechanism.outcome(reports).allocation
            cases.append(WitnessCase(Predicate(">", sum(allocation.quantities, Fraction(0)), Fraction(1)),
                                     _payload(reports=reports)))
    elif property_name == "allocative_efficiency":
        for types in mechanism.domain.type_profiles():
            chosen = mechanism.outcome(types).allocation
            chosen_welfare = mechanism.welfare(types, chosen)
            for alternative_index, alternative in enumerate(mechanism.feasible_allocations):
                cases.append(WitnessCase(Predicate(">", mechanism.welfare(types, alternative), chosen_welfare),
                                         _payload(true_types=types, alternative_index=alternative_index)))
    return WitnessProblem(property_name, PROPERTY_VERSIONS[property_name], tuple(cases))

