"""The integration interface (Principle 4).

Every external system sits behind this interface, never bespoke wiring. An
integration is a named provider of tools, which is exactly the shape an MCP
server exposes, so a local integration and a remote MCP server are
interchangeable to the loop. To add a system: implement get_tools and register
the integration. Nothing above this layer changes.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from ..tools.base import Tool


class Integration(ABC):
    name: str

    @abstractmethod
    def get_tools(self) -> list[Tool]:
        """Return the tools this integration contributes to the registry."""

    def health_check(self) -> bool:
        """Cheap liveness probe. Override for real systems."""
        return True

    def close(self) -> None:
        """Release any resources. Override if needed."""
        return None
