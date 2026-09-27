import sys,unittest
from dataclasses import replace
from fractions import Fraction
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; sys.path.insert(0,str(ROOT/"src"))
from epv.benchmarks import first_price_auction,second_price_auction,deficit_auction,always_agent_zero_mechanism
from epv.compiler import compile_property
from epv.properties import check_dsic
from epv.proofs import CheckerStatus,validate_domain_bundle
from epv.result import Status
from epv.robustness import auction_severity
from epv.solvers import SolverStatus,solve_cvc5,solve_z3
from epv.synthesis import AuctionTableProblem,SynthesisStatus,compile_search_existence,exact_mus,repair_payment_table,reserve_auction,synthesize,synthesize_reserve,table_mechanism,validate_synthesis_result

REQ=("dsic","ex_post_ir","weak_budget_balance","feasibility","allocative_efficiency")

class SynthesisTests(unittest.TestCase):
    def test_problem_hash_deterministic_and_sensitive(self):
        p=AuctionTableProblem((0,1),(0,1),REQ); self.assertEqual(p.problem_hash(),AuctionTableProblem((0,1),(0,1),REQ).problem_hash()); self.assertNotEqual(p.problem_hash(),AuctionTableProblem((0,1),(-1,0,1),REQ).problem_hash())
    def test_search_size_explicit(self): self.assertEqual(AuctionTableProblem((0,1),(0,1),REQ).search_size(),16); self.assertEqual(AuctionTableProblem((0,1),(0,),REQ,"all-feasible").search_size(),81)
    def test_synthesizes_and_post_verifies(self):
        p=AuctionTableProblem((0,1),(0,1),REQ); r=synthesize(p); self.assertIs(r.status,SynthesisStatus.SAT_CANDIDATE_FOUND); self.assertEqual(len(r.post_verification),5); self.assertTrue(all(x[1]=="BOUNDED VERIFIED" for x in r.post_verification)); self.assertTrue(validate_synthesis_result(p,r))
    def test_canonical_rediscovery_extensional_payments(self):
        p=AuctionTableProblem((0,1),(0,1),REQ,objective="expected_revenue",prior=((0,1),(1,1))); r=synthesize(p)
        self.assertEqual(r.objective_value,"1/2"); self.assertEqual(tuple(x[2] for x in r.candidate_table),(('0','0'),('0','1'),('0','0'),('1','0')))
    def test_multiple_solution_canonical_tie_break(self):
        p=AuctionTableProblem((0,1),(0,1),("feasibility",)); self.assertEqual(synthesize(p).candidate_table,synthesize(p).candidate_table)
    def test_tampered_result_rejected(self):
        p=AuctionTableProblem((0,1),(0,1),REQ); r=synthesize(p); self.assertFalse(validate_synthesis_result(p,replace(r,candidate_hash="sha256:00")))
    def test_timeout_not_unsat(self): self.assertIs(synthesize(AuctionTableProblem((0,1),(0,1),REQ),timeout_ms=-1).status,SynthesisStatus.TIMEOUT)
    def test_invalid_property_and_missing_prior_rejected(self):
        with self.assertRaises(ValueError): AuctionTableProblem((0,1),(0,1),("epv.matching.stability.v1",))
        with self.assertRaises(ValueError): AuctionTableProblem((0,1),(0,1),REQ,objective="expected_revenue")
    def test_cross_backend_status_agreement(self):
        for p in (AuctionTableProblem((0,1),(0,1),REQ),AuctionTableProblem((0,1),(0,),("dsic","allocative_efficiency"),"all-feasible")):
            q=compile_search_existence(p); expected=SolverStatus.SAT if synthesize(p).status is not SynthesisStatus.UNSAT_IN_DECLARED_CLASS else SolverStatus.UNSAT
            self.assertIs(solve_z3(q).status,expected); self.assertIs(solve_cvc5(q).status,expected)

