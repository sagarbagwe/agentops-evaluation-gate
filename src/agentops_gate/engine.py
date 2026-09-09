from __future__ import annotations

from collections.abc import Iterable

from .adapters import AgentAdapter
from .evaluators import DEFAULT_EVALUATORS, Evaluator
from .models import CaseResult, EvaluationCase, GateReport


class EvaluationEngine:
    def __init__(
        self,
        agent: AgentAdapter,
        evaluators: tuple[Evaluator, ...] = DEFAULT_EVALUATORS,
        threshold: float = 0.85,
    ) -> None:
        if not 0.0 <= threshold <= 1.0:
            raise ValueError("threshold must be between 0 and 1")
        if not evaluators:
            raise ValueError("at least one evaluator is required")
        self.agent = agent
        self.evaluators = evaluators
        self.threshold = threshold

    def run(self, cases: Iterable[EvaluationCase]) -> GateReport:
        results: list[CaseResult] = []
        for case in cases:
            trace = self.agent.invoke(case.input)
            metrics = tuple(evaluator.evaluate(case, trace) for evaluator in self.evaluators)
            total_weight = sum(evaluator.weight for evaluator in self.evaluators)
            weighted_score = sum(
                metric.score * evaluator.weight
                for metric, evaluator in zip(metrics, self.evaluators, strict=True)
            ) / total_weight
            hard_failure = any(metric.hard_failure for metric in metrics)
            passed = weighted_score >= self.threshold and not hard_failure
            results.append(
                CaseResult(
                    case_id=case.id,
                    score=weighted_score,
                    passed=passed,
                    trace=trace,
                    metrics=metrics,
                )
            )

        if not results:
            raise ValueError("dataset contains no evaluation cases")
        aggregate = sum(result.score for result in results) / len(results)
        gate_passed = aggregate >= self.threshold and all(result.passed for result in results)
        return GateReport(
            passed=gate_passed,
            aggregate_score=aggregate,
            threshold=self.threshold,
            cases=tuple(results),
        )