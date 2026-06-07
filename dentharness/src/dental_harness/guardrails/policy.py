"""Load the guardrail policy from data.

The policy lives in policy.yaml so a rule can be reviewed and changed without
touching enforcement code. This module only parses and validates it into typed
objects. It contains no enforcement logic.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Pattern

import yaml

DEFAULT_POLICY_PATH = Path(__file__).resolve().parent / "policy.yaml"


@dataclass(frozen=True)
class ActionAttrs:
    outbound: bool = False
    state_changing: bool = False
    phi_egress_authorized: bool = False


@dataclass(frozen=True)
class Policy:
    allowlist: frozenset[str]
    actions: dict[str, ActionAttrs]
    approval_require_for: frozenset[str]
    phi_sensitive_fields: frozenset[str]
    phi_patterns: dict[str, Pattern[str]]
    redaction_placeholder: str
    clinical_patterns: list[Pattern[str]]
    clinical_route_to: str
    responses: dict[str, str]

    def attrs(self, action: str) -> ActionAttrs:
        return self.actions.get(action, ActionAttrs())

    def response(self, code: str) -> str:
        return self.responses.get(code, "").strip()


def load_policy(path: str | Path | None = None) -> Policy:
    cfg_path = Path(path or DEFAULT_POLICY_PATH)
    data = yaml.safe_load(cfg_path.read_text(encoding="utf-8")) or {}

    scope = data.get("scope", {})
    actions_raw = data.get("actions", {}) or {}
    actions = {
        name: ActionAttrs(
            outbound=bool(attrs.get("outbound", False)),
            state_changing=bool(attrs.get("state_changing", False)),
            phi_egress_authorized=bool(attrs.get("phi_egress_authorized", False)),
        )
        for name, attrs in actions_raw.items()
    }

    phi = data.get("phi", {})
    phi_patterns = {
        name: re.compile(pattern)
        for name, pattern in (phi.get("patterns", {}) or {}).items()
    }

    clinical = data.get("clinical_advice", {})
    clinical_patterns = [
        re.compile(pattern, re.IGNORECASE)
        for pattern in (clinical.get("patterns", []) or [])
    ]

    return Policy(
        allowlist=frozenset(scope.get("allowlist", []) or []),
        actions=actions,
        approval_require_for=frozenset(
            data.get("approval", {}).get("require_for", []) or []
        ),
        phi_sensitive_fields=frozenset(
            f.lower() for f in (phi.get("sensitive_fields", []) or [])
        ),
        phi_patterns=phi_patterns,
        redaction_placeholder=phi.get("redaction_placeholder", "[REDACTED]"),
        clinical_patterns=clinical_patterns,
        clinical_route_to=clinical.get("route_to", "a licensed clinician"),
        responses=dict(data.get("responses", {}) or {}),
    )
