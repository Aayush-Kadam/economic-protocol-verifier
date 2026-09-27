import sys
import unittest
from fractions import Fraction
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from epv.benchmarks import first_price_auction  # noqa: E402
from epv.properties import check_dsic  # noqa: E402


class WitnessReplayTests(unittest.TestCase):
    def test_dsic_witness_replays_independently(self) -> None:
        mechanism = first_price_auction()
        witness = check_dsic(mechanism).witness
        agent = next(i for i, a in enumerate(mechanism.agents) if a.id == witness["agent"])
        theta = Fraction(witness["true_type"])
        truthful = Fraction(witness["truthful_report"])
        deviation = Fraction(witness["deviation_report"])
        others = iter(Fraction(value) for value in witness["other_reports"])
        truthful_profile = tuple(truthful if i == agent else next(others) for i in range(len(mechanism.agents)))
        deviation_profile = list(truthful_profile)
        deviation_profile[agent] = deviation
        truthful_outcome = mechanism.outcome(truthful_profile)
        deviation_outcome = mechanism.outcome(tuple(deviation_profile))
        self.assertGreater(
            mechanism.utility(agent, theta, deviation_outcome),
            mechanism.utility(agent, theta, truthful_outcome),
        )


if __name__ == "__main__":
    unittest.main()

