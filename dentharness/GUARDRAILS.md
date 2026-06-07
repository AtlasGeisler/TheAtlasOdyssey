# The Guardrail Ladder

The video's logic is that smarter models need fewer guardrails. That holds only
where the cost of a wrong action is low. Here it is high, so these barriers are
enforced in code, not in descriptions. A more capable model does not get more
latitude to send PHI, give clinical advice, act out of scope, or send something
a human never approved.

## Two kinds of rule

- Soft rules steer the model. They live in tool descriptions, the system
  prompt, and the knowledge files (voice, escalation phrasing, formatting). The
  model can, in principle, ignore them. They are handled separately and are not
  in this layer.
- Hard rules are barriers the model cannot bypass. They live in code under
  `src/dental_harness/guardrails/` and are expressed as data in `policy.yaml`.
  Every tool call routes through one enforcement entry point before the tool
  runs.

## Single enforcement entry point

`GuardrailEngine.evaluate(call, approved=...)` in `guardrails/engine.py`. The
agent loop calls it for every tool call in `loop.py::AgentLoop._run_tool`. The
tool's callback runs only if the engine returns an allow. A block or a hold
short-circuits before the callback. No tool may bypass this path, and per the
project constitution no tool may be added unless it routes through this layer.

Barriers run fail-closed and in this order. The first one that fires wins:

1. scope, 2. clinical advice, 3. PHI egress, 4. human approval.

Outcomes are `allow`, `block` (refused), and `hold` (kept, pending human
approval, nothing sent).

## The four hard rules

### Rule 1: PHI egress control
- Type: hard.
- Mechanism: `phi_egress_barrier` blocks any outbound action that is not
  authorized to carry PHI when the payload contains patient-identifying data.
  Authorization is per action in `policy.yaml` (`actions.*.phi_egress_authorized`).
  Detection is pattern-based for free text (SSN, phone, email, date of birth,
  MRN) in `redaction.py`. The same module redacts PHI from every log line
  through the lifecycle hooks, so PHI never lands in `logs/` either.
- Note: free-text personal names are not reliably pattern-detectable. That gap
  is backstopped by the human-approval gate (Rule 4): no outbound action leaves
  without a person reviewing it.

### Rule 2: Clinical-advice gate
- Type: hard.
- Mechanism: `clinical_advice_barrier` scans the call's text for requests or
  content involving diagnosis, treatment recommendation, prognosis, or clinical
  judgment, using the case-insensitive patterns in `policy.yaml`
  (`clinical_advice.patterns`). On a match it blocks and routes to a licensed
  clinician (`clinical_advice.route_to`). The patient-facing wording is the
  brand-voice refusal in `knowledge/templates/refusals.md`.

### Rule 3: Scope enforcement
- Type: hard.
- Mechanism: `scope_barrier` allows only actions on the allowlist
  (`scope.allowlist` in `policy.yaml`). Anything else is blocked by default.
  Approval does not widen scope.

### Rule 4: Human-approval gate
- Type: hard.
- Mechanism: `approval_barrier` holds any action whose attributes match
  `approval.require_for` (outbound or state-changing) unless it has been
  explicitly approved for that run. Without approval the action is held, not
  sent. The loop never auto-approves: `AgentLoop.approved_actions` is empty by
  default.

## Soft rules, for contrast (not enforced here)

| Concern                     | Type | Where enforced                          |
| --------------------------- | ---- | --------------------------------------- |
| Tone and voice              | Soft | tool descriptions, `knowledge/voice/`   |
| Escalation phrasing         | Soft | tool descriptions, system prompt        |
| Formatting and brand palette| Soft | `knowledge/brand/`, refusal templates   |
| Per-doctor preferences      | Soft | `knowledge/doctors/`                    |

## Policy as data

All thresholds, the allowlist, action attributes, PHI patterns and fields,
clinical patterns, and the refusal wording live in
`src/dental_harness/guardrails/policy.yaml`. A rule can be reviewed and changed
there without touching enforcement code. The code in `policy.py`, `barriers.py`,
`redaction.py`, and `engine.py` reads that data and applies it.

## Tests

`tests/test_guardrails.py` proves each barrier blocks exactly what it should and
allows what it should, including adversarial inputs: lookalike and injected tool
names, case tricks and prompt injection aimed at the clinical gate, PHI in
several formats including parenthesized and spaced phone numbers, approval
bypass attempts, and barrier-ordering checks. Run them with `pytest`.

## Known limitations

- Free-text personal names are not pattern-detected for egress. Mitigated by
  the approval gate.
- Clinical-advice detection is lexical. Heavy obfuscation (for example letters
  spaced apart) can evade the patterns. The approval gate and scope limits
  reduce the blast radius, and the pattern list is data and can be tightened.
- No PHI and no real systems at this stage. Synthetic data only until this
  layer is validated.
