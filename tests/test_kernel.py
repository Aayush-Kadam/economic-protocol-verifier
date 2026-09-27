import sys
import unittest
from dataclasses import FrozenInstanceError
from fractions import Fraction
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from epv.benchmarks import (  # noqa: E402
    deficit_auction,
    double_allocation_mechanism,
    first_price_auction,
    malformed_second_price_auction,
    second_price_auction,
)
from epv.canonical import canonical_bytes, mechanism_hash  # noqa: E402
from epv.eir import (  # noqa: E402
    Agent,
    Allocation,
    Assumption,
    DeterministicDirectMechanism,
    Outcome,
    VerificationDomain,
    exact,
)
from epv.properties import (  # noqa: E402
    check_allocative_efficiency,
    check_dsic,
    check_ex_post_ir,
    check_feasibility,
    check_strong_budget_balance,
    check_weak_budget_balance,
)
from epv.result import Status  # noqa: E402


class ExactArithmeticTests(unittest.TestCase):
    def test_float_is_rejected_everywhere_at_boundary(self) -> None:
        with self.assertRaises(TypeError):
            exact(0.5)
        with self.assertRaises(TypeError):
            Allocation((0.5, 0.5))
        with self.assertRaises(TypeError):
            VerificationDomain(((0.0,),), ((0,),))

    def test_irreducible_rational_normalization(self) -> None:
        self.assertEqual(exact(Fraction(2, 4)), Fraction(1, 2))

    def test_eir_is_immutable(self) -> None:
        agent = Agent("a")
        with self.assertRaises(FrozenInstanceError):
            agent.id = "b"  # type: ignore[misc]


class CanonicalAuctionTests(unittest.TestCase):
    def setUp(self) -> None:
        self.second = second_price_auction()

    def test_second_price_expected_properties(self) -> None:
        self.assertIs(check_dsic(self.second).status, Status.BOUNDED_VERIFIED)
        self.assertIs(check_ex_post_ir(self.second).status, Status.BOUNDED_VERIFIED)
        self.assertIs(check_weak_budget_balance(self.second).status, Status.BOUNDED_VERIFIED)
        self.assertIs(check_feasibility(self.second).status, Status.BOUNDED_VERIFIED)
        self.assertIs(check_allocative_efficiency(self.second).status, Status.BOUNDED_VERIFIED)
        self.assertIs(check_strong_budget_balance(self.second).status, Status.FALSIFIED)

    def test_equal_bids_use_explicit_lowest_id_tie_break(self) -> None:
        outcome = self.second.outcome((Fraction(2), Fraction(2)))
        self.assertEqual(outcome.label, "winner:0")
        self.assertEqual(outcome.allocation.quantities, (1, 0))
        self.assertEqual(outcome.transfers, (2, 0))

    def test_first_price_has_complete_dsic_witness(self) -> None:
        result = check_dsic(first_price_auction())
        self.assertIs(result.status, Status.FALSIFIED)
        self.assertEqual(
            set(result.witness),
            {"agent", "true_type", "truthful_report", "deviation_report", "other_reports",
             "truthful_outcome", "deviation_outcome", "truthful_transfer", "deviation_transfer",
             "truthful_utility", "deviation_utility", "utility_improvement"},
        )
        self.assertGreater(Fraction(result.witness["utility_improvement"]), 0)

    def test_malformed_second_price_is_caught(self) -> None:
        self.assertIs(check_dsic(malformed_second_price_auction()).status, Status.FALSIFIED)

    def test_deficit_and_double_allocation_are_caught(self) -> None:
        self.assertIs(check_weak_budget_balance(deficit_auction()).status, Status.FALSIFIED)
        self.assertIs(check_feasibility(double_allocation_mechanism()).status, Status.FALSIFIED)

    def test_canonical_hash_is_stable(self) -> None:
        other = second_price_auction()
        self.assertEqual(canonical_bytes(self.second), canonical_bytes(other))
        self.assertEqual(mechanism_hash(self.second), mechanism_hash(other))

    def test_semantically_different_valuation_changes_hash(self) -> None:
        base = self.second

        def zero_value(agent, theta, allocation):
            return Fraction(0)

        changed = DeterministicDirectMechanism(
            base.name, base.agents, base.domain, base.rule, zero_value, base.feasible,
            base.feasible_allocations, base.assumptions, base.tie_breaking, base.outside_options,
        )
        self.assertNotEqual(mechanism_hash(base), mechanism_hash(changed))


class TrueTypeReportSeparationTests(unittest.TestCase):
    def test_utility_uses_true_type_not_deviation_report(self) -> None:
        mechanism = first_price_auction(values=(0, 1, 2, 3))
        agent = 0
        true_type = Fraction(3)
        deviation_reports = (Fraction(2), Fraction(1))
        outcome = mechanism.outcome(deviation_reports)
        # Correct: value 3 minus payment 2 = 1. The report-based bug gives 2 - 2 = 0.
        self.assertEqual(mechanism.utility(agent, true_type, outcome), 1)
        self.assertNotEqual(mechanism.utility(agent, true_type, outcome), deviation_reports[agent] - outcome.transfers[agent])

    def test_dsic_checker_finds_underbid_using_true_value(self) -> None:
        result = check_dsic(first_price_auction(values=(0, 1, 2, 3)))
        self.assertIs(result.status, Status.FALSIFIED)
        self.assertNotEqual(result.witness["true_type"], result.witness["deviation_report"])


class PropertyIsolationTests(unittest.TestCase):
    def test_inefficient_rule_is_detected_even_when_feasible(self) -> None:
        base = second_price_auction(values=(0, 1))

        def rule(reports):
            return Outcome("always-0", Allocation((1, 0)), (0, 0))

        mechanism = DeterministicDirectMechanism(
            "inefficient", base.agents, base.domain, rule, base.value, base.feasible,
            base.feasible_allocations, base.assumptions, "always agent 0", base.outside_options,
        )
        self.assertIs(check_feasibility(mechanism).status, Status.BOUNDED_VERIFIED)
        self.assertIs(check_allocative_efficiency(mechanism).status, Status.FALSIFIED)

    def test_missing_tie_break_is_rejected(self) -> None:
        base = second_price_auction(values=(0, 1))
        with self.assertRaises(ValueError):
            DeterministicDirectMechanism(
                base.name, base.agents, base.domain, base.rule, base.value, base.feasible,
                base.feasible_allocations, base.assumptions, "", base.outside_options,
            )


if __name__ == "__main__":
    unittest.main()
