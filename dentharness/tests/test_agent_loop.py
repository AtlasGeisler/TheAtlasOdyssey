"""The agent loop driven by a scripted fake model — no network, no SDK."""

from __future__ import annotations

from typing import Any

from dentharness.agent import AssistantTurn, Toolbox, run_agent
from dentharness.agent.loop import ToolCall, ModelClient
from dentharness.pms import get_pms


class ScriptedClient(ModelClient):
    """Plays back a fixed list of AssistantTurns, one per create() call."""

    def __init__(self, turns: list[AssistantTurn]) -> None:
        self._turns = list(turns)
        self.calls: list[dict[str, Any]] = []

    def create(self, *, system, messages, tools) -> AssistantTurn:
        self.calls.append({"messages": list(messages), "tools": tools})
        return self._turns.pop(0)


def test_loop_executes_tool_then_answers() -> None:
    client = ScriptedClient(
        [
            AssistantTurn(
                text="Looking that up.",
                tool_calls=[
                    ToolCall(
                        id="t1",
                        name="get_ledger",
                        arguments={"patient_id": "P1"},
                    )
                ],
            ),
            AssistantTurn(text="Ada's balance is $400.00."),
        ]
    )
    result = run_agent(
        "What does Ada owe?", client=client, toolbox=Toolbox(get_pms())
    )
    assert result.answer == "Ada's balance is $400.00."
    assert result.turns == 2
    # The tool result must have been fed back into the second create() call.
    second_call_roles = [m["role"] for m in client.calls[1]["messages"]]
    assert "tool" in second_call_roles


def test_loop_stops_at_max_turns() -> None:
    looping = AssistantTurn(
        text="again",
        tool_calls=[
            ToolCall(id="x", name="get_patient", arguments={"patient_id": "P1"})
        ],
    )
    client = ScriptedClient([looping] * 10)
    result = run_agent(
        "loop forever",
        client=client,
        toolbox=Toolbox(get_pms()),
        max_turns=3,
    )
    assert result.turns == 3
    assert "max turns" in result.answer


def test_dispatch_unknown_tool() -> None:
    out = Toolbox(get_pms()).dispatch("frobnicate", {})
    assert "error" in out
