"""Build a model client from config (Principle 7)."""

from __future__ import annotations

from typing import Any, Callable

from .base import ModelClient
from .mock_client import MockModelClient

_PROVIDERS: dict[str, Callable[..., ModelClient]] = {
    "mock": MockModelClient,
}


def register_provider(name: str, factory: Callable[..., ModelClient]) -> None:
    _PROVIDERS[name] = factory


def build_model(model_config: dict[str, Any]) -> ModelClient:
    provider = model_config.get("provider", "mock")

    if provider == "anthropic":
        # Imported here so the dependency is only needed when actually used.
        from .anthropic_client import AnthropicModelClient

        return AnthropicModelClient(
            name=model_config.get("name", "claude-opus-4-8"),
            max_tokens=model_config.get("max_tokens", 1024),
            temperature=model_config.get("temperature", 0.0),
        )

    try:
        factory = _PROVIDERS[provider]
    except KeyError:
        raise ValueError(
            f"Unknown model provider {provider!r}. "
            f"Known: {sorted(_PROVIDERS) + ['anthropic']}"
        ) from None
    return factory(**model_config)
