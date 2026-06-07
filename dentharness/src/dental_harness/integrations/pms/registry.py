"""Adapter selection for the PMS integration.

Register your own adapter here. Select it by name or the DENTAL_HARNESS_PMS
environment variable.
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
    _FACTORIES[name] = factory


def available() -> list[str]:
    return sorted(_FACTORIES)


def get_pms(name: str | None = None) -> PMSAdapter:
    name = name or os.environ.get("DENTAL_HARNESS_PMS", "mock")
    try:
        return _FACTORIES[name]()
    except KeyError:
        raise ValueError(
            f"Unknown PMS adapter {name!r}. Available: {available()}"
        ) from None
