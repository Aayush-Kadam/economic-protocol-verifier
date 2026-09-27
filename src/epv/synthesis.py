from __future__ import annotations

import hashlib, json, time
from dataclasses import asdict, dataclass
from enum import Enum
from fractions import Fraction
from itertools import combinations, product

from .benchmarks import second_price_auction
from .compiler import compile_property
from .compiler import Predicate,WitnessCase,WitnessProblem
from .eir import Agent, Allocation, Assumption, DeterministicDirectMechanism, Outcome, VerificationDomain
from .properties import check_allocative_efficiency,check_dsic,check_ex_post_ir,check_feasibility,check_strong_budget_balance,check_weak_budget_balance
from .result import Status

CHECKS={"dsic":check_dsic,"ex_post_ir":check_ex_post_ir,"weak_budget_balance":check_weak_budget_balance,"strong_budget_balance":check_strong_budget_balance,"feasibility":check_feasibility,"allocative_efficiency":check_allocative_efficiency}

class SynthesisStatus(str,Enum):
    SAT_CANDIDATE_FOUND="SAT_CANDIDATE_FOUND"
    OPTIMAL_CANDIDATE_FOUND="OPTIMAL_CANDIDATE_FOUND"
    UNSAT_IN_DECLARED_CLASS="UNSAT_IN_DECLARED_CLASS"
    UNKNOWN="UNKNOWN"; TIMEOUT="TIMEOUT"; ERROR="ERROR"

@dataclass(frozen=True)
class AuctionTableProblem:
    values: tuple[int,...]
    payment_values: tuple[int,...]
    required_properties: tuple[str,...]
    allocation_family: str="efficient-lowest-index-tie"
    loser_payment: int=0
    objective: str|None=None
    prior: tuple[tuple[int,int],...]|None=None
    schema: str="epv-synthesis-problem-v1"
    domain_family: str="auction"
    def __post_init__(self):
        if len(self.values)<2 or tuple(sorted(set(self.values)))!=self.values: raise ValueError("values must be sorted unique integers")
        if not self.payment_values or any(isinstance(x,bool) or not isinstance(x,int) for x in self.payment_values): raise TypeError("finite integer payment bounds required")
        if any(p not in CHECKS for p in self.required_properties): raise ValueError("inapplicable or unknown auction property")
        if self.allocation_family not in {"efficient-lowest-index-tie","all-feasible"}: raise ValueError("unknown allocation family")
        if self.objective not in {None,"expected_revenue","expected_welfare"}: raise ValueError("unknown objective")
        if self.objective and self.prior is None: raise ValueError("optimization requires explicit exact prior")
    def canonical_bytes(self): return json.dumps(asdict(self),sort_keys=True,separators=(",",":")).encode()
    def problem_hash(self): return "sha256:"+hashlib.sha256(self.canonical_bytes()).hexdigest()
    def profiles(self): return tuple(product(self.values,repeat=2))
    def search_size(self):
        allocations=1 if self.allocation_family.startswith("efficient") else 3**len(self.profiles())
        return allocations*(len(self.payment_values)**len(self.profiles()))

@dataclass(frozen=True)
class SynthesisResult:
    schema: str; problem_hash: str; status: SynthesisStatus; search_size: int; candidates_checked: int
    candidate_hash: str|None=None; candidate_table: tuple|None=None; objective_value: str|None=None
    optimality: str="not applicable"; post_verification: tuple[tuple[str,str],...]=(); runtime_ms: float=0