class RepairTests(unittest.TestCase):
    def test_exact_payment_only_repair(self):
        p=AuctionTableProblem((0,1),(0,1),REQ); distance,m,payments=repair_payment_table(first_price_auction((0,1)),p)
        self.assertEqual(distance[:2],(1,1)); self.assertIs(check_dsic(m).status,Status.BOUNDED_VERIFIED); self.assertEqual(payments,(0,1,0,1))
    def test_repair_canonical_tie_break(self):
        p=AuctionTableProblem((0,1),(0,1),("feasibility",)); a=repair_payment_table(first_price_auction((0,1)),p); b=repair_payment_table(first_price_auction((0,1)),p); self.assertEqual(a[0],b[0])
    def test_no_repair_inside_bounds(self):
        p=AuctionTableProblem((0,1),(1,),REQ); self.assertIsNone(repair_payment_table(first_price_auction((0,1)),p))

class ImpossibilityTests(unittest.TestCase):
    def setUp(self): self.p=AuctionTableProblem((0,1),(1,),("ex_post_ir","weak_budget_balance"),"efficient-lowest-index-tie")
    def test_bounded_unsat(self): self.assertIs(synthesize(self.p).status,SynthesisStatus.UNSAT_IN_DECLARED_CLASS)
    def test_exact_mus(self): self.assertIn(("ex_post_ir",),exact_mus(self.p))
    def test_mus_minimality(self):
        core=("ex_post_ir",); self.assertIs(synthesize(AuctionTableProblem((0,1),(1,),core)).status,SynthesisStatus.UNSAT_IN_DECLARED_CLASS)
        for x in core:self.assertIsNot(synthesize(AuctionTableProblem((0,1),(1,),tuple(y for y in core if y!=x))).status,SynthesisStatus.UNSAT_IN_DECLARED_CLASS)
    def test_expanding_bounds_restores_sat(self): self.assertIsNot(synthesize(AuctionTableProblem((0,1),(0,1),("ex_post_ir","weak_budget_balance"))).status,SynthesisStatus.UNSAT_IN_DECLARED_CLASS)
    @unittest.skipUnless((ROOT/".tools/carcara-current").exists(),"pinned Carcara not installed")
    def test_bounded_impossibility_v3_certificate(self):
        q=compile_search_existence(self.p); result=validate_domain_bundle("auction_synthesis","epv.synthesis.auction_table.v1",self.p.problem_hash(),"epv.auction.synthesis.exists.v1",[c.predicate.holds() for c in q.cases],ROOT/"proofs/m6_bounded_impossibility",ROOT/".tools/carcara-current")
        self.assertIs(result.status,CheckerStatus.ACCEPTED)
    def test_cross_problem_certificate_rejected(self):
        changed=AuctionTableProblem((0,1),(0,1),("ex_post_ir","weak_budget_balance")); q=compile_search_existence(changed)
        result=validate_domain_bundle("auction_synthesis","epv.synthesis.auction_table.v1",changed.problem_hash(),"epv.auction.synthesis.exists.v1",[c.predicate.holds() for c in q.cases],ROOT/"proofs/m6_bounded_impossibility",ROOT/".tools/carcara-current")
        self.assertIs(result.status,CheckerStatus.REJECTED)

class ParameterTests(unittest.TestCase):
    def test_reserve_region_and_optimum(self):
        region,optimum,revenue=synthesize_reserve((0,1,2,3)); self.assertEqual(region,(0,1,2,3)); self.assertIn(optimum,region); self.assertIsInstance(revenue,Fraction)
    def test_reserve_boundary_no_sale(self): self.assertEqual(reserve_auction(3).outcome((2,2)).label,"no-sale")
    def test_reserve_type_rejected(self):
        with self.assertRaises(TypeError): reserve_auction(Fraction(1,2))

class SeverityTests(unittest.TestCase):
    def test_dsic_gain_zero(self): self.assertEqual(auction_severity(second_price_auction())["max_manipulation_gain"][0],0)
    def test_non_dsic_gain_positive(self): self.assertGreater(auction_severity(first_price_auction())["max_manipulation_gain"][0],0)
    def test_max_deficit_positive(self): self.assertGreater(auction_severity(deficit_auction())["max_deficit"][0],0)
    def test_welfare_loss_positive(self): self.assertGreater(auction_severity(always_agent_zero_mechanism())["max_welfare_loss"][0],0)
    def test_exact_metric_identity(self): self.assertEqual(auction_severity(second_price_auction())["property_id"],"epv.auction.severity_metrics.v1")

if __name__=="__main__":unittest.main()
