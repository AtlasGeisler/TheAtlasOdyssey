"""Practice management system integration (vendor-neutral)."""

from .adapter import PMSAdapter, PMSError, PatientNotFound
from .integration import PMSIntegration
from .models import (
    Appointment,
    AppointmentStatus,
    LedgerEntry,
    LedgerEntryDraft,
    Patient,
)
from .registry import available, get_pms, register

__all__ = [
    "PMSAdapter",
    "PMSError",
    "PatientNotFound",
    "PMSIntegration",
    "Patient",
    "Appointment",
    "AppointmentStatus",
    "LedgerEntry",
    "LedgerEntryDraft",
    "get_pms",
    "register",
    "available",
]
