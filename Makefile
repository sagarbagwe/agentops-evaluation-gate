.PHONY: test evaluate api

test:
	PYTHONPATH=src python -m unittest discover -s tests -v

evaluate:
	PYTHONPATH=src python -m agentops_gate.cli --dataset evals/golden.jsonl --report build/evaluation-report.json

api:
	uvicorn agentops_gate.api:app --reload