"""The model abstraction.

The model is the brain and a single swappable parameter (Principle 7). The
loop talks only to this interface, so any provider, or a deterministic mock,
can stand in. Messages are kept in a provider-neutral shape and each client
translates them to its own wire format.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Protocol


@dataclass
class ToolCall:
    """A model's request to run one tool."""

    id: str
    name: str
    arguments: dict[str, Any]


@dataclass
class ModelResponse:
    """One assistant turn: free text plus any tool calls requested."""

    text: str = ""
    tool_calls: list[ToolCall] = field(default_factory=list)

    @property
    def wants_tools(self) -> bool:
        return bool(self.tool_calls)


# Provider-neutral message shapes used in the conversation list:
#   {"role": "user", "content": str}
#   {"role": "assistant", "content": str, "tool_calls": [ToolCall, ...]}
#   {"role": "tool", "tool_results": [{"id", "name", "content"}, ...]}


class ModelClient(Protocol):
    """What the loop needs from any model."""

    name: str

    def complete(
        self,
        *,
        system: str,
        messages: list[dict[str, Any]],
        tools: list[dict[str, Any]],
    ) -> ModelResponse:
        """Produce the next assistant turn given the conversation and tools."""
        ...
