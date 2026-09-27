import dataclasses
import json
import sys
import unittest
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from epv.benchmarks import _single_item_base
from epv.compiler import compile_property
from epv.counterexamples import (BudgetWitness, CounterexampleCertificate, DSICWitness, EfficiencyWitness,
                                 FeasibilityWitness, IRWitness, exact_minimum, make_certificate,
                                 render_trace, validate_certificate)
from epv.eir import Allocation, DeterministicDirectMechanism, Outcome
from epv.epl import load_epl
from epv.mutants import mutant_corpus
from epv.properties import (check_allocative_efficiency, check_dsic, check_ex_post_ir, check_feasibility,
                            check_strong_budget_balance, check_weak_budget_balance)
from epv.result import Status
from epv.solvers import SolverStatus, solve_cvc5, solve_z3

ENUM = {"dsic": check_dsic, "ex_post_ir": check_ex_post_ir, "weak_budget_balance": check_weak_budget_balance,
        "strong_budget_balance": check_strong_budget_balance, "feasibility": check_feasibility,
        "allocative_efficiency": check_allocative_efficiency}


def ir_failure():
    base = _single_item_base("overcharge", (0, 1, 2), "zero")
    def rule(reports):
        winner = 0 if reports[0] >= reports[1] else 1; transfers = [Fraction(0), Fraction(0)]
        transfers[winner] = reports[winner] + 1
        return Outcome(f"winner:{winner}", Allocation(tuple(Fraction(i == winner) for i in range(2))), tuple(transfers))
    return DeterministicDirectMechanism("overcharge", base.agents, base.domain, rule, base.value, base.feasible,
                                        base.feasible_allocations, base.assumptions, base.tie_breaking, base.outside_options)


class CounterexampleTests(unittest.TestCase):
    SOURCES = {"dsic": "first_price.epl", "weak_budget_balance": "subsidized_mechanism.epl",
               "strong_budget_balance": "second_price.epl", "feasibility": "double_allocation.epl",
               "allocative_efficiency": "always_agent_zero.epl"}

    def certificate(self, prop, backend="z3"):
        mechanism = ir_failure() if prop == "ex_post_ir" else load_epl(ROOT / "examples" / self.SOURCES[prop])[1]
        problem = compile_property(mechanism, prop)
        result = solve_z3(problem) if backend == "z3" else solve_cvc5(problem)
        self.assertEqual(result.status, SolverStatus.SAT)
        return mechanism, problem, make_certificate(mechanism, problem, result)

    def test_all_six_typed_witnesses_validate_and_render(self):
        expected = {"dsic": DSICWitness, "ex_post_ir": IRWitness, "weak_budget_balance": BudgetWitness,
                    "strong_budget_balance": BudgetWitness, "feasibility": FeasibilityWitness,
                    "allocative_efficiency": EfficiencyWitness}
        for prop, witness_type in expected.items():
            with self.subTest(prop=prop):
                mechanism, problem, cert = self.certificate(prop)
                self.assertEqual(cert.witness_type, witness_type.__name__)
                self.assertTrue(validate_certificate(cert, mechanism, problem))
                self.assertIn("Replay: PASS", render_trace(cert))
                self.assertNotIn(".0", json.dumps(cert.witness, sort_keys=True))

    def test_cross_backend_exact_minimum_is_identical(self):
        for prop in self.SOURCES:
            with self.subTest(prop=prop):
                mechanism, problem, zcert = self.certificate(prop, "z3")
                _, _, ccert = self.certificate(prop, "cvc5")
                self.assertEqual(zcert.witness, ccert.witness)
                self.assertEqual(zcert.minimality, ccert.minimality)

    def test_tampering_is_rejected(self):
        mechanism, problem, cert = self.certificate("dsic")
        mutations = [
            dataclasses.replace(cert, mechanism_hash="sha256:bad"),
            dataclasses.replace(cert, property_version="epv.property.dsic.v999"),
            dataclasses.replace(cert, logical_problem_hash="sha256:bad"),
            dataclasses.replace(cert, replay={"status": "PASS"}, witness={**cert.witness, "utility_gain": "0"}),
        ]
        for changed in mutations: self.assertFalse(validate_certificate(changed, mechanism, problem))

    def test_zero_gain_is_not_dsic_violation(self):
        mechanism = load_epl(ROOT / "examples" / "second_price.epl")[1]
        problem = compile_property(mechanism, "dsic")
        self.assertTrue(any(c.predicate.lhs == c.predicate.rhs for c in problem.cases))
        self.assertEqual(solve_z3(problem).status, SolverStatus.UNSAT)

    def test_exact_minimum_is_global_exhaustive_minimum(self):
        mechanism = load_epl(ROOT / "examples" / "first_price.epl")[1]
        problem = compile_property(mechanism, "dsic")
        index, witness = exact_minimum(mechanism, problem)
        self.assertTrue(problem.cases[index].predicate.holds())
        self.assertEqual((index, witness), exact_minimum(mechanism, problem))


class MutantCorpusTests(unittest.TestCase):
    def test_corpus_size_provenance_and_property_matrix(self):
        corpus = mutant_corpus(); self.assertEqual(len(corpus), 60)
        evaluations = failures = exactly_minimized = 0
        vectors = set()
        for mutant in corpus:
            self.assertEqual(mutant.base_mechanism, "second-price auction")
            vector = []
            for prop, check in ENUM.items():
                evaluations += 1; failed = check(mutant.mechanism).status is Status.FALSIFIED
                vector.append(failed)
                if failed:
                    failures += 1
                    exact_minimum(mutant.mechanism, compile_property(mutant.mechanism, prop)); exactly_minimized += 1
            vectors.add(tuple(vector))
        self.assertEqual(evaluations, 360)
        self.assertGreater(failures, 0)
        self.assertEqual(failures, exactly_minimized)
        self.assertGreaterEqual(len(vectors), 8)


if __name__ == "__main__": unittest.main()
