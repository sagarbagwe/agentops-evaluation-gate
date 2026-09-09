from __future__ import annotations

from fastapi import FastAPI
from pydantic import BaseModel, Field

from .adapters import DemoSupportAgent
from .engine import EvaluationEngine
from .models import EvaluationCase

app = FastAPI(title="AgentOps Evaluation Gate", version="0.1.0")


class CasePayload(BaseModel):
    id: str
    input: str
    expected_keywords: list[str] = Field(default_factory=list)
    forbidden_tools: list[str] = Field(default_factory=list)
    max_latency_ms: float = 1_000.0
    max_cost_usd: float = 0.02


class EvaluationPayload(BaseModel):
    cases: list[CasePayload]
    threshold: float = Field(default=0.85, ge=0.0, le=1.0)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/evaluate")
def evaluate(payload: EvaluationPayload) -> dict:
    cases = [
        EvaluationCase.from_dict(case.model_dump())
        for case in payload.cases
    ]
    report = EvaluationEngine(DemoSupportAgent(), threshold=payload.threshold).run(cases)
    return report.to_dict()