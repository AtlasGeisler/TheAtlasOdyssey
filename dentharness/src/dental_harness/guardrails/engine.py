"""The single guardrail enforcement entry point.

Every tool call routes through GuardrailEngine.evaluate before the tool runs.
The engine runs the hard barriers in order and returns the first block or hold,
otherwise it allows. No tool may bypass this. The engine also exposes the PHI
redactor so logs are scrubbed through the same policy.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from ..models.base import ToolCall
from .barriers import DEFAULT_BARRIERS, Barrier, Decision, GuardrailContext
from .policy import Policy, load_policy
from .redaction import detect_phi, redact_value


class GuardrailEngine:
    def __init__(
        self, policy: Policy, barriers: list[Barrier] | None = None
    ) -> None:
        self.policy = policy
        self.barriers = barriers if barriers is not None else DEFAULT_BARRIERS

    def evaluate(self, call: ToolCall, *, approved: bool = False) -> Decision:
        """The hard barrier. Run before any tool executes."""
        ctx = GuardrailContext(call=call, policy=self.policy, approved=approved)
        for barrier in self.barriers:
            decision = barrier(ctx)
            if decision is not None:
                return decision
        return Decision.allow()

    def redact(self, value: Any) -> Any:
        """Scrub PHI from a value for safe logging."""
        return redact_value(value, self.policy)

    def contains_phi(self, text: str) -> bool:
        return bool(detect_phi(text, self.policy))


def load_engine(policy_path: str | Path | None = None) -> GuardrailEngine:
    """Build the engine the harness boots with, from the policy data file."""
    return GuardrailEngine(load_policy(policy_path))
