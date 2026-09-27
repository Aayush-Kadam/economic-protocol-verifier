import copy,json,random,shutil,sys,tempfile,time,unittest
from dataclasses import replace
from fractions import Fraction
from itertools import islice,permutations,product
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/"src"))
from epv.benchmarks import double_allocation_mechanism,first_price_auction,second_price_auction
from epv.canonical import mechanism_hash
from epv.compiler import compile_property
from epv.epl import EPLError,parse_epl
from epv.fair_division import AdditiveInstance,FairAllocation,compile_fair_division,fair_violations
from epv.matching import UNMATCHED,MatchingMarket,StrictPreference,compile_matching,deferred_acceptance,fixed_matching,matching_violations
from epv.properties import check_allocative_efficiency,check_dsic,check_ex_post_ir,check_feasibility,check_strong_budget_balance,check_weak_budget_balance
from epv.proofs import CheckerStatus,validate_bundle
from epv.result import Status
from epv.robustness import auction_severity
from epv.solvers import SolverStatus,solve_cvc5,solve_z3
from epv.synthesis import AuctionTableProblem,SynthesisStatus,exact_mus,repair_payment_table,synthesize,table_mechanism,validate_synthesis_result

CHECKS={"dsic":check_dsic,"ex_post_ir":check_ex_post_ir,"weak_budget_balance":check_weak_budget_balance,"strong_budget_balance":check_strong_budget_balance,"feasibility":check_feasibility,"allocative_efficiency":check_allocative_efficiency}

def independent_auction(table,prop):
    profiles=((0,0),(0,1),(1,0),(1,1)); outcomes={p:table[p] for p in profiles}
    if prop=="feasibility": return all(o[0] in (-1,0,1) for o in outcomes.values())
    if prop=="weak_budget_balance": return all(sum(o[1])>=0 for o in outcomes.values())
    if prop=="strong_budget_balance": return all(sum(o[1])==0 for o in outcomes.values())
    if prop=="ex_post_ir":
        return all((theta if o[0]==i else 0)-o[1][i]>=0 for p,o in outcomes.items() for i,theta in enumerate(p))
    if prop=="allocative_efficiency": return all((p[o[0]] if o[0] in (0,1) else 0)>=max(p) for p,o in outcomes.items())
    if prop=="dsic":
        for i,theta,other,dev in product(range(2),(0,1),(0,1),(0,1)):
            truth=(theta,other) if i==0 else (other,theta); altered=(dev,other) if i==0 else (other,dev)
            to,do=outcomes[truth],outcomes[altered]; tu=(theta if to[0]==i else 0)-to[1][i]; du=(theta if do[0]==i else 0)-do[1][i]
            if du>tu:return False
        return True
    raise ValueError(prop)

