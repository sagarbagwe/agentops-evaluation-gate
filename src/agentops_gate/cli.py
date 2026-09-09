from __future__ import annotations

import argparse
import os

from .adapters import DemoSupportAgent, HttpAgentAdapter
from .engine import EvaluationEngine
from .io import load_jsonl, write_report


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Evaluate an AI agent and enforce a release gate.")
    parser.add_argument("--dataset", required=True, help="Path to a JSONL evaluation dataset.")
    parser.add_argument("--report", default="build/evaluation-report.json")
    parser.add_argument("--endpoint", help="Optional deployed-agent HTTP endpoint.")
    parser.add_argument(
        "--threshold",
        type=float,
        default=float(os.getenv("AGENTOPS_GATE_THRESHOLD", "0.85")),
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    agent = HttpAgentAdapter(args.endpoint) if args.endpoint else DemoSupportAgent()
    report = EvaluationEngine(agent=agent, threshold=args.threshold).run(load_jsonl(args.dataset))
    write_report(report, args.report)
    decision = "PASS" if report.passed else "FAIL"
    print(f"{decision}: score={report.aggregate_score:.3f} threshold={report.threshold:.3f}")
    print(f"Report: {args.report}")
    return 0 if report.passed else 1


if __name__ == "__main__":
    raise SystemExit(main())