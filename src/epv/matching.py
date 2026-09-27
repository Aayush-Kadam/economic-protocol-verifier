from __future__ import annotations

import hashlib, json
from dataclasses import dataclass
from itertools import permutations, product

from .compiler import Predicate, WitnessCase, WitnessProblem
from .property_registry import require_applicable

UNMATCHED = "unmatched"


@dataclass(frozen=True)
class StrictPreference:
    order: tuple[str, ...]
    def __post_init__(self):
        if len(set(self.order)) != len(self.order) or UNMATCHED not in self.order: raise ValueError("preference must be strict and include unmatched exactly once")
    def prefers(self, a: str, b: str) -> bool: return self.order.index(a) < self.order.index(b)
    def acceptable(self, partner: str) -> bool: return self.prefers(partner, UNMATCHED)


@dataclass(frozen=True)
class MatchingOutcome:
    proposer_partners: tuple[str, ...]


@dataclass(frozen=True)
class MatchingMarket:
    proposers: tuple[str, ...]
    receivers: tuple[str, ...]
    proposer_preferences: tuple[StrictPreference, ...]
    receiver_preferences: tuple[StrictPreference, ...]
    semantics_version: str = "epv.matching.one_to_one_strict.v1"
    def __post_init__(self):
        if len(set(self.proposers)) != len(self.proposers) or len(set(self.receivers)) != len(self.receivers): raise ValueError("agent IDs must be unique")
        if len(self.proposer_preferences) != len(self.proposers) or len(self.receiver_preferences) != len(self.receivers): raise ValueError("one preference per agent")
        expected_r, expected_p = set(self.receivers) | {UNMATCHED}, set(self.proposers) | {UNMATCHED}
        if any(set(p.order) != expected_r for p in self.proposer_preferences) or any(set(p.order) != expected_p for p in self.receiver_preferences): raise ValueError("preferences must rank every counterpart and unmatched")

    def canonical_document(self):
        return {"domain_family":"matching", "semantics_version":self.semantics_version, "proposers":self.proposers, "receivers":self.receivers,
                "proposer_preferences":[p.order for p in self.proposer_preferences], "receiver_preferences":[p.order for p in self.receiver_preferences]}
    def semantic_hash(self): return "sha256:" + hashlib.sha256(json.dumps(self.canonical_document(),sort_keys=True,separators=(",",":")).encode()).hexdigest()
    def mechanism_hash(self, rule: str, proposing_side: str = "proposers"):
        if proposing_side not in {"proposers", "receivers"}: raise ValueError("invalid proposing side")
        doc={"market":self.canonical_document(),"mechanism":{"rule":rule,"proposing_side":proposing_side,"iteration":"lowest-index-free-first"}}
        return "sha256:"+hashlib.sha256(json.dumps(doc,sort_keys=True,separators=(",",":")).encode()).hexdigest()


def deferred_acceptance(market: MatchingMarket, proposer_reports=None, receiver_reports=None) -> MatchingOutcome:
    pp = proposer_reports or market.proposer_preferences; rp = receiver_reports or market.receiver_preferences
    free = list(range(len(market.proposers))); next_choice = [0]*len(free); held: dict[int,int] = {}
    while free:
        p = free.pop(0)
        while next_choice[p] < len(pp[p].order):
            target = pp[p].order[next_choice[p]]; next_choice[p] += 1
            if target == UNMATCHED: break
            r = market.receivers.index(target)
            if not rp[r].acceptable(market.proposers[p]): continue
            old = held.get(r)
            if old is None: held[r] = p
            elif rp[r].prefers(market.proposers[p], market.proposers[old]): held[r] = p; free.append(old)
            else: continue
            break
    partners = [UNMATCHED]*len(market.proposers)
    for r,p in held.items(): partners[p] = market.receivers[r]
    return MatchingOutcome(tuple(partners))


def fixed_matching(market: MatchingMarket) -> MatchingOutcome:
    return MatchingOutcome(tuple(market.receivers[i] if i < len(market.receivers) else UNMATCHED for i in range(len(market.proposers))))


