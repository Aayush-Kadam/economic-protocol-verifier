from __future__ import annotations

from fractions import Fraction

from .compiler import WitnessCase
from .eir import DeterministicDirectMechanism


def _f(value: str) -> Fraction:
    return Fraction(value)


def _profile(values) -> tuple[Fraction, ...]:
    return tuple(_f(v) for v in values)


def replay_case(mechanism: DeterministicDirectMechanism, property_name: str, case: WitnessCase) -> bool:
    data = case.payload
    if property_name == "dsic":
        agent, theta = int(data["agent"]), _f(data["true_type"])
        truth, deviation = _profile(data["truthful_reports"]), _profile(data["deviation_reports"])
        return mechanism.utility(agent, theta, mechanism.outcome(deviation)) > mechanism.utility(
            agent, theta, mechanism.outcome(truth))
    if property_name == "ex_post_ir":
        agent, types = int(data["agent"]), _profile(data["true_types"])
        return mechanism.utility(agent, types[agent], mechanism.outcome(types)) < mechanism.outside_options[agent]
    if property_name in {"weak_budget_balance", "strong_budget_balance"}:
        revenue = sum(mechanism.outcome(_profile(data["reports"])).transfers, Fraction(0))
        return revenue < 0 if property_name == "weak_budget_balance" else revenue != 0
    if property_name == "feasibility":
        return not mechanism.feasible(mechanism.outcome(_profile(data["reports"])).allocation)
    if property_name == "allocative_efficiency":
        types = _profile(data["true_types"])
        chosen = mechanism.outcome(types).allocation
        alternative = mechanism.feasible_allocations[int(data["alternative_index"])]
        return mechanism.welfare(types, alternative) > mechanism.welfare(types, chosen)
    raise ValueError(property_name)

