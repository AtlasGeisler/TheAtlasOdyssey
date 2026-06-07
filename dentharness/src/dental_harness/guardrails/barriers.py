"""The four hard barriers.

Each barrier is a pure function of a GuardrailContext. It returns a Decision to
block or hold, or None to let the call pass to the next barrier. Barriers are
code-enforced and cannot be talked past by the model: they inspect the actual
tool call, not the model's stated intent. Wording for any refusal comes from
the policy data, not from here.

The four rules:
  1. PHI egress control      phi_egress_barrier
  2. Clinical-advice gate    clinical_advice_barrier
  3. Scope enforcement       scope_barrier
  4. Human-approval gate     approval_barrier
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Optional

from ..models.base import ToolCall
from .policy import Policy
from .redaction import detect_phi


@dataclass(frozen=True)
class Decision:
    outcome: str  # "allow" | "block" | "hold"
    code: str = ""
    reason: str = ""  # internal detail for the audit log
    message: str = ""  # brand-voice text safe to surface

    @property
    def allowed(self) -> bool:
        return self.outcome == "allow"

    @classmethod
    def allow(cls) -> "Decision":
        return cls(outcome="allow")

    @classmethod
    def block(cls, code: str, reason: str, message: str) -> "Decision":
        return cls(outcome="block", code=code, reason=reason, message=message)

    @classmethod
    def hold(cls, code: str, reason: str, message: str) -> "Decision":
        return cls(outcome="hold", code=code, reason=reason, message=message)


@dataclass
class GuardrailContext:
    call: ToolCall
    policy: Policy
    approved: bool = False

    def attrs(self):
        return self.policy.attrs(self.call.name)

    def text_blob(self) -> str:
        """All string values in the arguments, concatenated for scanning."""
        return " ".join(_strings(self.call.arguments))


Barrier = Callable[[GuardrailContext], Optional[Decision]]


def scope_barrier(ctx: GuardrailContext) -> Optional[Decision]:
    """Rule 3. Default deny: only allowlisted actions may run."""
    if ctx.call.name not in ctx.policy.allowlist:
        return Decision.block(
            code="scope",
            reason=f"action {ctx.call.name!r} is not in the allowlist",
            message=ctx.policy.response("scope"),
        )
    return None


def clinical_advice_barrier(ctx: GuardrailContext) -> Optional[Decision]:
    """Rule 2. Block any call whose text seeks or carries clinical judgment."""
    blob = ctx.text_blob()
    for pattern in ctx.policy.clinical_patterns:
        if pattern.search(blob):
            return Decision.block(
                code="clinical_advice",
                reason=(
                    f"clinical-advice content matched /{pattern.pattern}/; "
                    f"routed to {ctx.policy.clinical_route_to}"
                ),
                message=ctx.policy.response("clinical_advice"),
            )
    return None


def phi_egress_barrier(ctx: GuardrailContext) -> Optional[Decision]:
    """Rule 1. Block PHI leaving via an outbound action not authorized for it."""
    attrs = ctx.attrs()
    if attrs.outbound and not attrs.phi_egress_authorized:
        found = detect_phi(ctx.text_blob(), ctx.policy)
        if found:
            return Decision.block(
                code="phi_egress",
                reason=f"unauthorized PHI in outbound payload: {sorted(found)}",
                message=ctx.policy.response("phi_egress"),
            )
    return None


def approval_barrier(ctx: GuardrailContext) -> Optional[Decision]:
    """Rule 4. Hold outbound or state-changing actions until a human approves."""
    attrs = ctx.attrs()
    require = ctx.policy.approval_require_for
    needs_approval = ("outbound" in require and attrs.outbound) or (
        "state_changing" in require and attrs.state_changing
    )
    if needs_approval and not ctx.approved:
        return Decision.hold(
            code="approval_required",
            reason="action requires explicit human approval before execution",
            message=ctx.policy.response("approval_required"),
        )
    return None


# Order matters and is fail-closed: deny out-of-scope first, refuse clinical
# advice, stop unauthorized PHI egress, then hold for approval.
DEFAULT_BARRIERS: list[Barrier] = [
    scope_barrier,
    clinical_advice_barrier,
    phi_egress_barrier,
    approval_barrier,
]


def _strings(value: Any) -> list[str]:
    if isinstance(value, str):
        return [value]
    if isinstance(value, dict):
        out: list[str] = []
        for v in value.values():
            out.extend(_strings(v))
        return out
    if isinstance(value, (list, tuple)):
        out = []
        for v in value:
            out.extend(_strings(v))
        return out
    return []
