from __future__ import annotations

from fractions import Fraction

from .eir import Agent, Allocation, Assumption, DeterministicDirectMechanism, Outcome, VerificationDomain


def _single_item_base(name: str, values: tuple[int, ...], payment_rule: str) -> DeterministicDirectMechanism:
    agents = (Agent("bidder-0"), Agent("bidder-1"))
    space = tuple(Fraction(v) for v in values)
    domain = VerificationDomain((space, space), (space, space))
    feasible_allocations = (Allocation((0, 0)), Allocation((1, 0)), Allocation((0, 1)))

    def rule(reports: tuple[Fraction, ...]) -> Outcome:
        winner = 0 if reports[0] >= reports[1] else 1
        allocation = Allocation(tuple(Fraction(i == winner) for i in range(2)))
        transfers = [Fraction(0), Fraction(0)]
        if payment_rule == "second-price":
            transfers[winner] = reports[1 - winner]
        elif payment_rule == "first-price":
            transfers[winner] = reports[winner]
        elif payment_rule == "subsidy":
            transfers[winner] = -1
        elif payment_rule == "zero":
            pass
        else:
            raise ValueError(payment_rule)
        return Outcome(f"winner:{winner}", allocation, tuple(transfers))

    def value(agent: int, theta: Fraction, allocation: Allocation) -> Fraction:
        return theta * allocation.quantities[agent]

    return DeterministicDirectMechanism(
        name=name,
        agents=agents,
        domain=domain,
        rule=rule,
        value=value,
        feasible=lambda a: sum(a.quantities, Fraction(0)) <= 1,
        feasible_allocations=feasible_allocations,
        assumptions=(
            Assumption("private_values", "each type is the bidder's value for one item"),
            Assumption("quasi_linear", "utility equals value of allocation minus payment"),
        ),
        tie_breaking="lowest agent index wins equal bids",
        outside_options=(Fraction(0), Fraction(0)),
    )


def second_price_auction(values: tuple[int, ...] = (0, 1, 2)) -> DeterministicDirectMechanism:
    return _single_item_base("second-price auction", values, "second-price")


def first_price_auction(values: tuple[int, ...] = (0, 1, 2)) -> DeterministicDirectMechanism:
    return _single_item_base("first-price auction", values, "first-price")


def malformed_second_price_auction(values: tuple[int, ...] = (0, 1, 2)) -> DeterministicDirectMechanism:
    return _single_item_base("malformed second-price auction (winner pays own bid)", values, "first-price")


def deficit_auction(values: tuple[int, ...] = (0, 1)) -> DeterministicDirectMechanism:
    return _single_item_base("subsidized allocation", values, "subsidy")


def double_allocation_mechanism(values: tuple[int, ...] = (0, 1)) -> DeterministicDirectMechanism:
    base = _single_item_base("double allocation mutant", values, "second-price")

    def rule(reports: tuple[Fraction, ...]) -> Outcome:
        return Outcome("both-win", Allocation((1, 1)), (0, 0))

    return DeterministicDirectMechanism(
        name=base.name,
        agents=base.agents,
        domain=base.domain,
        rule=rule,
        value=base.value,
        feasible=base.feasible,
        feasible_allocations=base.feasible_allocations,
        assumptions=base.assumptions,
        tie_breaking="not applicable; both agents are allocated",
        outside_options=base.outside_options,
    )


def always_agent_zero_mechanism(values: tuple[int, ...] = (0, 1, 2)) -> DeterministicDirectMechanism:
    base = _single_item_base("always_agent_zero", values, "zero")

    def rule(reports: tuple[Fraction, ...]) -> Outcome:
        return Outcome("always-0", Allocation((1, 0)), (0, 0))

    return DeterministicDirectMechanism(
        name=base.name, agents=base.agents, domain=base.domain, rule=rule, value=base.value,
        feasible=base.feasible, feasible_allocations=base.feasible_allocations,
        assumptions=base.assumptions, tie_breaking="not applicable; fixed allocation",
        outside_options=base.outside_options,
    )
