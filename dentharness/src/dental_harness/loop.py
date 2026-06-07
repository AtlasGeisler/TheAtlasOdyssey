"""The agent loop.

Model-driven (Principle 1): the loop never decides what to do next. It sends
the conversation and the available tools to the model, runs whatever tools the
model asks for, feeds the results back, and repeats until the model returns a
final answer. The only fixed machinery is safety and observability: every tool
call passes through the guardrail check and the lifecycle hooks.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .guardrails.engine import GuardrailEngine
from .logging.hooks import LifecycleHooks
from .models.base import ModelClient, ToolCall
from .tools.base import ToolRegistry


@dataclass
class AgentResult:
    answer: str
    turns: int
    transcript: list[dict[str, Any]] = field(default_factory=list)


class AgentLoop:
    def __init__(
        self,
        *,
        model: ModelClient,
        tools: ToolRegistry,
        guardrails: GuardrailEngine,
        hooks: LifecycleHooks,
        system_prompt: str,
        max_turns: int = 8,
        approved_actions: set[str] | None = None,
    ) -> None:
        self.model = model
        self.tools = tools
        self.guardrails = guardrails
        self.hooks = hooks
        self.system_prompt = system_prompt
        self.max_turns = max_turns
        # Actions a human has pre-approved for this run. Empty by default, so
        # outbound and state-changing actions are held, never auto-sent.
        self.approved_actions = set(approved_actions or [])

    def run(self, user_message: str) -> AgentResult:
        messages: list[dict[str, Any]] = [
            {"role": "user", "content": user_message}
        ]

        for turn in range(1, self.max_turns + 1):
            response = self.model.complete(
                system=self.system_prompt,
                messages=messages,
                tools=self.tools.schemas(),
            )
            messages.append(
                {
                    "role": "assistant",
                    "content": response.text,
                    "tool_calls": response.tool_calls,
                }
            )

            if not response.wants_tools:
                return AgentResult(response.text, turn, messages)

            tool_results = [
                {
                    "id": call.id,
                    "name": call.name,
                    "content": self._run_tool(call),
                }
                for call in response.tool_calls
            ]
            messages.append({"role": "tool", "tool_results": tool_results})

        return AgentResult(
            "Stopped: reached the maximum number of turns without a final "
            "answer.",
            self.max_turns,
            messages,
        )

    def _run_tool(self, call: ToolCall) -> dict[str, Any]:
        """Run one tool call through the guardrails and hooks. Never raises.

        The guardrail check is the single chokepoint: the tool runs only if the
        engine allows it. Blocks and holds short-circuit before any callback.
        """
        self.hooks.before_tool(call)

        decision = self.guardrails.evaluate(
            call, approved=call.name in self.approved_actions
        )

        if decision.allowed:
            tool = self.tools.get(call.name)
            if tool is None:
                result = {"error": f"unknown tool {call.name!r}"}
            else:
                try:
                    result = tool.callback(**call.arguments)
                except TypeError as exc:
                    result = {"error": f"bad arguments for {call.name}: {exc}"}
        else:
            # Blocked or held by a hard barrier. The tool never runs.
            result = {
                "status": decision.outcome,
                "guardrail": decision.code,
                "message": decision.message,
            }

        self.hooks.after_tool(call, result=result, decision=decision)
        return result
