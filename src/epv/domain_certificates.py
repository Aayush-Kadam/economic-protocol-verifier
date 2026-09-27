from __future__ import annotations

import hashlib, json
from dataclasses import asdict, dataclass

from .compiler import WitnessProblem


@dataclass(frozen=True)
class DomainCounterexample:
    schema: str
    domain_family: str
    domain_semantics_version: str
    mechanism_hash: str
    property_id: str
    logical_problem_hash: str
    case_index: int
    witness: dict
    replay_status: str = "PASS"
    def canonical_bytes(self): return json.dumps(asdict(self),sort_keys=True,separators=(",",":")).encode()
    def certificate_hash(self): return "sha256:"+hashlib.sha256(self.canonical_bytes()).hexdigest()


def make_domain_counterexample(domain_family, semantics_version, mechanism_hash, problem:WitnessProblem, case_index:int):
    if not 0 <= case_index < len(problem.cases) or not problem.cases[case_index].predicate.holds(): raise ValueError("case is not a replayable violation")
    return DomainCounterexample(f"epv-{domain_family}-counterexample-v1",domain_family,semantics_version,mechanism_hash,problem.property,problem.problem_hash(),case_index,problem.cases[case_index].payload)


def validate_domain_counterexample(cert, domain_family, semantics_version, mechanism_hash, problem):
    return cert.schema==f"epv-{domain_family}-counterexample-v1" and cert.domain_family==domain_family and cert.domain_semantics_version==semantics_version and cert.mechanism_hash==mechanism_hash and cert.property_id==problem.property and cert.logical_problem_hash==problem.problem_hash() and cert.replay_status=="PASS" and 0<=cert.case_index<len(problem.cases) and problem.cases[cert.case_index].predicate.holds() and cert.witness==problem.cases[cert.case_index].payload
