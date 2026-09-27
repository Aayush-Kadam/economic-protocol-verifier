import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from epv.compiler import PROPERTY_VERSIONS, Predicate, WitnessCase, WitnessProblem, compile_property
from epv.epl import load_epl
from epv.properties import (check_allocative_efficiency, check_dsic, check_ex_post_ir, check_feasibility,
                            check_strong_budget_balance, check_weak_budget_balance)
from epv.result import Status
from epv.solvers import SolverStatus, solve_cvc5, solve_z3
from epv.replay import replay_case
from epv.solvers import SolverResult
from epv.symbolic import interpret


ENUM = {"dsic": check_dsic, "ex_post_ir": check_ex_post_ir,
        "weak_budget_balance": check_weak_budget_balance, "strong_budget_balance": check_strong_budget_balance,
        "feasibility": check_feasibility, "allocative_efficiency": check_allocative_efficiency}


class DifferentialTests(unittest.TestCase):
    FILES = ["second_price.epl", "first_price.epl", "winner_pays_own_bid.epl",
             "subsidized_mechanism.epl", "double_allocation.epl", "always_agent_zero.epl"]

    def test_three_way_agreement_all_benchmarks_and_properties(self):
        for filename in self.FILES:
            _, mechanism = load_epl(ROOT / "examples" / filename)
            for property_name, enum in ENUM.items():
                with self.subTest(filename=filename, property=property_name):
                    problem = compile_property(mechanism, property_name)
                    expected = SolverStatus.SAT if enum(mechanism).status is Status.FALSIFIED else SolverStatus.UNSAT
                    z3_result, cvc5_result = solve_z3(problem), solve_cvc5(problem)
                    self.assertEqual(z3_result.status, expected)
                    self.assertEqual(cvc5_result.status, expected)
                    for result in (z3_result, cvc5_result):
                        if result.status is SolverStatus.SAT:
                            self.assertIsNotNone(result.case_index)
                            self.assertTrue(problem.cases[result.case_index].predicate.holds())
                            self.assertTrue(replay_case(mechanism, property_name, problem.cases[result.case_index]))

    def test_property_versions_and_problem_hash_stable(self):
        _, mechanism = load_epl(ROOT / "examples" / "second_price.epl")
        problem = compile_property(mechanism, "dsic")
        self.assertEqual(problem.property_version, "epv.property.dsic.v1")
        self.assertEqual(problem.problem_hash(), compile_property(mechanism, "dsic").problem_hash())
        self.assertEqual(problem.problem_hash(), "sha256:a89212907a9003e3ad79e7585ff4389fc0bb843ea709ba7c5488dec8d0b7ec34")

    def test_compiler_mutations_are_detectable_by_reference_expectation(self):
        _, mechanism = load_epl(ROOT / "examples" / "first_price.epl")
        correct = compile_property(mechanism, "dsic")
        reversed_problem = WitnessProblem("dsic", PROPERTY_VERSIONS["dsic"], tuple(
            WitnessCase(Predicate("<", case.predicate.lhs, case.predicate.rhs), case.payload) for case in correct.cases))
        self.assertEqual(solve_z3(correct).status, SolverStatus.SAT)
        # Reversal changes the witness set/hash; snapshot-like identity catches the compiler mutation.
        self.assertNotEqual(correct.problem_hash(), reversed_problem.problem_hash())

    def test_empty_formula_is_unsat_not_verified_by_status_adapter(self):
        empty = WitnessProblem("dsic", PROPERTY_VERSIONS["dsic"], ())
        self.assertEqual(solve_z3(empty).status, SolverStatus.UNSAT)
        self.assertEqual(solve_cvc5(empty).status, SolverStatus.UNSAT)

    def test_unknown_timeout_and_error_never_become_verified(self):
        empty = WitnessProblem("dsic", PROPERTY_VERSIONS["dsic"], ())
        for status in (SolverStatus.UNKNOWN, SolverStatus.TIMEOUT, SolverStatus.ERROR):
            result = SolverResult("fake", "0", status, 0, {}, reason_unknown="injected")
            self.assertNotEqual(interpret(empty, result).status, "BOUNDED VERIFIED")


if __name__ == "__main__": unittest.main()