class DifferentialCorpusTests(unittest.TestCase):
    def test_auction_generated_corpus_three_way_and_hand_oracle(self):
        problem=AuctionTableProblem((0,1),(-1,0,1),(),"all-feasible")
        rng=random.Random(7001); profiles=problem.profiles()
        for case in range(64):
            alloc=tuple(rng.choice((-1,0,1)) for _ in profiles); payments=tuple(rng.choice((-1,0,1)) for _ in profiles); m=table_mechanism(problem,alloc,payments)
            table={p:(alloc[k],tuple(int(x) for x in m.outcome(tuple(Fraction(y) for y in p)).transfers)) for k,p in enumerate(profiles)}
            for prop,check in CHECKS.items():
                expected=independent_auction(table,prop); actual=check(m).status is Status.BOUNDED_VERIFIED; self.assertEqual(actual,expected,(case,prop))
                q=compile_property(m,prop); solver_expected=SolverStatus.UNSAT if expected else SolverStatus.SAT
                self.assertIs(solve_z3(q).status,solver_expected);self.assertIs(solve_cvc5(q).status,solver_expected)
    def test_matching_generated_profiles(self):
        ps=tuple(StrictPreference(x) for x in permutations(("r0","r1",UNMATCHED)));rs=tuple(StrictPreference(x) for x in permutations(("p0","p1",UNMATCHED)))
        for k in range(24):
            m=MatchingMarket(("p0","p1"),("r0","r1"),(ps[k%6],ps[(k*3+1)%6]),(rs[(k*5)%6],rs[(k+2)%6])); out=deferred_acceptance(m)
            for prop in ("epv.matching.feasibility.v1","epv.matching.individual_rationality.v1","epv.matching.stability.v1"):
                rows=matching_violations(m,out,prop);q=compile_matching(m,deferred_acceptance,prop);expected=SolverStatus.SAT if any(v for v,_ in rows) else SolverStatus.UNSAT
                self.assertIs(solve_z3(q).status,expected);self.assertIs(solve_cvc5(q).status,expected)
    def test_fair_division_generated_corpus(self):
        for k,vals in enumerate(islice(product(range(3),repeat=6),32)):
            i=AdditiveInstance(("a0","a1"),("g0","g1","g2"),(vals[:3],vals[3:])); owners=tuple((k>>g)&1 for g in range(3)); a=FairAllocation(tuple(tuple(i.goods[g] for g,o in enumerate(owners) if o==agent) for agent in range(2)))
            for prop in ("epv.fair_division.feasibility.v1","epv.fair_division.envy_free.v1","epv.fair_division.ef1.v1","epv.fair_division.pareto_efficiency.v1"):
                rows=fair_violations(i,a,prop);q=compile_fair_division(i,a,prop);expected=SolverStatus.SAT if any(v for v,_ in rows) else SolverStatus.UNSAT
                self.assertIs(solve_z3(q).status,expected);self.assertIs(solve_cvc5(q).status,expected)

class MetamorphicAndMetricTests(unittest.TestCase):
    def test_positive_scaling_preserves_auction_vectors(self):
        for factory in (second_price_auction,first_price_auction):
            a,b=factory((0,1,2)),factory((0,2,4)); self.assertEqual(tuple(CHECKS[p](a).status for p in CHECKS),tuple(CHECKS[p](b).status for p in CHECKS))
    def test_severity_independent_consistency(self):
        problem=AuctionTableProblem((0,1),(-1,0,1),(),"all-feasible");rng=random.Random(91)
        for _ in range(40):
            alloc=tuple(rng.choice((-1,0,1)) for _ in problem.profiles());pay=tuple(rng.choice((-1,0,1)) for _ in problem.profiles());m=table_mechanism(problem,alloc,pay);s=auction_severity(m)
            self.assertEqual(check_dsic(m).status is Status.BOUNDED_VERIFIED,s["max_manipulation_gain"][0]==0)
            self.assertEqual(check_weak_budget_balance(m).status is Status.BOUNDED_VERIFIED,s["max_deficit"][0]==0)
            self.assertEqual(check_allocative_efficiency(m).status is Status.BOUNDED_VERIFIED,s["max_welfare_loss"][0]==0)
    def test_formatting_semantic_identity(self):
        raw=(ROOT/"examples/second_price.epl").read_text();a=parse_epl(raw);b=parse_epl(json.dumps(json.loads(raw),indent=7));self.assertNotEqual(a.source_hash,b.source_hash)

class ParserFuzzTests(unittest.TestCase):
    def setUp(self): self.base=json.loads((ROOT/"examples/second_price.epl").read_text())
    def test_200_malformed_inputs_fail_closed(self):
        malformed=["", "{", "[]", "null", "1", '"x"', "["*2000+"]"*2000]
        fields=[x for x in self.base if x!="verify"]
        for i in range(193):
            d=copy.deepcopy(self.base)
            if i%3==0: d.pop(fields[i%len(fields)],None)
            elif i%3==1: d[f"unknown_{i}"]=i
            else: d[["agents","types","reports","allocation","payments"][i%5]]=None
            malformed.append(json.dumps(d))
        for text in malformed:
            with self.subTest(prefix=text[:20]),self.assertRaises(EPLError):parse_epl(text)
    def test_resource_limits(self):
        with self.assertRaises(EPLError):parse_epl(" "*1_000_001)
        d=copy.deepcopy(self.base);d["types"]["integer"]={"min":0,"max":1000}
        with self.assertRaises(EPLError):parse_epl(json.dumps(d))
    def test_valid_format_fuzz(self):
        raw=self.base
        for indent in (None,0,1,2,4,8): self.assertEqual(mechanism_hash(__import__('epv.epl',fromlist=['elaborate']).elaborate(parse_epl(json.dumps(raw,indent=indent)))),mechanism_hash(second_price_auction()))

