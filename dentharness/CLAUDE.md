# CLAUDE.md, the project constitution

Every session working on the Dental Harness reads this file first and follows
it. This is the Dental Harness: an agent harness that wraps a model so it can
do the recurring operational and relationship work of a multi-location
endodontic practice. The model is the brain. The harness gives it tools,
governed memory, and enforced guardrails.

## The eight architectural principles (all future work follows these)

1. Model-driven architecture. Never hardcode the sequence of steps. Define
   tools plus a system prompt and let the model decide what to call and when.
   No routing logic except where determinism is legally or operationally
   required, which lives only in `src/dental_harness/deterministic/`.
2. A tool is four parts: a name, a precise plain-English description (the
   primary steering surface), an input schema, and a callback.
3. Reference knowledge (policies, templates, voice guides, per-doctor
   preferences) lives on the file system as inspectable files, not baked into
   code.
4. Integrations live behind a standard, MCP-ready interface, not bespoke
   wiring.
5. Lifecycle hooks log every tool call from day one.
6. Output structure is enforced through the input schema, not requested in
   prose.
7. The model is a single swappable parameter, chosen by config.
8. Simplicity gradient: prefer the thinnest harness that works, and plan to
   remove scaffolding as models improve.

## The Guardrail Ladder (non-negotiable healthcare layer)

The harness separates two kinds of rules and must always keep them separate:

- Soft rules (tone, escalation phrasing, voice) live in tool descriptions and
  the system prompt. They steer the model.
- Hard rules live in code in `src/dental_harness/guardrails/` as barriers the
  model cannot bypass. Every tool call routes through the guardrail check
  before the tool runs.

This separation is required. Do not move a hard rule into a description, and do
not rely on a description for anything that must not happen.

## Synthetic data only

No PHI and no real systems at this stage. Synthetic, fictional data only until
the safety layer is validated. Any directory that could hold patient data is
gitignored. Never commit real patient information.

## Writing rule (standing)

Never use em dashes or en dashes. Use commas instead. This applies to all code
comments, docs, generated drafts, and chat replies.

## United Endodontics brand palette

Use these for any formatted or visual output:

- Near-black `#1A1A1A`, primary text
- Deep forest green `#1E3A28`, headers and strong accents
- Primary green `#3A7D44`, primary actions and links
- Soft sage `#7CB68A`, secondary accents
- Warm cream `#F5F0E8`, backgrounds and surfaces

## How to run

- Offline by default. `config/config.yaml` uses the `mock` model provider, so
  the harness runs with no API key.
- `python -m dental_harness "your request"` from the `dentharness/` directory,
  with `src` on the path (see README).
- Switch to a live model by setting `model.provider: anthropic` in the config
  and providing `ANTHROPIC_API_KEY`. Default to a current Claude model.