def table_mechanism(problem:AuctionTableProblem, allocations, winner_payments):
    profiles=problem.profiles(); index={p:i for i,p in enumerate(profiles)}; space=tuple(Fraction(v) for v in problem.values)
    domain=VerificationDomain((space,space),(space,space)); feasible=(Allocation((0,0)),Allocation((1,0)),Allocation((0,1)))
    def rule(reports):
        k=index[tuple(int(x) for x in reports)]; winner=allocations[k]; alloc=Allocation((0,0) if winner==-1 else tuple(Fraction(i==winner) for i in range(2)))
        transfers=[Fraction(problem.loser_payment),Fraction(problem.loser_payment)]
        if winner!=-1: transfers[winner]=Fraction(winner_payments[k])
        return Outcome(f"table:{k}:winner:{winner}",alloc,tuple(transfers))
    def value(i,theta,a): return theta*a.quantities[i]
    return DeterministicDirectMechanism("synthesized finite auction",(Agent("bidder-0"),Agent("bidder-1")),domain,rule,value,lambda a:sum(a.quantities)<=1,feasible,(Assumption("search_class",problem.problem_hash()),),"table-declared; efficient family uses lowest index tie",(Fraction(0),Fraction(0)))


def _allocations(problem):
    if problem.allocation_family.startswith("efficient"):
        yield tuple(0 if a>=b else 1 for a,b in problem.profiles())
    else: yield from product((-1,0,1),repeat=len(problem.profiles()))

def _valid(m,requirements): return all(CHECKS[p](m).status is Status.BOUNDED_VERIFIED for p in requirements)
def _table(m,problem): return tuple((p,m.outcome(tuple(Fraction(x) for x in p)).label,tuple(str(x) for x in m.outcome(tuple(Fraction(x) for x in p)).transfers)) for p in problem.profiles())
def _objective(m,problem):
    if problem.objective is None:return Fraction(0)
    weights=dict(problem.prior); total=sum(weights.values()); value=Fraction(0)
    for profile in problem.profiles():
        probability=Fraction(weights[profile[0]]*weights[profile[1]],total*total); out=m.outcome(tuple(Fraction(x) for x in profile))
        value += probability*(sum(out.transfers) if problem.objective=="expected_revenue" else m.welfare(tuple(Fraction(x) for x in profile),out.allocation))
    return value


def synthesize(problem:AuctionTableProblem,timeout_ms=10000):
    start=time.perf_counter(); checked=0; valid=[]
    for alloc in _allocations(problem):
        for payments in product(problem.payment_values,repeat=len(problem.profiles())):
            if (time.perf_counter()-start)*1000>timeout_ms: return SynthesisResult("epv-synthesis-result-v1",problem.problem_hash(),SynthesisStatus.TIMEOUT,problem.search_size(),checked,runtime_ms=(time.perf_counter()-start)*1000)
            checked+=1; m=table_mechanism(problem,alloc,payments)
            if _valid(m,problem.required_properties): valid.append((_objective(m,problem),_table(m,problem),m,alloc,payments))
    runtime=(time.perf_counter()-start)*1000
    if not valid:return SynthesisResult("epv-synthesis-result-v1",problem.problem_hash(),SynthesisStatus.UNSAT_IN_DECLARED_CLASS,problem.search_size(),checked,runtime_ms=runtime)
    best=max(x[0] for x in valid); finalists=[x for x in valid if x[0]==best]; chosen=min(finalists,key=lambda x:json.dumps(x[1],separators=(",",":")))
    objective,table,m,_,_=chosen; verification=tuple((p,CHECKS[p](m).status.value) for p in problem.required_properties)
    from .canonical import mechanism_hash
    status=SynthesisStatus.OPTIMAL_CANDIDATE_FOUND if problem.objective else SynthesisStatus.SAT_CANDIDATE_FOUND
    return SynthesisResult("epv-synthesis-result-v1",problem.problem_hash(),status,problem.search_size(),checked,mechanism_hash(m),table,str(objective),"exhaustive enumeration; canonical lexical tie-break",verification,runtime)

