from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class PropertyMetadata:
    property_id: str
    domain_family: str
    formal_definition: str
    required_features: tuple[str, ...]
    quantifiers: str
    witness_definition: str
    assumptions: tuple[str, ...]
    assurance_support: tuple[str, ...] = ("V1", "V2", "V3")


PROPERTIES = {
    "epv.matching.feasibility.v1": PropertyMetadata("epv.matching.feasibility.v1", "matching", "one-to-one consistent assignment", ("strict_preferences",), "all outcomes", "duplicate or inconsistent partner", ("one_to_one",)),
    "epv.matching.individual_rationality.v1": PropertyMetadata("epv.matching.individual_rationality.v1", "matching", "every match is acceptable to both agents", ("outside_option",), "all agents", "assigned partner ranked below unmatched", ("strict_preferences",)),
    "epv.matching.stability.v1": PropertyMetadata("epv.matching.stability.v1", "matching", "no mutually preferred acceptable blocking pair", ("strict_preferences", "outside_option"), "all cross-side pairs", "both prefer each other to current assignments", ("one_to_one",)),
    "epv.matching.strategyproof_proposer.v1": PropertyMetadata("epv.matching.strategyproof_proposer.v1", "matching", "no proposer obtains a strictly preferred assignment by unilateral misreport", ("reports", "true_preferences"), "all proposers, profiles, deviations", "true ordinal preference favors deviation assignment", ("proposer_side",)),
    "epv.fair_division.feasibility.v1": PropertyMetadata("epv.fair_division.feasibility.v1", "fair_division", "each good assigned exactly once", ("indivisible_goods",), "all goods", "missing, duplicate, or unknown assignment", ("complete_allocation",)),
    "epv.fair_division.envy_free.v1": PropertyMetadata("epv.fair_division.envy_free.v1", "fair_division", "each agent values own bundle at least every other bundle", ("additive_values",), "all ordered agent pairs", "agent values another bundle more", ("nonnegative_values",)),
    "epv.fair_division.ef1.v1": PropertyMetadata("epv.fair_division.ef1.v1", "fair_division", "envy is eliminated by removing at most one good from the envied bundle", ("additive_values",), "all ordered agent pairs", "envy remains after every single-good removal", ("nonnegative_values",)),
    "epv.fair_division.pareto_efficiency.v1": PropertyMetadata("epv.fair_division.pareto_efficiency.v1", "fair_division", "no feasible allocation weakly improves all and strictly improves one", ("additive_values",), "all feasible alternatives", "Pareto-dominating allocation", ("complete_allocation",)),
}


def require_applicable(property_id: str, domain_family: str) -> PropertyMetadata:
    try: meta = PROPERTIES[property_id]
    except KeyError as exc: raise ValueError(f"unknown property: {property_id}") from exc
    if meta.domain_family != domain_family:
        raise ValueError(f"property {property_id} is inapplicable to {domain_family}")
    return meta
