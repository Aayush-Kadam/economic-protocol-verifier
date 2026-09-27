from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any


@dataclass(frozen=True)
class VerificationProvenance:
    mechanism_semantic_hash: str
    epl_source_hash: str | None
    property: str
    property_version: str
    domain: dict[str, Any]
    assumptions: tuple[str, ...]
    logical_problem_hash: str
    backend: str
    backend_version: str
    options: dict[str, Any]
    solver_result: str
    runtime_ms: float
    epv_commit: str

    def document(self) -> dict[str, Any]:
        return asdict(self)

