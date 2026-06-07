"""The agent loop.

Drives a tool-use conversation: send the user's request plus tool schemas to
the model, execute any tool calls against the Toolbox, feed results back, and
repeat until the model returns a final answer.

The model client is injected (see ModelClient) so this loop has no hard
dependency on any SDK — pass an AnthropicClient in production, or a scripted
fake in tests. When you wire the real one, default to the latest Claude model
(e.g. claude-opus-4-8 or claude-sonnet-4-6).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Protocol

from .tools import TOOL_SCHEMAS, Toolbox

SYSTEM_PROMPT = (
    "You are a dental practice assistant. Use the provided tools to look up "
    "patients, appointments, and ledger data, and to post charges or payments "
    "when explicitly asked. Never invent patient data — always call a tool. "
    "Confirm the patient identity before posting any ledger entry."
)


class ModelClient(Protocol):
    """Whatever talks to the LLM. Returns an assistant turn."""

    def create(
        self,
        *,
        system: str,
        messages: list[dict[str, Any]],
        tools: list[dict[str, Any]],
    ) -> "AssistantTurn":
        ...


@dataclass
class ToolCall:
    id: str
    name: str
    arguments: dict[str, Any]


@dataclass
class AssistantTurn:
    """Normalized model output: any text, plus any tool calls requested."""

    text: str = ""
    tool_calls: list[ToolCall] = field(default_factory=list)

    @property
    def wants_tools(self) -> bool:
        return bool(self.tool_calls)


@dataclass
class AgentResult:
    answer: str
    turns: int
    transcript: list[dict[str, Any]]


def run_agent(
    user_message: str,
    *,
    client: ModelClient,
    toolbox: Toolbox,
    max_turns: int = 8,
) -> AgentResult:
    messages: list[dict[str, Any]] = [
        {"role": "user", "content": user_message}
    ]

    for turn in range(1, max_turns + 1):
        assistant = client.create(
            system=SYSTEM_PROMPT, messages=messages, tools=TOOL_SCHEMAS
        )
        messages.append({"role": "assistant", "content": assistant.text})

        if not assistant.wants_tools:
            return AgentResult(
                answer=assistant.text, turns=turn, transcript=messages
            )

        tool_results = []
        for call in assistant.tool_calls:
            result = toolbox.dispatch(call.name, call.arguments)
            tool_results.append(
                {
                    "tool_call_id": call.id,
                    "name": call.name,
                    "result": result,
                }
            )
        messages.append({"role": "tool", "content": tool_results})

    return AgentResult(
        answer="Stopped: reached max turns without a final answer.",
        turns=max_turns,
        transcript=messages,
    )
