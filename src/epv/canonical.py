from __future__ import annotations

import hashlib
import json
from fractions import Fraction
from typing import Any

from .eir import Allocation, DeterministicDirectMechanism, Outcome


def rational(value: Fraction) -> dict[str, int]:
    return {"numerator": value.numerator, "denominator": value.denominator}


def allocation(value: Allocation) -> list[dict[str, int]]:
    return [rational(q) for q in value.quantities]


def outcome(value: Outcome) -> dict[str, Any]:
    return {
        "allocation": allocation(value.allocation),
        "label": value.label,
        "transfers": [rational(p) for p in value.transfers],
    }


def mechanism_document(mechanism: DeterministicDirectMechanism) -> dict[str, Any]:
    # Materializing the finite rule table makes the hash semantic rather than dependent on Python code identity.
    table = []
    for reports in mechanism.domain.report_profiles():
        table.append({"reports": [rational(r) for r in reports], "outcome": outcome(mechanism.outcome(reports))})
    declared_allocations = sorted(
        mechanism.feasible_allocations,
        key=lambda item: tuple(item.quantities),
    )
    valuation_table = []
    for agent, type_space in enumerate(mechanism.domain.type_spaces):
        for theta in type_space:
            for candidate in declared_allocations:
                valuation_table.append({
                    "agent": agent,
                    "true_type": rational(theta),
                    "allocation": allocation(candidate),
                    "value": rational(mechanism.value(agent, theta, candidate)),
                })
    return {
        "schema": "epv-eir-0.1",
        "name": mechanism.name,
        "agents": [agent.id for agent in mechanism.agents],
        "type_spaces": [[[v.numerator, v.denominator] for v in s] for s in mechanism.domain.type_spaces],
        "report_spaces": [[[v.numerator, v.denominator] for v in s] for s in mechanism.domain.report_spaces],
        "arithmetic": mechanism.domain.arithmetic,
        "tie_breaking": mechanism.tie_breaking,
        "outside_options": [rational(v) for v in mechanism.outside_options],
        "assumptions": [{"name": a.name, "detail": a.detail} for a in sorted(mechanism.assumptions)],
        "declared_allocations": [
            {"allocation": allocation(a), "feasible": mechanism.feasible(a)} for a in declared_allocations
        ],
        "valuation_table": valuation_table,
        "rule_table": table,
    }


def canonical_bytes(mechanism: DeterministicDirectMechanism) -> bytes:
    return json.dumps(
        mechanism_document(mechanism), sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode("utf-8")


def mechanism_hash(mechanism: DeterministicDirectMechanism) -> str:
    return "sha256:" + hashlib.sha256(canonical_bytes(mechanism)).hexdigest()
