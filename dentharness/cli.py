"""A tiny CLI to exercise the harness without an LLM.

This calls the tools directly so you can confirm an adapter works end-to-end
before wiring up a model. Run:

    python -m dentharness.cli patients Lovelace
    python -m dentharness.cli ledger P1
    python -m dentharness.cli appts P1
"""

from __future__ import annotations

import argparse
import json
import sys

from .agent.tools import Toolbox
from .pms import available, get_pms


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="dentharness")
    parser.add_argument(
        "--pms",
        default=None,
        help=f"adapter name (default: env or mock). available: {available()}",
    )
    sub = parser.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("patients", help="search patients")
    p.add_argument("query")

    p = sub.add_parser("appts", help="list appointments")
    p.add_argument("patient_id")
    p.add_argument("--on", default=None)

    p = sub.add_parser("ledger", help="show ledger and balance")
    p.add_argument("patient_id")

    args = parser.parse_args(argv)
    box = Toolbox(get_pms(args.pms))

    if args.cmd == "patients":
        out = box.find_patients(args.query)
    elif args.cmd == "appts":
        out = box.get_appointments(args.patient_id, on=args.on)
    elif args.cmd == "ledger":
        out = box.get_ledger(args.patient_id)
    else:  # pragma: no cover - argparse enforces
        parser.error("unknown command")

    json.dump(out, sys.stdout, indent=2)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
