from __future__ import annotations

import hashlib, json
from dataclasses import dataclass
from itertools import product

from .compiler import Predicate, WitnessCase, WitnessProblem
from .property_registry import require_applicable


@dataclass(frozen=True)
class AdditiveInstance:
    agents: tuple[str,...]; goods: tuple[str,...]; values: tuple[tuple[int,...],...]
    semantics_version: str = "epv.fair_division.additive_indivisible.v1"
    def __post_init__(self):
        if len(set(self.agents)) != len(self.agents) or len(set(self.goods)) != len(self.goods): raise ValueError("IDs must be unique")
        if len(self.values)!=len(self.agents) or any(len(row)!=len(self.goods) for row in self.values): raise ValueError("valuation matrix shape mismatch")
        if any(isinstance(v,bool) or not isinstance(v,int) or v<0 for row in self.values for v in row): raise TypeError("valuations must be nonnegative integers")
    def value(self,agent,bundle): return sum(self.values[agent][self.goods.index(g)] for g in bundle)
    def canonical_document(self): return {"domain_family":"fair_division","semantics_version":self.semantics_version,"agents":self.agents,"goods":self.goods,"values":self.values}
    def semantic_hash(self): return "sha256:"+hashlib.sha256(json.dumps(self.canonical_document(),sort_keys=True,separators=(",",":")).encode()).hexdigest()
    def mechanism_hash(self, rule: str, order: tuple[int,...]):
        if sorted(order)!=list(range(len(self.agents))): raise ValueError("order must permute all agents")
        doc={"instance":self.canonical_document(),"mechanism":{"rule":rule,"order":order,"tie_break":"declared-good-order"}}
        return "sha256:"+hashlib.sha256(json.dumps(doc,sort_keys=True,separators=(",",":")).encode()).hexdigest()


@dataclass(frozen=True)
class FairAllocation:
    bundles: tuple[tuple[str,...],...]


def round_robin(instance:AdditiveInstance, order=None)->FairAllocation:
    order=order or tuple(range(len(instance.agents))); remaining=list(instance.goods); bundles=[[] for _ in instance.agents]; turn=0
    while remaining:
        a=order[turn%len(order)]; best=max(remaining,key=lambda g:(instance.values[a][instance.goods.index(g)],-instance.goods.index(g)))
        bundles[a].append(best); remaining.remove(best); turn+=1
    return FairAllocation(tuple(tuple(x) for x in bundles))


def all_allocations(instance):
    for owners in product(range(len(instance.agents)),repeat=len(instance.goods)):
        yield FairAllocation(tuple(tuple(g for g,o in zip(instance.goods,owners,strict=True) if o==a) for a in range(len(instance.agents))))


def fair_violations(instance:AdditiveInstance, allocation:FairAllocation, property_id:str):
    require_applicable(property_id,"fair_division"); rows=[]
    flat=[g for b in allocation.bundles for g in b]
    if property_id.endswith("feasibility.v1"):
        for g in instance.goods: rows.append((flat.count(g)!=1,{"good":g,"assignment_count":flat.count(g)}))
        rows.extend((g not in instance.goods,{"unknown_good":g}) for g in flat)
    elif property_id.endswith("envy_free.v1"):
        for i,j in product(range(len(instance.agents)),repeat=2):
            own,other=instance.value(i,allocation.bundles[i]),instance.value(i,allocation.bundles[j])
            rows.append((other>own,{"envying_agent":instance.agents[i],"own_bundle":allocation.bundles[i],"other_agent":instance.agents[j],"envied_bundle":allocation.bundles[j],"own_value":own,"envied_value":other,"envy_gap":other-own}))
    elif property_id.endswith("ef1.v1"):
        for i,j in product(range(len(instance.agents)),repeat=2):
            own=instance.value(i,allocation.bundles[i]); removals=[instance.value(i,tuple(g for k,g in enumerate(allocation.bundles[j]) if k!=q)) for q in range(len(allocation.bundles[j]))]
            violation=instance.value(i,allocation.bundles[j])>own and all(x>own for x in removals)
            rows.append((violation,{"envying_agent":instance.agents[i],"envied_agent":instance.agents[j],"own_bundle":allocation.bundles[i],"envied_bundle":allocation.bundles[j],"own_value":own,"values_after_each_removal":removals}))
    elif property_id.endswith("pareto_efficiency.v1"):
        base=[instance.value(i,allocation.bundles[i]) for i in range(len(instance.agents))]
        for alt in all_allocations(instance):
            vals=[instance.value(i,alt.bundles[i]) for i in range(len(instance.agents))]; violation=all(x>=y for x,y in zip(vals,base,strict=True)) and any(x>y for x,y in zip(vals,base,strict=True))
            rows.append((violation,{"original_allocation":allocation.bundles,"alternative_allocation":alt.bundles,"original_values":base,"alternative_values":vals,"strictly_improved_agents":[instance.agents[i] for i,(x,y) in enumerate(zip(vals,base,strict=True)) if x>y]}))
    return rows


def compile_fair_division(instance,allocation,property_id):
    cases=tuple(WitnessCase(Predicate(">",int(v),0),p) for v,p in fair_violations(instance,allocation,property_id))
    return WitnessProblem(property_id,property_id,cases,"finite-additive-integer")


def replay_fair_division(problem,case): return case in problem.cases and case.predicate.holds()


def canonical_instance(): return AdditiveInstance(("a0","a1"),("g0","g1","g2"),((3,2,1),(3,3,3)))
