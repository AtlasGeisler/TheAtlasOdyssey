"""Command-line entry point.

    python -m dental_harness "draft a thank-you note to a referrer"

Loads config, builds the agent (model chosen by config), runs the loop, and
prints the final answer. The default config uses the offline mock provider so
this runs with no API key.
"""

from __future__ import annotations

import argparse
import sys

from .bootstrap import build_agent
from .config import load_settings


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="dental-harness")
    parser.add_argument("prompt", help="the request for the agent")
    parser.add_argument(
        "--config", default=None, help="path to a config.yaml (optional)"
    )
    args = parser.parse_args(argv)

    settings = load_settings(args.config)
    agent = build_agent(settings)
    result = agent.run(args.prompt)

    print(result.answer)
    print(f"\n[turns: {result.turns}, model: {agent.model.name}]", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
