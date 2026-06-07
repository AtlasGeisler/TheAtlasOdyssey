"""Adapter selection.

The agent never imports a concrete adapter. It asks the registry for one by
name (or via the DENTHARNESS_PMS env var), so swapping vendors is a config
change, not a code change. Register your own adapter here.
"""

from __future__ import annotations

import os
from typing import Callable

from .adapter import PMSAdapter
from .mock import MockPMS

_FACTORIES: dict[str, Callable[[], PMSAdapter]] = {
    "mock": MockPMS,
}


def register(name: str, factory: Callable[[], PMSAdapter]) -> None:
    """Register an adapter factory under a name. Call this for your vendor."""
    _FACTORIES[name] = factory


def available() -> list[str]:
    return sorted(_FACTORIES)


def get_pms(name: str | None = None) -> PMSAdapter:
    name = name or os.environ.get("DENTHARNESS_PMS", "mock")
    try:
        return _FACTORIES[name]()
    except KeyError:
        raise ValueError(
            f"Unknown PMS adapter {name!r}. Available: {available()}"
        ) from None
