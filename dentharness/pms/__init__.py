"""Vendor-neutral practice-management-system layer."""

from .adapter import PMSAdapter, PMSError, PatientNotFound
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
    "Patient",
    "Appointment",
    "AppointmentStatus",
    "LedgerEntry",
    "LedgerEntryDraft",
    "get_pms",
    "register",
    "available",
]
