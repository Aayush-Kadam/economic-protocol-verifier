import json
import shutil
import sys
import tempfile
import unittest
from unittest.mock import patch
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from epv.benchmarks import always_agent_zero_mechanism, first_price_auction, second_price_auction  # noqa: E402
from epv.proofs import CheckerStatus, check_alethe, proof_problem, sha256, validate_bundle  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "proofs" / "second_price_dsic"
CHECKER = ROOT / ".tools" / "carcara-current"


class M4ProofTests(unittest.TestCase):
    def test_formula_is_deterministic(self):
        self.assertEqual(proof_problem(second_price_auction(), "dsic"), proof_problem(second_price_auction(), "dsic"))

    def test_formula_is_unsat_claim_over_real_dsic_cases(self):
        text = proof_problem(second_price_auction(), "dsic").decode()
        self.assertEqual(text.count("(declare-fun violation_"), 54)
        self.assertNotIn("(assert violation_", text)

    def test_falsified_property_cannot_generate_unsat_proof(self):
        text = proof_problem(first_price_auction(), "dsic").decode()
        self.assertIn("(assert violation_", text)

    @unittest.skipUnless(CHECKER.exists(), "pinned Carcara not installed")
    def test_committed_certificate_is_independently_accepted(self):
        self.assertIs(validate_bundle(second_price_auction(), "dsic", FIXTURE, CHECKER).status, CheckerStatus.ACCEPTED)

    @unittest.skipUnless(CHECKER.exists(), "pinned Carcara not installed")
    def test_all_six_property_families_have_accepted_certificates(self):
        pairs = [
            (second_price_auction(), "dsic", "second_price_dsic"),
            (second_price_auction(), "ex_post_ir", "second_price_ex_post_ir"),
            (second_price_auction(), "weak_budget_balance", "second_price_weak_budget_balance"),
            (always_agent_zero_mechanism(), "strong_budget_balance", "always_zero_strong_budget_balance"),
            (second_price_auction(), "feasibility", "second_price_feasibility"),
            (second_price_auction(), "allocative_efficiency", "second_price_allocative_efficiency"),
        ]
        for mechanism, prop, directory in pairs:
            with self.subTest(property=prop):
                result = validate_bundle(mechanism, prop, ROOT / "proofs" / directory, CHECKER)
                self.assertIs(result.status, CheckerStatus.ACCEPTED)

    def _mutate(self, field, value):
        tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, tmp)
        shutil.copytree(FIXTURE, tmp / "b")
        manifest_path = tmp / "b" / "manifest.json"
        manifest = json.loads(manifest_path.read_text())
        manifest[field] = value
        manifest_path.write_text(json.dumps(manifest))
        return validate_bundle(second_price_auction(), "dsic", tmp / "b", CHECKER)

    def test_wrong_mechanism_hash_rejected(self): self.assertIs(self._mutate("mechanism_hash", "sha256:00").status, CheckerStatus.REJECTED)
    def test_wrong_property_rejected(self): self.assertIs(self._mutate("property", "feasibility").status, CheckerStatus.REJECTED)
    def test_wrong_domain_rejected(self): self.assertIs(self._mutate("domain", {}).status, CheckerStatus.REJECTED)
    def test_wrong_assumptions_rejected(self): self.assertIs(self._mutate("assumptions", []).status, CheckerStatus.REJECTED)
    def test_wrong_formula_hash_rejected(self): self.assertIs(self._mutate("logical_problem_hash", "sha256:00").status, CheckerStatus.REJECTED)
    def test_wrong_proof_hash_rejected(self): self.assertIs(self._mutate("proof_hash", "sha256:00").status, CheckerStatus.REJECTED)

    def test_missing_checker_never_yields_v3(self):
        result = validate_bundle(second_price_auction(), "dsic", FIXTURE, ROOT / "missing-carcara")
        self.assertIs(result.status, CheckerStatus.ERROR)

    def test_corrupt_proof_rejected_before_checker(self):
        tmp = Path(tempfile.mkdtemp()); self.addCleanup(shutil.rmtree, tmp)
        shutil.copytree(FIXTURE, tmp / "b")
        with (tmp / "b" / "proof.alethe").open("ab") as f: f.write(b"corrupt")
        self.assertIs(validate_bundle(second_price_auction(), "dsic", tmp / "b", CHECKER).status, CheckerStatus.REJECTED)

    @unittest.skipUnless(CHECKER.exists(), "pinned Carcara not installed")
    def test_timeout_never_yields_v3(self):
        import subprocess
        with patch("epv.proofs.subprocess.run", side_effect=subprocess.TimeoutExpired("carcara", 0.001)):
            result = check_alethe(CHECKER, FIXTURE / "proof.alethe", FIXTURE / "problem.smt2", 0.001)
        self.assertIs(result.status, CheckerStatus.TIMEOUT)

    def test_cross_problem_reuse_rejected(self):
        self.assertIs(validate_bundle(first_price_auction(), "dsic", FIXTURE, CHECKER).status, CheckerStatus.REJECTED)

    def test_fixture_hashes_match_bytes(self):
        manifest = json.loads((FIXTURE / "manifest.json").read_text())
        self.assertEqual(manifest["logical_problem_hash"], sha256((FIXTURE / "problem.smt2").read_bytes()))
        self.assertEqual(manifest["proof_hash"], sha256((FIXTURE / "proof.alethe").read_bytes()))


if __name__ == "__main__": unittest.main()
