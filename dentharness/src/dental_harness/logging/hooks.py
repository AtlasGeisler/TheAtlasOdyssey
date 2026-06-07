"""Lifecycle hooks that log every tool call from day one (Principle 5).

The loop fires before_tool before a call and after_tool once it resolves.
Every call is written as one JSON line to logs/tool_calls.jsonl, capturing the
tool, its arguments, the outcome, the guardrail decision, and the duration.
This is the audit spine the healthcare layer builds on.

Records are JSON Lines so they are append-only and trivially inspectable. The
logs directory is gitignored and must never hold real patient data.
"""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any

from ..models.base import ToolCall


class LifecycleHooks:
    def __init__(self, log_dir: str | Path) -> None:
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.log_file = self.log_dir / "tool_calls.jsonl"
        self._starts: dict[str, float] = {}

    def before_tool(self, call: ToolCall) -> None:
        self._starts[call.id] = time.monotonic()

    def after_tool(
        self,
        call: ToolCall,
        *,
        result: dict[str, Any],
        allowed: bool,
        block_reason: str = "",
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
            "arguments": call.arguments,
            "allowed": allowed,
            "block_reason": block_reason,
            "duration_ms": duration_ms,
            "outcome": "error" if isinstance(result, dict) and "error" in result
            else "ok",
        }
        with self.log_file.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(record, default=str) + "\n")
