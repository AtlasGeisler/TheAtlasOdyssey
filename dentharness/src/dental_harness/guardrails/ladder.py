"""The Guardrail Ladder (skeleton, filled in Prompt 2).

The ladder separates two kinds of rules:

  Soft rules  live in tool descriptions and the system prompt. They steer the
              model. The model can, in principle, ignore them.
  Hard rules  live here as code. They are barriers the model cannot bypass:
              every tool call passes through check() before it runs, and a
              hard rule can block it outright regardless of what the model
              decided.

This is the reserved space. The loop already calls check() before executing
any tool, so Prompt 2 adds rungs here without touching the loop. Today there
are no hard rules, so everything is allowed, but the seam is load-bearing.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from ..models.base import ToolCall

# A hard rule inspects a tool call and returns a reason string to BLOCK it,
# or None to allow it. Hard rules are pure and must not depend on the model.
HardRule = Callable[[ToolCall], str | None]


@dataclass(frozen=True)
class Decision:
    allowed: bool
    reason: str = ""

    @classmethod
    def allow(cls) -> "Decision":
        return cls(allowed=True)

    @classmethod
    def block(cls, reason: str) -> "Decision":
        return cls(allowed=False, reason=reason)


class GuardrailLadder:
    """Evaluates hard rules against a tool call before it executes."""

    def __init__(self, hard_rules: list[HardRule] | None = None) -> None:
        # Prompt 2 will populate the default ladder. Empty for now by design.
        self._hard_rules: list[HardRule] = list(hard_rules or [])

    def add_rule(self, rule: HardRule) -> None:
        self._hard_rules.append(rule)

    def check(self, call: ToolCall) -> Decision:
        """The hard barrier. Run before any tool executes."""
        for rule in self._hard_rules:
            reason = rule(call)
            if reason is not None:
                return Decision.block(reason)
        return Decision.allow()


def default_ladder() -> GuardrailLadder:
    """The ladder the harness boots with. Prompt 2 adds the rungs."""
    return GuardrailLadder(hard_rules=[])
