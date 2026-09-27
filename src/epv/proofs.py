from __future__ import annotations

import hashlib
import json
import os
import subprocess
from dataclasses import asdict, dataclass
from enum import Enum
from fractions import Fraction
from itertools import product
from pathlib import Path
from typing import Iterable

from .canonical import mechanism_document, mechanism_hash
from .eir import DeterministicDirectMechanism

SCHEMA = "epv-proof-certificate-v1"
PROPERTY_VERSION = "finite-exact-v1"
CHECKER_VERSION = "carcara 1.1.0 [git 051d2f7]"
PRODUCER = {"name": "cvc5", "version": "1.4.1"}


class CheckerStatus(str, Enum):
    ACCEPTED = "ACCEPTED"
    REJECTED = "REJECTED"
    UNSUPPORTED = "UNSUPPORTED"
    TIMEOUT = "TIMEOUT"
    ERROR = "ERROR"


@dataclass(frozen=True)
class CheckerResult:
    status: CheckerStatus
    stdout: str
    stderr: str


def _violations(m: DeterministicDirectMechanism, prop: str) -> list[bool]:
    out: list[bool] = []
    if prop == "dsic":
        for i in range(len(m.agents)):
            others = tuple(j for j in range(len(m.agents)) if j != i)
            for theta in m.domain.type_spaces[i]:
                for vals in product(*(m.domain.report_spaces[j] for j in others)):
                    base = [Fraction(0)] * len(m.agents)
                    for j, v in zip(others, vals, strict=True): base[j] = v
                    base[i] = m.truthful_report(i, theta)
                    truthful = m.utility(i, theta, m.outcome(tuple(base)))
                    for deviation in m.domain.report_spaces[i]:
                        candidate = list(base); candidate[i] = deviation
                        out.append(m.utility(i, theta, m.outcome(tuple(candidate))) > truthful)
    elif prop == "ex_post_ir":
        for types in m.domain.type_profiles():
            outcome = m.outcome(types)
            out.extend(m.utility(i, theta, outcome) < m.outside_options[i] for i, theta in enumerate(types))
    elif prop in {"weak_budget_balance", "strong_budget_balance"}:
        for reports in m.domain.report_profiles():
            revenue = sum(m.outcome(reports).transfers, Fraction(0))
            out.append(revenue < 0 if prop == "weak_budget_balance" else revenue != 0)
    elif prop == "feasibility":
        out.extend(not m.feasible(m.outcome(r).allocation) for r in m.domain.report_profiles())
    elif prop == "allocative_efficiency":
        for types in m.domain.type_profiles():
            chosen = m.welfare(types, m.outcome(types).allocation)
            out.extend(m.welfare(types, a) > chosen for a in m.feasible_allocations)
    else:
        raise ValueError(f"unsupported property: {prop}")
    return out


def proof_problem(m: DeterministicDirectMechanism, prop: str) -> bytes:
    """Canonical finite truth-table claim: some exact witness violates the property."""
    values = _violations(m, prop)
    if not values:
        raise ValueError("property produced no witness cases")
    names = [f"violation_{i}" for i in range(len(values))]
    lines = ["(set-logic QF_UF)"]
    lines += [f"(declare-fun {name} () Bool)" for name in names]
    lines.append(f"(assert (or {' '.join(names)}))")
    lines += [f"(assert {'%s' % n if v else '(not %s)' % n})" for n, v in zip(names, values, strict=True)]
    lines.append("(check-sat)")
    return ("\n".join(lines) + "\n").encode()


def sha256(data: bytes) -> str:
    return "sha256:" + hashlib.sha256(data).hexdigest()


def generate_alethe(problem: bytes) -> bytes:
    import cvc5
    from cvc5 import Kind
    text = problem.decode()
    vals = [line.split()[1] for line in text.splitlines() if line.startswith("(declare-fun")]
    truths = [not line.startswith("(assert (not") for line in text.splitlines() if line.startswith("(assert violation_") or line.startswith("(assert (not violation_")]
    s = cvc5.Solver(); s.setLogic("QF_UF")
    for k, v in {"produce-proofs":"true", "proof-format-mode":"alethe", "simplification":"none", "dag-thresh":"0", "proof-granularity":"theory-rewrite"}.items(): s.setOption(k, v)
    terms = [s.mkConst(s.getBooleanSort(), n) for n in vals]
    s.assertFormula(s.mkTerm(Kind.OR, *terms))
    for t, value in zip(terms, truths, strict=True): s.assertFormula(t if value else s.mkTerm(Kind.NOT, t))
    result = s.checkSat()
    if not result.isUnsat(): raise ValueError(f"proof exists only for UNSAT, got {result}")
    rendered = s.proofToString(s.getProof()[0], cvc5.ProofFormat.ALETHE)
    raw = rendered if isinstance(rendered, bytes) else rendered.encode()
    lines = raw.splitlines()
    if lines and lines[0].strip() == b"(" and lines[-1].strip() == b")": raw = b"\n".join(lines[1:-1]) + b"\n"
    return raw


