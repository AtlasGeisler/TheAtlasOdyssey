"""The vendor-neutral PMS interface.

This is the single seam between the agent and any practice-management system.
Implement this Protocol and the entire harness runs on your backend with no
changes anywhere else. You can be your own vendor: write a class with these
methods, register it, done. Open Dental, Dentrix, Eaglesoft, a flat-file
export, or a direct SQL view are all just additional implementations.
"""

from __future__ import annotations

from datetime import date
from typing import Protocol, Sequence, runtime_checkable

from .models import Appointment, LedgerEntry, LedgerEntryDraft, Patient


@runtime_checkable
class PMSAdapter(Protocol):
    """Minimal read/write surface a dental PMS must expose to the agent."""

    name: str

    def get_patient(self, patient_id: str) -> Patient:
        """Return a single patient. Raise PatientNotFound if absent."""
        ...

    def find_patients(self, query: str) -> Sequence[Patient]:
        """Search patients by name/phone/email. May return an empty list."""
        ...

    def get_appointments(
        self, patient_id: str, *, on: date | None = None
    ) -> Sequence[Appointment]:
        """Appointments for a patient, optionally filtered to a single day."""
        ...

    def get_ledger(self, patient_id: str) -> Sequence[LedgerEntry]:
        """Full ledger history for a patient, oldest first."""
        ...

    def post_ledger_entry(self, draft: LedgerEntryDraft) -> LedgerEntry:
        """Post a charge or payment. Returns the persisted entry with id."""
        ...


class PMSError(Exception):
    """Base class for adapter-raised errors."""


class PatientNotFound(PMSError):
    def __init__(self, patient_id: str) -> None:
        super().__init__(f"No patient with id {patient_id!r}")
        self.patient_id = patient_id
