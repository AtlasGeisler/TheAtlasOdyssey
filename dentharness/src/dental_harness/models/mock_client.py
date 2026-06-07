"""A deterministic, offline model client.

It needs no API key and no network, so the whole harness, the loop, the
hooks, and the guardrail seam, is runnable and testable end to end. It is a
real implementation of the ModelClient interface, selected by config like any
other provider.

Behavior: on its first turn it calls the first available tool once (deriving a
plausible argument from the user's message), then on the next turn it returns
a short final answer that reflects the tool result. This exercises the full
tool-use round trip without a live model.
"""

from __future__ import annotations

import json
from typing import Any

from .base import ModelClient, ModelResponse, ToolCall


class MockModelClient(ModelClient):
    name = "mock"

    def __init__(self, **_: Any) -> None:
        self._counter = 0

    def complete(
        self,
        *,
        system: str,
        messages: list[dict[str, Any]],
        tools: list[dict[str, Any]],
    ) -> ModelResponse:
        last = messages[-1] if messages else {}

        # If we just received tool results, summarize and finish.
        if last.get("role") == "tool":
            results = last.get("tool_results", [])
            summary = json.dumps(
                [r.get("content") for r in results], default=str
            )
            return ModelResponse(
                text=f"Done. Tool result: {summary}"
            )

        # First turn: if a tool exists, call it once.
        if tools:
            tool = tools[0]
            args = self._argue(tool, _user_text(messages))
            self._counter += 1
            return ModelResponse(
                text="Calling a tool to handle the request.",
                tool_calls=[
                    ToolCall(
                        id=f"mock-{self._counter}",
                        name=tool["name"],
                        arguments=args,
                    )
                ],
            )

        return ModelResponse(text="No tools are available, nothing to do.")

    @staticmethod
    def _argue(tool: dict[str, Any], user_text: str) -> dict[str, Any]:
        """Fill required string fields with the user's text as a stand-in."""
        schema = tool.get("input_schema", {})
        required = schema.get("required", [])
        props = schema.get("properties", {})
        args: dict[str, Any] = {}
        for field_name in required:
            if props.get(field_name, {}).get("type") == "string":
                args[field_name] = user_text
            else:
                args[field_name] = ""
        return args


def _user_text(messages: list[dict[str, Any]]) -> str:
    for msg in reversed(messages):
        if msg.get("role") == "user":
            return str(msg.get("content", ""))
    return ""
