from __future__ import annotations

import argparse
import json
import platform
import sys
import time
from dataclasses import asdict
from pathlib import Path

from .canonical import mechanism_hash
from .compiler import compile_property
from .counterexamples import CounterexampleCertificate, make_certificate, render_trace, validate_certificate
from .epl import EPLError, load_epl
from .proofs import CHECKER_VERSION, CheckerStatus, sha256, validate_bundle
from .properties import (
    check_allocative_efficiency, check_dsic, check_ex_post_ir, check_feasibility,
    check_strong_budget_balance, check_weak_budget_balance,
)
from .solvers import SolverStatus, solve_cvc5, solve_z3
from .synthesis import AuctionTableProblem, repair_payment_table, synthesize
from .benchmarks import first_price_auction

CHECKS = {
    "dsic": check_dsic, "ex_post_ir": check_ex_post_ir,
    "weak_budget_balance": check_weak_budget_balance,
    "strong_budget_balance": check_strong_budget_balance,
    "feasibility": check_feasibility,
    "allocative_efficiency": check_allocative_efficiency,
}
ROOT = Path(__file__).resolve().parents[2]


def _emit(document: dict, as_json: bool) -> None:
    if as_json:
        print(json.dumps(document, sort_keys=True, indent=2))
        return
    order = ("mechanism", "property", "verification_domain", "assumptions", "status",
             "assurance_level", "backend", "runtime_ms", "mechanism_hash", "problem_hash",
             "certificate", "limitations")
    for key in order:
        if key in document:
            value = document[key]
            if isinstance(value, (list, tuple)): value = ", ".join(str(x) for x in value)
            print(f"{key.replace('_', ' ').title()}: {value}")


def _verify(args: argparse.Namespace) -> int:
    started = time.perf_counter()
    ast, mechanism = load_epl(args.source)
    prop = args.property or (ast.verify[0] if ast.verify else None)
    if prop not in CHECKS:
        raise ValueError("choose an auction property with --property")
    problem = compile_property(mechanism, prop)
    status = "UNKNOWN"; assurance = "V1"; backend = "exhaustive"; certificate = None
    if args.assurance == "v1":
        result = CHECKS[prop](mechanism); status = result.status.value
        if result.witness is not None: certificate = "structured witness in output"
    elif args.assurance == "v2":
        solver = solve_z3(problem) if args.backend == "z3" else solve_cvc5(problem)
        backend = solver.backend; assurance = "V2"
        status = "BOUNDED VERIFIED" if solver.status is SolverStatus.UNSAT else (
            "COUNTEREXAMPLE FOUND" if solver.status is SolverStatus.SAT else solver.status.value)
        if solver.status is SolverStatus.SAT:
            cert = make_certificate(mechanism, problem, solver)
            certificate = cert.certificate_hash()
            if args.certificate_out:
                Path(args.certificate_out).write_text(json.dumps(asdict(cert), sort_keys=True, indent=2)+"\n", encoding="utf-8")
    else:
        if not args.proof_dir: raise ValueError("V3 requires --proof-dir")
        checker = Path(args.checker or ROOT / ".tools" / "carcara-current")
        checked = validate_bundle(mechanism, prop, Path(args.proof_dir), checker)
        backend = f"cvc5 proof + {CHECKER_VERSION}"; assurance = "V3"
        status = "BOUNDED VERIFIED - V3" if checked.status is CheckerStatus.ACCEPTED else checked.status.value
        manifest = json.loads((Path(args.proof_dir)/"manifest.json").read_text(encoding="utf-8"))
        certificate = manifest.get("proof_hash")
    document = {
        "mechanism": ast.protocol, "property": prop,
        "verification_domain": f"{len(ast.agent_ids)} agents; integer values/reports in [{ast.type_min},{ast.type_max}]",
        "assumptions": list(ast.assumptions), "status": status, "assurance_level": assurance,
        "backend": backend, "runtime_ms": round((time.perf_counter()-started)*1000, 3),
        "mechanism_hash": mechanism_hash(mechanism), "problem_hash": problem.problem_hash(),
        "certificate": certificate, "limitations": ["finite declared domain only", "economic translation remains trusted"],
    }
    _emit(document, args.json)
    return 0 if status.startswith("BOUNDED VERIFIED") else 2 if "COUNTEREXAMPLE" in status else 1


def _replay(args: argparse.Namespace) -> int:
    _, mechanism = load_epl(args.source); problem = compile_property(mechanism, args.property)
    raw = json.loads(Path(args.certificate).read_text(encoding="utf-8"))
    raw["assumptions"] = tuple(raw["assumptions"])
    raw["witness"] = {key: tuple(value) if isinstance(value, list) else value
                      for key, value in raw["witness"].items()}
    cert = CounterexampleCertificate(**raw)
    valid = validate_certificate(cert, mechanism, problem)
    if args.json: print(json.dumps({"status": "PASS" if valid else "REJECTED", "certificate_hash": cert.certificate_hash()}))
    else: print(render_trace(cert) if valid else "CERTIFICATE REJECTED")
    return 0 if valid else 1


