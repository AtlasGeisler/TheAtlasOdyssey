# Dental Harness

An agent harness that wraps a model so it can do the recurring operational and
relationship work of a multi-location endodontic practice: referral intake and
triage, referring-doctor report drafting, front-desk call routing, insurance
and eligibility, billing-policy responses, scheduling and recall, and patient
education.

The model is the brain. The harness gives it tools, governed memory, and
enforced guardrails. See `ARCHITECTURE.md` for the design and `CLAUDE.md` for
the project constitution.

## Status

Prompt 1 skeleton: a runnable, model-driven loop that calls a placeholder tool
and returns a result, with a swappable model, lifecycle logging, a reserved
guardrail seam, an MCP-ready integration interface, and file-based memory. All
data is synthetic. No PHI, no real systems.

## Requirements

- Python 3.11 or newer
- The harness runs offline with the built-in `mock` model provider, so no API
  key is needed to try it. PyYAML is the only runtime dependency.

## Setup

```bash
cd dentharness
python -m venv .venv && source .venv/bin/activate   # optional
pip install -e .            # installs PyYAML and the dental-harness command
# or, without installing:
pip install PyYAML
```

## Run

From the `dentharness/` directory:

```bash
# if installed with pip install -e .
dental-harness "draft a thank-you note to a referring doctor"

# or without installing
PYTHONPATH=src python -m dental_harness "draft a thank-you note"
```

The default config (`config/config.yaml`) uses the offline mock model, so this
runs with no API key. Every tool call is logged to `logs/tool_calls.jsonl`.

## Use a live model

Edit `config/config.yaml`:

```yaml
model:
  provider: anthropic
  name: claude-opus-4-8
```

Then `pip install anthropic` and set `ANTHROPIC_API_KEY` (copy `.env.example`
to `.env`). The model is the only thing that changes. The loop, tools, and
guardrails are untouched.

## Tests and eval

```bash
pip install pytest
pytest                 # unit tests
python eval/run_eval.py   # file-driven scenario checks
```

## Layout

```
config/        config.yaml (model choice, paths)
src/dental_harness/
  loop.py        model-driven loop
  bootstrap.py   wiring
  models/        swappable model clients
  tools/         four-part tools + registry
  integrations/  MCP-ready interface + PMS integration
  guardrails/    Guardrail Ladder seam
  memory/        file-based governed memory
  logging/       lifecycle hooks (per-call audit log)
  deterministic/ reserved seam for required routing
knowledge/     inspectable reference files (policies, templates, voice, doctors)
data/synthetic/  synthetic data only
eval/          scenario checks
tests/         unit tests
```

## Writing rule

This project never uses em dashes or en dashes. Use commas instead.
