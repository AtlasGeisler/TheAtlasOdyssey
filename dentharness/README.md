# DentHarness

A **vendor-neutral** harness for building a dental practice agent. The agent,
its tools, and its data models never touch a specific practice-management
system (PMS). Everything goes through one small interface — `PMSAdapter` — so
you can **be your own vendor**: implement that interface against whatever
backend you have, register it, and the whole harness runs unchanged.

## Layout

```
dentharness/
  pms/
    models.py      # vendor-neutral Patient / Appointment / LedgerEntry
    adapter.py     # PMSAdapter Protocol — the one seam
    mock.py        # MockPMS — reference impl + template (in-memory seed data)
    registry.py    # name -> adapter factory; selects via env or arg
  agent/
    tools.py       # validated tool wrappers + Anthropic tool schemas
    loop.py        # tool-use loop, model client injected (no SDK dependency)
  cli.py           # exercise adapters without an LLM
  tests/           # mock PMS + agent loop, fully offline
```

## Try it (no LLM, no dependencies)

```bash
python -m dentharness.cli patients Lovelace
python -m dentharness.cli ledger P1
python -m dentharness.cli appts P1
```

## Run the tests

```bash
pip install pytest
pytest dentharness/tests -q
```

## Be your own vendor

1. Write a class implementing the five `PMSAdapter` methods
   (`get_patient`, `find_patients`, `get_appointments`, `get_ledger`,
   `post_ledger_entry`), translating your data into the `pms/models.py` types.
   Copy `mock.py` as a starting point.
2. Register it:

   ```python
   from dentharness.pms import register
   register("mine", MyPMS)
   ```

3. Select it with `DENTHARNESS_PMS=mine` or `get_pms("mine")`.

Nothing above the adapter changes. Open Dental, Dentrix, Eaglesoft, a SQL
view, or a CSV export are all just more adapters — and several can coexist.

## Wiring a real model

`agent/loop.py` injects a `ModelClient`. Provide one backed by the Anthropic
SDK (default to a current Claude model such as `claude-opus-4-8` or
`claude-sonnet-4-6`), translating its tool-use blocks into the loop's
`AssistantTurn` / `ToolCall`. Tests use a scripted fake instead, so the loop
logic is verified without any network calls.

See `DESIGN.md` for the rationale.
