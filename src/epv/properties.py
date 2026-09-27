from __future__ import annotations

from fractions import Fraction
from itertools import product

from .eir import DeterministicDirectMechanism, Profile
from .result import AssuranceLevel, Status, VerificationResult


def _q(value: Fraction) -> str:
    return str(value.numerator) if value.denominator == 1 else f"{value.numerator}/{value.denominator}"


def check_dsic(mechanism: DeterministicDirectMechanism) -> VerificationResult:
    checked = 0
    n = len(mechanism.agents)
    for agent in range(n):
        other_indices = tuple(i for i in range(n) if i != agent)
        other_spaces = tuple(mechanism.domain.report_spaces[i] for i in other_indices)
        for theta in mechanism.domain.type_spaces[agent]:
            truthful = mechanism.truthful_report(agent, theta)
            for other_values in product(*other_spaces):
                base = [Fraction(0)] * n
                for index, value in zip(other_indices, other_values, strict=True):
                    base[index] = value
                base[agent] = truthful
                truthful_reports = tuple(base)
                truthful_outcome = mechanism.outcome(truthful_reports)
                truthful_utility = mechanism.utility(agent, theta, truthful_outcome)
                for deviation in mechanism.domain.report_spaces[agent]:
                    checked += 1
                    deviating = list(base)
                    deviating[agent] = deviation
                    deviation_reports = tuple(deviating)
                    deviation_outcome = mechanism.outcome(deviation_reports)
                    deviation_utility = mechanism.utility(agent, theta, deviation_outcome)
                    if deviation_utility > truthful_utility:
                        witness = {
                            "agent": mechanism.agents[agent].id,
                            "true_type": _q(theta),
                            "truthful_report": _q(truthful),
                            "deviation_report": _q(deviation),
                            "other_reports": tuple(_q(v) for v in other_values),
                            "truthful_outcome": truthful_outcome.label,
                            "deviation_outcome": deviation_outcome.label,
                            "truthful_transfer": _q(truthful_outcome.transfers[agent]),
                            "deviation_transfer": _q(deviation_outcome.transfers[agent]),
                            "truthful_utility": _q(truthful_utility),
                            "deviation_utility": _q(deviation_utility),
                            "utility_improvement": _q(deviation_utility - truthful_utility),
                        }
                        return VerificationResult("dsic", Status.FALSIFIED, AssuranceLevel.V1, checked, witness)
    return VerificationResult("dsic", Status.BOUNDED_VERIFIED, AssuranceLevel.V1, checked)


def check_ex_post_ir(mechanism: DeterministicDirectMechanism) -> VerificationResult:
    checked = 0
    for types in mechanism.domain.type_profiles():
        outcome = mechanism.outcome(types)
        for agent, theta in enumerate(types):
            checked += 1
            utility = mechanism.utility(agent, theta, outcome)
            if utility < mechanism.outside_options[agent]:
                return VerificationResult("ex_post_ir", Status.FALSIFIED, AssuranceLevel.V1, checked, {
                    "agent": mechanism.agents[agent].id,
                    "true_types": tuple(_q(v) for v in types),
                    "outcome": outcome.label,
                    "utility": _q(utility),
                    "outside_option": _q(mechanism.outside_options[agent]),
                })
    return VerificationResult("ex_post_ir", Status.BOUNDED_VERIFIED, AssuranceLevel.V1, checked)


def _check_budget(mechanism: DeterministicDirectMechanism, strong: bool) -> VerificationResult:
    checked = 0
    name = "strong_budget_balance" if strong else "weak_budget_balance"
    for reports in mechanism.domain.report_profiles():
        checked += 1
        outcome = mechanism.outcome(reports)
        revenue = sum(outcome.transfers, Fraction(0))
        violates = revenue != 0 if strong else revenue < 0
        if violates:
            return VerificationResult(name, Status.FALSIFIED, AssuranceLevel.V1, checked, {
                "reports": tuple(_q(v) for v in reports),
                "outcome": outcome.label,
                "transfers": tuple(_q(v) for v in outcome.transfers),
                "mechanism_revenue": _q(revenue),
            })
    return VerificationResult(name, Status.BOUNDED_VERIFIED, AssuranceLevel.V1, checked)


def check_weak_budget_balance(mechanism: DeterministicDirectMechanism) -> VerificationResult:
    return _check_budget(mechanism, strong=False)


def check_strong_budget_balance(mechanism: DeterministicDirectMechanism) -> VerificationResult:
    return _check_budget(mechanism, strong=True)


def check_feasibility(mechanism: DeterministicDirectMechanism) -> VerificationResult:
    checked = 0
    for reports in mechanism.domain.report_profiles():
        checked += 1
        outcome = mechanism.outcome(reports)
        if not mechanism.feasible(outcome.allocation):
            return VerificationResult("feasibility", Status.FALSIFIED, AssuranceLevel.V1, checked, {
                "reports": tuple(_q(v) for v in reports),
                "outcome": outcome.label,
                "allocation": tuple(_q(v) for v in outcome.allocation.quantities),
            })
    return VerificationResult("feasibility", Status.BOUNDED_VERIFIED, AssuranceLevel.V1, checked)


def check_allocative_efficiency(mechanism: DeterministicDirectMechanism) -> VerificationResult:
    checked = 0
    for types in mechanism.domain.type_profiles():
        checked += 1
        chosen = mechanism.outcome(types).allocation
        chosen_welfare = mechanism.welfare(types, chosen)
        for alternative in mechanism.feasible_allocations:
            if not mechanism.feasible(alternative):
                raise ValueError("declared efficiency comparison allocation is infeasible")
            alternative_welfare = mechanism.welfare(types, alternative)
            if alternative_welfare > chosen_welfare:
                return VerificationResult("allocative_efficiency", Status.FALSIFIED, AssuranceLevel.V1, checked, {
                    "true_types": tuple(_q(v) for v in types),
                    "chosen_allocation": tuple(_q(v) for v in chosen.quantities),
                    "better_allocation": tuple(_q(v) for v in alternative.quantities),
                    "chosen_welfare": _q(chosen_welfare),
                    "better_welfare": _q(alternative_welfare),
                })
    return VerificationResult("allocative_efficiency", Status.BOUNDED_VERIFIED, AssuranceLevel.V1, checked)

