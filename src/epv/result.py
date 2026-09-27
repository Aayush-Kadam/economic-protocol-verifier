from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from types import MappingProxyType
from typing import Any, Mapping


class Status(str, Enum):
    BOUNDED_VERIFIED = "BOUNDED VERIFIED"
    FALSIFIED = "FALSIFIED / COUNTEREXAMPLE FOUND"
    UNKNOWN = "UNKNOWN"
    OUTSIDE_FRAGMENT = "OUTSIDE VERIFIED FRAGMENT"


class AssuranceLevel(str, Enum):
    V1 = "V1 exhaustive bounded verification"


@dataclass(frozen=True)
class VerificationResult:
    property: str
    status: Status
    assurance_level: AssuranceLevel
    checked_cases: int
    witness: Mapping[str, Any] | None = None
    limitations: tuple[str, ...] = ("finite declared domain only",)

    def __post_init__(self) -> None:
        if self.status is Status.FALSIFIED and self.witness is None:
            raise ValueError("falsified results require a witness")
        if self.status is Status.BOUNDED_VERIFIED and self.witness is not None:
            raise ValueError("verified result cannot carry a violation witness")
        if self.witness is not None:
            object.__setattr__(self, "witness", MappingProxyType(dict(self.witness)))