def check_alethe(checker: Path, proof: Path, problem: Path, timeout: float = 30) -> CheckerResult:
    if not checker.is_file():
        return CheckerResult(CheckerStatus.ERROR, "", "checker executable missing")
    def linux_path(path: Path) -> str:
        resolved = str(path.resolve()).replace("\\", "/")
        return f"/mnt/{resolved[0].lower()}{resolved[2:]}"
    command = [str(checker), "check", str(proof), str(problem)]
    version_command = [str(checker), "--version"]
    if os.name == "nt" and checker.suffix == "":
        command = ["wsl.exe", linux_path(checker), "check", linux_path(proof), linux_path(problem)]
        version_command = ["wsl.exe", linux_path(checker), "--version"]
    try:
        version = subprocess.run(version_command, capture_output=True, text=True, timeout=timeout)
        if version.returncode != 0 or version.stdout.strip() != CHECKER_VERSION:
            return CheckerResult(CheckerStatus.UNSUPPORTED, version.stdout, "unexpected checker identity/version")
        p = subprocess.run(command, capture_output=True, text=True, timeout=timeout)
    except subprocess.TimeoutExpired: return CheckerResult(CheckerStatus.TIMEOUT, "", "timeout")
    except OSError as exc: return CheckerResult(CheckerStatus.ERROR, "", str(exc))
    word = p.stdout.strip().splitlines()[-1:] or [""]
    status = CheckerStatus.ACCEPTED if p.returncode == 0 and word[0] == "valid" else (CheckerStatus.UNSUPPORTED if "holey" in p.stdout else CheckerStatus.REJECTED)
    return CheckerResult(status, p.stdout, p.stderr)


def _domain(m: DeterministicDirectMechanism) -> dict:
    return {"type_spaces": [[[x.numerator, x.denominator] for x in s] for s in m.domain.type_spaces], "report_spaces": [[[x.numerator, x.denominator] for x in s] for s in m.domain.report_spaces], "arithmetic": m.domain.arithmetic}


def write_bundle(m: DeterministicDirectMechanism, prop: str, directory: Path, checker_version: str, epv_commit: str) -> Path:
    directory.mkdir(parents=True, exist_ok=True)
    problem = proof_problem(m, prop); proof = generate_alethe(problem)
    (directory / "problem.smt2").write_bytes(problem); (directory / "proof.alethe").write_bytes(proof)
    manifest = {"schema": SCHEMA, "assurance": "V3_BOUNDED", "property": prop, "property_version": PROPERTY_VERSION,
        "mechanism_hash": mechanism_hash(m), "mechanism": mechanism_document(m), "domain": _domain(m),
        "assumptions": [asdict(a) for a in sorted(m.assumptions)], "logical_problem_hash": sha256(problem), "proof_hash": sha256(proof),
        "proof_format": "alethe", "producer": PRODUCER,
        "checker": {"name":"carcara", "version":checker_version, "required_result":"valid"}, "epv_commit": epv_commit}
    (directory / "manifest.json").write_text(json.dumps(manifest, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    return directory


def validate_bundle(m: DeterministicDirectMechanism, prop: str, directory: Path, checker: Path, timeout: float = 30) -> CheckerResult:
    try: manifest = json.loads((directory / "manifest.json").read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc: return CheckerResult(CheckerStatus.REJECTED, "", str(exc))
    problem = (directory / "problem.smt2").read_bytes(); proof = (directory / "proof.alethe").read_bytes()
    expected = proof_problem(m, prop)
    bindings = manifest.get("schema") == SCHEMA and manifest.get("assurance") == "V3_BOUNDED" and manifest.get("property") == prop and manifest.get("property_version") == PROPERTY_VERSION and manifest.get("mechanism_hash") == mechanism_hash(m) and manifest.get("mechanism") == mechanism_document(m) and manifest.get("domain") == _domain(m) and manifest.get("assumptions") == [asdict(a) for a in sorted(m.assumptions)] and manifest.get("logical_problem_hash") == sha256(problem) and manifest.get("proof_hash") == sha256(proof) and manifest.get("proof_format") == "alethe" and manifest.get("producer") == PRODUCER and manifest.get("checker") == {"name":"carcara", "version":CHECKER_VERSION, "required_result":"valid"} and isinstance(manifest.get("epv_commit"), str) and len(manifest["epv_commit"]) == 40 and problem == expected
    if not bindings: return CheckerResult(CheckerStatus.REJECTED, "", "certificate binding mismatch")
    return check_alethe(checker, directory / "proof.alethe", directory / "problem.smt2", timeout)
