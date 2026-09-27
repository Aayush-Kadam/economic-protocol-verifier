import sys, unittest
import json
from dataclasses import replace
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]; sys.path.insert(0,str(ROOT/"src"))
from epv.benchmarks import n_bidder_second_price_auction, second_price_auction
from epv.canonical import mechanism_hash
from epv.compiler import compile_property
from epv.domain_certificates import make_domain_counterexample,validate_domain_counterexample
from epv.fair_division import AdditiveInstance,FairAllocation,all_allocations,canonical_instance,compile_fair_division,fair_violations,round_robin
from epv.matching import UNMATCHED,MatchingMarket,MatchingOutcome,StrictPreference,canonical_market,compile_matching,deferred_acceptance,fixed_matching,matching_violations
from epv.property_registry import PROPERTIES,require_applicable
from epv.proofs import CheckerStatus,validate_domain_bundle
from epv.solvers import SolverStatus,solve_cvc5,solve_z3


class AuctionGeneralizationTests(unittest.TestCase):
    def test_n_bidder_properties(self):
        for n in (2,3,4):
            m=n_bidder_second_price_auction(n,(0,1))
            for p in ("dsic","ex_post_ir","weak_budget_balance","feasibility","allocative_efficiency"):
                with self.subTest(n=n,p=p): self.assertIs(solve_z3(compile_property(m,p)).status,SolverStatus.UNSAT)
    def test_tie_break_and_second_highest(self):
        out=n_bidder_second_price_auction(4).outcome((2,2,1,0)); self.assertEqual(out.label,"winner:0"); self.assertEqual(out.transfers,(2,0,0,0))
    def test_reject_one_bidder(self):
        with self.assertRaises(ValueError): n_bidder_second_price_auction(1)
    def test_historical_hash_unchanged(self): self.assertEqual(mechanism_hash(second_price_auction()),"sha256:36e5a80cee0d610f1eaee7d6bc794625bbfd2b89a91a15a44c9c2d77ea4867b9")


class MatchingSemanticTests(unittest.TestCase):
    def setUp(self): self.m=canonical_market(); self.da=deferred_acceptance(self.m)
    def test_da_exact_outcome(self): self.assertEqual(self.da.proposer_partners,("r1","r0"))
    def test_da_feasible_ir_stable(self):
        for p in ("epv.matching.feasibility.v1","epv.matching.individual_rationality.v1","epv.matching.stability.v1"):
            self.assertFalse(any(v for v,_ in matching_violations(self.m,self.da,p)))
    def test_da_proposer_strategyproof_on_declared_domain(self):
        problem=compile_matching(self.m,deferred_acceptance,"epv.matching.strategyproof_proposer.v1")
        self.assertIs(solve_z3(problem).status,SolverStatus.UNSAT); self.assertIs(solve_cvc5(problem).status,SolverStatus.UNSAT)
    def test_fixed_rule_has_blocking_pair(self):
        problem=compile_matching(self.m,fixed_matching,"epv.matching.stability.v1")
        self.assertIs(solve_z3(problem).status,SolverStatus.SAT); self.assertTrue(problem.cases[solve_z3(problem).case_index].predicate.holds())
    def test_blocking_pair_witness_fields(self):
        problem=compile_matching(self.m,fixed_matching,"epv.matching.stability.v1"); case=next(c for c in problem.cases if c.predicate.holds())
        self.assertEqual(set(case.payload),{"agent_a","agent_b","a_current_partner","b_current_partner","a_comparison","b_comparison"})
    def test_duplicate_receiver_is_infeasible(self):
        bad=MatchingOutcome(("r0","r0")); self.assertTrue(any(v for v,_ in matching_violations(self.m,bad,"epv.matching.feasibility.v1")))
    def test_ties_and_missing_unmatched_rejected(self):
        with self.assertRaises(ValueError): StrictPreference(("r0","r0",UNMATCHED))
        with self.assertRaises(ValueError): StrictPreference(("r0","r1"))
    def test_wrong_partner_universe_rejected(self):
        with self.assertRaises(ValueError): MatchingMarket(("p",),("r",),(StrictPreference(("x",UNMATCHED)),),(StrictPreference(("p",UNMATCHED)),))
    def test_ordinal_comparison_not_cardinal(self): self.assertTrue(self.m.proposer_preferences[0].prefers("r0","r1")); self.assertFalse(hasattr(self.m.proposer_preferences[0],"utility"))
    def test_matching_hash_changes_with_proposer_side_order(self):
        changed=MatchingMarket(tuple(reversed(self.m.proposers)),self.m.receivers,tuple(reversed(self.m.proposer_preferences)),self.m.receiver_preferences)
        self.assertNotEqual(self.m.semantic_hash(),changed.semantic_hash())
        self.assertNotEqual(self.m.mechanism_hash("deferred_acceptance","proposers"),self.m.mechanism_hash("deferred_acceptance","receivers"))
    def test_matching_counterexample_replays_and_tamper_fails(self):
        problem=compile_matching(self.m,fixed_matching,"epv.matching.stability.v1"); i=next(i for i,c in enumerate(problem.cases) if c.predicate.holds()); cert=make_domain_counterexample("matching",self.m.semantics_version,self.m.semantic_hash(),problem,i)
        self.assertTrue(validate_domain_counterexample(cert,"matching",self.m.semantics_version,self.m.semantic_hash(),problem)); self.assertFalse(validate_domain_counterexample(replace(cert,property_id="x"),"matching",self.m.semantics_version,self.m.semantic_hash(),problem))
    def test_matching_three_way_agreement(self):
        for mech,p,expected in [(deferred_acceptance,"epv.matching.stability.v1",SolverStatus.UNSAT),(fixed_matching,"epv.matching.stability.v1",SolverStatus.SAT),(deferred_acceptance,"epv.matching.strategyproof_proposer.v1",SolverStatus.UNSAT)]:
            q=compile_matching(self.m,mech,p); self.assertEqual(solve_z3(q).status,expected); self.assertEqual(solve_cvc5(q).status,expected)


