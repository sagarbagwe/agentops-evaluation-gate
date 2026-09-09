from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from agentops_gate.adapters import DemoSupportAgent
from agentops_gate.engine import EvaluationEngine
from agentops_gate.io import load_jsonl, write_report


class IoTest(unittest.TestCase):
    def test_dataset_and_report_round_trip(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            dataset = root / "cases.jsonl"
            dataset.write_text(
                json.dumps(
                    {
                        "id": "login",
                        "input": "I forgot my password",
                        "expected_keywords": ["password", "secure"],
                    }
                )
                + "\n",
                encoding="utf-8",
            )
            report_path = root / "report.json"
            report = EvaluationEngine(DemoSupportAgent()).run(load_jsonl(dataset))
            write_report(report, report_path)
            stored = json.loads(report_path.read_text(encoding="utf-8"))
            self.assertEqual(stored["summary"]["total_cases"], 1)
            self.assertTrue(stored["passed"])


if __name__ == "__main__":
    unittest.main()