def compile_search_existence(problem:AuctionTableProblem):
    cases=[]
    for alloc in _allocations(problem):
        for payments in product(problem.payment_values,repeat=len(problem.profiles())):
            m=table_mechanism(problem,alloc,payments); valid=_valid(m,problem.required_properties)
            cases.append(WitnessCase(Predicate(">",int(valid),0),{"allocations":alloc,"payments":payments}))
    return WitnessProblem("auction_synthesis_exists","epv.auction.synthesis.exists.v1",tuple(cases),"finite-mechanism-table")

def validate_synthesis_result(problem,result):
    if result.schema!="epv-synthesis-result-v1" or result.problem_hash!=problem.problem_hash() or result.search_size!=problem.search_size(): return False
    fresh=synthesize(problem)
    keys=("status","candidate_hash","candidate_table","objective_value","optimality","post_verification")
    return all(getattr(result,k)==getattr(fresh,k) for k in keys)


def exact_mus(problem:AuctionTableProblem):
    props=problem.required_properties; cores=[]
    for size in range(1,len(props)+1):
        for subset in combinations(props,size):
            candidate=AuctionTableProblem(problem.values,problem.payment_values,subset,problem.allocation_family,problem.loser_payment)
            if synthesize(candidate).status is SynthesisStatus.UNSAT_IN_DECLARED_CLASS and all(synthesize(AuctionTableProblem(problem.values,problem.payment_values,tuple(x for x in subset if x!=removed),problem.allocation_family,problem.loser_payment)).status is not SynthesisStatus.UNSAT_IN_DECLARED_CLASS for removed in subset): cores.append(subset)
    return tuple(cores)


def repair_payment_table(baseline:DeterministicDirectMechanism,problem:AuctionTableProblem):
    if problem.allocation_family!="efficient-lowest-index-tie": raise ValueError("M6 repair supports payment-only efficient allocation")
    base=[]
    for p in problem.profiles():
        o=baseline.outcome(tuple(Fraction(x) for x in p)); winner=0 if o.allocation.quantities[0] else 1; base.append(int(o.transfers[winner]))
    valid=[]
    alloc=tuple(0 if a>=b else 1 for a,b in problem.profiles())
    for payments in product(problem.payment_values,repeat=len(base)):
        m=table_mechanism(problem,alloc,payments)
        if _valid(m,problem.required_properties):
            distance=(sum(a!=b for a,b in zip(payments,base,strict=True)),sum(abs(a-b) for a,b in zip(payments,base,strict=True)),payments)
            valid.append((distance,m,payments))
    if not valid:return None
    return min(valid,key=lambda x:x[0])


def reserve_auction(reserve:int,values=(0,1,2)):
    if isinstance(reserve,bool) or not isinstance(reserve,int): raise TypeError("integer reserve required")
    base=second_price_auction(values); n=2
    def rule(reports):
        winner=min(range(n),key=lambda i:(-reports[i],i))
        if reports[winner]<reserve:return Outcome("no-sale",Allocation((0,0)),(0,0))
        payment=max(Fraction(reserve),reports[1-winner]); transfers=[Fraction(0),Fraction(0)]; transfers[winner]=payment
        return Outcome(f"winner:{winner}",Allocation(tuple(Fraction(i==winner) for i in range(n))),tuple(transfers))
    return DeterministicDirectMechanism(f"second-price reserve {reserve}",base.agents,base.domain,rule,base.value,base.feasible,base.feasible_allocations,base.assumptions,"lowest index wins eligible tie",base.outside_options)


def synthesize_reserve(reserves,values=(0,1,2)):
    rows=[]
    for r in reserves:
        m=reserve_auction(r,values); valid=all(CHECKS[p](m).status is Status.BOUNDED_VERIFIED for p in ("dsic","ex_post_ir","weak_budget_balance"))
        revenue=sum((sum(m.outcome(tuple(Fraction(x) for x in p)).transfers) for p in product(values,repeat=2)),Fraction(0))/len(values)**2
        if valid: rows.append((revenue,r))
    return tuple(r for _,r in rows),max(rows)[1] if rows else None,max(rows)[0] if rows else None
