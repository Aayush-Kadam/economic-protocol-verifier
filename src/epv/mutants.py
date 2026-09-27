from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction

from .benchmarks import _single_item_base
from .eir import Allocation, DeterministicDirectMechanism, Outcome


@dataclass(frozen=True)
class Mutant:
    mechanism: DeterministicDirectMechanism
    base_mechanism: str
    mutation_operator: str
    mutation_location: str
    expected_impact: str


def mutant_corpus() -> tuple[Mutant, ...]:
    allocations = ("highest", "reverse", "fixed0", "fixed1", "both", "nobody")
    payments = ("second", "own", "zero", "winner_subsidy", "loser_subsidy",
                "winner_surcharge", "fixed_one", "negative_all", "swap_second", "double_second")
    result = []
    for allocation_mode in allocations:
        for payment_mode in payments:
            name = f"mutant.{allocation_mode}.{payment_mode}"
            base = _single_item_base(name, (0, 1, 2), "zero")
            def rule(reports, allocation_mode=allocation_mode, payment_mode=payment_mode):
                high = 0 if reports[0] >= reports[1] else 1
                winner = 1-high if allocation_mode == "reverse" else high
                quantities = {"highest": tuple(Fraction(i == winner) for i in range(2)),
                              "reverse": tuple(Fraction(i == winner) for i in range(2)),
                              "fixed0": (Fraction(1), Fraction(0)), "fixed1": (Fraction(0), Fraction(1)),
                              "both": (Fraction(1), Fraction(1)), "nobody": (Fraction(0), Fraction(0))}[allocation_mode]
                active = winner if allocation_mode in {"highest", "reverse"} else (0 if allocation_mode == "fixed0" else 1)
                transfers = [Fraction(0), Fraction(0)]
                if payment_mode == "second": transfers[active] = reports[1-active]
                elif payment_mode == "own": transfers[active] = reports[active]
                elif payment_mode == "winner_subsidy": transfers[active] = -1
                elif payment_mode == "loser_subsidy": transfers[1-active] = -1
                elif payment_mode == "winner_surcharge": transfers[active] = reports[active] + 1
                elif payment_mode == "fixed_one": transfers[active] = 1
                elif payment_mode == "negative_all": transfers[:] = [Fraction(-1), Fraction(-1)]
                elif payment_mode == "swap_second": transfers[1-active] = reports[1-active]
                elif payment_mode == "double_second": transfers[active] = 2 * reports[1-active]
                return Outcome(f"{allocation_mode}:{active}", Allocation(quantities), tuple(transfers))
            mechanism = DeterministicDirectMechanism(
                name, base.agents, base.domain, rule, base.value, base.feasible, base.feasible_allocations,
                base.assumptions, f"mutation-defined deterministic rule: {allocation_mode}", base.outside_options)
            result.append(Mutant(mechanism, "second-price auction",
                                 f"allocation={allocation_mode};payment={payment_mode}",
                                 "allocation/payment rule", "empirical property vector; no guessed guarantee"))
    return tuple(result)

