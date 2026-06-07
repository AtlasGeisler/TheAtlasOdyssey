"""A tool is four parts (Principle 2).

A name, a precise plain-English description (the primary steering surface), an
input schema (which is how output structure gets enforced, Principle 6), and a
callback. Nothing more. The registry is a flat collection the loop draws from.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable

ToolCallback = Callable[..., dict[str, Any]]


@dataclass(frozen=True)
class Tool:
    name: str
    description: str
    input_schema: dict[str, Any]
    callback: ToolCallback

    def schema(self) -> dict[str, Any]:
        """The declaration handed to the model (Anthropic tool-use shape)."""
        return {
            "name": self.name,
            "description": self.description,
            "input_schema": self.input_schema,
        }


class ToolRegistry:
    def __init__(self) -> None:
        self._tools: dict[str, Tool] = {}

    def register(self, tool: Tool) -> None:
        if tool.name in self._tools:
            raise ValueError(f"Duplicate tool name: {tool.name!r}")
        self._tools[tool.name] = tool

    def add_many(self, tools: list[Tool]) -> None:
        for tool in tools:
            self.register(tool)

    def get(self, name: str) -> Tool | None:
        return self._tools.get(name)

    def all(self) -> list[Tool]:
        return list(self._tools.values())

    def schemas(self) -> list[dict[str, Any]]:
        return [tool.schema() for tool in self._tools.values()]
