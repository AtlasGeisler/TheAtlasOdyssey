"""A trivial placeholder tool for the skeleton.

It proves the loop can hand the model a tool, run its callback, log the call,
and feed the result back. Replace or supplement with real tools later.
"""

from __future__ import annotations

from typing import Any

from .base import Tool


def _echo(message: str) -> dict[str, Any]:
    return {"echo": message}


def build_placeholder_tool() -> Tool:
    return Tool(
        name="echo",
        description=(
            "Echo a short message back verbatim. Use this only to confirm the "
            "harness can call a tool end to end. Provide the text to echo as "
            "'message'. Returns the same text under the key 'echo'."
        ),
        input_schema={
            "type": "object",
            "properties": {
                "message": {
                    "type": "string",
                    "description": "The text to echo back unchanged.",
                }
            },
            "required": ["message"],
        },
        callback=_echo,
    )
