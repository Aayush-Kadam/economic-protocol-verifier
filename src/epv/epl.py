from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from fractions import Fraction
from pathlib import Path
from typing import Any

from .benchmarks import _single_item_base, double_allocation_mechanism
from .eir import Allocation, DeterministicDirectMechanism, Outcome


SUPPORTED_PROPERTIES = {
    "dsic", "ex_post_ir", "weak_budget_balance", "strong_budget_balance",
    "feasibility", "allocative_efficiency",
}


@dataclass(frozen=True)
class SourceLocation:
    file: str
    line: int
    column: int


class EPLError(ValueError):
    def __init__(self, category: str, message: str, location: SourceLocation):
        self.category = category
        self.location = location
        super().__init__(f"{category}: {message}\nat {location.file}:{location.line}:{location.column}")


@dataclass(frozen=True)
class ProtocolAST:
    protocol: str
    agent_ids: tuple[str, ...]
    type_min: int
    type_max: int
    report_min: int
    report_max: int
    allocation_rule: str
    payment_rule: str
    tie_break: str
    transfer_sign: str
    utility_rule: str
    feasibility_rule: str
    capacity: int
    outside_option: int
    assumptions: tuple[str, ...]
    verify: tuple[str, ...]
    source_hash: str


def _loc(text: str, filename: str, token: str) -> SourceLocation:
    index = text.find(f'"{token}"')
    if index < 0:
        return SourceLocation(filename, 1, 1)
    line = text.count("\n", 0, index) + 1
    previous = text.rfind("\n", 0, index)
    return SourceLocation(filename, line, index - previous)


def _error(text: str, filename: str, token: str, category: str, message: str) -> None:
    raise EPLError(category, message, _loc(text, filename, token))


