# Architecture

The Dental Harness wraps a model so it can do the recurring operational and
relationship work of a multi-location endodontic practice: referral intake and
triage, referring-doctor report drafting, front-desk call routing, insurance
and eligibility, billing-policy responses, scheduling and recall, and patient
education.

The model is the brain. The harness gives it tools, governed memory, and
enforced guardrails. The harness is deliberately thin.

## The eight principles

### 1. Model-driven architecture
The loop never hardcodes a sequence of steps. It sends the conversation and the
available tools to the model, runs whatever the model asks for, feeds results
back, and repeats. See `src/dental_harness/loop.py`. The only place
determinism is allowed is `src/dental_harness/deterministic/`, reserved for
logic that is legally or operationally required to be fixed. It is empty today,
on purpose, so any future determinism is a visible, deliberate choice.

### 2. A tool is four parts
A name, a precise plain-English description, an input schema, and a callback.
See the `Tool` dataclass in `src/dental_harness/tools/base.py`. The description
is the primary steering surface and is treated as a first-class artifact.

### 3. Reference knowledge lives on the file system
Policies, templates, voice guides, per-doctor preferences, and even the system
prompt live as inspectable files under `knowledge/`, loaded at runtime, never
baked into code.

### 4. Integrations behind a standard interface (MCP-ready)
Every external system implements the `Integration` interface in
`src/dental_harness/integrations/base.py`, which exposes a named set of tools.
That is the same shape an MCP server presents, so a local integration and a
remote MCP server are interchangeable to the loop. The practice management
system is the first integration, with a vendor-neutral adapter behind it.

### 5. Lifecycle hooks log every tool call from day one
`src/dental_harness/logging/hooks.py` fires before and after every tool call
and writes one JSON line per call to `logs/tool_calls.jsonl`, capturing the
tool, arguments, outcome, guardrail decision, and duration. This is the audit
spine the healthcare layer builds on.

### 6. Output structure is enforced through the input schema
Tools declare JSON Schema on their inputs. Structured output is expressed as a
tool whose schema is the contract, not as a prose request to the model.

### 7. The model is a single swappable parameter
`config/config.yaml` selects the model provider. `models/registry.py` builds
it. The loop depends only on the `ModelClient` interface, so swapping models or
providers, or dropping in the offline mock, is a config edit.

### 8. Simplicity gradient
Prefer the thinnest harness that works, and plan to remove scaffolding as
models improve. Candidates to revisit as models get stronger: the mock model
client, the verbosity of tool descriptions, and any retry or formatting helpers
we add later. We track these here and prune deliberately.

## The healthcare layer

Two non-negotiables are reserved now and built next:

- The Guardrail Ladder separates soft rules, which live in tool descriptions
  and the system prompt and merely steer the model, from hard rules, which live
  in code as barriers the model cannot bypass. The loop already routes every
  tool call through `guardrails.check()` before the tool runs, so the rungs are
  added without touching the loop. See `src/dental_harness/guardrails/`.
- Synthetic data only until safety is validated. Enforced by `.gitignore` and
  stated as a hard rule in `CLAUDE.md`. No PHI, no real systems.

## Component map

```
src/dental_harness/
  loop.py            the model-driven loop (Principle 1)
  bootstrap.py       wiring: model + tools + guardrails + hooks + prompt
  config.py          YAML config loader (Principles 3, 7)
  __main__.py        CLI entry point
  models/            swappable model clients (Principle 7)
  tools/             four-part tools + registry (Principles 2, 6)
  integrations/      MCP-ready interface + PMS integration (Principle 4)
  guardrails/        the Guardrail Ladder (healthcare layer)
  memory/            file-based governed memory (Principle 3)
  logging/           lifecycle hooks, per-call audit log (Principle 5)
  deterministic/     reserved seam for required routing (Principle 1)
knowledge/           inspectable reference files (Principle 3)
data/synthetic/      synthetic data only
eval/                file-driven scenario checks
tests/               unit tests
```

## Data flow of one turn

1. `bootstrap.build_agent` assembles the loop from config.
2. The loop sends system prompt, messages, and tool schemas to the model.
3. The model returns text or tool calls.
4. For each tool call: `hooks.before_tool`, then `guardrails.check`, then the
   tool callback if allowed, then `hooks.after_tool`.
5. Tool results go back to the model. Repeat until a final answer or the turn
   limit.
