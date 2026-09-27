from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from itertools import product
from types import MappingProxyType
from typing import Callable, Iterable, Mapping, TypeAlias


Exact: TypeAlias = int | Fraction
TypeValue: TypeAlias = Fraction
ReportValue: TypeAlias = Fraction
Profile: TypeAlias = tuple[Fraction, ...]


def exact(value: Exact) -> Fraction:
    if isinstance(value, bool) or isinstance(value, float):
        raise TypeError("trusted arithmetic accepts only int or Fraction")
    if not isinstance(value, (int, Fraction)):
        raise TypeError(f"unsupported numeric type: {type(value).__name__}")
    return Fraction(value)


@dataclass(frozen=True, order=True)
class Agent:
    id: str

    def __post_init__(self) -> None:
        if not self.id:
            raise ValueError("agent id must be nonempty")


@dataclass(frozen=True)
class Allocation:
    quantities: tuple[Fraction, ...]

    def __post_init__(self) -> None:
        normalized = tuple(exact(q) for q in self.quantities)
        if any(q < 0 for q in normalized):
            raise ValueError("allocation quantities must be nonnegative")
        object.__setattr__(self, "quantities", normalized)


@dataclass(frozen=True)
class Outcome:
    label: str
    allocation: Allocation
    transfers: tuple[Fraction, ...]

    def __post_init__(self) -> None:
        object.__setattr__(self, "transfers", tuple(exact(p) for p in self.transfers))


@dataclass(frozen=True, order=True)
class Assumption:
    name: str
    detail: str


@dataclass(frozen=True)
class VerificationDomain:
    type_spaces: tuple[tuple[Fraction, ...], ...]
    report_spaces: tuple[tuple[Fraction, ...], ...]
    arithmetic: str = "exact-rational"

    def __post_init__(self) -> None:
        types = tuple(tuple(exact(v) for v in space) for space in self.type_spaces)
        reports = tuple(tuple(exact(v) for v in space) for space in self.report_spaces)
        if not types or any(not space for space in types + reports):
            raise ValueError("all finite spaces must be nonempty")
        if len(types) != len(reports):
            raise ValueError("each agent needs a type and report space")
        if self.arithmetic != "exact-rational":
            raise ValueError("M1 supports exact-rational arithmetic only")
        object.__setattr__(self, "type_spaces", types)
        object.__setattr__(self, "report_spaces", reports)

    def type_profiles(self) -> Iterable[Profile]:
        return product(*self.type_spaces)

    def report_profiles(self) -> Iterable[Profile]:
        return product(*self.report_spaces)


Rule = Callable[[Profile], Outcome]
ValueFunction = Callable[[int, Fraction, Allocation], Fraction]
FeasibilityPredicate = Callable[[Allocation], bool]


@dataclass(frozen=True)
class DeterministicDirectMechanism:
    name: str
    agents: tuple[Agent, ...]
    domain: VerificationDomain
    rule: Rule
    value: ValueFunction
    feasible: FeasibilityPredicate
    feasible_allocations: tuple[Allocation, ...]
    assumptions: tuple[Assumption, ...]
    tie_breaking: str
    outside_options: tuple[Fraction, ...]

    def __post_init__(self) -> None:
        n = len(self.agents)
        if n == 0 or n != len(self.domain.type_spaces):
            raise ValueError("agent count must match the domain")
        if not self.tie_breaking.strip():
            raise ValueError("tie-breaking must be explicit")
        if len(self.outside_options) != n:
            raise ValueError("one outside option is required per agent")
        object.__setattr__(self, "outside_options", tuple(exact(v) for v in self.outside_options))
        if not self.feasible_allocations:
            raise ValueError("efficiency checking requires declared feasible allocations")
        for reports in self.domain.report_profiles():
            self._validate_outcome(self.rule(reports))

    def _validate_outcome(self, outcome: Outcome) -> None:
        if len(outcome.allocation.quantities) != len(self.agents):
            raise ValueError("allocation arity must match agents")
        if len(outcome.transfers) != len(self.agents):
            raise ValueError("transfer arity must match agents")

    def outcome(self, reports: Profile) -> Outcome:
        if len(reports) != len(self.agents):
            raise ValueError("report profile arity mismatch")
        normalized = tuple(exact(v) for v in reports)
        for report, space in zip(normalized, self.domain.report_spaces, strict=True):
            if report not in space:
                raise ValueError("report outside declared space")
        result = self.rule(normalized)
        self._validate_outcome(result)
        return result

    def truthful_report(self, agent: int, true_type: Fraction) -> Fraction:
        if true_type not in self.domain.report_spaces[agent]:
            raise ValueError("M1 direct mechanisms require truth to be a valid report")
        return true_type

    def utility(self, agent: int, true_type: Fraction, outcome: Outcome) -> Fraction:
        # Deliberately receives true_type; no report is available to confuse with it.
        return exact(self.value(agent, exact(true_type), outcome.allocation)) - outcome.transfers[agent]

    def welfare(self, true_types: Profile, allocation: Allocation) -> Fraction:
        return sum((exact(self.value(i, theta, allocation)) for i, theta in enumerate(true_types)), Fraction(0))

