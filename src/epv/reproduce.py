from __future__ import annotations
import argparse, json, subprocess, sys, time
from pathlib import Path
from .benchmarks import first_price_auction, second_price_auction
from .compiler import compile_property
from .counterexamples import make_certificate, validate_certificate
from .proofs import CheckerStatus, validate_bundle
from .properties import check_dsic
from .solvers import solve_cvc5, solve_z3
from .synthesis import AuctionTableProblem, repair_payment_table, synthesize

ROOT=Path(__file__).resolve().parents[2]
REQ=("dsic","ex_post_ir","weak_budget_balance","feasibility","allocative_efficiency")

def run(full: bool=False) -> int:
    started=time.perf_counter(); checks={}
    good=second_price_auction(); bad=first_price_auction(); good_problem=compile_property(good,"dsic"); bad_problem=compile_property(bad,"dsic")
    checks["v1_second_price_dsic"]=check_dsic(good).status.value
    cvc5=solve_cvc5(good_problem); z3=solve_z3(good_problem)
    checks["v2_cvc5"]=cvc5.status.value; checks["v2_z3"]=z3.status.value
    bad_result=solve_cvc5(bad_problem); cert=make_certificate(bad,bad_problem,bad_result)
    checks["counterexample_replay"]="PASS" if validate_certificate(cert,bad,bad_problem) else "FAIL"
    checker=ROOT/".tools"/"carcara-current"
    proof=validate_bundle(good,"dsic",ROOT/"proofs"/"second_price_dsic",checker)
    checks["v3_second_price_dsic"]=proof.status.value
    p=AuctionTableProblem((0,1),(0,1),REQ); checks["synthesis"]=synthesize(p).status.value
    checks["repair"]="OPTIMAL_REPAIR_FOUND" if repair_payment_table(first_price_auction((0,1)),p) else "NO_REPAIR"
    tests=None
    if full:
        proc=subprocess.run([sys.executable,"-m","unittest","discover","-s","tests","-v"],cwd=ROOT,text=True,capture_output=True)
        tests={"returncode":proc.returncode,"summary":next((x for x in reversed(proc.stderr.splitlines()) if x.startswith("Ran ")),"unknown")}
    ok=(checks["v1_second_price_dsic"]=="BOUNDED VERIFIED" and checks["v2_cvc5"]=="UNSAT" and checks["v2_z3"]=="UNSAT" and checks["counterexample_replay"]=="PASS" and checks["v3_second_price_dsic"]==CheckerStatus.ACCEPTED.value and "FOUND" in checks["synthesis"] and checks["repair"]=="OPTIMAL_REPAIR_FOUND" and (not full or tests["returncode"]==0))
    print(json.dumps({"schema":"epv-reproduction-v1","mode":"full" if full else "representative","checks":checks,"tests":tests,"runtime_seconds":round(time.perf_counter()-started,3),"status":"PASS" if ok else "FAIL"},sort_keys=True,indent=2))
    return 0 if ok else 1

def main(argv=None):
    p=argparse.ArgumentParser(); p.add_argument("--full",action="store_true"); return run(p.parse_args(argv).full)
if __name__=="__main__": raise SystemExit(main())
