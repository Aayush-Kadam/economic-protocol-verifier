import csv
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class M0ArtifactTests(unittest.TestCase):
    def test_mandatory_artifacts_exist_and_are_nonempty(self) -> None:
        required = [
            "NOVELTY_AUDIT.md",
            "SCIENTIFIC_SCOPE.md",
            "FORMAL_PROBLEM.md",
            "FALSIFICATION_FRAMEWORK.md",
            "LITERATURE_REVIEW.md",
            "PRIOR_ART_MATRIX.csv",
            "COMPLEXITY_MAP.md",
            "TRUST_MODEL.md",
            "ARCHITECTURE.md",
            "docs/milestones/M0.md",
        ]
        for relative in required:
            path = ROOT / relative
            self.assertTrue(path.is_file(), relative)
            self.assertGreater(path.stat().st_size, 100, relative)

    def test_bibliography_is_structured_and_complete(self) -> None:
        records = json.loads((ROOT / "docs/literature/sources.json").read_text(encoding="utf-8"))
        self.assertGreaterEqual(len(records), 10)
        required = {"id", "title", "authors", "year", "venue", "url", "problem",
                    "mechanism_classes", "properties", "formalism", "solver_or_prover",
                    "proof_certification", "synthesis", "open_source", "relevance", "overlap"}
        for record in records:
            self.assertFalse(required - record.keys(), record["id"])
            self.assertTrue(record["url"].startswith("https://"))

    def test_prior_art_matrix_has_required_columns(self) -> None:
        with (ROOT / "PRIOR_ART_MATRIX.csv").open(encoding="utf-8", newline="") as handle:
            rows = list(csv.DictReader(handle))
        self.assertGreaterEqual(len(rows), 8)
        self.assertEqual(
            set(rows[0]),
            {"contribution_candidate", "prior_work", "exact_overlap", "what_epv_might_add",
             "novelty_confidence", "evidence", "risk"},
        )

    def test_no_broad_priority_claim(self) -> None:
        text = (ROOT / "NOVELTY_AUDIT.md").read_text(encoding="utf-8").lower()
        self.assertIn("broad concept is not novel", text)
        self.assertNotIn("first ever", text)


if __name__ == "__main__":
    unittest.main()