class FairDivisionSemanticTests(unittest.TestCase):
    def setUp(self): self.i=canonical_instance(); self.a=round_robin(self.i)
    def test_round_robin_deterministic(self): self.assertEqual(self.a,round_robin(self.i)); self.assertEqual(self.a.bundles,(("g0","g2"),("g1",)))
    def test_round_robin_feasible_and_ef1(self):
        for p in ("epv.fair_division.feasibility.v1","epv.fair_division.ef1.v1"):
            self.assertFalse(any(v for v,_ in fair_violations(self.i,self.a,p)))
    def test_round_robin_can_fail_envy_free(self): self.assertTrue(any(v for v,_ in fair_violations(self.i,self.a,"epv.fair_division.envy_free.v1")))
    def test_double_allocation_detected(self):
        bad=FairAllocation((("g0","g1"),("g0","g2"))); self.assertTrue(any(v for v,_ in fair_violations(self.i,bad,"epv.fair_division.feasibility.v1")))
    def test_dropped_good_detected(self):
        bad=FairAllocation((("g0",),("g1",))); self.assertTrue(any(v for v,_ in fair_violations(self.i,bad,"epv.fair_division.feasibility.v1")))
    def test_float_and_negative_rejected(self):
        with self.assertRaises(TypeError): AdditiveInstance(("a",),("g",),((0.5,),))
        with self.assertRaises(TypeError): AdditiveInstance(("a",),("g",),((-1,),))
    def test_envy_uses_envier_valuation(self):
        rows=fair_violations(self.i,self.a,"epv.fair_division.envy_free.v1"); witness=next(p for v,p in rows if v); self.assertEqual(witness["envying_agent"],"a1"); self.assertEqual(witness["envied_value"],6)
    def test_ef1_removes_from_envied_bundle(self):
        bad=AdditiveInstance(("a0","a1"),("g0","g1","g2"),((2,2,0),(5,5,0))); allocation=FairAllocation((("g2",),("g0","g1")))
        self.assertTrue(any(v for v,_ in fair_violations(bad,allocation,"epv.fair_division.ef1.v1")))
    def test_pareto_not_total_welfare(self):
        instance=AdditiveInstance(("a0","a1"),("g0",),((10,),(9,))); allocation=FairAllocation((("g0",),()))
        self.assertFalse(any(v for v,_ in fair_violations(instance,allocation,"epv.fair_division.pareto_efficiency.v1")))
    def test_inefficient_allocation_has_full_witness(self):
        instance=AdditiveInstance(("a0","a1"),("g0","g1"),((2,1),(0,0))); allocation=FairAllocation(((),("g0","g1"))); problem=compile_fair_division(instance,allocation,"epv.fair_division.pareto_efficiency.v1"); case=next(c for c in problem.cases if c.predicate.holds()); self.assertIn("strictly_improved_agents",case.payload)
    def test_all_allocations_count(self): self.assertEqual(len(tuple(all_allocations(self.i))),8)
    def test_good_rename_metamorphism(self):
        renamed=AdditiveInstance(self.i.agents,("x","y","z"),self.i.values); renamed_a=round_robin(renamed)
        self.assertEqual([v for v,_ in fair_violations(self.i,self.a,"epv.fair_division.ef1.v1")],[v for v,_ in fair_violations(renamed,renamed_a,"epv.fair_division.ef1.v1")])
    def test_hash_changes_goods_and_values(self):
        self.assertNotEqual(self.i.semantic_hash(),AdditiveInstance(self.i.agents,("x","g1","g2"),self.i.values).semantic_hash()); self.assertNotEqual(self.i.semantic_hash(),AdditiveInstance(self.i.agents,self.i.goods,((4,2,1),(3,3,3))).semantic_hash())
        self.assertNotEqual(self.i.mechanism_hash("round_robin",(0,1)),self.i.mechanism_hash("round_robin",(1,0)))
    def test_fair_counterexample_replays_and_tamper_fails(self):
        problem=compile_fair_division(self.i,self.a,"epv.fair_division.envy_free.v1"); i=next(i for i,c in enumerate(problem.cases) if c.predicate.holds()); cert=make_domain_counterexample("fair-division",self.i.semantics_version,self.i.semantic_hash(),problem,i)
        self.assertTrue(validate_domain_counterexample(cert,"fair-division",self.i.semantics_version,self.i.semantic_hash(),problem)); self.assertFalse(validate_domain_counterexample(replace(cert,mechanism_hash="x"),"fair-division",self.i.semantics_version,self.i.semantic_hash(),problem))
    def test_fair_three_way_agreement(self):
        for p,expected in [("epv.fair_division.feasibility.v1",SolverStatus.UNSAT),("epv.fair_division.ef1.v1",SolverStatus.UNSAT),("epv.fair_division.envy_free.v1",SolverStatus.SAT)]:
            q=compile_fair_division(self.i,self.a,p); self.assertEqual(solve_z3(q).status,expected); self.assertEqual(solve_cvc5(q).status,expected)