def _pairs_no_duplicates(text: str, filename: str):
    def hook(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                _error(text, filename, key, "DuplicateDefinition", f"duplicate key '{key}'")
            result[key] = value
        return result
    return hook


def parse_epl(text: str, filename: str = "<memory>") -> ProtocolAST:
    if not isinstance(text, str):
        raise EPLError("TypeError", "EPL source must be text", SourceLocation(filename, 1, 1))
    if len(text.encode("utf-8")) > 1_000_000:
        raise EPLError("ResourceLimit", "EPL source exceeds 1,000,000 bytes", SourceLocation(filename, 1, 1))
    try:
        raw = json.loads(text, object_pairs_hook=_pairs_no_duplicates(text, filename), parse_float=lambda value: (_error(
            text, filename, value, "UnsupportedNumericType", "floating-point literals are forbidden"
        )))
    except EPLError:
        raise
    except (json.JSONDecodeError, RecursionError) as exc:
        if isinstance(exc, RecursionError):
            raise EPLError("ResourceLimit", "JSON nesting is too deep", SourceLocation(filename, 1, 1)) from None
        raise EPLError("SyntaxError", exc.msg, SourceLocation(filename, exc.lineno, exc.colno)) from None
    if not isinstance(raw, dict):
        _error(text, filename, "protocol", "TypeError", "top-level EPL value must be an object")
    allowed = {"schema", "protocol", "agents", "types", "reports", "resource", "allocation", "payments",
               "utility", "feasibility", "outside_option", "assumptions", "verify"}
    unknown = set(raw) - allowed
    if unknown:
        key = sorted(unknown)[0]
        _error(text, filename, key, "UnsupportedConstruct", f"unknown top-level field '{key}'")
    required = allowed - {"verify"}
    missing = required - set(raw)
    if missing:
        key = sorted(missing)[0]
        _error(text, filename, "protocol", "MissingField", f"required field '{key}' is missing")
    if raw["schema"] != "epv-epl-0.1":
        _error(text, filename, "schema", "UnsupportedSchema", "expected 'epv-epl-0.1'")

    if not isinstance(raw["protocol"], str) or not raw["protocol"] or len(raw["protocol"]) > 256:
        _error(text, filename, "protocol", "InvalidProtocol", "protocol must be a nonempty string of at most 256 characters")
    agents = raw["agents"]
    if not isinstance(agents, dict):
        _error(text, filename, "agents", "InvalidAgents", "agents must be an object")
    if set(agents) == {"ids"}:
        ids = agents["ids"]
        if not isinstance(ids, list) or not ids or any(not isinstance(v, str) or not v for v in ids):
            _error(text, filename, "agents", "InvalidAgents", "ids must be a nonempty string list")
        if len(ids) != len(set(ids)):
            _error(text, filename, "agents", "DuplicateAgent", "agent ids must be unique")
        agent_ids = tuple(ids)
    elif set(agents) == {"count", "prefix"}:
        count = agents["count"]
        if isinstance(count, bool) or not isinstance(count, int) or count <= 0:
            _error(text, filename, "count", "InvalidAgents", "agent count must be a positive integer")
        if not isinstance(agents["prefix"], str) or not agents["prefix"]:
            _error(text, filename, "prefix", "InvalidAgents", "agent prefix must be nonempty")
        agent_ids = tuple(f"{agents['prefix']}-{i}" for i in range(count))
    else:
        _error(text, filename, "agents", "InvalidAgents", "use exactly ids, or count plus prefix")

    def domain(section: str) -> tuple[int, int]:
        value = raw[section]
        if not isinstance(value, dict) or set(value) != {"integer"} or set(value["integer"]) != {"min", "max"}:
            _error(text, filename, section, "InvalidDomain", "expected integer min/max domain")
        lo, hi = value["integer"]["min"], value["integer"]["max"]
        if any(isinstance(v, bool) or not isinstance(v, int) for v in (lo, hi)):
            _error(text, filename, section, "UnsupportedNumericType", "domain bounds must be integers")
        if lo > hi:
            _error(text, filename, section, "InvalidDomain", "domain minimum exceeds maximum")
        if hi - lo + 1 > 1000:
            _error(text, filename, section, "ResourceLimit", "integer domain may contain at most 1000 values")
        return lo, hi

    type_min, type_max = domain("types")
    report_min, report_max = domain("reports")
    resource = raw["resource"]
    if resource != {"kind": "single_indivisible", "capacity": 1}:
        _error(text, filename, "resource", "UnsupportedConstruct", "M2 supports one indivisible item of capacity 1")
    allocation = raw["allocation"]
    if not isinstance(allocation, dict):
        _error(text, filename, "allocation", "InvalidAllocation", "allocation must be an object")
    if set(allocation) != {"rule", "tie_break"}:
        _error(text, filename, "allocation", "InvalidAllocation", "allocation requires rule and tie_break")
    if allocation["rule"] not in {"highest_report", "all_agents", "agent_zero"}:
        _error(text, filename, "rule", "UnsupportedConstruct", "unsupported allocation rule")
    if not allocation["tie_break"]:
        _error(text, filename, "tie_break", "MissingTieBreak", "tie-breaking must be explicit")
    if allocation["tie_break"] not in {"lowest_id", "not_applicable"}:
        _error(text, filename, "tie_break", "UnsupportedConstruct", "unsupported tie-breaking rule")
    if allocation["rule"] == "highest_report" and allocation["tie_break"] != "lowest_id":
        _error(text, filename, "tie_break", "MissingTieBreak", "highest_report requires lowest_id")
    payments = raw["payments"]
    if not isinstance(payments, dict):
        _error(text, filename, "payments", "InvalidPayments", "payments must be an object")
    if set(payments) != {"rule", "sign"} or payments["sign"] != "agent_pays_mechanism":
        _error(text, filename, "payments", "TransferSignError", "sign must be agent_pays_mechanism")
    if payments["rule"] not in {"second_highest", "own_report", "winner_subsidy_one", "zero"}:
        _error(text, filename, "payments", "UnsupportedConstruct", "unsupported payment rule")
    if raw["utility"] != {"rule": "quasi_linear_private_value"}:
        _error(text, filename, "utility", "UtilityTypeError", "unsupported or ill-typed utility")
    if raw["feasibility"] != {"rule": "single_item_capacity"}:
        _error(text, filename, "feasibility", "InvalidFeasibility", "unsupported feasibility rule")
    outside = raw["outside_option"]
    if isinstance(outside, bool) or not isinstance(outside, int):
        _error(text, filename, "outside_option", "UnsupportedNumericType", "outside option must be an integer")
    assumptions = raw["assumptions"]
    if not isinstance(assumptions, list) or any(not isinstance(v, str) for v in assumptions):
        _error(text, filename, "assumptions", "TypeError", "assumptions must be strings")
    if set(assumptions) != {"private_values", "quasi_linear"} or len(assumptions) != 2:
        _error(text, filename, "assumptions", "UnsupportedAssumption",
               "M2 requires exactly private_values and quasi_linear")
    verify = raw.get("verify", [])
    if not isinstance(verify, list) or any(v not in SUPPORTED_PROPERTIES for v in verify):
        _error(text, filename, "verify", "UnknownProperty", "verify contains an unsupported property")
    return ProtocolAST(
        str(raw["protocol"]), agent_ids, type_min, type_max, report_min, report_max,
        allocation["rule"], payments["rule"], allocation["tie_break"], payments["sign"],
        raw["utility"]["rule"], raw["feasibility"]["rule"], 1, outside,
        tuple(assumptions), tuple(verify), "sha256:" + hashlib.sha256(text.encode()).hexdigest(),
    )


def elaborate(ast: ProtocolAST) -> DeterministicDirectMechanism:
    if ast.type_min != ast.report_min or ast.type_max != ast.report_max:
        raise EPLError("DomainMismatch", "direct truth reports require identical type/report domains in M2",
                       SourceLocation("<ast>", 1, 1))
    values = tuple(range(ast.type_min, ast.type_max + 1))
    if len(ast.agent_ids) != 2:
        raise EPLError("UnsupportedConstruct", "M2 single-item templates currently require exactly two agents",
                       SourceLocation("<ast>", 1, 1))
    if ast.allocation_rule == "highest_report":
        payment = {"second_highest": "second-price", "own_report": "first-price",
                   "winner_subsidy_one": "subsidy", "zero": "zero"}[ast.payment_rule]
        mechanism = _single_item_base(ast.protocol, values, payment)
    else:
        base = _single_item_base(ast.protocol, values, "second-price")
        def rule(reports):
            quantities = (Fraction(1), Fraction(1)) if ast.allocation_rule == "all_agents" else (Fraction(1), Fraction(0))
            return Outcome("both-win" if ast.allocation_rule == "all_agents" else "always-0", Allocation(quantities), (0, 0))
        mechanism = DeterministicDirectMechanism(
            ast.protocol, base.agents, base.domain, rule, base.value, base.feasible, base.feasible_allocations,
            base.assumptions,
            "not applicable; both agents are allocated" if ast.allocation_rule == "all_agents"
            else "not applicable; fixed allocation",
            tuple(Fraction(ast.outside_option) for _ in base.agents),
        )
    # Preserve exact agent identity and outside options while reusing audited rule construction.
    return DeterministicDirectMechanism(
        mechanism.name, tuple(type(mechanism.agents[0])(v) for v in ast.agent_ids), mechanism.domain,
        mechanism.rule, mechanism.value, mechanism.feasible, mechanism.feasible_allocations,
        mechanism.assumptions, mechanism.tie_breaking,
        tuple(Fraction(ast.outside_option) for _ in mechanism.agents),
    )


def load_epl(path: str | Path) -> tuple[ProtocolAST, DeterministicDirectMechanism]:
    target = Path(path)
    text = target.read_text(encoding="utf-8")
    ast = parse_epl(text, str(target))
    return ast, elaborate(ast)
