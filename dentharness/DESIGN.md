# DentHarness — design notes

## Goal

A dental agent you own end to end, not locked to any single PMS vendor. The
defining constraint: **exactly one seam** between the agent and the outside
world, so the vendor is a swappable detail.

## The seam: `PMSAdapter`

`pms/adapter.py` defines a `Protocol` with five methods. Everything the agent
can do to a practice management system is expressed there in vendor-neutral
terms. Two consequences:

- **You can be your own vendor.** Implement the Protocol against your own
  database/API and the agent runs on it with zero changes elsewhere.
- **Multiple vendors coexist.** Open Dental, Dentrix, etc. are each just
  another implementation; the registry picks one at runtime.

`@runtime_checkable` means `isinstance(x, PMSAdapter)` works for quick checks,
but the real contract is the method signatures + the `pms/models.py` types.

## Canonical models

`pms/models.py` holds frozen dataclasses (`Patient`, `Appointment`,
`LedgerEntry`, ...). Adapters translate vendor data *into* these, so nothing
above the adapter ever sees a vendor field. Money is `Decimal`; ledger
amounts are signed (+charge / −payment) to keep balance math trivial and
exact.

## Tools vs. adapter

`agent/tools.py` is deliberately thin: validate/parse arguments, call the
adapter, return JSON-serializable dicts. Keeping business rules out of the
tools means a new vendor only implements data access, not policy. The
`TOOL_SCHEMAS` are Anthropic tool-use declarations; `Toolbox.dispatch` routes
a tool name + args to the implementation and turns adapter errors into
structured `{"error": ...}` results the model can react to.

## The loop

`agent/loop.py` is a standard tool-use loop with the **model client
injected** (`ModelClient` Protocol). This keeps the loop SDK-free and
trivially testable: production passes an Anthropic-backed client; tests pass a
scripted fake. A `max_turns` guard prevents runaway tool loops. When wiring
the real client, default to a current Claude model (`claude-opus-4-8` /
`claude-sonnet-4-6`).

## Testing

All tests are offline. `test_mock_pms.py` covers the reference adapter and
registry; `test_agent_loop.py` drives the loop with a scripted client,
asserting tool results are fed back and that the turn limit holds.

## Safety posture

The system prompt forbids inventing patient data (always call a tool) and
requires confirming identity before posting ledger entries. Writes are
funneled through the single `post_ledger_entry` method, the natural place to
add audit logging, authz, or a human-approval gate.

## Deliberately out of scope (next steps)

- Real adapter(s) for a production PMS.
- Authn/authz and per-user scoping.
- Audit log + approval workflow on writes.
- Scheduling writes (create/reschedule/cancel appointments).
- PHI handling / HIPAA controls before any real patient data.