class ApplicabilityTests(unittest.TestCase):
    def test_all_metadata_complete(self):
        for key,m in PROPERTIES.items(): self.assertEqual(key,m.property_id); self.assertTrue(m.formal_definition and m.quantifiers and m.witness_definition)
    def test_cross_domain_requests_rejected(self):
        for prop,domain in [("epv.matching.stability.v1","auction"),("epv.fair_division.ef1.v1","voting"),("epv.matching.feasibility.v1","fair_division")]:
            with self.subTest(prop=prop,domain=domain),self.assertRaises(ValueError): require_applicable(prop,domain)
    def test_unknown_property_rejected(self):
        with self.assertRaises(ValueError): require_applicable("epv.voting.condorcet.v1","fair_division")
    def test_cross_domain_hashes_are_namespaced(self): self.assertNotEqual(canonical_market().semantic_hash(),canonical_instance().semantic_hash())


class NewDomainProofTests(unittest.TestCase):
    CHECKER=ROOT/".tools"/"carcara-current"
    @unittest.skipUnless(CHECKER.exists(),"pinned Carcara not installed")
    def test_matching_stability_v3(self):
        m=canonical_market(); p="epv.matching.stability.v1"; flags=[v for v,_ in matching_violations(m,deferred_acceptance(m),p)]
        self.assertIs(validate_domain_bundle("matching",m.semantics_version,m.mechanism_hash("deferred_acceptance"),p,flags,ROOT/"proofs/matching_da_stability",self.CHECKER).status,CheckerStatus.ACCEPTED)
    @unittest.skipUnless(CHECKER.exists(),"pinned Carcara not installed")
    def test_fair_division_ef1_v3(self):
        f=canonical_instance(); p="epv.fair_division.ef1.v1"; flags=[v for v,_ in fair_violations(f,round_robin(f),p)]
        self.assertIs(validate_domain_bundle("fair_division",f.semantics_version,f.mechanism_hash("round_robin",(0,1)),p,flags,ROOT/"proofs/fair_round_robin_ef1",self.CHECKER).status,CheckerStatus.ACCEPTED)
    def test_auction_certificate_domain_swap_rejected(self):
        m=canonical_market(); p="epv.matching.stability.v1"; flags=[v for v,_ in matching_violations(m,deferred_acceptance(m),p)]
        result=validate_domain_bundle("matching",m.semantics_version,m.semantic_hash(),p,flags,ROOT/"proofs/second_price_dsic",self.CHECKER)
        self.assertIs(result.status,CheckerStatus.REJECTED)

    def test_benchmark_registry_balance(self):
        data=json.loads((ROOT/"benchmarks/m5/registry.json").read_text()); self.assertEqual(len(data["cases"]),12)
        self.assertEqual({d:sum(c["domain"]==d for c in data["cases"]) for d in ("auction","matching","fair_division")},{"auction":4,"matching":4,"fair_division":4})
        self.assertEqual(sum(c["polarity"]=="positive" for c in data["cases"]),6)

    def test_domain_proof_metadata_tamper_rejected(self):
        m=canonical_market(); p="epv.matching.stability.v1"; flags=[v for v,_ in matching_violations(m,deferred_acceptance(m),p)]
        result=validate_domain_bundle("matching",m.semantics_version,m.mechanism_hash("fixed"),p,flags,ROOT/"proofs/matching_da_stability",self.CHECKER)
        self.assertIs(result.status,CheckerStatus.REJECTED)

if __name__=="__main__": unittest.main()
