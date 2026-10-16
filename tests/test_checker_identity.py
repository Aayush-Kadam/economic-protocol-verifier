"""A fresh clone can lengthen git's unique abbreviated revision."""
import json
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from epv.proofs import CHECKER_COMMIT, CheckerStatus, check_alethe


class CheckerIdentityTests(unittest.TestCase):
    def probe(self, identity, version_code=0, proof_output="valid", proof_code=0):
        with tempfile.TemporaryDirectory() as directory:
            checker = Path(directory) / "checker.exe"
            checker.touch()
            responses = [
                subprocess.CompletedProcess([], version_code, identity, ""),
                subprocess.CompletedProcess([], proof_code, proof_output, ""),
            ]
            with patch("epv.proofs.subprocess.run", side_effect=responses) as run:
                result = check_alethe(checker, Path("proof.alethe"), Path("problem.smt2"))
            return result, run.call_count

    def test_pinned_short_long_and_full_revisions_are_accepted(self):
        for length in (7, 8, 12, 40):
            with self.subTest(length=length):
                result, calls = self.probe(f"carcara 1.1.0 [git {CHECKER_COMMIT[:length]}]\n")
                self.assertIs(result.status, CheckerStatus.ACCEPTED)
                self.assertEqual(calls, 2)

    def test_other_or_malformed_identities_never_run_the_proof(self):
        for identity in (
            "carcara 1.1.1 [git 051d2f79]",
            "carcara 1.1.0 [git 051d2f70]",
            "carcara 1.1.0 [git 051d2f]",
            "carcara 1.1.0 [git 051d2f79-dirty]",
            "carcara 1.1.0 [git 051d2f79] extra",
            "carcara 1.1.0 [git 051d2f7900000000000000000000000000000000]",
        ):
            with self.subTest(identity=identity):
                result, calls = self.probe(identity)
                self.assertIs(result.status, CheckerStatus.UNSUPPORTED)
                self.assertEqual(calls, 1)

    def test_failed_identity_probe_or_invalid_proof_never_accepts(self):
        version = f"carcara 1.1.0 [git {CHECKER_COMMIT}]"
        self.assertIs(self.probe(version, version_code=1)[0].status, CheckerStatus.UNSUPPORTED)
        self.assertIs(self.probe(version, proof_output="invalid", proof_code=1)[0].status, CheckerStatus.REJECTED)

    def test_identity_pin_matches_tool_lock(self):
        lock = json.loads((Path(__file__).resolve().parents[1] / "tools.lock.json").read_text())
        self.assertEqual(CHECKER_COMMIT, lock["carcara"]["git_commit"])
