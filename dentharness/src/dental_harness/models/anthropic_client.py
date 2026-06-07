"""The Anthropic-backed model client.

This is the production brain. It translates the provider-neutral message list
into Anthropic tool-use blocks and back. The SDK is imported lazily so the
harness still runs offline with the mock provider when anthropic is not
installed. Default to a current Claude model via config (for example
claude-opus-4-8 or claude-sonnet-4-6).
"""

from __future__ import annotations

import os
from typing import Any

from .base import ModelClient, ModelResponse, ToolCall


class AnthropicModelClient(ModelClient):
    def __init__(
        self,
        *,
        name: str = "claude-opus-4-8",
        max_tokens: int = 1024,
        temperature: float = 0.0,
        api_key: str | None = None,
    ) -> None:
        try:
            import anthropic
        except ImportError as exc:  # pragma: no cover - depends on env
            raise RuntimeError(
                "The anthropic package is not installed. Install it with "
                "'pip install anthropic', or set model.provider to 'mock'."
            ) from exc

        self.name = name
        self._max_tokens = max_tokens
        self._temperature = temperature
        self._client = anthropic.Anthropic(
            api_key=api_key or os.environ.get("ANTHROPIC_API_KEY")
        )

    def complete(
        self,
        *,
        system: str,
        messages: list[dict[str, Any]],
        tools: list[dict[str, Any]],
    ) -> ModelResponse:
        resp = self._client.messages.create(
            model=self.name,
            system=system,
            max_tokens=self._max_tokens,
            temperature=self._temperature,
            tools=tools,
            messages=_to_anthropic(messages),
        )
        return _from_anthropic(resp)


def _to_anthropic(messages: list[dict[str, Any]]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for msg in messages:
        role = msg.get("role")
        if role == "user":
            out.append({"role": "user", "content": msg.get("content", "")})
        elif role == "assistant":
            blocks: list[dict[str, Any]] = []
            if msg.get("content"):
                blocks.append({"type": "text", "text": msg["content"]})
            for call in msg.get("tool_calls", []):
                blocks.append(
                    {
                        "type": "tool_use",
                        "id": call.id,
                        "name": call.name,
                        "input": call.arguments,
                    }
                )
            out.append({"role": "assistant", "content": blocks})
        elif role == "tool":
            blocks = [
                {
                    "type": "tool_result",
                    "tool_use_id": r["id"],
                    "content": _stringify(r["content"]),
                }
                for r in msg.get("tool_results", [])
            ]
            out.append({"role": "user", "content": blocks})
    return out


def _from_anthropic(resp: Any) -> ModelResponse:
    text_parts: list[str] = []
    tool_calls: list[ToolCall] = []
    for block in resp.content:
        if block.type == "text":
            text_parts.append(block.text)
        elif block.type == "tool_use":
            tool_calls.append(
                ToolCall(id=block.id, name=block.name, arguments=dict(block.input))
            )
    return ModelResponse(text="".join(text_parts), tool_calls=tool_calls)


def _stringify(content: Any) -> str:
    import json

    if isinstance(content, str):
        return content
    return json.dumps(content, default=str)
