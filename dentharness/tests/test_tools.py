from dental_harness.tools.base import Tool, ToolRegistry
from dental_harness.tools.placeholder import build_placeholder_tool


def test_placeholder_echo():
    tool = build_placeholder_tool()
    assert tool.callback(message="hi") == {"echo": "hi"}
    assert tool.schema()["name"] == "echo"
    assert "message" in tool.schema()["input_schema"]["properties"]


def test_registry_register_and_get():
    reg = ToolRegistry()
    reg.register(build_placeholder_tool())
    assert reg.get("echo") is not None
    assert reg.get("missing") is None
    assert [s["name"] for s in reg.schemas()] == ["echo"]


def test_registry_rejects_duplicates():
    reg = ToolRegistry()
    reg.register(build_placeholder_tool())
    try:
        reg.register(build_placeholder_tool())
    except ValueError:
        pass
    else:
        raise AssertionError("expected duplicate registration to fail")
