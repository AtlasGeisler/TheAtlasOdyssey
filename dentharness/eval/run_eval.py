"""A tiny file-driven eval harness.

Each case in eval/cases is a JSON file with a prompt and simple expectations.
The eval runs the agent with the offline mock provider and checks the
transcript. This is intentionally thin scaffolding to grow as the harness does.

Run:
    python eval/run_eval.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

# Make src importable when run directly.
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from dental_harness.bootstrap import build_agent  # noqa: E402
from dental_harness.config import load_settings  # noqa: E402

CASES_DIR = Path(__file__).resolve().parent / "cases"


def _tools_called(transcript: list[dict]) -> list[str]:
    names: list[str] = []
    for msg in transcript:
        for call in msg.get("tool_calls", []) or []:
            names.append(call.name)
    return names


def run() -> int:
    settings = load_settings()
    cases = sorted(CASES_DIR.glob("*.json"))
    if not cases:
        print("No eval cases found.")
        return 0

    failures = 0
    for case_path in cases:
        case = json.loads(case_path.read_text(encoding="utf-8"))
        agent = build_agent(settings)
        result = agent.run(case["prompt"])

        ok = True
        expect_tool = case.get("expect_tool")
        if expect_tool and expect_tool not in _tools_called(result.transcript):
            ok = False
        expect_substr = case.get("expect_answer_contains")
        if expect_substr and expect_substr not in result.answer:
            ok = False

        status = "PASS" if ok else "FAIL"
        if not ok:
            failures += 1
        print(f"[{status}] {case_path.name}: {case.get('name', '')}")

    print(f"\n{len(cases) - failures}/{len(cases)} cases passed.")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(run())
