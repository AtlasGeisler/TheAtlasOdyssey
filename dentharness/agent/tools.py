"""Agent-callable tools.

Each tool is a thin, validated wrapper over the PMSAdapter. Tools return
plain JSON-serializable dicts so they can feed straight into a model's
tool-use loop (Anthropic tool use, or any other). The TOOL_SCHEMAS list is
the Anthropic-format declaration you hand to the API.
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal, InvalidOperation
from typing import Any, Callable

from ..pms import LedgerEntryDraft, PMSAdapter
from ..pms.adapter import PatientNotFound
from ..pms.models import Appointment, LedgerEntry, Patient


def _patient_dict(p: Patient) -> dict[str, Any]:
    return {
        "id": p.id,
        "name": p.full_name,
        "date_of_birth": p.date_of_birth.isoformat() if p.date_of_birth else None,
        "phone": p.phone,
        "email": p.email,
    }


def _appt_dict(a: Appointment) -> dict[str, Any]:
    return {
        "id": a.id,
        "patient_id": a.patient_id,
        "start": a.start.isoformat(),
        "end": a.end.isoformat(),
        "provider": a.provider,
        "status": a.status.value,
        "operatory": a.operatory,
        "notes": a.notes,
    }


def _ledger_dict(e: LedgerEntry) -> dict[str, Any]:
    return {
        "id": e.id,
        "patient_id": e.patient_id,
        "posted_at": e.posted_at.isoformat(),
        "amount": str(e.amount),
        "description": e.description,
        "code": e.code,
    }


class Toolbox:
    """Binds a PMS adapter to the callable tool implementations."""

    def __init__(self, pms: PMSAdapter) -> None:
        self.pms = pms

    def find_patients(self, query: str) -> dict[str, Any]:
        results = self.pms.find_patients(query)
        return {"patients": [_patient_dict(p) for p in results]}

    def get_patient(self, patient_id: str) -> dict[str, Any]:
        return _patient_dict(self.pms.get_patient(patient_id))

    def get_appointments(
        self, patient_id: str, on: str | None = None
    ) -> dict[str, Any]:
        on_date = date.fromisoformat(on) if on else None
        appts = self.pms.get_appointments(patient_id, on=on_date)
        return {"appointments": [_appt_dict(a) for a in appts]}

    def get_ledger(self, patient_id: str) -> dict[str, Any]:
        entries = self.pms.get_ledger(patient_id)
        balance = sum((e.amount for e in entries), Decimal("0"))
        return {
            "entries": [_ledger_dict(e) for e in entries],
            "balance": str(balance),
        }

    def post_ledger_entry(
        self,
        patient_id: str,
        amount: str,
        description: str,
        code: str | None = None,
    ) -> dict[str, Any]:
        try:
            value = Decimal(amount)
        except (InvalidOperation, TypeError):
            return {"error": f"amount {amount!r} is not a valid number"}
        entry = self.pms.post_ledger_entry(
            LedgerEntryDraft(
                patient_id=patient_id,
                amount=value,
                description=description,
                code=code,
            )
        )
        return {"posted": _ledger_dict(entry)}

    # -- dispatch -------------------------------------------------------

    def dispatch(self, name: str, arguments: dict[str, Any]) -> dict[str, Any]:
        fn: Callable[..., dict[str, Any]] | None = getattr(self, name, None)
        if fn is None or name not in _TOOL_NAMES:
            return {"error": f"unknown tool {name!r}"}
        try:
            return fn(**arguments)
        except PatientNotFound as exc:
            return {"error": str(exc)}
        except TypeError as exc:
            return {"error": f"bad arguments for {name}: {exc}"}


# Anthropic tool-use schema declarations.
TOOL_SCHEMAS: list[dict[str, Any]] = [
    {
        "name": "find_patients",
        "description": "Search for patients by name, phone, or email.",
        "input_schema": {
            "type": "object",
            "properties": {"query": {"type": "string"}},
            "required": ["query"],
        },
    },
    {
        "name": "get_patient",
        "description": "Fetch a single patient by id.",
        "input_schema": {
            "type": "object",
            "properties": {"patient_id": {"type": "string"}},
            "required": ["patient_id"],
        },
    },
    {
        "name": "get_appointments",
        "description": "List a patient's appointments, optionally for one day (YYYY-MM-DD).",
        "input_schema": {
            "type": "object",
            "properties": {
                "patient_id": {"type": "string"},
                "on": {"type": "string", "description": "ISO date filter"},
            },
            "required": ["patient_id"],
        },
    },
    {
        "name": "get_ledger",
        "description": "Get a patient's ledger history and current balance.",
        "input_schema": {
            "type": "object",
            "properties": {"patient_id": {"type": "string"}},
            "required": ["patient_id"],
        },
    },
    {
        "name": "post_ledger_entry",
        "description": (
            "Post a charge (positive amount) or payment/credit (negative "
            "amount) to a patient's ledger."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "patient_id": {"type": "string"},
                "amount": {"type": "string", "description": "Decimal as string"},
                "description": {"type": "string"},
                "code": {"type": "string", "description": "Optional CDT code"},
            },
            "required": ["patient_id", "amount", "description"],
        },
    },
]

_TOOL_NAMES = {schema["name"] for schema in TOOL_SCHEMAS}
