"""Lifecycle hooks that log every tool call from day one (Principle 5).

The loop fires before_tool before a call and after_tool once it resolves.
Every call is written as one JSON line to logs/tool_calls.jsonl, capturing the
tool, its (PHI-redacted) arguments, the guardrail decision, the outcome, and
the duration. This is the audit spine the healthcare layer builds on.

PHI is redacted before anything is written, through the same policy the
guardrail engine uses (Rule 1: redact PHI from all logs). Records are JSON
Lines so they are append-only and trivially inspectable. The logs directory is
gitignored and must never hold real patient data.
"""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any, Callable

from ..guardrails.barriers import Decision
from ..models.base import ToolCall

Redactor = Callable[[Any], Any]


class LifecycleHooks:
    def __init__(
        self, log_dir: str | Path, redactor: Redactor | None = None
    ) -> None:
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.log_file = self.log_dir / "tool_calls.jsonl"
        # Identity redactor if none supplied, so logging never silently leaks
        # by simply forgetting to pass one. Bootstrap always supplies the real
        # PHI redactor.
        self._redact: Redactor = redactor or (lambda value: value)
        self._starts: dict[str, float] = {}

    def before_tool(self, call: ToolCall) -> None:
        self._starts[call.id] = time.monotonic()

    def after_tool(
        self,
        call: ToolCall,
        *,
        result: dict[str, Any],
        decision: Decision,
    ) -> None:
        started = self._starts.pop(call.id, None)
        duration_ms = (
            round((time.monotonic() - started) * 1000, 2)
            if started is not None
            else None
        )
        record = {
            "ts": time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime()),
            "tool_call_id": call.id,
            "tool": call.name,
            "arguments": self._redact(call.arguments),
            "outcome": decision.outcome,
            "allowed": decision.allowed,
            "guardrail_code": decision.code,
            "reason": decision.reason,
            "result_status": "error"
            if isinstance(result, dict) and "error" in result
            else "ok",
            "duration_ms": duration_ms,
        }
        with self.log_file.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(record, default=str) + "\n")