def _check_proof(args: argparse.Namespace) -> int:
    args.assurance = "v3"; args.proof_dir = args.bundle; args.certificate_out = None
    return _verify(args)


REQ = ("dsic", "ex_post_ir", "weak_budget_balance", "feasibility", "allocative_efficiency")


def _synthesize(args: argparse.Namespace) -> int:
    problem = AuctionTableProblem((0,1), tuple(args.payments), REQ)
    result = synthesize(problem, timeout_ms=args.timeout_ms)
    doc = asdict(result); doc["status"] = result.status.value; doc["search_class"] = problem.allocation_family
    print(json.dumps(doc, default=str, sort_keys=True, indent=2))
    return 0 if "FOUND" in result.status.value else 2


def _repair(args: argparse.Namespace) -> int:
    problem = AuctionTableProblem((0,1), tuple(args.payments), REQ)
    result = repair_payment_table(first_price_auction((0,1)), problem)
    if result is None: print(json.dumps({"status":"NO_REPAIR_IN_DECLARED_CLASS", "search_size":problem.search_size()})); return 2
    distance, mechanism, payments = result
    print(json.dumps({"status":"OPTIMAL_REPAIR_FOUND", "search_size":problem.search_size(),
                      "distance":{"changed_cells":distance[0],"absolute_adjustment":distance[1]},
                      "payments":payments,"mechanism_hash":mechanism_hash(mechanism),
                      "optimality":"exhaustive finite enumeration"}, default=str, indent=2))
    return 0


def _doctor(args: argparse.Namespace) -> int:
    tools = {"python": platform.python_version(), "platform": platform.platform()}
    try:
        import cvc5
        tools["cvc5"] = cvc5.__version__
    except ImportError:
        tools["cvc5"] = "missing"
    try:
        import z3
        tools["z3"] = z3.get_version_string()
    except ImportError:
        tools["z3"] = "missing"
    checker = Path(args.checker or ROOT/".tools"/"carcara-current")
    tools["carcara_expected"] = CHECKER_VERSION
    if checker.is_file():
        try:
            _, mechanism = load_epl(ROOT/"examples"/"second_price.epl")
            result = validate_bundle(mechanism, "dsic", ROOT/"proofs"/"second_price_dsic", checker)
            tools["carcara_probe"] = result.status.value
            tools["v3_ready"] = result.status is CheckerStatus.ACCEPTED
        except (EPLError, OSError, ValueError) as exc:
            tools["carcara_probe"] = f"ERROR: {exc}"
            tools["v3_ready"] = False
    else:
        tools["carcara_probe"] = "missing (V3 unavailable)"
        tools["v3_ready"] = False
    tools["v1_v2_ready"] = tools["cvc5"] != "missing" and tools["z3"] != "missing"
    print(json.dumps(tools, sort_keys=True, indent=2))
    return 0 if tools["v1_v2_ready"] else 1


def build_parser() -> argparse.ArgumentParser:
    p=argparse.ArgumentParser(prog="epv",description="Bounded verification and synthesis for selected finite economic protocols")
    sub=p.add_subparsers(dest="command",required=True)
    v=sub.add_parser("verify"); v.add_argument("source"); v.add_argument("--property"); v.add_argument("--assurance",choices=("v1","v2","v3"),default="v1"); v.add_argument("--backend",choices=("cvc5","z3"),default="cvc5"); v.add_argument("--proof-dir"); v.add_argument("--checker"); v.add_argument("--certificate-out"); v.add_argument("--json",action="store_true"); v.set_defaults(func=_verify)
    r=sub.add_parser("replay"); r.add_argument("certificate"); r.add_argument("--source",required=True); r.add_argument("--property",required=True); r.add_argument("--json",action="store_true"); r.set_defaults(func=_replay)
    c=sub.add_parser("check-proof"); c.add_argument("bundle"); c.add_argument("--source",required=True); c.add_argument("--property",required=True); c.add_argument("--checker"); c.add_argument("--backend",default="cvc5"); c.add_argument("--json",action="store_true"); c.set_defaults(func=_check_proof)
    s=sub.add_parser("synthesize"); s.add_argument("--payments",nargs="+",type=int,default=(0,1)); s.add_argument("--timeout-ms",type=int,default=10000); s.set_defaults(func=_synthesize)
    rp=sub.add_parser("repair"); rp.add_argument("--payments",nargs="+",type=int,default=(0,1)); rp.set_defaults(func=_repair)
    d=sub.add_parser("doctor"); d.add_argument("--checker"); d.set_defaults(func=_doctor)
    b=sub.add_parser("benchmark"); b.add_argument("--full",action="store_true"); b.set_defaults(func=lambda a: __import__("epv.reproduce",fromlist=["run"]).run(a.full))
    return p


def main(argv: list[str] | None=None) -> int:
    try:
        args = build_parser().parse_args(argv)
        return args.func(args)
    except (EPLError, ValueError, OSError, json.JSONDecodeError) as exc:
        print(f"EPV ERROR: {exc}", file=sys.stderr); return 1


if __name__ == "__main__": raise SystemExit(main())
