"""PHI detection and redaction.

Used by two barriers and by the logging hooks, so PHI never reaches a log or
an outbound payload unredacted. Detection is pattern-based for free text and
field-name based for structured arguments. Free-text personal names are not
reliably detectable by pattern, which is a known limitation documented in
GUARDRAILS.md and backstopped by the human-approval gate.
"""

from __future__ import annotations

from typing import Any

from .policy import Policy


def detect_phi(text: str, policy: Policy) -> list[str]:
    """Return the kinds of PHI found in free text, empty if none."""
    if not text:
        return []
    return [name for name, pat in policy.phi_patterns.items() if pat.search(text)]


def redact_text(text: str, policy: Policy) -> str:
    out = text
    for pat in policy.phi_patterns.values():
        out = pat.sub(policy.redaction_placeholder, out)
    return out


def redact_value(value: Any, policy: Policy) -> Any:
    """Recursively redact PHI from a structure for safe logging.

    A value under a sensitive field name is replaced wholesale. Free text is
    scrubbed by pattern. Lists and dicts are walked.
    """
    if isinstance(value, dict):
        redacted: dict[Any, Any] = {}
        for key, val in value.items():
            if isinstance(key, str) and key.lower() in policy.phi_sensitive_fields:
                redacted[key] = (
                    policy.redaction_placeholder
                    if val not in (None, "")
                    else val
                )
            else:
                redacted[key] = redact_value(val, policy)
        return redacted
    if isinstance(value, list):
        return [redact_value(v, policy) for v in value]
    if isinstance(value, str):
        return redact_text(value, policy)
    return value
