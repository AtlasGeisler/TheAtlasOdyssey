import json

from dental_harness.guardrails.ladder import default_ladder
from dental_harness.logging.hooks import LifecycleHooks
from dental_harness.loop import AgentLoop
from dental_harness.models.mock_client import MockModelClient
from dental_harness.tools.base import ToolRegistry
from dental_harness.tools.placeholder import build_placeholder_tool


def _agent(tmp_path):
    tools = ToolRegistry()
    tools.register(build_placeholder_tool())
    return AgentLoop(
        model=MockModelClient(),
        tools=tools,
        guardrails=default_ladder(),
        hooks=LifecycleHooks(tmp_path / "logs"),
        system_prompt="test",
        max_turns=8,
    )


def test_loop_calls_tool_then_answers(tmp_path):
    agent = _agent(tmp_path)
    result = agent.run("please echo hello")
    assert result.turns == 2
    assert "Tool result" in result.answer


def test_loop_logs_every_tool_call(tmp_path):
    agent = _agent(tmp_path)
    agent.run("echo this")
    log_file = tmp_path / "logs" / "tool_calls.jsonl"
    assert log_file.exists()
    lines = [json.loads(line) for line in log_file.read_text().splitlines()]
    assert len(lines) == 1
    assert lines[0]["tool"] == "echo"
    assert lines[0]["allowed"] is True


def test_loop_stops_at_max_turns(tmp_path):
    # A model that always asks for a tool, never finishing.
    class Looping(MockModelClient):
        def complete(self, *, system, messages, tools):
            from dental_harness.models.base import ModelResponse, ToolCall

            return ModelResponse(
                text="again",
                tool_calls=[
                    ToolCall(id="x", name="echo", arguments={"message": "m"})
                ],
            )

    tools = ToolRegistry()
    tools.register(build_placeholder_tool())
    agent = AgentLoop(
        model=Looping(),
        tools=tools,
        guardrails=default_ladder(),
        hooks=LifecycleHooks(tmp_path / "logs"),
        system_prompt="test",
        max_turns=3,
    )
    result = agent.run("loop")
    assert result.turns == 3
    assert "maximum number of turns" in result.answer
