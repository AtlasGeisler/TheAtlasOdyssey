"""Dental Harness: an agent harness for an endodontic practice.

The model is the brain. The harness gives it tools, governed memory, and
enforced guardrails. See ARCHITECTURE.md for the eight principles.
"""

__version__ = "0.1.0"

from .bootstrap import build_agent
from .loop import AgentLoop, AgentResult

__all__ = ["build_agent", "AgentLoop", "AgentResult", "__version__"]
