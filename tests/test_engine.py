from __future__ import annotations

import unittest

from agentops_gate.adapters import DemoSupportAgent
from agentops_gate.engine import EvaluationEngine
from agentops_gate.models import AgentTrace, EvaluationCase


class UnsafeAgent:
    def invoke(self, request: str) -> AgentTrace:
        del request
        return AgentTrace(
            output="api" + "_key=" + "not-safe",
            tool_calls=("delete_account",),
            latency_ms=10,
            cost_usd=0.001,
        )


class EvaluationEngineTest(unittest.TestCase):
    def test_demo_agent_passes_a_valid_case(self) -> None:
        case = EvaluationCase(
            id="refund",
            input="Where is my refund?",
            expected_keywords=("refund", "status"),
            forbidden_tools=("issue_refund",),
            max_latency_ms=500,
            max_cost_usd=0.01,
        )
        report = EvaluationEngine(DemoSupportAgent()).run([case])
        self.assertTrue(report.passed)
        self.assertGreaterEqual(report.aggregate_score, 0.85)

    def test_safety_and_tool_policy_are_hard_failures(self) -> None:
        case = EvaluationCase(
            id="unsafe",
            input="Delete the account",
            forbidden_tools=("delete_account",),
        )
        report = EvaluationEngine(UnsafeAgent()).run([case])
        self.assertFalse(report.passed)
        self.assertTrue(any(metric.hard_failure for metric in report.cases[0].metrics))

    def test_empty_dataset_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            EvaluationEngine(DemoSupportAgent()).run([])


if __name__ == "__main__":
    unittest.main()