"""The Guardrail Ladder.

Soft rules steer the model from tool descriptions and the knowledge files.
Hard rules live here as code-enforced barriers the model cannot bypass. Every
tool call routes through GuardrailEngine.evaluate before the tool runs.

See GUARDRAILS.md for the rule-by-rule map of soft versus hard and the
enforcement mechanism for each.
"""

from .barriers import Decision, GuardrailContext
from .engine import GuardrailEngine, load_engine
from .policy import Policy, load_policy

__all__ = [
    "GuardrailEngine",
    "load_engine",
    "Decision",
    "GuardrailContext",
    "Policy",
    "load_policy",
]
