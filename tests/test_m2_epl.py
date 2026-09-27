import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from epv.benchmarks import (always_agent_zero_mechanism, deficit_auction, double_allocation_mechanism,
                            first_price_auction, second_price_auction)
from epv.canonical import canonical_bytes, mechanism_hash
from epv.epl import EPLError, elaborate, load_epl, parse_epl
from epv.properties import (check_allocative_efficiency, check_dsic, check_ex_post_ir, check_feasibility,
                            check_strong_budget_balance, check_weak_budget_balance)


class EPLEquivalenceTests(unittest.TestCase):
    CASES = {
        "second_price.epl": second_price_auction,
        "first_price.epl": first_price_auction,
        "subsidized_mechanism.epl": lambda values=(0, 1, 2): deficit_auction(values),
        "double_allocation.epl": lambda values=(0, 1, 2): double_allocation_mechanism(values),
        "always_agent_zero.epl": always_agent_zero_mechanism,
    }

    def test_epl_and_direct_mechanisms_are_semantically_identical(self):
        for filename, factory in self.CASES.items():
            with self.subTest(filename=filename):
                _, parsed = load_epl(ROOT / "examples" / filename)
                direct = factory()
                self.assertEqual(canonical_bytes(parsed), canonical_bytes(direct))
                self.assertEqual(mechanism_hash(parsed), mechanism_hash(direct))
                checks = (check_dsic, check_ex_post_ir, check_weak_budget_balance,
                          check_strong_budget_balance, check_feasibility, check_allocative_efficiency)
                self.assertEqual([f(parsed).status for f in checks], [f(direct).status for f in checks])

    def test_formatting_changes_source_hash_not_semantic_hash(self):
        path = ROOT / "examples" / "second_price.epl"
        text = path.read_text(encoding="utf-8")
        compact = json.dumps(json.loads(text), separators=(",", ":"))
        ast_a, mechanism_a = parse_epl(text, str(path)), elaborate(parse_epl(text, str(path)))
        ast_b, mechanism_b = parse_epl(compact, "compact.epl"), elaborate(parse_epl(compact, "compact.epl"))
        self.assertNotEqual(ast_a.source_hash, ast_b.source_hash)
        self.assertEqual(mechanism_hash(mechanism_a), mechanism_hash(mechanism_b))

    def test_domain_bounds_are_inclusive_and_exact(self):
        ast, mechanism = load_epl(ROOT / "examples" / "second_price.epl")
        self.assertEqual(mechanism.domain.type_spaces[0], (0, 1, 2))
        self.assertEqual(mechanism.domain.report_spaces[0], (0, 1, 2))

    def test_verification_relevant_changes_change_hash_or_fail_closed(self):
        original = json.loads((ROOT / "examples" / "second_price.epl").read_text())
        _, baseline = load_epl(ROOT / "examples" / "second_price.epl")
        changes = [
            ("type domain", lambda v: v["types"]["integer"].update(max=3)),
            ("report domain", lambda v: v["reports"]["integer"].update(max=3)),
            ("allocation", lambda v: v["allocation"].update(rule="agent_zero", tie_break="not_applicable")),
            ("payment", lambda v: v["payments"].update(rule="own_report")),
            ("tie break", lambda v: v["allocation"].update(tie_break="not_applicable")),
            ("resource", lambda v: v["resource"].update(capacity=2)),
            ("utility", lambda v: v["utility"].update(rule="reported_value")),
            ("feasibility", lambda v: v["feasibility"].update(rule="none")),
            ("assumptions", lambda v: v.update(assumptions=["quasi_linear"])),
            ("agents", lambda v: v.update(agents={"count": 3, "prefix": "bidder"})),
        ]
        for label, mutate in changes:
            value = json.loads(json.dumps(original)); mutate(value)
            try:
                changed = elaborate(parse_epl(json.dumps(value), f"{label}.epl"))
            except EPLError:
                continue
            self.assertNotEqual(mechanism_hash(baseline), mechanism_hash(changed), label)


class EPLFailureTests(unittest.TestCase):
    def base(self):
        return json.loads((ROOT / "examples" / "second_price.epl").read_text(encoding="utf-8"))

    def assert_category(self, value, category, token):
        text = json.dumps(value, indent=2)
        with self.assertRaises(EPLError) as caught:
            parse_epl(text, "invalid.epl")
        self.assertEqual(caught.exception.category, category)
        self.assertGreaterEqual(caught.exception.location.line, 1)
        self.assertIn("invalid.epl", str(caught.exception))

    def test_missing_tie_break(self):
        value = self.base(); value["allocation"].pop("tie_break")
        self.assert_category(value, "InvalidAllocation", "allocation")

    def test_invalid_domain(self):
        value = self.base(); value["types"]["integer"] = {"min": 3, "max": 1}
        self.assert_category(value, "InvalidDomain", "types")

    def test_float_rejected(self):
        text = (ROOT / "examples" / "second_price.epl").read_text().replace('"min": 0', '"min": 0.0', 1)
        with self.assertRaises(EPLError) as caught: parse_epl(text, "float.epl")
        self.assertEqual(caught.exception.category, "UnsupportedNumericType")

    def test_unknown_property(self):
        value = self.base(); value["verify"] = ["fair"]
        self.assert_category(value, "UnknownProperty", "verify")

    def test_duplicate_agent(self):
        value = self.base(); value["agents"] = {"ids": ["a", "a"]}
        self.assert_category(value, "DuplicateAgent", "agents")

    def test_undefined_or_unknown_construct(self):
        value = self.base(); value["python"] = "eval('bad')"
        self.assert_category(value, "UnsupportedConstruct", "python")

    def test_wrong_transfer_sign(self):
        value = self.base(); value["payments"]["sign"] = "mechanism_pays_agent"
        self.assert_category(value, "TransferSignError", "payments")

    def test_duplicate_json_key_rejected(self):
        with self.assertRaises(EPLError) as caught:
            parse_epl('{"schema":"epv-epl-0.1","schema":"x"}', "duplicate.epl")
        self.assertEqual(caught.exception.category, "DuplicateDefinition")


if __name__ == "__main__": unittest.main()
