from __future__ import annotations

import json
import time
import urllib.request
from typing import Protocol

from .models import AgentTrace


class AgentAdapter(Protocol):
    def invoke(self, request: str) -> AgentTrace:
        ...


class DemoSupportAgent:
    """Deterministic agent used to exercise the complete gate without a model."""

    def invoke(self, request: str) -> AgentTrace:
        started = time.perf_counter()
        normalized = request.lower()

        if "refund" in normalized:
            output = (
                "I can check the refund status using the order record. "
                "No refund will be issued without customer confirmation."
            )
            tools = ("search_orders",)
        elif "password" in normalized or "login" in normalized:
            output = (
                "I can help with account access. Start the secure password-reset "
                "flow; I will never request or expose the existing password."
            )
            tools = ("lookup_account", "create_reset_link")
        else:
            output = "I can help investigate the request and provide the next safe action."
            tools = ("search_knowledge_base",)

        elapsed = (time.perf_counter() - started) * 1_000
        return AgentTrace(
            output=output,
            tool_calls=tools,
            latency_ms=max(elapsed, 8.0),
            cost_usd=0.0002,
            metadata={"provider": "deterministic-demo"},
        )


class HttpAgentAdapter:
    """Adapter for a deployed agent that implements a small JSON contract."""

    def __init__(self, endpoint: str, timeout_seconds: float = 30.0) -> None:
        self.endpoint = endpoint
        self.timeout_seconds = timeout_seconds

    def invoke(self, request: str) -> AgentTrace:
        body = json.dumps({"input": request}).encode("utf-8")
        http_request = urllib.request.Request(
            self.endpoint,
            data=body,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        started = time.perf_counter()
        with urllib.request.urlopen(http_request, timeout=self.timeout_seconds) as response:
            payload = json.loads(response.read().decode("utf-8"))
        measured_latency = (time.perf_counter() - started) * 1_000
        payload.setdefault("latency_ms", measured_latency)
        return AgentTrace.from_dict(payload)