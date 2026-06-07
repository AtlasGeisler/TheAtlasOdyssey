"""Assemble a runnable agent from settings.

This is the wiring point: it reads config, builds the swappable model, gathers
tools from the placeholder and from every registered integration, loads the
system prompt from the knowledge files, and attaches the guardrail check and
lifecycle logging. Adding an integration here is the only change needed to give
the model new tools.
"""

from __future__ import annotations

from pathlib import Path

from .config import Settings, load_settings
from .guardrails.ladder import default_ladder
from .integrations.pms import PMSIntegration
from .logging.hooks import LifecycleHooks
from .loop import AgentLoop
from .models.registry import build_model
from .tools.base import ToolRegistry
from .tools.placeholder import build_placeholder_tool

_FALLBACK_SYSTEM_PROMPT = (
    "You are the Dental Harness assistant for a multi-location endodontic "
    "practice. Use the available tools to do the work. Do not invent patient "
    "data, always call a tool. All data in this environment is synthetic."
)


def load_system_prompt(settings: Settings) -> str:
    prompt_file = settings.path("knowledge") / "system_prompt.md"
    if prompt_file.exists():
        return prompt_file.read_text(encoding="utf-8").strip()
    return _FALLBACK_SYSTEM_PROMPT


def build_agent(settings: Settings | None = None) -> AgentLoop:
    settings = settings or load_settings()

    tools = ToolRegistry()
    tools.register(build_placeholder_tool())
    # Integrations contribute their tools through the standard interface.
    tools.add_many(PMSIntegration().get_tools())

    return AgentLoop(
        model=build_model(settings.model),
        tools=tools,
        guardrails=default_ladder(),
        hooks=LifecycleHooks(settings.path("logs")),
        system_prompt=load_system_prompt(settings),
        max_turns=settings.max_turns,
    )
