from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass(frozen=True)
class EvaluationCase:
    id: str
    input: str
    expected_keywords: tuple[str, ...] = ()
    forbidden_tools: tuple[str, ...] = ()
    max_latency_ms: float = 1_000.0
    max_cost_usd: float = 0.02
    metadata: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, value: dict[str, Any]) -> "EvaluationCase":
        return cls(
            id=str(value["id"]),
            input=str(value["input"]),
            expected_keywords=tuple(value.get("expected_keywords", [])),
            forbidden_tools=tuple(value.get("forbidden_tools", [])),
            max_latency_ms=float(value.get("max_latency_ms", 1_000.0)),
            max_cost_usd=float(value.get("max_cost_usd", 0.02)),
            metadata=dict(value.get("metadata", {})),
        )


@dataclass(frozen=True)
class AgentTrace:
    output: str
    tool_calls: tuple[str, ...] = ()
    latency_ms: float = 0.0
    cost_usd: float = 0.0
    metadata: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, value: dict[str, Any]) -> "AgentTrace":
        return cls(
            output=str(value.get("output", "")),
            tool_calls=tuple(value.get("tool_calls", [])),
            latency_ms=float(value.get("latency_ms", 0.0)),
            cost_usd=float(value.get("cost_usd", 0.0)),
            metadata=dict(value.get("metadata", {})),
        )


@dataclass(frozen=True)
class MetricResult:
    name: str
    score: float
    passed: bool
    details: str
    hard_failure: bool = False


@dataclass(frozen=True)
class CaseResult:
    case_id: str
    score: float
    passed: bool
    trace: AgentTrace
    metrics: tuple[MetricResult, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "case_id": self.case_id,
            "score": round(self.score, 4),
            "passed": self.passed,
            "trace": asdict(self.trace),
            "metrics": [asdict(metric) for metric in self.metrics],
        }


@dataclass(frozen=True)
class GateReport:
    passed: bool
    aggregate_score: float
    threshold: float
    cases: tuple[CaseResult, ...]

    def to_dict(self) -> dict[str, Any]:
        passed_cases = sum(1 for case in self.cases if case.passed)
        return {
            "passed": self.passed,
            "aggregate_score": round(self.aggregate_score, 4),
            "threshold": self.threshold,
            "summary": {
                "total_cases": len(self.cases),
                "passed_cases": passed_cases,
                "failed_cases": len(self.cases) - passed_cases,
            },
            "cases": [case.to_dict() for case in self.cases],
        }