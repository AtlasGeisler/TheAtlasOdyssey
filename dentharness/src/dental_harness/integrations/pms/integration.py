"""The PMS integration: exposes the adapter as a set of tools.

This is the first concrete Integration. It binds a PMSAdapter and presents
read and write operations as four-part tools. Output structure is enforced
through each tool's input schema (Principle 6). All data is synthetic.
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal, InvalidOperation
from typing import Any

from ...tools.base import Tool
from ..base import Integration
from .adapter import PatientNotFound
from .models import Appointment, LedgerEntry, LedgerEntryDraft, Patient
from .registry import get_pms


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


class PMSIntegration(Integration):
    name = "pms"

    def __init__(self, adapter_name: str | None = None) -> None:
        self.pms = get_pms(adapter_name)

    # -- tool callbacks -------------------------------------------------

    def _find_patients(self, query: str) -> dict[str, Any]:
        return {"patients": [_patient_dict(p) for p in self.pms.find_patients(query)]}

    def _get_patient(self, patient_id: str) -> dict[str, Any]:
        try:
            return _patient_dict(self.pms.get_patient(patient_id))
        except PatientNotFound as exc:
            return {"error": str(exc)}

    def _get_appointments(
        self, patient_id: str, on: str | None = None
    ) -> dict[str, Any]:
        try:
            on_date = date.fromisoformat(on) if on else None
            appts = self.pms.get_appointments(patient_id, on=on_date)
        except PatientNotFound as exc:
            return {"error": str(exc)}
        return {"appointments": [_appt_dict(a) for a in appts]}

    def _get_ledger(self, patient_id: str) -> dict[str, Any]:
        try:
            entries = self.pms.get_ledger(patient_id)
        except PatientNotFound as exc:
            return {"error": str(exc)}
        balance = sum((e.amount for e in entries), Decimal("0"))
        return {
            "entries": [_ledger_dict(e) for e in entries],
            "balance": str(balance),
        }

    def _post_ledger_entry(
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
        try:
            entry = self.pms.post_ledger_entry(
                LedgerEntryDraft(
                    patient_id=patient_id,
                    amount=value,
                    description=description,
                    code=code,
                )
            )
        except PatientNotFound as exc:
            return {"error": str(exc)}
        return {"posted": _ledger_dict(entry)}

    # -- Integration ----------------------------------------------------

    def get_tools(self) -> list[Tool]:
        return [
            Tool(
                name="pms_find_patients",
                description=(
                    "Search the practice management system for patients by "
                    "name, phone, or email. Returns a list of matching "
                    "patients with their ids. Use this first when you only "
                    "have a name. All data is synthetic."
                ),
                input_schema={
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "Name, phone, or email fragment.",
                        }
                    },
                    "required": ["query"],
                },
                callback=self._find_patients,
            ),
            Tool(
                name="pms_get_patient",
                description=(
                    "Fetch a single patient record by its id. Use after "
                    "pms_find_patients to confirm identity."
                ),
                input_schema={
                    "type": "object",
                    "properties": {
                        "patient_id": {"type": "string"},
                    },
                    "required": ["patient_id"],
                },
                callback=self._get_patient,
            ),
            Tool(
                name="pms_get_appointments",
                description=(
                    "List a patient's appointments. Optionally restrict to a "
                    "single calendar day with 'on' in YYYY-MM-DD format."
                ),
                input_schema={
                    "type": "object",
                    "properties": {
                        "patient_id": {"type": "string"},
                        "on": {
                            "type": "string",
                            "description": "Optional ISO date filter, YYYY-MM-DD.",
                        },
                    },
                    "required": ["patient_id"],
                },
                callback=self._get_appointments,
            ),
            Tool(
                name="pms_get_ledger",
                description=(
                    "Get a patient's full ledger history and current balance. "
                    "Positive amounts are charges, negative amounts are "
                    "payments or credits."
                ),
                input_schema={
                    "type": "object",
                    "properties": {
                        "patient_id": {"type": "string"},
                    },
                    "required": ["patient_id"],
                },
                callback=self._get_ledger,
            ),
            Tool(
                name="pms_post_ledger_entry",
                description=(
                    "Post a charge (positive amount) or a payment or credit "
                    "(negative amount) to a patient's ledger. This is a write. "
                    "Confirm patient identity before calling. Amount is a "
                    "decimal string, for example '125.00' or '-50.00'."
                ),
                input_schema={
                    "type": "object",
                    "properties": {
                        "patient_id": {"type": "string"},
                        "amount": {
                            "type": "string",
                            "description": "Decimal as a string.",
                        },
                        "description": {"type": "string"},
                        "code": {
                            "type": "string",
                            "description": "Optional CDT procedure code.",
                        },
                    },
                    "required": ["patient_id", "amount", "description"],
                },
                callback=self._post_ledger_entry,
            ),
        ]