def receiver_partner(market, outcome, receiver):
    rid = market.receivers.index(receiver)
    matches = [market.proposers[i] for i,x in enumerate(outcome.proposer_partners) if x == receiver]
    return matches[0] if len(matches) == 1 else UNMATCHED


def matching_violations(market: MatchingMarket, outcome: MatchingOutcome, property_id: str):
    require_applicable(property_id, "matching"); rows=[]
    if property_id.endswith("feasibility.v1"):
        for r in market.receivers:
            count=outcome.proposer_partners.count(r); rows.append((count > 1,{"receiver":r,"assignment_count":count}))
        rows.extend((x not in set(market.receivers)|{UNMATCHED},{"proposer":market.proposers[i],"partner":x}) for i,x in enumerate(outcome.proposer_partners))
    elif property_id.endswith("individual_rationality.v1"):
        for i,r in enumerate(outcome.proposer_partners):
            if r != UNMATCHED:
                j=market.receivers.index(r); rows.append((not market.proposer_preferences[i].acceptable(r) or not market.receiver_preferences[j].acceptable(market.proposers[i]),{"proposer":market.proposers[i],"receiver":r}))
    elif property_id.endswith("stability.v1"):
        for i,p in enumerate(market.proposers):
            for j,r in enumerate(market.receivers):
                current_r=outcome.proposer_partners[i]; current_p=receiver_partner(market,outcome,r)
                blocks=market.proposer_preferences[i].acceptable(r) and market.receiver_preferences[j].acceptable(p) and market.proposer_preferences[i].prefers(r,current_r) and market.receiver_preferences[j].prefers(p,current_p)
                rows.append((blocks,{"agent_a":p,"agent_b":r,"a_current_partner":current_r,"b_current_partner":current_p,"a_comparison":f"{r} preferred to {current_r}","b_comparison":f"{p} preferred to {current_p}"}))
    else: raise ValueError("strategy-proofness requires profile compiler")
    return rows


def ranking_universe(items): return tuple(StrictPreference(x) for x in permutations(tuple(items)+(UNMATCHED,)))


def compile_matching(market: MatchingMarket, mechanism, property_id: str, report_domain=None) -> WitnessProblem:
    require_applicable(property_id,"matching"); cases=[]
    if property_id.endswith("strategyproof_proposer.v1"):
        domain=report_domain or tuple(ranking_universe(market.receivers))
        for i in range(len(market.proposers)):
            truthful=market.proposer_preferences; base=mechanism(market, truthful, market.receiver_preferences)
            for deviation in domain:
                reports=list(truthful); reports[i]=deviation
                altered=mechanism(market,tuple(reports),market.receiver_preferences)
                violation=market.proposer_preferences[i].prefers(altered.proposer_partners[i],base.proposer_partners[i])
                payload={"manipulating_agent":market.proposers[i],"true_ranking":market.proposer_preferences[i].order,"truthful_report":truthful[i].order,"deviation_report":deviation.order,"truthful_assignment":base.proposer_partners[i],"deviation_assignment":altered.proposer_partners[i],"ordinal_comparison":f"{altered.proposer_partners[i]} preferred to {base.proposer_partners[i]}"}
                cases.append(WitnessCase(Predicate(">",int(violation),0),payload))
    else:
        for violation,payload in matching_violations(market, mechanism(market), property_id): cases.append(WitnessCase(Predicate(">",int(violation),0),payload))
    return WitnessProblem(property_id,property_id,tuple(cases),"finite-strict-ordinal")


def replay_matching(problem, case): return case in problem.cases and case.predicate.holds()


def canonical_market() -> MatchingMarket:
    return MatchingMarket(("p0","p1"),("r0","r1"),(StrictPreference(("r0","r1",UNMATCHED)),StrictPreference(("r0","r1",UNMATCHED))),
                          (StrictPreference(("p1","p0",UNMATCHED)),StrictPreference(("p0","p1",UNMATCHED))))