class CertificateAttackTests(unittest.TestCase):
    CHECKER=ROOT/".tools/carcara-current"; FIX=ROOT/"proofs/second_price_dsic"
    def _copy(self):
        tmp=Path(tempfile.mkdtemp());self.addCleanup(shutil.rmtree,tmp);shutil.copytree(self.FIX,tmp/"b");return tmp/"b"
    def test_15_manifest_mutations_rejected(self):
        fields=["schema","assurance","property","property_version","mechanism_hash","mechanism","domain","assumptions","logical_problem_hash","proof_hash","proof_format","producer","checker","epv_commit"]
        for field in fields:
            b=self._copy();p=b/"manifest.json";d=json.loads(p.read_text());d[field]=None;p.write_text(json.dumps(d));self.assertIs(validate_bundle(second_price_auction(),"dsic",b,self.CHECKER).status,CheckerStatus.REJECTED,field)
    def test_missing_files_fail_closed(self):
        for filename in ("proof.alethe","problem.smt2"):
            b=self._copy();(b/filename).unlink();self.assertIs(validate_bundle(second_price_auction(),"dsic",b,self.CHECKER).status,CheckerStatus.REJECTED)
    @unittest.skipUnless(CHECKER.exists(),"pinned Carcara not installed")
    def test_truncated_proofs_never_accept(self):
        for divisor in (2,3,4):
            b=self._copy();p=b/"proof.alethe";raw=p.read_bytes()[:len(p.read_bytes())//divisor];p.write_bytes(raw);d=json.loads((b/"manifest.json").read_text());import hashlib;d["proof_hash"]="sha256:"+hashlib.sha256(raw).hexdigest();(b/"manifest.json").write_text(json.dumps(d));self.assertIsNot(validate_bundle(second_price_auction(),"dsic",b,self.CHECKER).status,CheckerStatus.ACCEPTED)

class SynthesisHostileTests(unittest.TestCase):
    def test_32_tiny_searches_match_independent_exhaustion(self):
        props=("dsic","ex_post_ir","weak_budget_balance","feasibility","allocative_efficiency")
        for mask in range(32):
            selected=tuple(p for i,p in enumerate(props) if mask>>i&1);problem=AuctionTableProblem((0,1),(0,1),selected);r=synthesize(problem);self.assertTrue(validate_synthesis_result(problem,r));self.assertIsNot(r.status,SynthesisStatus.UNSAT_IN_DECLARED_CLASS)
    def test_repair_rejects_out_of_class_baseline(self):
        p=AuctionTableProblem((0,1),(0,1),("dsic",));
        with self.assertRaises(ValueError):repair_payment_table(double_allocation_mechanism((0,1)),p)
    def test_malformed_priors_rejected(self):
        for prior in (((0,1),),((0,1),(0,2),(1,1)),((0,-1),(1,2)),((0,0),(1,0))):
            with self.assertRaises(ValueError):AuctionTableProblem((0,1),(0,1),("dsic",),objective="expected_revenue",prior=prior)
    def test_fake_nonminimal_core_detected(self):
        p=AuctionTableProblem((0,1),(1,),("ex_post_ir","weak_budget_balance"));self.assertEqual(exact_mus(p),(("ex_post_ir",),));self.assertNotIn(("ex_post_ir","weak_budget_balance"),exact_mus(p))

class MutationAnalysisTests(unittest.TestCase):
    def test_critical_mutant_families_are_killed(self):
        m=first_price_auction();p=compile_property(m,"dsic");truth=[c.predicate.holds() for c in p.cases]
        mutants=[not any(truth),not any(truth[:-1]),all(truth),False,any(c.predicate.lhs<c.predicate.rhs for c in p.cases),any(c.predicate.lhs>=c.predicate.rhs for c in p.cases)]
        expected=check_dsic(m).status is Status.FALSIFIED
        self.assertTrue(expected);self.assertTrue(any(truth));self.assertGreaterEqual(sum(x!=expected for x in mutants),4)

if __name__=="__main__":unittest.main()
